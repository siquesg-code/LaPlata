from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


# Chat
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    role: str
    content: str
    tool_used: Optional[str] = None
    created_at: Optional[datetime] = None


# Task
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[date] = None
    assignee: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    assignee: Optional[str] = None


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
    to_address: str
    subject: str
    body: str
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
    description: str
    amount: float
    category: str = "other"
    expense_date: Optional[date] = None
    vendor: Optional[str] = None


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
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    doc_type: Optional[str] = None


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
    title: str
    description: Optional[str] = None
    attendees: Optional[str] = None
    meeting_date: date
    meeting_time: Optional[str] = None
    duration_minutes: int = 60
    location: Optional[str] = None


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
    title: str
    content: str
    report_type: Optional[str] = None


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
