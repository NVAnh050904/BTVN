import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from sqlalchemy import String, Float, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# -----------------------------------------------------------------------------
# 1. DATABASE & ORM SETUP (Async SQLite)
# -----------------------------------------------------------------------------
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class ItemDB(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    discount_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


# -----------------------------------------------------------------------------
# 2. DB DEPENDENCY INJECTION
# -----------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Inject database session into route handlers."""
    async with AsyncSessionLocal() as session:
        yield session


# -----------------------------------------------------------------------------
# 3. PYDANTIC V2 MODELS & VALIDATORS
# -----------------------------------------------------------------------------
class ItemCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Tên item")
    price: float = Field(..., description="Giá gốc")
    discount_price: Optional[float] = Field(default=None, description="Giá giảm")

    # --- Pydantic V2 Field Validator ---
    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title không được chỉ chứa khoảng trắng")
        return v.strip()

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Price phải lớn hơn 0")
        return v

    # --- Pydantic V2 Model Validator (Cross-field validation) ---
    @model_validator(mode="after")
    def validate_discount(self) -> "ItemCreate":
        if self.discount_price is not None:
            if self.discount_price <= 0:
                raise ValueError("Discount price phải lớn hơn 0")
            if self.discount_price >= self.price:
                raise ValueError("Discount price phải nhỏ hơn price")
        return self


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None


class ItemResponse(ItemCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# -----------------------------------------------------------------------------
# 4. LIFESPAN MANAGEMENT
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý khởi tạo bảng khi startup & đóng engine khi shutdown."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.state.is_ready = True
    print("[Startup] App ready & DB tables created.")
    yield
    app.state.is_ready = False
    await engine.dispose()
    print("[Shutdown] DB engine disposed.")


# -----------------------------------------------------------------------------
# 5. FASTAPI APPLICATION SETUP & CORS
# -----------------------------------------------------------------------------
app = FastAPI(title="FastAPI Homework - Item API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# 6. HEALTH ENDPOINTS
# -----------------------------------------------------------------------------
@app.get("/health/live", tags=["Health"])
async def health_live():
    return {"status": "live"}


@app.get("/health/ready", tags=["Health"])
async def health_ready(db: AsyncSession = Depends(get_db)):
    if not getattr(app.state, "is_ready", False):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="App chưa sẵn sàng")
    await db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "connected"}


# -----------------------------------------------------------------------------
# 7. CRUD ENDPOINTS
# -----------------------------------------------------------------------------
@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(item_in: ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = ItemDB(**item_in.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@app.get("/items", response_model=List[ItemResponse], tags=["Items"])
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ItemDB))
    return result.scalars().all()


@app.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(ItemDB, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} không tồn tại")
    return item


@app.put("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def update_item(item_id: int, item_in: ItemUpdate, db: AsyncSession = Depends(get_db)):
    item = await db.get(ItemDB, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} không tồn tại")
    
    update_data = item_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    await db.commit()
    await db.refresh(item)
    return item


@app.delete("/items/{item_id}", tags=["Items"])
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(ItemDB, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} không tồn tại")
    await db.delete(item)
    await db.commit()
    return {"message": f"Đã xóa thành công item {item_id}"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
