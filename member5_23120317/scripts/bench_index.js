#!/usr/bin/env node
/**
 * Kiểm chứng đề xuất tối ưu trên BẢN SAO database (không đụng DB đang chạy):
 *   1. EXPLAIN QUERY PLAN của truy vấn Order History & Login trước/sau khi thêm index
 *   2. Đo thời gian truy vấn my-orders cho 500 user trước/sau index
 *   3. Đo thời gian khi giới hạn (phân trang) LIMIT 20
 *
 *   node scripts/bench_index.js <path-to-copy-of-database.sqlite>
 */
const path = require("path");
const sqlite3 = require(path.resolve(__dirname, "..", "..", "eshop-sut", "backend", "node_modules", "sqlite3"));
const db = new sqlite3.Database(process.argv[2]);
const all = (sql, p = []) => new Promise((ok, ko) => db.all(sql, p, (e, r) => (e ? ko(e) : ok(r))));
const run = (sql) => new Promise((ok, ko) => db.run(sql, (e) => (e ? ko(e) : ok())));

async function bench(label, sql, ids) {
  const t = process.hrtime.bigint();
  let rows = 0;
  for (const id of ids) rows += (await all(sql, [id])).length;
  const ms = Number(process.hrtime.bigint() - t) / 1e6;
  console.log(`| ${label} | ${ids.length} | ${(ms / ids.length).toFixed(3)} | ${(rows / ids.length).toFixed(0)} |`);
}

(async () => {
  const [{ n }] = await all("SELECT COUNT(*) n FROM orders");
  const ids = (await all("SELECT id FROM users WHERE email LIKE 'perf5_%'")).map((r) => r.id);
  console.log(`orders = ${n}, users = ${ids.length}\n`);
  const Q = "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC";
  const QL = Q + " LIMIT 20";

  console.log("EXPLAIN trước index:", (await all("EXPLAIN QUERY PLAN " + Q, [3])).map((r) => r.detail).join(" ; "));
  console.log("EXPLAIN login     :", (await all("EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = ?", ["x"])).map((r) => r.detail).join(" ; "));
  console.log("\n| Biến thể | Số truy vấn | ms / truy vấn | rows trả về TB |\n|---|---:|---:|---:|");
  await bench("Hiện tại (không index, không LIMIT)", Q, ids);
  await bench("Không index + LIMIT 20", QL, ids);
  await run("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id, id DESC)");
  await run("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)");
  await bench("Index (user_id,id) , không LIMIT", Q, ids);
  await bench("Index (user_id,id) + LIMIT 20", QL, ids);
  console.log("\nEXPLAIN sau index :", (await all("EXPLAIN QUERY PLAN " + Q, [3])).map((r) => r.detail).join(" ; "));
  console.log("EXPLAIN login sau :", (await all("EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = ?", ["x"])).map((r) => r.detail).join(" ; "));
  db.close();
})();
