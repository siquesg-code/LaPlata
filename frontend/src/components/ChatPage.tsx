import { useState, useEffect, useRef } from "react";
import { Send, Bot, User, Trash2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { sendChat, getChatHistory, clearChatHistory, type ChatMessage } from "@/api";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getChatHistory().then(setMessages).catch(console.error);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg: ChatMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const response = await sendChat(input);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    await clearChatHistory();
    setMessages([]);
  };

  const toolBadgeColor = (tool: string | null | undefined) => {
    if (!tool) return "";
    const colors: Record<string, string> = {
      create_task: "bg-green-100 text-green-800",
      list_tasks: "bg-blue-100 text-blue-800",
      complete_task: "bg-emerald-100 text-emerald-800",
      draft_email: "bg-purple-100 text-purple-800",
      add_expense: "bg-orange-100 text-orange-800",
      schedule_meeting: "bg-cyan-100 text-cyan-800",
      generate_report: "bg-rose-100 text-rose-800",
      summarize_document: "bg-yellow-100 text-yellow-800",
      get_dashboard: "bg-indigo-100 text-indigo-800",
    };
    return colors[tool] || "bg-zinc-100 text-zinc-800";
  };

  const renderMarkdown = (text: string) => {
    // Simple markdown rendering
    const lines = text.split("\n");
    return lines.map((line, i) => {
      if (line.startsWith("## ")) {
        return (
          <h2 key={i} className="text-lg font-bold mt-3 mb-1">
            {line.slice(3)}
          </h2>
        );
      }
      if (line.startsWith("# ")) {
        return (
          <h1 key={i} className="text-xl font-bold mt-3 mb-1">
            {line.slice(2)}
          </h1>
        );
      }
      if (line.startsWith("### ")) {
        return (
          <h3 key={i} className="text-base font-semibold mt-2 mb-1">
            {line.slice(4)}
          </h3>
        );
      }
      if (line.startsWith("- ")) {
        const content = line.slice(2);
        const parts = content.split(/(\*\*.*?\*\*)/g);
        return (
          <li key={i} className="ml-4 list-disc">
            {parts.map((part, partIdx) => {
              const boldMatch = part.match(/^\*\*(.*?)\*\*$/);
              return boldMatch ? <strong key={partIdx}>{boldMatch[1]}</strong> : part;
            })}
          </li>
        );
      }
      if (line.trim() === "") {
        return <br key={i} />;
      }
      const parts: (string | JSX.Element)[] = [];
      const boldRegex = /\*\*(.*?)\*\*/g;
      let lastIndex = 0;
      let match: RegExpExecArray | null;

      while ((match = boldRegex.exec(line)) !== null) {
        if (match.index > lastIndex) {
          parts.push(line.slice(lastIndex, match.index));
        }
        parts.push(<strong key={`${i}-b-${match.index}`}>{match[1]}</strong>);
        lastIndex = match.index + match[0].length;
      }

      if (lastIndex < line.length) {
        parts.push(line.slice(lastIndex));
      }

      return <p key={i}>{parts}</p>;
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b bg-white px-6 py-4 flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-xl font-bold text-zinc-900">AI Assistant</h1>
          <p className="text-sm text-zinc-500">
            Chat with your AI business admin assistant
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={handleClear}>
          <Trash2 className="w-4 h-4 mr-2" />
          Clear Chat
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-6" ref={scrollRef}>
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-20">
              <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
                <Bot className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-lg font-semibold text-zinc-900 mb-2">
                Welcome to AI Admin Assistant
              </h2>
              <p className="text-zinc-500 mb-6 max-w-md mx-auto">
                I can help you manage tasks, draft emails, track expenses, schedule
                meetings, and more. Try one of these:
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {[
                  "Show me my dashboard",
                  "Create task Review budget",
                  "Add expense $200 for software",
                  "Schedule meeting tomorrow",
                  "Draft email about project update",
                ].map((suggestion) => (
                  <Button
                    key={suggestion}
                    variant="outline"
                    size="sm"
                    className="text-xs"
                    onClick={() => {
                      setInput(suggestion);
                    }}
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0 mt-1">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <Card
                className={`max-w-2xl px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white border-blue-600"
                    : "bg-white"
                }`}
              >
                {msg.tool_used && (
                  <Badge className={`mb-2 text-xs ${toolBadgeColor(msg.tool_used)}`}>
                    {msg.tool_used.replace(/_/g, " ")}
                  </Badge>
                )}
                <div className={`text-sm leading-relaxed ${msg.role === "user" ? "text-white" : "text-zinc-800"}`}>
                  {msg.role === "assistant" ? renderMarkdown(msg.content) : msg.content}
                </div>
              </Card>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-full bg-zinc-200 flex items-center justify-center shrink-0 mt-1">
                  <User className="w-4 h-4 text-zinc-600" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <Card className="px-4 py-3 bg-white">
                <div className="flex items-center gap-2 text-sm text-zinc-500">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Thinking...
                </div>
              </Card>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t bg-white px-6 py-4 shrink-0">
        <div className="max-w-3xl mx-auto flex gap-3">
          <Input
            placeholder="Type a message... (e.g., 'Create task Review Q1 budget')"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={loading}
            className="flex-1"
          />
          <Button onClick={handleSend} disabled={loading || !input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
