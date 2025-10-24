from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Unicode
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    phone_numb = Column(Unicode(255), unique=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))