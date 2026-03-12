import { useState, useEffect } from "react";
import { BarChart3 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getReports, type ReportItem } from "@/api";

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportItem[]>([]);

  useEffect(() => {
    getReports().then(setReports).catch(console.error);
  }, []);

  const renderMarkdown = (text: string) => {
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
        const content = line.slice(2).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        return (
          <li
            key={i}
            className="ml-4 list-disc"
            dangerouslySetInnerHTML={{ __html: content }}
          />
        );
      }
      if (line.trim() === "") return <br key={i} />;
      const content = line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      return <p key={i} dangerouslySetInnerHTML={{ __html: content }} />;
    });
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900">Reports</h1>
        <p className="text-sm text-zinc-500">
          Generated reports. Ask the AI to generate new ones!
        </p>
      </div>

      <div className="space-y-4">
        {reports.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-zinc-500">
              No reports yet. Ask the AI to &ldquo;Generate expense report&rdquo; or
              &ldquo;Generate task report&rdquo;!
            </CardContent>
          </Card>
        ) : (
          reports.map((report) => (
            <Card key={report.id}>
              <CardContent className="p-6">
                <div className="flex items-start gap-3 mb-4">
                  <div className="w-8 h-8 rounded-full bg-rose-100 flex items-center justify-center shrink-0">
                    <BarChart3 className="w-4 h-4 text-rose-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-zinc-900">{report.title}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      {report.report_type && (
                        <Badge className="bg-rose-100 text-rose-800">
                          {report.report_type}
                        </Badge>
                      )}
                      {report.created_at && (
                        <span className="text-xs text-zinc-400">
                          {new Date(report.created_at).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="text-sm text-zinc-700 leading-relaxed border-t pt-4">
                  {renderMarkdown(report.content)}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
