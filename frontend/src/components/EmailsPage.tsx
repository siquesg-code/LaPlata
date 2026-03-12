import { useState, useEffect } from "react";
import { Plus, Trash2, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { getEmails, createEmail, deleteEmail, type EmailItem } from "@/api";

export default function EmailsPage() {
  const [emails, setEmails] = useState<EmailItem[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newEmail, setNewEmail] = useState({ to_address: "", subject: "", body: "" });

  const loadEmails = () => {
    getEmails().then(setEmails).catch(console.error);
  };

  useEffect(() => {
    loadEmails();
  }, []);

  const handleCreate = async () => {
    if (!newEmail.to_address.trim() || !newEmail.subject.trim()) return;
    await createEmail(newEmail);
    setNewEmail({ to_address: "", subject: "", body: "" });
    setDialogOpen(false);
    loadEmails();
  };

  const handleDelete = async (id: number) => {
    await deleteEmail(id);
    loadEmails();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">Emails</h1>
          <p className="text-sm text-zinc-500">Manage your drafted emails</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Email
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Draft New Email</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label>To</Label>
                <Input
                  placeholder="recipient@example.com"
                  value={newEmail.to_address}
                  onChange={(e) => setNewEmail({ ...newEmail, to_address: e.target.value })}
                />
              </div>
              <div>
                <Label>Subject</Label>
                <Input
                  placeholder="Email subject"
                  value={newEmail.subject}
                  onChange={(e) => setNewEmail({ ...newEmail, subject: e.target.value })}
                />
              </div>
              <div>
                <Label>Body</Label>
                <Textarea
                  placeholder="Email body..."
                  rows={6}
                  value={newEmail.body}
                  onChange={(e) => setNewEmail({ ...newEmail, body: e.target.value })}
                />
              </div>
              <Button onClick={handleCreate} className="w-full">
                Save Draft
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-3">
        {emails.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-zinc-500">
              No emails yet. Draft one or ask the AI to compose emails for you!
            </CardContent>
          </Card>
        ) : (
          emails.map((email) => (
            <Card key={email.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center shrink-0 mt-0.5">
                      <Mail className="w-4 h-4 text-purple-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-zinc-900">{email.subject}</h3>
                      <p className="text-sm text-zinc-500">To: {email.to_address}</p>
                      <p className="text-sm text-zinc-600 mt-2 whitespace-pre-wrap line-clamp-3">
                        {email.body}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge
                          className={
                            email.status === "sent"
                              ? "bg-green-100 text-green-800"
                              : "bg-yellow-100 text-yellow-800"
                          }
                        >
                          {email.status}
                        </Badge>
                        {email.created_at && (
                          <span className="text-xs text-zinc-400">
                            {new Date(email.created_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(email.id)}
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
