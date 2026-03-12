import { useState, useEffect } from "react";
import { Plus, Trash2, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  getExpenses,
  createExpense,
  deleteExpense,
  getExpenseSummary,
  type ExpenseItem,
  type ExpenseSummaryData,
} from "@/api";

const categoryColors: Record<string, string> = {
  travel: "bg-blue-100 text-blue-800",
  office: "bg-green-100 text-green-800",
  software: "bg-purple-100 text-purple-800",
  marketing: "bg-orange-100 text-orange-800",
  salary: "bg-cyan-100 text-cyan-800",
  utilities: "bg-yellow-100 text-yellow-800",
  other: "bg-zinc-100 text-zinc-800",
};

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<ExpenseItem[]>([]);
  const [summary, setSummary] = useState<ExpenseSummaryData | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newExpense, setNewExpense] = useState({
    description: "",
    amount: "",
    category: "other",
    vendor: "",
    expense_date: "",
  });

  const load = () => {
    getExpenses().then(setExpenses).catch(console.error);
    getExpenseSummary().then(setSummary).catch(console.error);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async () => {
    if (!newExpense.description.trim() || !newExpense.amount) return;
    await createExpense({
      description: newExpense.description,
      amount: parseFloat(newExpense.amount),
      category: newExpense.category,
      vendor: newExpense.vendor || undefined,
      expense_date: newExpense.expense_date || undefined,
    });
    setNewExpense({ description: "", amount: "", category: "other", vendor: "", expense_date: "" });
    setDialogOpen(false);
    load();
  };

  const handleDelete = async (id: number) => {
    await deleteExpense(id);
    load();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">Expenses</h1>
          <p className="text-sm text-zinc-500">Track and manage your business expenses</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Expense
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Expense</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label>Description</Label>
                <Input
                  placeholder="Expense description"
                  value={newExpense.description}
                  onChange={(e) => setNewExpense({ ...newExpense, description: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Amount ($)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={newExpense.amount}
                    onChange={(e) => setNewExpense({ ...newExpense, amount: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Category</Label>
                  <Select
                    value={newExpense.category}
                    onValueChange={(v) => setNewExpense({ ...newExpense, category: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="travel">Travel</SelectItem>
                      <SelectItem value="office">Office</SelectItem>
                      <SelectItem value="software">Software</SelectItem>
                      <SelectItem value="marketing">Marketing</SelectItem>
                      <SelectItem value="salary">Salary</SelectItem>
                      <SelectItem value="utilities">Utilities</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Vendor</Label>
                  <Input
                    placeholder="Vendor (optional)"
                    value={newExpense.vendor}
                    onChange={(e) => setNewExpense({ ...newExpense, vendor: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Date</Label>
                  <Input
                    type="date"
                    value={newExpense.expense_date}
                    onChange={(e) => setNewExpense({ ...newExpense, expense_date: e.target.value })}
                  />
                </div>
              </div>
              <Button onClick={handleCreate} className="w-full">
                Add Expense
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Card */}
      {summary && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-6">
              <div>
                <p className="text-sm text-zinc-500">Total Expenses</p>
                <p className="text-3xl font-bold text-zinc-900">
                  ${summary.total.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="text-sm text-zinc-500">
                {summary.count} expense{summary.count !== 1 ? "s" : ""}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Expense List */}
      <div className="space-y-3">
        {expenses.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-zinc-500">
              No expenses yet. Add one or ask the AI to track expenses for you!
            </CardContent>
          </Card>
        ) : (
          expenses.map((expense) => (
            <Card key={expense.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
                      <DollarSign className="w-4 h-4 text-emerald-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-zinc-900">{expense.description}</h3>
                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        <Badge className={categoryColors[expense.category] || "bg-zinc-100"}>
                          {expense.category}
                        </Badge>
                        {expense.vendor && (
                          <span className="text-xs text-zinc-500">{expense.vendor}</span>
                        )}
                        {expense.expense_date && (
                          <span className="text-xs text-zinc-500">{expense.expense_date}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-lg text-zinc-900">
                      ${expense.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(expense.id)}
                      className="text-zinc-400 hover:text-red-600"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
