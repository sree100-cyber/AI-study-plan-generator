import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta, time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Study Scheduler", layout="wide")

st.title("⏰ AI Study Scheduler")
st.caption("Add tasks → AI prioritizes → Smart scheduling")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

def get_study_duration(hardness):
    if hardness == "Easy":
        return timedelta(minutes=45)
    elif hardness == "Medium":
        return timedelta(hours=1, minutes=30)
    else:  # Hard
        return timedelta(hours=2)

def generate_ai_time(free_start, free_end, hardness):
    duration = get_study_duration(hardness)
    free_minutes = int((free_end - free_start).total_seconds() // 60)
    study_minutes = int(duration.total_seconds() // 60)

    if study_minutes >= free_minutes:
        return free_start, free_end

    offset = random.randint(0, free_minutes - study_minutes)
    ai_start = free_start + timedelta(minutes=offset)
    ai_end = ai_start + duration
    return ai_start, ai_end

def remaining_time(deadline):
    now = datetime.now()
    diff = deadline - now

    if diff.total_seconds() <= 0:
        return "Deadline passed"

    hours = diff.total_seconds() / 3600
    if hours > 24:
        return f"{int(hours // 24)} day(s)"
    else:
        return f"{int(hours)} hour(s)"

def format_time(dt):
    """Convert datetime or time object to 12-hour string with AM/PM"""
    if isinstance(dt, datetime):
        return dt.strftime("%I:%M %p")
    elif isinstance(dt, time):
        return dt.strftime("%I:%M %p")
    else:
        return str(dt)

st.subheader("➕ Add New Task")

col1, col2 = st.columns(2)

with col1:
    task_name = st.text_input("Task Name")
    hardness = st.selectbox("Hardness", ["Easy", "Medium", "Hard"])

with col2:
    st.markdown("⏰ **Free Time Slot (12-hour format)**")

    # Free Start & End Time (12-hour format)
    free_start_time = st.time_input(
        "Start Time",
        value=datetime.strptime("09:00 AM", "%I:%M %p").time()
    )
    free_end_time = st.time_input(
        "End Time",
        value=datetime.strptime("12:00 PM", "%I:%M %p").time()
    )

# Deadline Input
st.markdown("📅 **Deadline**")
deadline_date = st.date_input("Deadline Date")
deadline_time_input = st.time_input(
    "Deadline Time",
    value=datetime.strptime("06:00 PM", "%I:%M %p").time()
)


if st.button("➕ Add Task"):
    free_start = datetime.combine(datetime.today(), free_start_time)
    free_end = datetime.combine(datetime.today(), free_end_time)
    deadline_dt = datetime.combine(deadline_date, deadline_time_input)

    ai_start, ai_end = generate_ai_time(free_start, free_end, hardness)

    st.session_state.tasks.append({
        "Task": task_name,
        "Hardness": hardness,
        "Free Time": f"{format_time(free_start)} – {format_time(free_end)}",
        "AI Preferred Time": f"{format_time(ai_start)} – {format_time(ai_end)}",
        "Deadline": deadline_dt,
        "Remaining": remaining_time(deadline_dt)
    })

    st.success("Task added successfully!")

# ---------------- TASK TABLE ----------------
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)

    # Prioritize Hard tasks first
    hardness_rank = {"Hard": 1, "Medium": 2, "Easy": 3}
    df["Priority"] = df["Hardness"].map(hardness_rank)

    df = df.sort_values(by=["Priority", "Deadline"])

    st.subheader("📋 AI-Managed Task List")
    st.dataframe(
        df[["Task", "Hardness", "Free Time", "AI Preferred Time", "Remaining"]],
        use_container_width=True
    )

    # ---------------- AI RECOMMENDATION ----------------
    top = df.iloc[0]
    st.subheader("🧠 AI Recommendation")
    st.success(
        f"Start **{top['Task']}** at **{top['AI Preferred Time']}** "
        f"({top['Remaining']} remaining)"
    )
else:
    st.info("👈 Add tasks from above to generate AI schedule")
