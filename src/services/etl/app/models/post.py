from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger, DateTime, Text, PrimaryKeyConstraint, Index, ForeignKey

from ..db_base import Base  # если у тебя есть общий Base

class Post(Base):
    __tablename__ = "posts"

    username: Mapped[str] = mapped_column(String(255), ForeignKey("channels.username", ondelete="CASCADE"), nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    text: Mapped[str | None] = mapped_column(Text)

    views_now: Mapped[int | None] = mapped_column(Integer)
    forwards_now: Mapped[int | None] = mapped_column(Integer)
    replies_now: Mapped[int | None] = mapped_column(Integer)
    reactions_now: Mapped[int | None] = mapped_column(Integer)

    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("username", "message_id", name="pk_posts"),
        Index("ix_posts_user_date", "username", "posted_at"),
    )