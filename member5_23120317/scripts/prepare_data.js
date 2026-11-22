#!/usr/bin/env node
/**
 * Người 5 – Chuẩn bị dữ liệu tài khoản & đơn hàng cho Workflow 5.
 *
 * LƯU Ý: backend DROP & seed lại DB mỗi lần `node server.js` khởi động,
 * nên script này phải chạy SAU khi server đã lên.
 *
 *   node scripts/prepare_data.js [--users 500] [--orders 3] [--base http://localhost:3000]
 *
 * Kết quả:
 *   data/users.csv     email,password,shipping_address   (đăng ký qua POST /api/register)
 *   data/products.csv  product_id,quantity,keyword        (lấy từ GET /api/products)
 *   Mỗi user được tạo sẵn N đơn qua POST /api/checkout để Order History có dữ liệu.
 */
const fs = require("fs");
const path = require("path");

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, v, i, a) => (v.startsWith("--") ? [...acc, [v.slice(2), a[i + 1]]] : acc), []),
);
const BASE = args.base || "http://localhost:3000";
const N_USERS = parseInt(args.users || "500", 10);
const N_ORDERS = parseInt(args.orders || "3", 10);
const PASSWORD = "Perf5@1234"; // thỏa FR-01: hoa, thường, số, ký tự đặc biệt, >= 8
const DATA_DIR = path.resolve(__dirname, "..", "data");
const STREETS = ["Le Loi", "Nguyen Hue", "Hai Ba Trung", "Vo Van Tan", "Cach Mang Thang 8", "Nguyen Van Cu"];
const DISTRICTS = ["Q1", "Q3", "Q5", "Q10", "Binh Thanh", "Thu Duc"];

async function api(method, url, body, token) {
  const res = await fetch(BASE + url, {
    method,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let json;
  try { json = JSON.parse(text); } catch { json = text; }
  if (!res.ok) throw new Error(`${method} ${url} -> ${res.status} ${text.slice(0, 200)}`);
  return json;
}

async function pool(items, limit, fn) {
  let i = 0;
  const workers = Array.from({ length: limit }, async () => {
    while (i < items.length) { const idx = i++; await fn(items[idx], idx); }
  });
  await Promise.all(workers);
}

(async () => {
  fs.mkdirSync(DATA_DIR, { recursive: true });

  // 1) Sản phẩm
  const products = await api("GET", "/api/products");
  if (!Array.isArray(products) || products.length === 0) throw new Error("Không lấy được danh sách sản phẩm");
  const prodRows = [];
  for (const p of products) {
    const kw = p.name.split(" ")[0]; // từ khóa tìm kiếm an toàn (không ký tự đặc biệt)
    for (const qty of [1, 2]) prodRows.push(`${p.id},${qty},${kw}`);
  }
  fs.writeFileSync(path.join(DATA_DIR, "products.csv"), "product_id,quantity,keyword\n" + prodRows.join("\n") + "\n");
  console.log(`products.csv: ${prodRows.length} dòng từ ${products.length} sản phẩm`);

  // 2) Kiểm tra trùng: register không chặn email trùng (bug B9) -> tự kiểm tra để tránh nhân bản
  const users = Array.from({ length: N_USERS }, (_, k) => {
    const n = String(k + 1).padStart(3, "0");
    return {
      name: `Perf5 User ${n}`,
      email: `perf5_user_${n}@eshop.test`,
      password: PASSWORD,
      address: `${(k % 200) + 1} ${STREETS[k % STREETS.length]} ${DISTRICTS[k % DISTRICTS.length]} TP.HCM`,
    };
  });

  let created = 0, existed = 0, orders = 0;
  await pool(users, 10, async (u) => {
    // thử login trước: nếu đã tồn tại thì không đăng ký lại
    let token;
    try {
      token = (await api("POST", "/api/login", { email: u.email, password: u.password })).token;
      existed++;
    } catch {
      await api("POST", "/api/register", { name: u.name, email: u.email, password: u.password });
      token = (await api("POST", "/api/login", { email: u.email, password: u.password })).token;
      created++;
    }
    const history = await api("GET", "/api/orders/my-orders", null, token);
    for (let j = history.length; j < N_ORDERS; j++) {
      const p = products[(j + created) % products.length];
      await api("POST", "/api/checkout", { total_amount: Number(p.price), shipping_address: u.address }, token);
      orders++;
    }
  });

  fs.writeFileSync(
    path.join(DATA_DIR, "users.csv"),
    "email,password,shipping_address\n" + users.map((u) => `${u.email},${u.password},${u.address}`).join("\n") + "\n",
  );
  console.log(`users.csv: ${users.length} user (mới tạo ${created}, đã có ${existed}); đã tạo thêm ${orders} đơn hàng lịch sử`);
})().catch((e) => { console.error("FAILED:", e.message); process.exit(1); });
