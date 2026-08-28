# FastAPI Homework - Mini Item API

Dự án FastAPI mini nhỏ gọn, ngắn gọn, đúng trọng tâm yêu cầu bài tập về nhà.

## Các thành phần chính

- **Mã nguồn ngắn gọn**: Toàn bộ logic nằm gọn trong `main.py` (~100 dòng code).
- **Pydantic V2**: Sử dụng `@field_validator` và `@model_validator(mode='after')` (không dùng Pydantic V1).
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
