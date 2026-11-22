#!/usr/bin/env node
/**
 * Reset trạng thái khóa tài khoản (FR-02) giữa các lần chạy Stress/Spike.
 * Dùng thư viện sqlite3 sẵn có của backend, ghi thẳng vào database.sqlite
 * (không cần restart server — restart sẽ xóa toàn bộ dữ liệu đã chuẩn bị).
 *
 *   node scripts/reset_lockout.js [--report]
 */
const path = require("path");
const BACKEND = path.resolve(__dirname, "..", "..", "eshop-sut", "backend");
const sqlite3 = require(path.join(BACKEND, "node_modules", "sqlite3"));
const db = new sqlite3.Database(path.join(BACKEND, "database.sqlite"));

db.serialize(() => {
  db.get(
    "SELECT COUNT(*) AS locked FROM users WHERE locked_until IS NOT NULL OR login_attempts > 0",
    (err, r) => console.log(`Trước reset: ${r ? r.locked : "?"} user có login_attempts>0 hoặc đang bị khóa`),
  );
  db.run("UPDATE users SET login_attempts = 0, locked_until = NULL", function (err) {
    if (err) { console.error(err.message); process.exit(1); }
    console.log(`Đã reset ${this.changes} user`);
  });
  if (process.argv.includes("--report")) {
    db.get("SELECT COUNT(*) AS n FROM orders", (e, r) => console.log(`Số đơn hàng hiện có: ${r.n}`));
  }
});
db.close();
