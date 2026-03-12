import { useState } from "react";
import Layout from "@/components/Layout";
import ChatPage from "@/components/ChatPage";
import DashboardPage from "@/components/DashboardPage";
import TasksPage from "@/components/TasksPage";
import EmailsPage from "@/components/EmailsPage";
import ExpensesPage from "@/components/ExpensesPage";
import MeetingsPage from "@/components/MeetingsPage";
import DocumentsPage from "@/components/DocumentsPage";
import ReportsPage from "@/components/ReportsPage";

function App() {
  const [page, setPage] = useState("chat");

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
    <Layout currentPage={page} onNavigate={setPage}>
      {renderPage()}
    </Layout>
  );
}

export default App;
