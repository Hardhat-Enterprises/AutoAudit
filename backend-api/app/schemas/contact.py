"""Pydantic schemas for Contact Us submissions."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ContactSubmissionBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    company: str | None = Field(None, max_length=255)
    subject: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1)
    source: str | None = Field(None, max_length=50)


class ContactSubmissionCreate(ContactSubmissionBase):
    pass


class ContactSubmissionUpdate(BaseModel):
    status: str | None = Field(None, min_length=1, max_length=20)
    priority: str | None = Field(None, min_length=1, max_length=20)
    assigned_to: int | None = None
    resolved_at: datetime | None = None


class ContactSubmissionRead(ContactSubmissionBase):
    id: UUID
    status: str
    priority: str
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True


class SubmissionNoteCreate(BaseModel):
    note: str = Field(..., min_length=1)
    is_internal: bool = True


class SubmissionNoteRead(BaseModel):
    id: UUID
    submission_id: UUID
    admin_user_id: int | None
    note: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubmissionHistoryRead(BaseModel):
    id: UUID
    submission_id: UUID
    admin_user_id: int | None
    action: str
    field_name: str | None
    old_value: str | None
    new_value: str | None
    created_at: datetime

    class Config:
        from_attributes = True

"""Pydantic schemas for Contact Us submissions."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ContactSubmissionBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    company: str | None = Field(None, max_length=255)
    subject: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1)
    source: str | None = Field(None, max_length=50)


class ContactSubmissionCreate(ContactSubmissionBase):
    pass


class ContactSubmissionUpdate(BaseModel):
    status: str | None = Field(None, max_length=20)
    priority: str | None = Field(None, max_length=20)
    assigned_to: int | None = None
    resolved_at: datetime | None = None


class ContactSubmissionRead(ContactSubmissionBase):
    id: UUID
    status: str
    priority: str
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True


class SubmissionNoteCreate(BaseModel):
    note: str = Field(..., min_length=1)
    is_internal: bool = True


class SubmissionNoteRead(BaseModel):
    id: UUID
    submission_id: UUID
    admin_user_id: int | None
    note: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubmissionHistoryRead(BaseModel):
    id: UUID
    submission_id: UUID
    admin_user_id: int | None
    action: str
    field_name: str | None
    old_value: str | None
    new_value: str | None
    created_at: datetime

    class Config:
        from_attributes = True
