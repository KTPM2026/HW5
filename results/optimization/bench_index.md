orders = 117431, users = 500

EXPLAIN trước index: SCAN orders
EXPLAIN login     : SCAN users

| Biến thể | Số truy vấn | ms / truy vấn | rows trả về TB |
|---|---:|---:|---:|
| Hiện tại (không index, không LIMIT) | 500 | 10.679 | 235 |
| Không index + LIMIT 20 | 500 | 0.559 | 20 |
| Index (user_id,id) , không LIMIT | 500 | 1.201 | 235 |
| Index (user_id,id) + LIMIT 20 | 500 | 0.180 | 20 |

EXPLAIN sau index : SEARCH orders USING INDEX idx_orders_user_id (user_id=?)
EXPLAIN login sau : SEARCH users USING INDEX idx_users_email (email=?)
