"""
Common field types shared across all schema modules.

This module defines reusable Pydantic field types that can be used
across different schema modules to ensure consistency and reduce duplication.
"""

import ipaddress
import uuid
from datetime import datetime
from typing import Annotated

from pydantic import Field


class CommonFieldTypes:
    """Common field types used across multiple schema modules."""

    EncryptedField = Annotated[
        str,
        Field(
            title="Encrypted Field",
            min_length=1,
            description="Encrypted value of the field",
            examples=["U2FsdGVkX1+..."],
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
            examples=["5d41402abc4b2a76b9719d911017c592"],
        ),
    ]

    Id = Annotated[
        int,
        Field(
            title="ID",
            description="Unique identifier",
            examples=[1, 2, 3],
            default=1,
        ),
    ]

    IpAddress = Annotated[
        ipaddress.IPv4Address,
        Field(
            title="IP Address",
            description="IP address of the user",
            examples=["192.168.1.1"],
        ),
    ]

    Timestamp = Annotated[
        datetime,
        Field(
            title="Timestamp",
            description="Timestamp of the event",
            examples=[datetime(2023, 1, 1, 0, 0, 0)],
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
            examples=["abc123"],
        ),
    ]

    UserAgent = Annotated[
        str,
        Field(
            title="User Agent",
            description="User agent string of the client",
            examples=[
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110"
            ],
        ),
    ]

    UUID = Annotated[
        uuid.UUID,
        Field(
            title="ID",
            description="Unique identifier",
            examples=[uuid.uuid4()],
            default_factory=uuid.uuid4,
        ),
    ]
