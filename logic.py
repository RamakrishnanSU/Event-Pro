import pandas as pd
import matplotlib.pyplot as plt
import os
from data_handler import DataHandler

# Use current directory for files to make it portable
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

class EventLogic:
    def __init__(self):
        self.handler = DataHandler()
        self.event_file = os.path.join(WORKING_DIR, "events.csv")
        self.task_file = os.path.join(WORKING_DIR, "tasks.csv")
        self.attendee_file = os.path.join(WORKING_DIR, "attendees.csv")

    # ================= EVENTS =================
    def get_events(self):
        df = self.handler.load_from_csv(self.event_file)
        return df if isinstance(df, pd.DataFrame) and not df.empty else pd.DataFrame(columns=['id', 'name', 'date', 'time', 'location'])

    def add_event(self, name, date, time, location, description):
        events = self.get_events().to_dict('records')
        # Simple ID generation: max id + 1
        new_id = 1 if not events else max([int(e['id']) for e in events]) + 1
        
        new_event = {
            "id": new_id,
            "name": name,
            "date": str(date),
            "time": str(time),
            "location": location,
            "description": description
        }
        events.append(new_event)
        return self.handler.save_to_csv(events, self.event_file)

    # ================= ATTENDEES =================
    def get_attendees(self, event_id=None):
        df = self.handler.load_from_csv(self.attendee_file)
        if df.empty:
            return pd.DataFrame(columns=['event_id', 'name', 'email', 'rsvp', 'role', 'dietary'])
        
        if event_id:
            # Filter for specific event
            return df[df['event_id'] == int(event_id)]
        return df

    def add_attendee(self, event_id, name, email, rsvp, role, dietary):
        attendees = self.get_attendees().to_dict('records') # Load ALL attendees
        new_attendee = {
            "event_id": int(event_id),
            "name": name,
            "email": email,
            "rsvp": rsvp,
            "role": role,
            "dietary": dietary
        }
        attendees.append(new_attendee)
        return self.handler.save_to_csv(attendees, self.attendee_file)

    # ================= TASKS =================
    def get_tasks(self, event_id=None):
        df = self.handler.load_from_csv(self.task_file)
        if df.empty:
             return pd.DataFrame(columns=['event_id', 'task_name', 'status', 'deadline', 'priority'])
        
        if event_id:
            return df[df['event_id'] == int(event_id)]
        return df

    def add_task(self, event_id, task_name, status, deadline, priority="Medium"):
        tasks = self.get_tasks().to_dict('records') # Load ALL tasks
        new_task = {
            "event_id": int(event_id),
            "task_name": task_name,
            "status": status,
            "deadline": str(deadline),
            "priority": priority
        }
        tasks.append(new_task)
        return self.handler.save_to_csv(tasks, self.task_file)

    def update_task_status(self, event_id, task_name, new_status):
        tasks = self.get_tasks().to_dict('records')
        updated = False
        for task in tasks:
            if str(task.get("event_id")) == str(event_id) and task["task_name"] == task_name:
                task["status"] = new_status
                updated = True
        
        if updated:
            self.handler.save_to_csv(tasks, self.task_file)
            return "Task updated successfully."
        return "Task not found."

    # ================= ANALYTICS (Returns Figures) =================
    def get_rsvp_pie_chart(self, event_id):
        attendees = self.get_attendees(event_id)
        if attendees.empty: return None
        
        rsvp_counts = attendees['rsvp'].value_counts()
        fig, ax = plt.subplots()
        rsvp_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_title('RSVP Status')
        ax.set_ylabel('')
        return fig

    def get_task_status_chart(self, event_id):
        tasks = self.get_tasks(event_id)
        if tasks.empty: return None

        status_counts = tasks['status'].value_counts()
        fig, ax = plt.subplots()
        status_counts.plot(kind='bar', color=['red', 'orange', 'green', 'purple'], ax=ax)
        ax.set_title('Task Status')
        return fig

    def get_timeline_chart(self, event_id):
        events = self.get_events()
        tasks = self.get_tasks(event_id)
        
        if events.empty or tasks.empty: return None
        
        event = events[events['id'] == int(event_id)]
        if event.empty: return None
        
        # Logic from your original code, adapted for web
        tasks['deadline'] = pd.to_datetime(tasks['deadline'])
        event_date = pd.to_datetime(event['date'].values[0])

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.axvline(x=event_date, color='r', linestyle='--', label='Event Date')

        for i, task in tasks.reset_index().iterrows():
            color = 'green' if task['status'] == 'Completed' else 'orange'
            ax.scatter(task['deadline'], i, color=color, s=100)
            ax.text(task['deadline'], i, f"  {task['task_name']}", va='center')

        ax.set_title('Project Timeline')
        ax.set_yticks([])
        fig.autofmt_xdate()
        return fig