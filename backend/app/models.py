from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Date, Enum as SAEnum
from app.database import Base
import enum


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EmailStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"


class ExpenseCategory(str, enum.Enum):
    TRAVEL = "travel"
    OFFICE = "office"
    SOFTWARE = "software"
    MARKETING = "marketing"
    SALARY = "salary"
    UTILITIES = "utilities"
    OTHER = "other"


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    tool_used = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=TaskStatus.TODO.value)
    priority = Column(String(20), default=TaskPriority.MEDIUM.value)
    due_date = Column(Date, nullable=True)
    assignee = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, autoincrement=True)
    to_address = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(20), default=EmailStatus.DRAFT.value)
    created_at = Column(DateTime, default=datetime.utcnow)


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(50), default=ExpenseCategory.OTHER.value)
    expense_date = Column(Date, default=date.today)
    vendor = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    doc_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    attendees = Column(Text, nullable=True)  # comma-separated
    meeting_date = Column(Date, nullable=False)
    meeting_time = Column(String(10), nullable=True)  # HH:MM
    duration_minutes = Column(Integer, default=60)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    report_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
