from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Auth
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    organization_name: str = Field(..., min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    organization_id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Chat
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    role: str
    content: str
    tool_used: Optional[str] = None
    created_at: Optional[datetime] = None


# Task
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[date] = None
    assignee: Optional[str] = Field(None, max_length=100)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    assignee: Optional[str] = Field(None, max_length=100)


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[date]
    assignee: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Email
class EmailCreate(BaseModel):
    to_address: EmailStr
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1, max_length=50000)
    status: str = "draft"


class EmailOut(BaseModel):
    id: int
    to_address: str
    subject: str
    body: str
    status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Expense
class ExpenseCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    amount: float = Field(..., gt=0)
    category: str = "other"
    expense_date: Optional[date] = None
    vendor: Optional[str] = Field(None, max_length=255)


class ExpenseOut(BaseModel):
    id: int
    description: str
    amount: float
    category: str
    expense_date: Optional[date]
    vendor: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExpenseSummary(BaseModel):
    total: float
    by_category: dict[str, float]
    count: int


# Document
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = Field(None, max_length=100000)
    summary: Optional[str] = Field(None, max_length=5000)
    doc_type: Optional[str] = Field(None, max_length=50)


class DocumentOut(BaseModel):
    id: int
    title: str
    content: Optional[str]
    summary: Optional[str]
    doc_type: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Meeting
class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    attendees: Optional[str] = Field(None, max_length=2000)
    meeting_date: date
    meeting_time: Optional[str] = Field(None, max_length=10)
    duration_minutes: int = Field(60, ge=1, le=1440)
    location: Optional[str] = Field(None, max_length=255)


class MeetingOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    attendees: Optional[str]
    meeting_date: date
    meeting_time: Optional[str]
    duration_minutes: int
    location: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Report
class ReportCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1, max_length=100000)
    report_type: Optional[str] = Field(None, max_length=50)


class ReportOut(BaseModel):
    id: int
    title: str
    content: str
    report_type: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Dashboard
class DashboardStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    total_expenses: float
    total_emails: int
    upcoming_meetings: int
    total_documents: int
    total_reports: int
