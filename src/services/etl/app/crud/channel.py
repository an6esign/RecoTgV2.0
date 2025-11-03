# app/crud/channel.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.channel import Channel, ChannelStat

def upsert_channel(db: Session, payload: dict) -> Channel:
    obj = db.scalar(select(Channel).where(Channel.channel == payload["channel"]))
    if obj:
        for k, v in payload.items():
            if v is not None:
                setattr(obj, k, v)
    else:
        obj = Channel(**payload)
        db.add(obj)
    db.flush()
    return obj

def upsert_stat(db: Session, channel_id: int, date_, payload: dict) -> ChannelStat:
    obj = db.scalar(select(ChannelStat).where(
        ChannelStat.channel_id == channel_id, ChannelStat.date == date_
    ))
    if obj:
        for k, v in payload.items():
            if v is not None:
                setattr(obj, k, v)
    else:
        obj = ChannelStat(channel_id=channel_id, date=date_, **payload)
        db.add(obj)
    db.flush()
    return obj
