from __future__ import annotations
import csv
from io import TextIOWrapper
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    status,
    Response,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.models.channel import Channel, ChannelStat
from app.schemas.channel import (
    ChannelCreate,
    ChannelRead,
    BulkUpsertReport,
    ChannelUpsertResponse,
)
from app.crud.channel import upsert_channel, ChannelConflictError


router = APIRouter(prefix="/channels", tags=["channels"])

REQUIRED_HEADERS = [
    "username",
    "channel",
    "name",
    "description",
    "image",
    "category",
    "country",
    "subscribers",
]


# =====================================================================
# 🔹 Получение информации о канале
# =====================================================================
@router.get("/{username}", response_model=ChannelRead)
async def get_channel(username: str, db: AsyncSession = Depends(get_db)):
    obj = await db.scalar(select(Channel).where(Channel.username == username))
    if not obj:
        raise HTTPException(404, "Канал не найден")

    return ChannelRead(
        username=obj.username,
        channel=obj.channel,
        name=obj.name,
        description=obj.description,
        image=obj.image,
        category=obj.category,
        country=obj.country,
        subscribers=obj.subscribers or 0,
    )


# =====================================================================
# 🔹 Создание или обновление канала вручную
# =====================================================================
@router.post("", response_model=ChannelUpsertResponse)
async def create_or_update_channel(
    body: ChannelCreate, response: Response, db: AsyncSession = Depends(get_db)
):
    try:
        obj, created = await upsert_channel(db, body.model_dump())
        await db.commit()

        response.status_code = (
            status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
        message = (
            "Канал был создан успешно"
            if created
            else "Данные канала были успешно обновлены"
        )

        return ChannelUpsertResponse(
            message=message,
            channel=ChannelRead(
                username=obj.username,
                channel=obj.channel,
                name=obj.name,
                description=obj.description,
                image=obj.image,
                category=obj.category,
                country=obj.country,
                subscribers=obj.subscribers or 0,
            ),
        )

    except (ChannelConflictError, IntegrityError):
        await db.rollback()
        raise HTTPException(status_code=400, detail="Что-то пошло не так")
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Что-то пошло не так")


# =====================================================================
# 🔹 Массовая загрузка каналов из CSV
# =====================================================================
@router.post("/upload", response_model=BulkUpsertReport)
async def upload_csv(
    file: UploadFile = File(..., description="CSV с заголовками: " + ",".join(REQUIRED_HEADERS)),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Ожидается CSV файл")

    # ОДИН TextIOWrapper на весь парсинг — не создаём второй и не делаем seek(0)
    text_stream = TextIOWrapper(file.file, encoding="utf-8", newline="")
    reader = csv.DictReader(text_stream)

    headers = [h.strip() for h in (reader.fieldnames or [])]
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        raise HTTPException(status_code=400, detail=f"Нет заголовков: {missing}")

    BATCH = 1000
    inserted = updated = skipped = errors = total = 0
    sample_errors: list[str] = []
    buffer: list[dict] = []

    async def process_batch(rows: List[dict]):
        nonlocal inserted, updated, errors
        if not rows:
            return

        usernames = [r["username"] for r in rows]
        existing = set(
            [u for (u,) in (await db.execute(select(Channel.username).where(Channel.username.in_(usernames)))).all()]
        )

        for r in rows:
            try:
                r["subscribers"] = int(r["subscribers"]) if r.get("subscribers") not in (None, "") else 0
                for k, v in r.items():
                    if isinstance(v, str):
                        r[k] = v.strip() or None

                _, created = await upsert_channel(db, r)
                if created:
                    inserted += 1
                elif r["username"] in existing:
                    updated += 1
                else:
                    inserted += 1
            except ChannelConflictError as e:
                errors += 1
                if len(sample_errors) < 5:
                    sample_errors.append(
                        f"{r.get('username')} -> конфликт: channel '{e.channel}' принадлежит '{e.existing_username}'"
                    )
            except Exception as e:
                errors += 1
                if len(sample_errors) < 5:
                    sample_errors.append(f"{r.get('username')}: {e}")

        await db.commit()

    for row in reader:
        total += 1
        if not row.get("username"):
            skipped += 1
            continue
        cleaned = {k: (row.get(k) or "").strip() for k in REQUIRED_HEADERS}
        buffer.append(cleaned)
        if len(buffer) >= BATCH:
            await process_batch(buffer)
            buffer.clear()

    if buffer:
        await process_batch(buffer)

    # важно: НЕ закрываем text_stream вручную (Starlette сам разрулит UploadFile)
    return BulkUpsertReport(
        total_rows=total,
        inserted=inserted,
        updated=updated,
        skipped=skipped,
        errors=errors,
        sample_errors=sample_errors,
    )

