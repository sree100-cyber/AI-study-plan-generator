import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

# ---------------- PAGE CONFIG ----------------
st.set_page_config("AI Study Scheduler", "⏰", layout="wide")
st.title("⏰ AI Study Scheduler")
st.caption("Smart AI planner for students")

# ---------------- SESSION STATE ----------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ---------------- AI LOGIC ----------------
HARDNESS_WEIGHT = {"Easy": 1, "Medium": 2, "Hard": 3}

def study_duration(hardness):
    return {
        "Easy": timedelta(minutes=45),
        "Medium": timedelta(hours=1, minutes=30),
        "Hard": timedelta(hours=2)
    }[hardness]

def ai_priority(task):
    hours_left = max((task["Deadline"] - datetime.now()).total_seconds() / 3600, 0)
    urgency = 1 if hours_left > 24 else 3 if hours_left > 6 else 5
    return HARDNESS_WEIGHT[task["Hardness"]] * 2 + urgency * 3

def remaining(deadline):
    diff = deadline - datetime.now()
    if diff.total_seconds() <= 0:
        return "Expired"
    hrs = diff.total_seconds() / 3600
    return f"{int(hrs)} hrs" if hrs < 24 else f"{int(hrs//24)} days"

def fmt(t): return t.strftime("%I:%M %p")

# ---------------- SIDEBAR ADD TASK ----------------
st.sidebar.header("➕ Add Task")

name = st.sidebar.text_input("Task Name")
hardness = st.sidebar.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
free_date = st.sidebar.date_input(
    "Free Time Date",
    value=datetime.today().date()
)


start = st.sidebar.time_input("Free Start", time(9, 0))
end = st.sidebar.time_input("Free End", time(12, 0))

date = st.sidebar.date_input("Deadline Date")
dtime = st.sidebar.time_input("Deadline Time", time(18, 0))

if st.sidebar.button("Add Task"):
    free_start = datetime.combine(free_date, start)
    free_end = datetime.combine(free_date, end)

    deadline = datetime.combine(date, dtime)

    st.session_state.tasks.append({
        "Task": name,
        "Hardness": hardness,
        "FreeStart": free_start,
        "FreeEnd": free_end,
        "Deadline": deadline,
        "Status": "Pending"
    })
    st.sidebar.success("Task added!")

# ---------------- MAIN ----------------
if not st.session_state.tasks:
    st.info("Add tasks to generate schedule")
    st.stop()

df = pd.DataFrame(st.session_state.tasks)
df["Priority"] = df.apply(ai_priority, axis=1)
df["Duration"] = df["Hardness"].apply(study_duration)
df = df.sort_values("Priority", ascending=False)

# ---------------- AI TIME ALLOCATION ----------------
schedule = []
current_time = datetime.combine(datetime.today(), time(9, 0))

for _, row in df.iterrows():
    if row["Status"] == "Completed":
        continue

    start = max(current_time, row["FreeStart"])
    end = start + row["Duration"]

    schedule.append({
        **row,
        "AI Start": start,
        "AI End": end,
        "Remaining": remaining(row["Deadline"])
    })

    current_time = end + timedelta(minutes=15)  # break

sch = pd.DataFrame(schedule)

# ---------------- CALENDAR STYLE VIEW ----------------
st.subheader("📅 Today’s AI Schedule")

today = datetime.today().date()
if sch.empty or "AI Start" not in sch.columns:
    st.info("No tasks scheduled for today")
    today_tasks = pd.DataFrame()
else:
    today_tasks = sch[sch["AI Start"].dt.date == today]

if today_tasks.empty:
    st.info("No tasks scheduled today")
else:
    for i, r in today_tasks.iterrows():
        with st.expander(f"🕒 {fmt(r['AI Start'])} – {fmt(r['AI End'])} | {r['Task']}"):
            st.write(f"🔥 Difficulty: {r['Hardness']}")
            st.write(f"⏳ Remaining: {r['Remaining']}")

            col1, col2, col3 = st.columns(3)

            if col1.button("✅ Complete", key=f"c{i}"):
                st.session_state.tasks[i]["Status"] = "Completed"
                st.rerun()


            if col2.button("✏️ Edit", key=f"e{i}"):
                st.session_state.tasks[i]["Task"] = st.text_input(
                    "New name", r["Task"], key=f"t{i}"
                )

            if col3.button("🗑 Delete", key=f"d{i}"):
                st.session_state.tasks.pop(i)
                st.rerun()


# ---------------- UPCOMING ----------------
st.subheader("🗓 Upcoming Tasks")

required_cols = {"Task", "Hardness", "Remaining", "AI Start", "AI End"}

if sch.empty or not required_cols.issubset(sch.columns):
    st.info("No upcoming tasks scheduled")
else:
    upcoming = sch[sch["AI Start"].dt.date > today]

    if upcoming.empty:
        st.info("No upcoming tasks scheduled")
    else:
        st.dataframe(
            upcoming[list(required_cols)],
            use_container_width=True,
            hide_index=True
        )


# ---------------- FOOTER ----------------
st.caption("Built by Sree | CSE – Data Analytics | AI-powered Planner")
