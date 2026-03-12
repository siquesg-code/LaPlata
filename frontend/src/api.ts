const API_URL = import.meta.env.VITE_API_URL || "";

function getBaseUrl(): string {
  if (API_URL) return API_URL;
  // Build origin without embedded credentials (handles user:pass@domain URLs)
  const loc = window.location;
  return `${loc.protocol}//${loc.host}`;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const base = getBaseUrl();
  const url = `${base}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Chat
export interface ChatMessage {
  role: string;
  content: string;
  tool_used?: string | null;
  created_at?: string | null;
}

export function sendChat(message: string): Promise<ChatMessage> {
  return request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

export function getChatHistory(): Promise<ChatMessage[]> {
  return request("/api/chat/history");
}

export function clearChatHistory(): Promise<{ message: string }> {
  return request("/api/chat/history", { method: "DELETE" });
}

// Tasks
export interface TaskItem {
  id: number;
  title: string;
  description?: string | null;
  status: string;
  priority: string;
  due_date?: string | null;
  assignee?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export function getTasks(status?: string): Promise<TaskItem[]> {
  const params = status ? `?status=${status}` : "";
  return request(`/api/tasks${params}`);
}

export function createTask(task: Partial<TaskItem>): Promise<TaskItem> {
  return request("/api/tasks", {
    method: "POST",
    body: JSON.stringify(task),
  });
}

export function updateTask(id: number, data: Partial<TaskItem>): Promise<TaskItem> {
  return request(`/api/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteTask(id: number): Promise<{ message: string }> {
  return request(`/api/tasks/${id}`, { method: "DELETE" });
}

// Emails
export interface EmailItem {
  id: number;
  to_address: string;
  subject: string;
  body: string;
  status: string;
  created_at?: string | null;
}

export function getEmails(): Promise<EmailItem[]> {
  return request("/api/emails");
}

export function createEmail(email: Partial<EmailItem>): Promise<EmailItem> {
  return request("/api/emails", {
    method: "POST",
    body: JSON.stringify(email),
  });
}

export function deleteEmail(id: number): Promise<{ message: string }> {
  return request(`/api/emails/${id}`, { method: "DELETE" });
}

// Expenses
export interface ExpenseItem {
  id: number;
  description: string;
  amount: number;
  category: string;
  expense_date?: string | null;
  vendor?: string | null;
  created_at?: string | null;
}

export interface ExpenseSummaryData {
  total: number;
  by_category: Record<string, number>;
  count: number;
}

export function getExpenses(): Promise<ExpenseItem[]> {
  return request("/api/expenses");
}

export function createExpense(expense: Partial<ExpenseItem>): Promise<ExpenseItem> {
  return request("/api/expenses", {
    method: "POST",
    body: JSON.stringify(expense),
  });
}

export function getExpenseSummary(): Promise<ExpenseSummaryData> {
  return request("/api/expenses/summary");
}

export function deleteExpense(id: number): Promise<{ message: string }> {
  return request(`/api/expenses/${id}`, { method: "DELETE" });
}

// Documents
export interface DocumentItem {
  id: number;
  title: string;
  content?: string | null;
  summary?: string | null;
  doc_type?: string | null;
  created_at?: string | null;
}

export function getDocuments(): Promise<DocumentItem[]> {
  return request("/api/documents");
}

export function createDocument(doc: Partial<DocumentItem>): Promise<DocumentItem> {
  return request("/api/documents", {
    method: "POST",
    body: JSON.stringify(doc),
  });
}

export function deleteDocument(id: number): Promise<{ message: string }> {
  return request(`/api/documents/${id}`, { method: "DELETE" });
}

// Meetings
export interface MeetingItem {
  id: number;
  title: string;
  description?: string | null;
  attendees?: string | null;
  meeting_date: string;
  meeting_time?: string | null;
  duration_minutes: number;
  location?: string | null;
  created_at?: string | null;
}

export function getMeetings(): Promise<MeetingItem[]> {
  return request("/api/meetings");
}

export function createMeeting(meeting: Partial<MeetingItem>): Promise<MeetingItem> {
  return request("/api/meetings", {
    method: "POST",
    body: JSON.stringify(meeting),
  });
}

export function deleteMeeting(id: number): Promise<{ message: string }> {
  return request(`/api/meetings/${id}`, { method: "DELETE" });
}

// Reports
export interface ReportItem {
  id: number;
  title: string;
  content: string;
  report_type?: string | null;
  created_at?: string | null;
}

export function getReports(): Promise<ReportItem[]> {
  return request("/api/reports");
}

// Dashboard
export interface DashboardStats {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  total_expenses: number;
  total_emails: number;
  upcoming_meetings: number;
  total_documents: number;
  total_reports: number;
}

export function getDashboard(): Promise<DashboardStats> {
  return request("/api/dashboard");
}
