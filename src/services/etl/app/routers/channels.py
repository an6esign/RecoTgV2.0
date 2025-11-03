# app/routers/channels.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
import pandas as pd
from datetime import date
from ..db import SessionLocal
from ..models.channel import Channel, ChannelStat
from ..crud.channel import upsert_channel, upsert_stat

router = APIRouter(prefix="/channels", tags=["channels"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("")
def create_or_update_channel(body: dict, db: Session = Depends(get_db)):
    # ожидаем ключи: channel, username, name, ...
    if "channel" not in body:
        raise HTTPException(400, "channel (url) is required")
    obj = upsert_channel(db, body)
    db.commit(); db.refresh(obj)
    return obj

@router.get("/{channel_id}")
def get_channel(channel_id: int, db: Session = Depends(get_db)):
    obj = db.get(Channel, channel_id)
    if not obj: raise HTTPException(404, "Channel not found")
    latest = db.scalar(select(ChannelStat).where(
        ChannelStat.channel_id==channel_id
    ).order_by(ChannelStat.date.desc()))
    return {"channel": obj, "latest_stat": latest}

@router.post("/{channel_id}/stats")
def put_stat(channel_id: int, body: dict, db: Session = Depends(get_db)):
    # ожидаем: {"date": "2025-10-31", ... метрики ...}
    if "date" not in body:
        raise HTTPException(400, "date is required (YYYY-MM-DD)")
    d = date.fromisoformat(body["date"])
    stat = upsert_stat(db, channel_id, d, {k:v for k,v in body.items() if k!="date"})
    # обновим снэпшот подписчиков, если пришло значение
    subs = body.get("subscribers")
    if subs is not None:
        ch = db.get(Channel, channel_id)
        ch.subscribers = subs
    db.commit(); db.refresh(stat)
    return stat

