import { useState, useEffect } from "react";
import { Plus, Trash2, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { getDocuments, createDocument, deleteDocument, type DocumentItem } from "@/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newDoc, setNewDoc] = useState({ title: "", content: "", doc_type: "" });

  const load = () => {
    getDocuments().then(setDocuments).catch(console.error);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async () => {
    if (!newDoc.title.trim()) return;
    await createDocument({
      title: newDoc.title,
      content: newDoc.content,
      doc_type: newDoc.doc_type || undefined,
    });
    setNewDoc({ title: "", content: "", doc_type: "" });
    setDialogOpen(false);
    load();
  };

  const handleDelete = async (id: number) => {
    await deleteDocument(id);
    load();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">Documents</h1>
          <p className="text-sm text-zinc-500">Store and summarize your documents</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Document
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Document</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label>Title</Label>
                <Input
                  placeholder="Document title"
                  value={newDoc.title}
                  onChange={(e) => setNewDoc({ ...newDoc, title: e.target.value })}
                />
              </div>
              <div>
                <Label>Type</Label>
                <Input
                  placeholder="e.g., report, memo, policy (optional)"
                  value={newDoc.doc_type}
                  onChange={(e) => setNewDoc({ ...newDoc, doc_type: e.target.value })}
                />
              </div>
              <div>
                <Label>Content</Label>
                <Textarea
                  placeholder="Document content..."
                  rows={8}
                  value={newDoc.content}
                  onChange={(e) => setNewDoc({ ...newDoc, content: e.target.value })}
                />
              </div>
              <Button onClick={handleCreate} className="w-full">
                Save Document
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-3">
        {documents.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-zinc-500">
              No documents yet. Add one or ask the AI to summarize documents for you!
            </CardContent>
          </Card>
        ) : (
          documents.map((doc) => (
            <Card key={doc.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center shrink-0 mt-0.5">
                      <FileText className="w-4 h-4 text-yellow-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium text-zinc-900">{doc.title}</h3>
                        {doc.doc_type && (
                          <Badge className="bg-zinc-100 text-zinc-800">{doc.doc_type}</Badge>
                        )}
                      </div>
                      {doc.summary && (
                        <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-800">
                          <strong>Summary:</strong> {doc.summary}
                        </div>
                      )}
                      {doc.content && !doc.summary && (
                        <p className="text-sm text-zinc-500 mt-1 line-clamp-2">{doc.content}</p>
                      )}
                      {doc.created_at && (
                        <span className="text-xs text-zinc-400 mt-2 inline-block">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(doc.id)}
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
