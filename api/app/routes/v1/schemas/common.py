"""
Common field types shared across all schema modules.

This module defines reusable Pydantic field types that can be used
across different schema modules to ensure consistency and reduce duplication.
"""

import ipaddress
import uuid
from datetime import datetime, timedelta, timezone
from random import choice, randint
from string import ascii_letters
from sys import maxsize as MAX_SIZE
from typing import Annotated

from app.utility.security import create_verification_token, encrypt_field, hash_field
from pydantic import AfterValidator, Field


def validate_future_timestamp(value: datetime) -> datetime:
    """Validate that the timestamp is in the future."""
    now = datetime.now(timezone.utc) if value.tzinfo is not None else datetime.now()
    if value <= now:
        raise ValueError("Timestamp must be in the future")
    return value


def validate_non_future_timestamp(value: datetime) -> datetime:
    """Validate that the timestamp is not in the future."""
    now = datetime.now(timezone.utc) if value.tzinfo is not None else datetime.now()
    if value > now:
        raise ValueError("Timestamp cannot be in the future")
    return value


class CommonFieldTypes:
    """Common field types used across multiple schema modules."""

    Email = Annotated[
        str,
        Field(
            title="Email",
            description="Email address of the user",
            example="user@example.com",
        ),
    ]

    EncryptedField = Annotated[
        str,
        Field(
            title="Encrypted Field",
            min_length=1,
            description="Encrypted value of the field",
            example=encrypt_field("".join(choice(ascii_letters) for _ in range(10))),
        ),
    ]

    FutureTimestamp = Annotated[
        datetime,
        Field(
            title="Future Timestamp",
            description="Timestamp that must be in the future",
            examples=[
                datetime.now() + timedelta(days=360),
                datetime.now() + timedelta(minutes=15),
            ],
        ),
        AfterValidator(validate_future_timestamp),
    ]

    HashedField = Annotated[
        str,
        Field(
            title="Hashed Field",
            pattern=r"^[a-f0-9]{64}$",
            min_length=64,
            max_length=64,
            description="Hash of the field",
            example=hash_field("".join(choice(ascii_letters) for _ in range(10))),
        ),
    ]

    Id = Annotated[
        int,
        Field(
            title="ID",
            description="Unique identifier",
            example=randint(1, MAX_SIZE),
            default=1,
        ),
    ]

    IpAddress = Annotated[
        ipaddress.IPv4Address,
        Field(
            title="IP Address",
            description="IP address of the user",
            example="192.168.1.1",
        ),
    ]

    NonFutureTimestamp = Annotated[
        datetime,
        Field(
            title="Non-Future Timestamp",
            description="Timestamp that cannot be in the future",
            examples=[datetime.now(), datetime(2020, 1, 1, 0, 0, 0)],
        ),
        AfterValidator(validate_non_future_timestamp),
    ]

    Token = Annotated[
        str,
        Field(
            title="Token",
            pattern=r"^[a-zA-Z0-9_-]{32,128}$",
            min_length=32,
            max_length=128,
            description="Unique token for the pending user",
            example=create_verification_token(),
        ),
    ]

    UserAgent = Annotated[
        str,
        Field(
            title="User Agent",
            description="User agent string of the client",
            example="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110",
        ),
    ]

    UUID = Annotated[
        uuid.UUID,
        Field(
            title="ID",
            description="Unique identifier",
            example=uuid.uuid4(),
            default_factory=uuid.uuid4,
        ),
    ]
