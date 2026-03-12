import { useEffect, useState } from "react";
import Layout from "@/components/Layout";
import LoginPage from "@/components/LoginPage";
import RegisterPage from "@/components/RegisterPage";
import ChatPage from "@/components/ChatPage";
import DashboardPage from "@/components/DashboardPage";
import TasksPage from "@/components/TasksPage";
import EmailsPage from "@/components/EmailsPage";
import ExpensesPage from "@/components/ExpensesPage";
import MeetingsPage from "@/components/MeetingsPage";
import DocumentsPage from "@/components/DocumentsPage";
import ReportsPage from "@/components/ReportsPage";
import { getMe, login, register, logout, type UserInfo } from "@/api";

function App() {
  const [page, setPage] = useState("chat");
  const [authView, setAuthView] = useState<"login" | "register">("login");
  const [user, setUser] = useState<UserInfo | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      getMe()
        .then(setUser)
        .catch(() => localStorage.removeItem("access_token"))
        .finally(() => setAuthLoading(false));
    } else {
      setAuthLoading(false);
    }
  }, []);

  const handleLogin = async (email: string, password: string) => {
    setAuthError(null);
    try {
      const res = await login(email, password);
      localStorage.setItem("access_token", res.access_token);
      const me = await getMe();
      setUser(me);
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Login failed");
    }
  };

  const handleRegister = async (data: {
    email: string;
    password: string;
    full_name: string;
    organization_name: string;
  }) => {
    setAuthError(null);
    try {
      const res = await register(data);
      localStorage.setItem("access_token", res.access_token);
      const me = await getMe();
      setUser(me);
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Registration failed");
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-50">
        <p className="text-zinc-400">Loading...</p>
      </div>
    );
  }

  if (!user) {
    if (authView === "register") {
      return (
        <RegisterPage
          onRegister={handleRegister}
          onSwitchToLogin={() => { setAuthView("login"); setAuthError(null); }}
          error={authError}
        />
      );
    }
    return (
      <LoginPage
        onLogin={handleLogin}
        onSwitchToRegister={() => { setAuthView("register"); setAuthError(null); }}
        error={authError}
      />
    );
  }

  const renderPage = () => {
    switch (page) {
      case "chat":
        return <ChatPage />;
      case "dashboard":
        return <DashboardPage />;
      case "tasks":
        return <TasksPage />;
      case "emails":
        return <EmailsPage />;
      case "expenses":
        return <ExpensesPage />;
      case "meetings":
        return <MeetingsPage />;
      case "documents":
        return <DocumentsPage />;
      case "reports":
        return <ReportsPage />;
      default:
        return <ChatPage />;
    }
  };

  return (
    <Layout currentPage={page} onNavigate={setPage} user={user} onLogout={logout}>
      {renderPage()}
    </Layout>
  );
}

export default App;
