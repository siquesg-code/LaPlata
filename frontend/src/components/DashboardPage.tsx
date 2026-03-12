import { useState, useEffect } from "react";
import {
  CheckSquare,
  Mail,
  DollarSign,
  Calendar,
  FileText,
  BarChart3,
  TrendingUp,
  Clock,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { getDashboard, getExpenseSummary, type DashboardStats, type ExpenseSummaryData } from "@/api";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899"];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [expenseSummary, setExpenseSummary] = useState<ExpenseSummaryData | null>(null);

  useEffect(() => {
    getDashboard().then(setStats).catch(console.error);
    getExpenseSummary().then(setExpenseSummary).catch(console.error);
  }, []);

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-zinc-500">Loading dashboard...</p>
      </div>
    );
  }

  const statCards = [
    {
      title: "Total Tasks",
      value: stats.total_tasks,
      icon: CheckSquare,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      title: "Completed Tasks",
      value: stats.completed_tasks,
      icon: TrendingUp,
      color: "text-green-600",
      bg: "bg-green-50",
    },
    {
      title: "Pending Tasks",
      value: stats.pending_tasks,
      icon: Clock,
      color: "text-orange-600",
      bg: "bg-orange-50",
    },
    {
      title: "Total Expenses",
      value: `$${stats.total_expenses.toLocaleString("en-US", { minimumFractionDigits: 2 })}`,
      icon: DollarSign,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
    },
    {
      title: "Emails Drafted",
      value: stats.total_emails,
      icon: Mail,
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
    {
      title: "Upcoming Meetings",
      value: stats.upcoming_meetings,
      icon: Calendar,
      color: "text-cyan-600",
      bg: "bg-cyan-50",
    },
    {
      title: "Documents",
      value: stats.total_documents,
      icon: FileText,
      color: "text-yellow-600",
      bg: "bg-yellow-50",
    },
    {
      title: "Reports",
      value: stats.total_reports,
      icon: BarChart3,
      color: "text-rose-600",
      bg: "bg-rose-50",
    },
  ];

  const taskChartData = [
    { name: "To Do", value: stats.pending_tasks - (stats.total_tasks - stats.completed_tasks - stats.pending_tasks), fill: "#3b82f6" },
    { name: "Done", value: stats.completed_tasks, fill: "#10b981" },
  ].filter((d) => d.value > 0);

  const expenseChartData = expenseSummary
    ? Object.entries(expenseSummary.by_category).map(([key, val]) => ({
        name: key.charAt(0).toUpperCase() + key.slice(1),
        amount: val,
      }))
    : [];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900">Dashboard</h1>
        <p className="text-sm text-zinc-500">Overview of your business operations</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <Card key={card.title}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-zinc-500">{card.title}</p>
                    <p className="text-2xl font-bold mt-1">{card.value}</p>
                  </div>
                  <div className={`w-10 h-10 rounded-lg ${card.bg} flex items-center justify-center`}>
                    <Icon className={`w-5 h-5 ${card.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Task Status Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Task Status</CardTitle>
          </CardHeader>
          <CardContent>
            {taskChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={taskChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {taskChartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-zinc-400">
                No tasks yet. Create some via the AI chat!
              </div>
            )}
          </CardContent>
        </Card>

        {/* Expense Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Expenses by Category</CardTitle>
          </CardHeader>
          <CardContent>
            {expenseChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={expenseChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                  <Bar dataKey="amount" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-zinc-400">
                No expenses yet. Track them via the AI chat!
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
