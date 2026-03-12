import { useState, useEffect } from "react";
import { Plus, Trash2, Calendar, Clock, MapPin, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { getMeetings, createMeeting, deleteMeeting, type MeetingItem } from "@/api";

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<MeetingItem[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newMeeting, setNewMeeting] = useState({
    title: "",
    description: "",
    attendees: "",
    meeting_date: "",
    meeting_time: "10:00",
    duration_minutes: 60,
    location: "",
  });

  const load = () => {
    getMeetings().then(setMeetings).catch(console.error);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async () => {
    if (!newMeeting.title.trim() || !newMeeting.meeting_date) return;
    await createMeeting({
      ...newMeeting,
      duration_minutes: newMeeting.duration_minutes || 60,
    });
    setNewMeeting({
      title: "",
      description: "",
      attendees: "",
      meeting_date: "",
      meeting_time: "10:00",
      duration_minutes: 60,
      location: "",
    });
    setDialogOpen(false);
    load();
  };

  const handleDelete = async (id: number) => {
    await deleteMeeting(id);
    load();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">Meetings</h1>
          <p className="text-sm text-zinc-500">Schedule and manage your meetings</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Meeting
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Schedule New Meeting</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label>Title</Label>
                <Input
                  placeholder="Meeting title"
                  value={newMeeting.title}
                  onChange={(e) => setNewMeeting({ ...newMeeting, title: e.target.value })}
                />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea
                  placeholder="Meeting agenda (optional)"
                  value={newMeeting.description}
                  onChange={(e) =>
                    setNewMeeting({ ...newMeeting, description: e.target.value })
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Date</Label>
                  <Input
                    type="date"
                    value={newMeeting.meeting_date}
                    onChange={(e) =>
                      setNewMeeting({ ...newMeeting, meeting_date: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label>Time</Label>
                  <Input
                    type="time"
                    value={newMeeting.meeting_time}
                    onChange={(e) =>
                      setNewMeeting({ ...newMeeting, meeting_time: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Duration (minutes)</Label>
                  <Input
                    type="number"
                    value={newMeeting.duration_minutes}
                    onChange={(e) =>
                      setNewMeeting({
                        ...newMeeting,
                        duration_minutes: parseInt(e.target.value) || 60,
                      })
                    }
                  />
                </div>
                <div>
                  <Label>Location</Label>
                  <Input
                    placeholder="Room or link"
                    value={newMeeting.location}
                    onChange={(e) =>
                      setNewMeeting({ ...newMeeting, location: e.target.value })
                    }
                  />
                </div>
              </div>
              <div>
                <Label>Attendees</Label>
                <Input
                  placeholder="Comma-separated names"
                  value={newMeeting.attendees}
                  onChange={(e) =>
                    setNewMeeting({ ...newMeeting, attendees: e.target.value })
                  }
                />
              </div>
              <Button onClick={handleCreate} className="w-full">
                Schedule Meeting
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-3">
        {meetings.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-zinc-500">
              No meetings scheduled. Create one or ask the AI to schedule meetings for you!
            </CardContent>
          </Card>
        ) : (
          meetings.map((meeting) => (
            <Card key={meeting.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="w-8 h-8 rounded-full bg-cyan-100 flex items-center justify-center shrink-0 mt-0.5">
                      <Calendar className="w-4 h-4 text-cyan-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-zinc-900">{meeting.title}</h3>
                      {meeting.description && (
                        <p className="text-sm text-zinc-500 mt-1">{meeting.description}</p>
                      )}
                      <div className="flex items-center gap-4 mt-2 flex-wrap text-sm text-zinc-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5" />
                          {meeting.meeting_date}
                        </span>
                        {meeting.meeting_time && (
                          <span className="flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5" />
                            {meeting.meeting_time} ({meeting.duration_minutes}min)
                          </span>
                        )}
                        {meeting.location && (
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3.5 h-3.5" />
                            {meeting.location}
                          </span>
                        )}
                        {meeting.attendees && (
                          <span className="flex items-center gap-1">
                            <Users className="w-3.5 h-3.5" />
                            {meeting.attendees}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(meeting.id)}
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
