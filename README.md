# FastAPI Homework - Mini Item API

Dự án FastAPI mini 

## Các thành phần chính

- **Mã nguồn ngắn gọn**: Toàn bộ logic nằm gọn trong `main.py` (~100 dòng code).
- **Pydantic V2**: Sử dụng `@field_validator` và `@model_validator(mode='after')` 
- **SQLite Database**: Cơ sở dữ liệu SQLite bất đồng bộ (`sqlite+aiosqlite`).
- **Dependency Injection**: Hàm `get_db()` cung cấp AsyncSession qua `Depends`.
- **Lifespan Manager**: Quản lý vòng đời khởi tạo bảng và đóng engine (`@asynccontextmanager`).
- **Health Endpoints**: Endpoint `/health/live` và `/health/ready`.
- **CRUD Operations**: Tạo, đọc danh sách, xem chi tiết, cập nhật và xóa item (`/items`).

---

## Hướng dẫn khởi chạy

```bash
# 1. Cài đặt môi trường với uv
uv sync

# 2. Khởi chạy Uvicorn Server
uv run uvicorn main:app --reload

# 3. Chạy script test tự động
./curl.sh
```

---

## OpenAPI Documentation

Truy cập Swagger UI tại: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Log test API (`curl.sh`)

Log kết quả chạy thực tế của script `./curl.sh`:

```text
======================================================================
STARTING FASTAPI MINI HOMEWORK TESTS ON http://127.0.0.1:8000
======================================================================

1. Testing Liveness Probe (/health/live)...
{"status":"live"}


2. Testing Readiness Probe (/health/ready)...
{"status":"ready","database":"connected"}


3. Testing Create Item (POST /items)...
{"title":"Sach Lap trinh Python","price":150000.0,"discount_price":120000.0,"id":1}

Created Item ID: 1

4. Testing Pydantic V2 Validation Error (discount_price >= price)...
{"detail":[{"type":"value_error","loc":["body"],"msg":"Value error, Discount price phải nhỏ hơn price","input":{"title":"Invalid Item","price":100.0,"discount_price":200.0},"ctx":{"error":{}}}]}


5. Testing Get List of Items (GET /items)...
[{"title":"Sach Lap trinh Python","price":150000.0,"discount_price":120000.0,"id":1}]


6. Testing Get Item Detail (GET /items/1)...
{"title":"Sach Lap trinh Python","price":150000.0,"discount_price":120000.0,"id":1}


7. Testing Update Item (PUT /items/1)...
{"title":"Sach Lap trinh Python FastAPI V2","price":180000.0,"discount_price":140000.0,"id":1}


8. Testing Delete Item (DELETE /items/1)...
{"message":"Đã xóa thành công item 1"}


9. Verifying Item Deletion (GET /items/1)...
{"detail":"Item 1 không tồn tại"}


======================================================================
ALL API TESTS COMPLETED!
======================================================================
```
