"""Task 1 / W01-W09: outdoor snapshot handling of missing, zero, and time data."""

from __future__ import annotations

import unittest

from _support import load_script

outdoor = load_script("build_outdoor_risk_pages")

MILD = [
    {"name": "Today", "startTime": "2026-09-28T06:00:00-07:00", "endTime": "2026-09-28T18:00:00-07:00",
     "temperature": 65, "temperatureUnit": "F", "windSpeed": "5 mph", "shortForecast": "Sunny",
     "probabilityOfPrecipitation": {"value": 10}},
    {"name": "Tonight", "startTime": "2026-09-28T18:00:00-07:00", "endTime": "2026-09-29T06:00:00-07:00",
     "temperature": 55, "temperatureUnit": "F", "windSpeed": "5 mph", "shortForecast": "Clear",
     "probabilityOfPrecipitation": {"value": None}},
]
GOOD_AIR = [{"ReportingArea": "Area", "ParameterName": "PM2.5", "AQI": 20, "Category": {"Name": "Good"},
             "DateObserved": "2026-09-28 ", "HourObserved": 11, "LocalTimeZone": "PST"}]
LOCATION = outdoor.LOCATIONS["seattle-dog-rain-walk-risk"]


def page_for(periods, air, meta=None):
    return outdoor.build_page("seattle-dog-rain-walk-risk", LOCATION, periods, meta or {}, air)


class MissingData(unittest.TestCase):
    def test_w01_empty_weather_and_air_is_not_low(self):
        level, reasons = outdoor.risk_score([], [])
        self.assertEqual(level, "unavailable")
        self.assertNotIn("no major stressor", " ".join(reasons))
        page = page_for([], [])
        html = outdoor.render_page(page["slug"], page, "2026-09-29T04:00:00+09:00")
        self.assertIn("Data unavailable", html)
        self.assertNotIn("Planning label: Low", html)
        self.assertIn("No NWS forecast period returned", html)

    def test_w02_weather_without_aqi_is_incomplete(self):
        level, reasons = outdoor.risk_score(MILD, [])
        self.assertEqual(level, "incomplete")
        self.assertTrue(any("AirNow" in r for r in reasons))
        page = page_for(MILD, [])
        self.assertEqual(page["data_status"], {"weather": "available", "air_quality": "unavailable", "overall": "partial"})
        html = outdoor.render_page(page["slug"], page, "x")
        self.assertIn("65F", html)
        self.assertIn("no overall planning label", html)

    def test_negative_aqi_sentinel_is_missing(self):
        level, _ = outdoor.risk_score(MILD, [{"AQI": -1}])
        self.assertEqual(level, "incomplete")

    def test_complete_mild_snapshot_is_low_with_neutral_wording(self):
        level, reasons = outdoor.risk_score(MILD, GOOD_AIR)
        self.assertEqual(level, "low")
        self.assertEqual(reasons, ["no listed input crossed the site's planning thresholds"])


class ZeroAndUnits(unittest.TestCase):
    def test_w03_zero_temperature_and_zero_aqi_are_displayed(self):
        periods = [dict(MILD[0], temperature=0)]
        air = [dict(GOOD_AIR[0], AQI=0)]
        page = page_for(periods, air)
        self.assertEqual(page["airnow"][0]["aqi"], 0)
        html = outdoor.render_page(page["slug"], page, "x")
        self.assertIn("<td>0F</td>", html)
        self.assertRegex(html, r"<td>PM2\.5</td><td>0</td>")
        level, reasons = outdoor.risk_score(periods, air)
        self.assertEqual(level, "moderate")  # 0F crosses the cold threshold (3 points)
        self.assertIn("cold low near 0F", reasons)

    def test_w04_units_and_invalid_values(self):
        celsius = [dict(MILD[0], temperature=36, temperatureUnit="C")]
        level, reasons = outdoor.risk_score(celsius, GOOD_AIR)
        self.assertIn("forecast high near 96.8F", reasons)
        self.assertEqual(level, "moderate")
        for bad in ("70", float("nan"), float("inf"), True, None):
            with self.subTest(bad=bad):
                self.assertIsNone(outdoor.temperature_f({"temperature": bad, "temperatureUnit": "F"}))
        self.assertIsNone(outdoor.temperature_f({"temperature": 70, "temperatureUnit": "K"}))
        self.assertEqual(outdoor.risk_score([{"temperature": "70"}], GOOD_AIR)[0], "unavailable")
        self.assertEqual(outdoor.temperature_f({"temperature": 70.5, "temperatureUnit": "F"}), 70.5)


