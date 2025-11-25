import streamlit as st
import pandas as pd
from logic import EventLogic

# Initialize the logic engine
logic = EventLogic()

# Page Config
st.set_page_config(page_title="Event Manager", layout="wide")
st.title("🎉 Event Manager Dashboard")

# Sidebar Navigation
menu = st.sidebar.radio("Menu", ["Events", "Attendees", "Task Manager", "Analytics"])

# --- 1. EVENTS PAGE ---
if menu == "Events":
    st.header("Manage Events")
    
    # Input Form
    with st.expander("➕ Create New Event"):
        with st.form("event_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Event Name")
            loc = col2.text_input("Location")
            date = col1.date_input("Date")
            time = col2.time_input("Time")
            desc = st.text_area("Description")
            
            if st.form_submit_button("Save Event"):
                res = logic.add_event(name, date, time, loc, desc)
                st.success(res)
    
    # Display Table
    st.subheader("Upcoming Events")
    events_df = logic.get_events()
    if not events_df.empty:
        st.dataframe(events_df, use_container_width=True)
    else:
        st.info("No events found. Create one above!")

# --- 2. ATTENDEES PAGE ---
elif menu == "Attendees":
    st.header("Guest List Management")
    
    # Select Event
    events_df = logic.get_events()
    if events_df.empty:
        st.warning("Please create an event first.")
    else:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_event_id = st.selectbox("Select Event", options=event_names.keys(), format_func=lambda x: event_names[x])
        
        # Add Attendee Form
        with st.expander("Add Attendee"):
            with st.form("attendee_form"):
                c1, c2 = st.columns(2)
                a_name = c1.text_input("Name")
                a_email = c2.text_input("Email")
                a_rsvp = c1.selectbox("RSVP", ["Pending", "Confirmed", "Declined"])
                a_role = c2.text_input("Role (e.g. Guest, Speaker)")
                a_diet = st.text_input("Dietary Restrictions")
                
                if st.form_submit_button("Add Guest"):
                    res = logic.add_attendee(selected_event_id, a_name, a_email, a_rsvp, a_role, a_diet)
                    st.success(res)
        
        # Show List
        attendees = logic.get_attendees(selected_event_id)
        st.write(f"**Guest List for {event_names[selected_event_id]}**")
        st.dataframe(attendees, use_container_width=True)

# --- 3. TASKS PAGE ---
elif menu == "Task Manager":
    st.header("✅ Task Tracker")
    
    events_df = logic.get_events()
    if events_df.empty:
        st.warning("Create an event to manage tasks.")
    else:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_event_id = st.selectbox("Select Event to Manage", options=event_names.keys(), format_func=lambda x: event_names[x])
        
        # Create Task
        with st.expander("New Task"):
            with st.form("task_form"):
                t_name = st.text_input("Task Name")
                c1, c2 = st.columns(2)
                t_status = c1.selectbox("Status", ["Not Started", "In Progress", "Completed", "Delayed"])
                t_prio = c2.selectbox("Priority", ["Low", "Medium", "High"])
                t_dead = st.date_input("Deadline")
                
                if st.form_submit_button("Add Task"):
                    logic.add_task(selected_event_id, t_name, t_status, t_dead, t_prio)
                    st.success("Task added!")
                    st.rerun() # Refresh to show new task immediately

        # View & Update Tasks
        tasks = logic.get_tasks(selected_event_id)
        if not tasks.empty:
            st.subheader("Current Tasks")
            
            # Editable Data Editor (New Streamlit feature!)
            edited_df = st.data_editor(
                tasks, 
                column_config={
                    "status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Not Started", "In Progress", "Completed", "Delayed"],
                        required=True,
                    )
                },
                hide_index=True,
                key="editor"
            )
            
            # Note: Implementing real-time save from data_editor needs extra logic, 
            # for simplicity we use a manual update box below for guaranteed saving.
            
            st.divider()
            st.caption("To update status permanently:")
            c1, c2, c3 = st.columns([2, 2, 1])
            task_to_update = c1.selectbox("Select Task", tasks['task_name'])
            new_status = c2.selectbox("New Status", ["Not Started", "In Progress", "Completed", "Delayed"], key="s_update")
            if c3.button("Update Status"):
                res = logic.update_task_status(selected_event_id, task_to_update, new_status)
                st.success(res)
                st.rerun()

# --- 4. ANALYTICS PAGE ---
elif menu == "Analytics":
    st.header("📊 Event Analytics")
    
    events_df = logic.get_events()
    if events_df.empty:
        st.warning("No events available.")
    else:
        event_names = dict(zip(events_df['id'], events_df['name']))
        eid = st.selectbox("Analyze Event", options=event_names.keys(), format_func=lambda x: event_names[x])
        
        tab1, tab2, tab3 = st.tabs(["RSVP Stats", "Task Progress", "Timeline"])
        
        with tab1:
            fig = logic.get_rsvp_pie_chart(eid)
            if fig: st.pyplot(fig)
            else: st.info("No attendee data yet.")
            
        with tab2:
            fig = logic.get_task_status_chart(eid)
            if fig: st.pyplot(fig)
            else: st.info("No task data yet.")
            
        with tab3:
            fig = logic.get_timeline_chart(eid)
            if fig: st.pyplot(fig)
            else: st.info("Add tasks and deadlines to see the timeline.")