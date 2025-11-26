import pandas as pd
import matplotlib.pyplot as plt
from data_handler import DataHandler

class EventLogic:
    def __init__(self):
        self.handler = DataHandler()
        self.sheet_events = "events"
        self.sheet_tasks = "tasks"
        self.sheet_attendees = "attendees"

    # ================= EVENTS =================
    def get_events(self):
        df = self.handler.load_data(self.sheet_events)
        required_cols = ['id', 'name', 'date', 'time', 'location', 'description']
        if df.empty: return pd.DataFrame(columns=required_cols)
        for col in required_cols:
            if col not in df.columns: df[col] = ""
        if 'id' in df.columns:
             df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        return df

    def add_event(self, name, date, time, location, description):
        events_df = self.get_events()
        events = events_df.to_dict('records')
        new_id = 1 if not events else max([int(e['id']) for e in events]) + 1
        new_event = {"id": new_id, "name": name, "date": str(date), "time": str(time), "location": location, "description": description}
        events.append(new_event)
        return self.handler.save_data(events, self.sheet_events)

    # --- NEW: DELETE EVENT ---
    def delete_event(self, event_id):
        # 1. Delete the event itself
        res = self.handler.delete_data(self.sheet_events, "id", event_id)
        # 2. Optional: Delete associated data (Cleanup)
        self.handler.delete_data(self.sheet_attendees, "event_id", event_id)
        self.handler.delete_data(self.sheet_tasks, "event_id", event_id)
        return res

    # ================= ATTENDEES =================
    def get_attendees(self, event_id=None):
        df = self.handler.load_data(self.sheet_attendees)
        cols = ['event_id', 'name', 'email', 'rsvp', 'role', 'dietary']
        if df.empty: return pd.DataFrame(columns=cols)
        if 'event_id' in df.columns:
             df['event_id'] = pd.to_numeric(df['event_id'], errors='coerce').fillna(0).astype(int)
        if event_id: return df[df['event_id'] == int(event_id)]
        return df

    def add_attendee(self, event_id, name, email, rsvp, role, dietary):
        df = self.handler.load_data(self.sheet_attendees)
        attendees = df.to_dict('records') if not df.empty else []
        new_att = {"event_id": int(event_id), "name": name, "email": email, "rsvp": rsvp, "role": role, "dietary": dietary}
        attendees.append(new_att)
        return self.handler.save_data(attendees, self.sheet_attendees)

    # ================= TASKS =================
    def get_tasks(self, event_id=None):
        df = self.handler.load_data(self.sheet_tasks)
        cols = ['event_id', 'task_name', 'status', 'deadline', 'priority']
        if df.empty: return pd.DataFrame(columns=cols)
        if 'event_id' in df.columns:
             df['event_id'] = pd.to_numeric(df['event_id'], errors='coerce').fillna(0).astype(int)
        if event_id: return df[df['event_id'] == int(event_id)]
        return df

    def add_task(self, event_id, task_name, status, deadline, priority="Medium"):
        df = self.handler.load_data(self.sheet_tasks)
        tasks = df.to_dict('records') if not df.empty else []
        new_task = {"event_id": int(event_id), "task_name": task_name, "status": status, "deadline": str(deadline), "priority": priority}
        tasks.append(new_task)
        return self.handler.save_data(tasks, self.sheet_tasks)

    # ================= ANALYTICS =================
    def get_rsvp_pie_chart(self, event_id):
        attendees = self.get_attendees(event_id)
        if attendees.empty: return None
        rsvp_counts = attendees['rsvp'].value_counts()
        fig, ax = plt.subplots(figsize=(4,3))
        fig.patch.set_alpha(0.0) 
        ax.patch.set_alpha(0.0)
        
        # Determine text color based on theme via logic arg isn't ideal, 
        # but standard white/black usually works if we set auto colors.
        # For now keeping white as base, will adjust in app.py control if needed.
        wedges, texts, autotexts = ax.pie(
            rsvp_counts, 
            labels=rsvp_counts.index, 
            autopct='%1.1f%%', 
            textprops={'color':"white"} # You might want to make this dynamic later
        )
        return fig

    def get_task_status_chart(self, event_id):
        tasks = self.get_tasks(event_id)
        if tasks.empty: return None
        status_counts = tasks['status'].value_counts()
        fig, ax = plt.subplots(figsize=(4,3))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        status_counts.plot(kind='bar', color=['#FF4B4B', '#FFA500', '#4CAF50'], ax=ax)
        ax.tick_params(colors='white', axis='x')
        ax.tick_params(colors='white', axis='y')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        return fig
