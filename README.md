# intelligent-timetable-scheduler

# 📅 Intelligent Timetable Scheduler

A smart, automated timetable generation system built with **Streamlit**, designed for engineering colleges. It handles department-specific subjects, teacher assignments, lab scheduling, and generates optimized weekly timetables.

> Created by **CODE BLOODED**

---

## 🚀 Features

- **Department-wise subject loading** — Pre-defined subjects for ECE, Mechanical, CSE, and EEE across all 8 semesters
- **Smart teacher assignment** — Each teacher can handle a maximum of 2 subjects (any combination of theory/lab)
- **Lab scheduling** — Set specific day, session (FN/AN), and lab floor for each lab subject
- **Teacher preferences** — Mark free periods for teachers; the scheduler respects these during generation
- **Optimized generation** — Runs multiple iterations and picks the best timetable based on a quality score
- **Constraint validation** — Checks for max 2 periods/subject/day, session splits, and lab conflicts
- **Analytics dashboard** — Workload distribution, subject distribution, daily load, and session-wise analysis
- **Export options** — Download timetable as CSV or Excel (with summary and workload sheets)

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) — Web UI
- [Pandas](https://pandas.pydata.org/) — Data handling
- [Plotly](https://plotly.com/python/) — Charts and analytics
- [OpenPyXL](https://openpyxl.readthedocs.io/) — Excel export

---

---

## 📖 How to Use

### Step 1 — Setup
- Select your **Department**, **Regulation**, **Semester**, and **Classroom**
- Pre-defined subjects for that combination will load automatically

### Step 2 — Subjects
- Assign teachers to theory subjects
- Schedule labs by setting the day, session (Forenoon/Afternoon), and lab floor
- Add custom subjects or labs if needed
- Delete or restore subjects as required

### Step 3 — Preferences *(Optional)*
- Set free periods for assigned teachers
- The scheduler will avoid placing classes for them during those slots

### Step 4 — Generate
- Choose the number of optimization iterations
- Click **Generate Timetable**
- View the timetable, quality score, and allocation status
- Re-generate if needed for a better result

### Step 5 — Analytics
- View teacher workload distribution
- Analyze subject distribution across FN/AN sessions
- Check daily load and utilization rates

---
---

## ⚠️ Constraints

- Maximum **2 subjects per teacher** (theory + lab, theory + theory, or lab + lab)
- Maximum **2 periods per subject per day**
- Two periods of the same subject on the same day must be in the **same session** (FN or AN)
- No two labs can be scheduled on the **same day and session**
- Total periods available per week: **40** (8 periods × 5 days)
---

made by Yogesh S
