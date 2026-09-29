"""Task 2 / B01-B08: BLS normalization defenses."""

from __future__ import annotations

import copy
import unittest

from _support import load_script

bls = load_script("build_bls_cost_pages")

FOOD, SUPPLIES, SERVICES = (item["series_id"] for item in bls.SERIES.values())


def row(year, month, value, footnotes=None, calc=None):
    period = "M13" if month == 13 else f"M{month:02d}"
    name = "Annual" if month == 13 else bls.MONTH_NAMES[month - 1]
    out = {"year": str(year), "period": period, "periodName": name, "value": str(value), "footnotes": footnotes or [{}]}
    if calc:
        out["calculations"] = {"pct_changes": calc}
    return out


def series(series_id, rows):
    return {"seriesID": series_id, "catalog": {"series_title": "t"}, "data": rows}


def good_rows():
    return [row(2026, m, 200 + m) for m in range(8, 0, -1)] + [row(2025, m, 190 + m) for m in range(12, 0, -1)]


def raw(*items):
    return {"status": "REQUEST_SUCCEEDED", "Results": {"series": list(items)}}


def full_raw():
    return raw(series(FOOD, good_rows()), series(SUPPLIES, good_rows()), series(SERVICES, good_rows()))


class Normalization(unittest.TestCase):
    def test_b01_empty_rows_is_structured_error(self):
        with self.assertRaises(bls.BLSDataError):
            bls.normalize_data(raw(series(FOOD, [])))

    def test_b02_empty_series_list_never_yields_empty_hub(self):
        with self.assertRaises(bls.BLSDataError):
            bls.normalize_data(raw())
        with self.assertRaises(bls.BLSDataError):
            bls.validate_dataset({"pages": {}})

    def test_b03_missing_series_is_partial_and_keeps_previous(self):
        previous = bls.normalize_data(full_raw())
        result = bls.normalize_data(raw(series(FOOD, good_rows()), series(SUPPLIES, [])), previous)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["missing_series"], ["pet-supplies-inflation", "pet-services-inflation"])
        self.assertEqual(result["pages"]["pet-supplies-inflation"]["status"], "stale")
        self.assertEqual(result["pages"]["pet-food-inflation"]["status"], "available")
        html = bls.render_page("pet-supplies-inflation", result["pages"]["pet-supplies-inflation"], result["updated"])
        self.assertIn("keeps the previous saved reading", html)
        # Without a previous snapshot, the missing series is omitted, not faked.
        alone = bls.normalize_data(raw(series(FOOD, good_rows())))
        self.assertEqual(list(alone["pages"]), ["pet-food-inflation"])

    def test_b04_m13_is_excluded_from_monthly_data(self):
        rows = [row(2026, 13, 280)] + good_rows()
        page = bls.normalize_data(raw(series(FOOD, rows)))["pages"]["pet-food-inflation"]
        self.assertEqual(page["latest"]["period"], "August")
        self.assertTrue(all(h["period_code"] != "M13" for h in page["history"]))

    def test_b05_unsorted_rows_pick_newest_month(self):
        rows = list(reversed(good_rows()))
        page = bls.normalize_data(raw(series(FOOD, rows)))["pages"]["pet-food-inflation"]
        self.assertEqual((page["latest"]["year"], page["latest"]["period"]), ("2026", "August"))
        self.assertEqual(page["history"][1]["period"], "July")

    def test_b06_yoy_unavailable_without_same_month_prior_year(self):
        rows = [row(2026, m, 200 + m) for m in range(8, 0, -1)]
        page = bls.normalize_data(raw(series(FOOD, rows)))["pages"]["pet-food-inflation"]
        self.assertIsNone(page["latest"]["year_over_year_same_month"])
        html = bls.render_page("pet-food-inflation", page, "2026-09-23")
        self.assertIn("year-over-year calculation from the downloaded series is not available", html)
        # Zero / dash / non-numeric values are not valid denominators.
        rows = [row(2026, 8, 210), {"year": "2025", "period": "M08", "value": "0"}, {"year": "2025", "period": "M07", "value": "-"}]
        page = bls.normalize_data(raw(series(FOOD, rows)))["pages"]["pet-food-inflation"]
        self.assertIsNone(page["latest"]["year_over_year_same_month"])
        self.assertEqual(len(page["history"]), 1)

    def test_b07_footnotes_and_gaps_are_preserved(self):
        rows = [row(2026, 8, 210, [{"code": "P", "text": "Preliminary"}]), row(2026, 6, 205), row(2026, 5, 204)]
        page = bls.normalize_data(raw(series(FOOD, rows)))["pages"]["pet-food-inflation"]
        self.assertEqual(page["latest"]["footnotes"], ["Preliminary"])
        self.assertEqual(page["missing_months"], ["July 2026"])
        html = bls.render_page("pet-food-inflation", page, "2026-09-23")
        self.assertIn("Preliminary", html)
        self.assertIn("No reading was returned for July 2026", html)

    def test_b08_same_input_keeps_update_date(self):
        first = bls.normalize_data(full_raw())
        first["updated"] = "2026-01-01"
        second = bls.normalize_data(full_raw(), copy.deepcopy(first))
        self.assertEqual(second["updated"], "2026-01-01")
        self.assertEqual(second["pages"], first["pages"])
        changed = full_raw()
        changed["Results"]["series"][0]["data"][0]["value"] = "999"
        third = bls.normalize_data(changed, copy.deepcopy(first))
        self.assertNotEqual(third["updated"], "2026-01-01")

    def test_duplicates_are_ignored(self):
        rows = [row(2026, 8, 210), row(2026, 8, 999)] + good_rows()[1:]
        page = bls.normalize_data(raw(series(FOOD, rows)))["pages"]["pet-food-inflation"]
        self.assertEqual(page["latest"]["value"], "210")

    def test_legacy_snapshot_renders(self):
        import json
        legacy = json.loads((bls.DATA_DIR / "bls_pet_cost_cpi.json").read_text(encoding="utf-8"))
        bls.validate_dataset(legacy)
        for slug, page in legacy["pages"].items():
            self.assertIn("Recent BLS readings", bls.render_page(slug, page, legacy["updated"]))


if __name__ == "__main__":
    unittest.main()
