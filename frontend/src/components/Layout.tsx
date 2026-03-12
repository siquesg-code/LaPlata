import { ReactNode } from "react";
import {
  MessageSquare,
  LayoutDashboard,
  CheckSquare,
  Mail,
  DollarSign,
  Calendar,
  FileText,
  BarChart3,
  Bot,
  LogOut,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import type { UserInfo } from "@/api";

interface LayoutProps {
  children: ReactNode;
  currentPage: string;
  onNavigate: (page: string) => void;
  user: UserInfo;
  onLogout: () => void;
}

const navItems = [
  { id: "chat", label: "AI Chat", icon: MessageSquare },
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "tasks", label: "Tasks", icon: CheckSquare },
  { id: "emails", label: "Emails", icon: Mail },
  { id: "expenses", label: "Expenses", icon: DollarSign },
  { id: "meetings", label: "Meetings", icon: Calendar },
  { id: "documents", label: "Documents", icon: FileText },
  { id: "reports", label: "Reports", icon: BarChart3 },
];

export default function Layout({ children, currentPage, onNavigate, user, onLogout }: LayoutProps) {
  return (
    <div className="flex h-screen bg-zinc-50">
      {/* Sidebar */}
      <aside className="w-64 bg-zinc-900 text-white flex flex-col shrink-0">
        <div className="p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight">AI Admin</h1>
            <p className="text-xs text-zinc-400">Business Assistant</p>
          </div>
        </div>
        <Separator className="bg-zinc-700" />
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <Button
                key={item.id}
                variant="ghost"
                className={`w-full justify-start gap-3 text-sm font-medium ${
                  isActive
                    ? "bg-blue-600 text-white hover:bg-blue-700 hover:text-white"
                    : "text-zinc-300 hover:bg-zinc-800 hover:text-white"
                }`}
                onClick={() => onNavigate(item.id)}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </Button>
            );
          })}
        </nav>
        <div className="p-4 space-y-3">
          <div className="rounded-lg bg-zinc-800 p-3">
            <p className="text-sm font-medium text-zinc-200 truncate">{user.full_name}</p>
            <p className="text-xs text-zinc-400 truncate">{user.email}</p>
          </div>
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-sm text-zinc-400 hover:text-white hover:bg-zinc-800"
            onClick={onLogout}
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </Button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
