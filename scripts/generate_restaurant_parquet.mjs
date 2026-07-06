/**
 * Generate data/restaurant.parquet from Hugging Face zomato.csv
 * (Node fallback when Python is unavailable).
 */
import { createWriteStream, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { pipeline } from "node:stream/promises";
import duckdb from "duckdb";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const DATA_DIR = join(ROOT, "data");
const CSV_PATH = join(DATA_DIR, "zomato.csv");
const PARQUET_PATH = join(DATA_DIR, "restaurant.parquet");
const CSV_URL =
  "https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation/resolve/main/zomato.csv";

async function downloadCsv() {
  if (existsSync(CSV_PATH)) {
    console.log(`Using cached CSV: ${CSV_PATH}`);
    return;
  }
  mkdirSync(DATA_DIR, { recursive: true });
  console.log("Downloading zomato.csv (~574 MB)...");
  const res = await fetch(CSV_URL);
  if (!res.ok) {
    throw new Error(`Failed to download CSV: ${res.status} ${res.statusText}`);
  }
  await pipeline(res.body, createWriteStream(CSV_PATH));
  console.log(`Saved ${CSV_PATH}`);
}

function runExec(db, sql) {
  return new Promise((resolve, reject) => {
    db.run(sql, (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

function runQuery(db, sql) {
  return new Promise((resolve, reject) => {
    db.all(sql, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

async function main() {
  await downloadCsv();
  mkdirSync(DATA_DIR, { recursive: true });

  const db = new duckdb.Database(":memory:");
  const conn = db.connect();
  const csv = CSV_PATH.replace(/\\/g, "/");
  const parquet = PARQUET_PATH.replace(/\\/g, "/");

  const exportSql = `
    COPY (
      WITH cleaned AS (
        SELECT
          trim(name) AS name,
          trim(location) AS location,
          trim(cuisines) AS cuisines,
          TRY_CAST(
            NULLIF(regexp_replace(trim("approx_cost(for two people)"), '[^0-9.]', '', 'g'), '')
            AS DOUBLE
          ) AS cost_for_two,
          trim(rate) AS rate_raw
        FROM read_csv_auto('${csv}', header=true, ignore_errors=true)
        WHERE name IS NOT NULL AND trim(name) <> ''
          AND location IS NOT NULL AND trim(location) <> ''
      )
      SELECT
        substr(sha256(name || '|' || location), 1, 32) AS id,
        name,
        location,
        cuisines,
        cost_for_two,
        CASE
          WHEN cost_for_two IS NULL THEN NULL
          WHEN cost_for_two <= 400 THEN 'low'
          WHEN cost_for_two <= 800 THEN 'medium'
          ELSE 'high'
        END AS budget_tier,
        CASE
          WHEN rate_raw IS NULL OR upper(rate_raw) IN ('NEW', '-', 'NAN') THEN NULL
          ELSE TRY_CAST(
            NULLIF(regexp_extract(rate_raw, '^([0-9.]+)', 1), '')
            AS DOUBLE
          )
        END AS rating
      FROM cleaned
    ) TO '${parquet}' (FORMAT PARQUET);
  `;

  await runExec(conn, exportSql);

  const stats = await runQuery(
    conn,
    `SELECT COUNT(*) AS count FROM read_parquet('${parquet}')`
  );

  conn.close();
  db.close();

  console.log(`Wrote ${stats[0].count} restaurants to ${PARQUET_PATH}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