class PeriodsAndTimes(unittest.TestCase):
    def test_w05_every_evaluated_period_is_displayed(self):
        periods = [dict(MILD[0], name=f"P{i}") for i in range(outdoor.FORECAST_PERIODS - 1)]
        periods.append(dict(MILD[0], name="Last", temperature=99))
        level, reasons = outdoor.risk_score(periods, GOOD_AIR)
        self.assertIn("forecast high near 99F", reasons)
        page = page_for(periods, GOOD_AIR)
        html = outdoor.render_page(page["slug"], page, "x")
        self.assertIn("Last (Sep 28", html)
        self.assertIn("<td>99F</td>", html)

    def test_w06_w07_times_are_preserved_and_shown(self):
        page = page_for(MILD, GOOD_AIR, {"generatedAt": "2026-09-28T10:00:00+00:00"})
        self.assertEqual(page["nws_periods"][0]["startTime"], "2026-09-28T06:00:00-07:00")
        self.assertEqual(page["airnow"][0]["localTimeZone"], "PST")
        html = outdoor.render_page(page["slug"], page, "2026-09-29T04:00:00+09:00")
        self.assertIn("Today (Sep 28, 06:00 local, UTC-07:00)", html)
        self.assertIn("2026-09-28 11:00 PST", html)
        self.assertIn("NWS forecast generated 2026-09-28T10:00:00+00:00", html)
        self.assertIn("not a live reading", html)

    def test_legacy_snapshot_without_times_still_renders(self):
        legacy = {**LOCATION, "slug": "s", "risk_level": "low", "reasons": ["r"],
                  "nws_periods": [{"name": "Today", "temperature": 65, "temperatureUnit": "F"}],
                  "airnow": [{"parameter": "O3", "aqi": 10, "dateObserved": "2026-09-28", "hourObserved": 11}]}
        html = outdoor.render_page("s", legacy, "x")
        self.assertIn("<td>Today</td>", html)
        self.assertIn("2026-09-28 11:00", html)


class DatasetValidation(unittest.TestCase):
    def full_dataset(self, **override):
        pages = {slug: outdoor.build_page(slug, loc, MILD, {}, GOOD_AIR) for slug, loc in outdoor.LOCATIONS.items()}
        pages.update(override)
        return {"updated": "t", "pages": pages}

    def test_w08_invalid_dataset_is_rejected_before_writing(self):
        with self.assertRaises(RuntimeError):
            outdoor.validate_dataset({"updated": "t", "pages": {}})
        ds = self.full_dataset()
        del ds["pages"]["seattle-dog-rain-walk-risk"]
        with self.assertRaises(RuntimeError):
            outdoor.validate_dataset(ds)
        bad = dict(page_for([], []), risk_level="low")
        with self.assertRaises(RuntimeError):
            outdoor.validate_dataset(self.full_dataset(**{"seattle-dog-rain-walk-risk": bad}))
        outdoor.validate_dataset(self.full_dataset())

    def test_w09_label_is_described_as_site_label_not_official(self):
        page = page_for(MILD, GOOD_AIR)
        sentence = outdoor.risk_sentence(page)
        self.assertIn("not an official warning or safety rating", sentence)
        index = outdoor.render_index(self.full_dataset())
        self.assertIn("Missing inputs are never counted as good conditions", index)

    def test_db_contract_risk_level_never_null(self):
        for periods, air in (([], []), (MILD, []), (MILD, GOOD_AIR)):
            self.assertIn(page_for(periods, air)["risk_level"], outdoor.RISK_LEVELS)


class SecretRedaction(unittest.TestCase):
    def test_a06_api_key_is_redacted(self):
        url = "https://www.airnowapi.org/aq/observation/zipCode/current/?format=json&zipCode=1&API_KEY=SECRET123"
        redacted = outdoor.redact_url(url)
        self.assertNotIn("SECRET123", redacted)
        self.assertIn("zipCode=1", redacted)


if __name__ == "__main__":
    unittest.main()
