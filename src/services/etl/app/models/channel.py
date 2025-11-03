# src/services/etl/app/models/channel.py
from __future__ import annotations
from typing import Optional
from datetime import date, datetime

from sqlalchemy import (
    Integer, Float, String, Date, ForeignKey, Index, Text,
    PrimaryKeyConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..db_base import Base  # где лежит твой Base

class Channel(Base):
    __tablename__ = "channels"

    username: Mapped[str] = mapped_column(String(255), primary_key=True)
    channel:  Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    name:     Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image:       Mapped[Optional[str]] = mapped_column(String(512))
    category:    Mapped[Optional[str]] = mapped_column(String(100), index=True)
    country:     Mapped[Optional[str]] = mapped_column(String(50), index=True)
    subscribers: Mapped[Optional[int]] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    stats = relationship("ChannelStat", back_populates="channel", cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
        Index("ix_channels_category", "category"),
        Index("ix_channels_country", "country"),
    )


class ChannelStat(Base):
    __tablename__ = "channel_stats"

    # ОБЯЗАТЕЛЬНО: PK составной -> два поля ниже должны входить в PK
    username: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("channels.username", ondelete="CASCADE"),
        nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)

    subscribers: Mapped[Optional[int]] = mapped_column(Integer)
    subscribers_day_delta:   Mapped[Optional[int]] = mapped_column(Integer)
    subscribers_week_delta:  Mapped[Optional[int]] = mapped_column(Integer)
    subscribers_month_delta: Mapped[Optional[int]] = mapped_column(Integer)

    citation_index:     Mapped[Optional[int]] = mapped_column(Integer)
    mentioned_channels: Mapped[Optional[int]] = mapped_column(Integer)
    mentions:           Mapped[Optional[int]] = mapped_column(Integer)
    reposts:            Mapped[Optional[int]] = mapped_column(Integer)

    avg_reach:      Mapped[Optional[int]] = mapped_column(Integer)
    avg_reach_ads:  Mapped[Optional[int]] = mapped_column(Integer)
    avg_views_12h:  Mapped[Optional[int]] = mapped_column(Integer)
    avg_views_24h:  Mapped[Optional[int]] = mapped_column(Integer)
    avg_views_48h:  Mapped[Optional[int]] = mapped_column(Integer)

    err:             Mapped[Optional[float]] = mapped_column(Float)
    err24:           Mapped[Optional[float]] = mapped_column(Float)
    engagement_rate: Mapped[Optional[float]] = mapped_column(Float)
    forwards:        Mapped[Optional[int]] = mapped_column(Integer)
    comments:        Mapped[Optional[int]] = mapped_column(Integer)
    reactions:       Mapped[Optional[int]] = mapped_column(Integer)

    posts_total: Mapped[Optional[int]] = mapped_column(Integer)
    posts_day:   Mapped[Optional[int]] = mapped_column(Integer)
    posts_week:  Mapped[Optional[int]] = mapped_column(Integer)
    posts_month: Mapped[Optional[int]] = mapped_column(Integer)

    collected_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    channel = relationship("Channel", back_populates="stats")

    __table_args__ = (
        PrimaryKeyConstraint("username", "date", name="pk_channel_stats"),
        Index("ix_channel_stats_date", "date"),
        # (опционально, для читаемости — PK уже гарантирует уникальность)
        UniqueConstraint("username", "date", name="uq_channel_stats_day"),
    )
