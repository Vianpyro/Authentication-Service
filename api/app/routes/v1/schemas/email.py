"""
Pydantic schemas for email-related operations.

This module provides Pydantic schemas for validating email-related data,
such as email requests and responses.
"""

from typing import Annotated, Any, Dict, List

from pydantic import BaseModel, EmailStr, Field


class EmailFieldTypes:
    """Reusable field types for email-related schemas."""

    Recipient = Annotated[
        List[EmailStr],
        Field(
            title="Email Recipients",
            min_length=1,
            description="A list of email addresses to send the email to.",
            example=["user1@example.com", "user2@example.com"],
        ),
    ]

    Subject = Annotated[
        str,
        Field(
            title="Email Subject",
            min_length=1,
            max_length=255,
            description="The subject of the email.",
            example="Welcome to our service!",
        ),
    ]

    Body = Annotated[
        Dict[str, Any],
        Field(
            title="Email Body",
            min_length=1,
            description="The content of the email.",
            example="Thank you for signing up for our service.",
        ),
    ]

    TemplatePath = Annotated[
        str,
        Field(
            title="Email Template Path",
            pattern=r"^[a-z0-9_]+\.html$",
            min_length=1,
            description="The file path to the email template.",
            example="welcome_email.html",
        ),
    ]


class BaseEmailSchema(BaseModel):
    """Base schema for email-related operations."""

    recipients: EmailFieldTypes.Recipient
    subject: EmailFieldTypes.Subject
    body: EmailFieldTypes.Body
    template_path: EmailFieldTypes.TemplatePath


class RegistrationEmailSchema(BaseEmailSchema):
    """Schema for registration emails."""

    subject: EmailFieldTypes.Subject = Annotated[str, Field(default="Authentication Service - Email Confirmation")]

    template_path: EmailFieldTypes.TemplatePath
