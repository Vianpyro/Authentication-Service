"""
This module defines the SQLAlchemy ORM model that correspond to the database users table.
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model representing authenticated users."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    app_id = Column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )

    email_encrypted = Column(Text, nullable=False)
    email_hash = Column(String(64), nullable=False)
    password_hash = Column(Text, nullable=False)
    phone_encrypted = Column(Text)
    phone_hash = Column(String(64))

    is_email_verified = Column(Boolean, nullable=False, default=True)
    is_2fa_enabled = Column(Boolean, nullable=False, default=False)
    is_suspended = Column(Boolean, nullable=False, default=False)
    failed_login_count = Column(Boolean, nullable=False, default=0)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_login_at = Column(DateTime(timezone=True))
    scheduled_for_deletion_at = Column(DateTime(timezone=True))
    account_locked_at = Column(DateTime(timezone=True))
