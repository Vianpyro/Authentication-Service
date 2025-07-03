"""
Common field types shared across all schema modules.

This module defines reusable Pydantic field types that can be used
across different schema modules to ensure consistency and reduce duplication.
"""

import ipaddress
import uuid
from datetime import datetime
from random import choice, randint
from string import ascii_letters
from sys import maxsize as MAX_SIZE
from typing import Annotated

from app.utility.security import create_verification_token, encrypt_field, hash_field
from pydantic import Field


class CommonFieldTypes:
    """Common field types used across multiple schema modules."""

    EncryptedField = Annotated[
        str,
        Field(
            title="Encrypted Field",
            min_length=1,
            description="Encrypted value of the field",
            example=encrypt_field("".join(choice(ascii_letters) for _ in range(10))),
        ),
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

    Timestamp = Annotated[
        datetime,
        Field(
            title="Timestamp",
            description="Timestamp of the event",
            example=datetime(2023, 1, 1, 0, 0, 0),
        ),
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
