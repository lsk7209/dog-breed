const fs = require("fs");
const path = require("path");
const { createClient } = require("@libsql/client");

const root = path.resolve(__dirname, "..");

function readSecret(envName, fallbackPath) {
  const fromEnv = process.env[envName];
  if (fromEnv && fromEnv.trim()) return fromEnv.trim();
  if (fallbackPath && fs.existsSync(fallbackPath)) {
    return fs.readFileSync(fallbackPath, "utf8").trim();
  }
  throw new Error(`${envName} is missing`);
}

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function periodNumber(period) {
  const months = {
    January: "M01",
    February: "M02",
    March: "M03",
    April: "M04",
    May: "M05",
    June: "M06",
    July: "M07",
    August: "M08",
    September: "M09",
    October: "M10",
    November: "M11",
    December: "M12",
  };
  return months[period] || period;
}

async function ensureSchema(db) {
  await db.batch(
    [
      `create table if not exists public_data_snapshots (
        source text not null,
        snapshot_date text not null,
        payload_json text not null,
        synced_at text not null,
        primary key (source, snapshot_date)
      )`,
      `create table if not exists bls_pet_cpi_observations (
        series_id text not null,
        slug text not null,
        item text not null,
        year integer not null,
        period text not null,
        period_name text not null,
        value real not null,
        updated_at text not null,
        primary key (series_id, year, period)
      )`,
      `create table if not exists api_health_checks (
        provider text not null,
        checked_at text not null,
        ok integer not null,
        details_json text not null,
        primary key (provider, checked_at)
      )`,
    ],
    "write",
  );
}

async function syncBls(db, syncedAt) {
  const data = readJson("data/bls_pet_cost_cpi.json");
  await db.execute({
    sql: `insert into public_data_snapshots (source, snapshot_date, payload_json, synced_at)
          values (?, ?, ?, ?)
          on conflict(source, snapshot_date) do update set payload_json = excluded.payload_json, synced_at = excluded.synced_at`,
    args: ["bls_pet_cost_cpi", data.updated, JSON.stringify(data), syncedAt],
  });

  let rows = 0;
  for (const [slug, page] of Object.entries(data.pages || {})) {
    const item = page.catalog?.item || page.title || slug;
    for (const row of page.history || []) {
      await db.execute({
        sql: `insert into bls_pet_cpi_observations
              (series_id, slug, item, year, period, period_name, value, updated_at)
              values (?, ?, ?, ?, ?, ?, ?, ?)
              on conflict(series_id, year, period) do update set
                slug = excluded.slug,
                item = excluded.item,
                period_name = excluded.period_name,
                value = excluded.value,
                updated_at = excluded.updated_at`,
        args: [
          page.series_id,
          slug,
          item,
          Number(row.year),
          periodNumber(row.period),
          row.period,
          Number(row.value),
          syncedAt,
        ],
      });
      rows += 1;
    }
  }
  return { snapshot: data.updated, rows };
}

async function syncApiStatus(db, syncedAt) {
  const statusPath = path.join(root, "data/public_api_status.json");
  if (!fs.existsSync(statusPath)) return { checks: 0, skipped: true };

  const data = readJson("data/public_api_status.json");
  await db.execute({
    sql: `insert into public_data_snapshots (source, snapshot_date, payload_json, synced_at)
          values (?, ?, ?, ?)
          on conflict(source, snapshot_date) do update set payload_json = excluded.payload_json, synced_at = excluded.synced_at`,
    args: ["public_api_status", data.checked_at, JSON.stringify(data), syncedAt],
  });

  let checks = 0;
  for (const [provider, details] of Object.entries(data.checks || {})) {
    await db.execute({
      sql: `insert into api_health_checks (provider, checked_at, ok, details_json)
            values (?, ?, ?, ?)
            on conflict(provider, checked_at) do update set
              ok = excluded.ok,
              details_json = excluded.details_json`,
      args: [provider, data.checked_at, details.ok ? 1 : 0, JSON.stringify(details)],
    });
    checks += 1;
  }
  return { checked_at: data.checked_at, checks };
}

async function main() {
  const url = readSecret("TURSO_DATABASE_URL", "D:/env/turso_database_url.txt");
  const authToken = readSecret("TURSO_AUTH_TOKEN", "D:/env/turso_auth_token.txt");
  const db = createClient({ url, authToken });
  const syncedAt = new Date().toISOString();

  await ensureSchema(db);
  const bls = await syncBls(db, syncedAt);
  const apiStatus = await syncApiStatus(db, syncedAt);
  const check = await db.execute("select count(*) as count from bls_pet_cpi_observations");

  console.log(
    JSON.stringify({
      ok: true,
      bls,
      apiStatus,
      total_bls_observations: Number(check.rows[0].count),
    }),
  );
}

main().catch((error) => {
  console.error(JSON.stringify({ ok: false, error: error.name, message: error.message }));
  process.exit(1);
});
