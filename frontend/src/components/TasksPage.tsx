import { useState, useEffect } from "react";
import { Plus, Trash2, CheckCircle, Circle, Clock, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
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
import { Textarea } from "@/components/ui/textarea";
import { getTasks, createTask, updateTask, deleteTask, type TaskItem } from "@/api";

const priorityConfig: Record<string, { color: string; icon: typeof AlertTriangle }> = {
  urgent: { color: "bg-red-100 text-red-800", icon: AlertTriangle },
  high: { color: "bg-orange-100 text-orange-800", icon: AlertTriangle },
  medium: { color: "bg-blue-100 text-blue-800", icon: Clock },
  low: { color: "bg-zinc-100 text-zinc-800", icon: Circle },
};

const statusConfig: Record<string, { label: string; color: string }> = {
  todo: { label: "To Do", color: "bg-zinc-100 text-zinc-800" },
  in_progress: { label: "In Progress", color: "bg-blue-100 text-blue-800" },
  done: { label: "Done", color: "bg-green-100 text-green-800" },
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    priority: "medium",
    status: "todo",
    due_date: "",
    assignee: "",
  });

  const loadTasks = () => {
    const statusParam = filter === "all" ? undefined : filter;
    getTasks(statusParam).then(setTasks).catch(console.error);
  };

  useEffect(() => {
    loadTasks();
  }, [filter]);

  const handleCreate = async () => {
    if (!newTask.title.trim()) return;
    await createTask({
      ...newTask,
      due_date: newTask.due_date || undefined,
      assignee: newTask.assignee || undefined,
    });
    setNewTask({ title: "", description: "", priority: "medium", status: "todo", due_date: "", assignee: "" });
    setDialogOpen(false);
    loadTasks();
  };

  const handleStatusChange = async (id: number, status: string) => {
    await updateTask(id, { status });
    loadTasks();
  };

  const handleDelete = async (id: number) => {
    await deleteTask(id);
    loadTasks();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">Tasks</h1>
          <p className="text-sm text-zinc-500">Manage your tasks and to-dos</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Task
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Task</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label>Title</Label>
                <Input
                  placeholder="Task title"
                  value={newTask.title}
                  onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea
                  placeholder="Task description (optional)"
                  value={newTask.description}
                  onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Priority</Label>
                  <Select
                    value={newTask.priority}
                    onValueChange={(v) => setNewTask({ ...newTask, priority: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Due Date</Label>
                  <Input
                    type="date"
                    value={newTask.due_date}
                    onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <Label>Assignee</Label>
                <Input
                  placeholder="Assigned to (optional)"
                  value={newTask.assignee}
                  onChange={(e) => setNewTask({ ...newTask, assignee: e.target.value })}
                />
              </div>
              <Button onClick={handleCreate} className="w-full">
                Create Task
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {["all", "todo", "in_progress", "done"].map((f) => (
          <Button
            key={f}
            variant={filter === f ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter(f)}
          >
            {f === "all" ? "All" : f === "in_progress" ? "In Progress" : f === "todo" ? "To Do" : "Done"}
          </Button>
        ))}
      </div>

      {/* Task List */}
      <div className="space-y-3">
        {tasks.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-zinc-500">
              No tasks found. Create one or ask the AI to create tasks for you!
            </CardContent>
          </Card>
        ) : (
          tasks.map((task) => (
            <Card key={task.id} className={task.status === "done" ? "opacity-60" : ""}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <button
                      onClick={() =>
                        handleStatusChange(
                          task.id,
                          task.status === "done" ? "todo" : task.status === "todo" ? "in_progress" : "done"
                        )
                      }
                      className="mt-0.5"
                    >
                      {task.status === "done" ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : task.status === "in_progress" ? (
                        <Clock className="w-5 h-5 text-blue-600" />
                      ) : (
                        <Circle className="w-5 h-5 text-zinc-400" />
                      )}
                    </button>
                    <div className="flex-1">
                      <h3
                        className={`font-medium ${
                          task.status === "done" ? "line-through text-zinc-500" : "text-zinc-900"
                        }`}
                      >
                        {task.title}
                      </h3>
                      {task.description && (
                        <p className="text-sm text-zinc-500 mt-1">{task.description}</p>
                      )}
                      <div className="flex items-center gap-2 mt-2 flex-wrap">
                        <Badge className={priorityConfig[task.priority]?.color || "bg-zinc-100"}>
                          {task.priority}
                        </Badge>
                        <Badge className={statusConfig[task.status]?.color || "bg-zinc-100"}>
                          {statusConfig[task.status]?.label || task.status}
                        </Badge>
                        {task.due_date && (
                          <span className="text-xs text-zinc-500">Due: {task.due_date}</span>
                        )}
                        {task.assignee && (
                          <span className="text-xs text-zinc-500">@{task.assignee}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(task.id)}
                    className="text-zinc-400 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
