import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import random
import json
from datetime import datetime
from io import BytesIO
import base64

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Intelligent Timetable Scheduler",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #7f7f7f;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS = [f"P{i}" for i in range(1, 9)]
PERIODS_FN = PERIODS[:4]
PERIODS_AN = PERIODS[4:]

# ENHANCED: Department and Semester specific teachers
TEACHERS_BY_DEPT_SEMESTER = {
    "ECE": {
        "I": ["Dr. Priya", "Dr. Kumar", "Prof. Lakshmi", "Dr. Ravi", "Prof. Meena",
              "Dr. Suresh", "Prof. Divya", "Dr. Anand"],
        "II": ["Dr. Alice", "Dr. Bob", "Prof. Charlie", "Dr. David", "Prof. Eva",
               "Dr. Kumar", "Prof. Ravi", "Dr. Suresh"],
        "III": ["Dr. Ganesh", "Prof. Sowmya", "Dr. Karthik", "Prof. Usha",
                "Dr. Vijay", "Prof. Jaya", "Dr. Gopal"],
        "IV": ["Dr. Rajesh", "Prof. Sangeetha", "Dr. Prakash", "Prof. Kavitha",
               "Dr. Mohan", "Prof. Rani", "Dr. Murali"],
        "V": ["Dr. Venkat", "Prof. Swathi", "Dr. Balaji", "Prof. Sudha",
              "Dr. Arun", "Prof. Deepak", "Dr. Ramesh"],
        "VI": ["Dr. Paramesh", "Prof. Santhosh", "Dr. Rajeshwari", "Prof. Gopal",
               "Dr. Anand", "Prof. Vijay", "Dr. Kumar"],
        "VII": ["Dr. Suresh", "Prof. Usha", "Dr. Ravi", "Prof. Jaya",
                "Dr. Meena", "Prof. Divya", "Dr. Karthik"],
        "VIII": ["Dr. Prakash", "Prof. Kavitha", "Dr. Mohan", "Prof. Rani",
                 "Dr. Venkat", "Prof. Swathi"]
    },
    "Mechanical": {
        "I": ["Dr. Ramesh", "Prof. Latha", "Dr. Sunil", "Prof. Pooja",
              "Dr. Kiran", "Prof. Sneha", "Dr. Rajiv"],
        "II": ["Dr. Arun", "Prof. Priya", "Dr. Mahesh", "Prof. Sowmya",
               "Dr. Naveen", "Prof. Renu", "Dr. Santosh"],
        "III": ["Dr. Vikram", "Prof. Anitha", "Dr. Mohan", "Prof. Radha",
                "Dr. Karthik", "Prof. Uma", "Dr. Rajesh"],
        "IV": ["Dr. Ganesh", "Prof. Lakshmi", "Dr. Suresh", "Prof. Kavya",
               "Dr. Prakash", "Prof. Meera", "Dr. Venkat"],
        "V": ["Dr. Balaji", "Prof. Divya", "Dr. Kumar", "Prof. Sangeetha",
              "Dr. Ravi", "Prof. Jaya", "Dr. Anand"],
        "VI": ["Dr. Murali", "Prof. Swathi", "Dr. Gopal", "Prof. Sudha",
               "Dr. Vijay", "Prof. Usha", "Dr. Paramesh"],
        "VII": ["Dr. Santhosh", "Prof. Rani", "Dr. Deepak", "Prof. Kavitha",
                "Dr. Ramesh", "Prof. Priya", "Dr. Arun"],
        "VIII": ["Dr. Mohan", "Prof. Sowmya", "Dr. Kiran", "Prof. Pooja",
                 "Dr. Rajiv", "Prof. Latha"]
    },
    "CSE": {
        "I": ["Dr. Priya", "Prof. Arun", "Dr. Deepak", "Prof. Lakshmi",
              "Dr. Mohan", "Prof. Sowmya", "Dr. Karthik"],
        "II": ["Dr. Meena", "Prof. Ramesh", "Dr. Divya", "Prof. Suresh",
               "Dr. Ravi", "Prof. Jaya", "Dr. Kumar"],
        "III": ["Dr. Ganesh", "Prof. Sangeetha", "Dr. Prakash", "Prof. Kavitha",
                "Dr. Balaji", "Prof. Rani", "Dr. Venkat"],
        "IV": ["Dr. Murali", "Prof. Swathi", "Dr. Gopal", "Prof. Sudha",
               "Dr. Vijay", "Prof. Usha", "Dr. Anand"],
        "V": ["Dr. Paramesh", "Prof. Santhosh", "Dr. Rajeshwari", "Prof. Divya",
              "Dr. Karthik", "Prof. Meena", "Dr. Ramesh"],
        "VI": ["Dr. Arun", "Prof. Priya", "Dr. Deepak", "Prof. Lakshmi",
               "Dr. Mohan", "Prof. Sowmya", "Dr. Kumar"],
        "VII": ["Dr. Ravi", "Prof. Jaya", "Dr. Suresh", "Prof. Usha",
                "Dr. Ganesh", "Prof. Sangeetha", "Dr. Prakash"],
        "VIII": ["Dr. Balaji", "Prof. Rani", "Dr. Venkat", "Prof. Swathi",
                 "Dr. Murali", "Prof. Sudha"]
    },
    "EEE": {
        "I": ["Dr. Balaji", "Prof. Sangeetha", "Dr. Prakash", "Prof. Kavitha",
              "Dr. Ganesh", "Prof. Rani", "Dr. Murali"],
        "II": ["Dr. Swathi", "Prof. Venkat", "Dr. Sudha", "Prof. Gopal",
               "Dr. Vijay", "Prof. Usha", "Dr. Anand"],
        "III": ["Dr. Paramesh", "Prof. Santhosh", "Dr. Rajeshwari", "Prof. Divya",
                "Dr. Karthik", "Prof. Meena", "Dr. Ramesh"],
        "IV": ["Dr. Arun", "Prof. Priya", "Dr. Deepak", "Prof. Lakshmi",
               "Dr. Mohan", "Prof. Sowmya", "Dr. Kumar"],
        "V": ["Dr. Ravi", "Prof. Jaya", "Dr. Suresh", "Prof. Usha",
              "Dr. Ganesh", "Prof. Sangeetha", "Dr. Prakash"],
        "VI": ["Dr. Balaji", "Prof. Rani", "Dr. Venkat", "Prof. Swathi",
               "Dr. Murali", "Prof. Sudha", "Dr. Gopal"],
        "VII": ["Dr. Vijay", "Prof. Divya", "Dr. Anand", "Prof. Meena",
                "Dr. Paramesh", "Prof. Santhosh", "Dr. Karthik"],
        "VIII": ["Dr. Ramesh", "Prof. Lakshmi", "Dr. Arun", "Prof. Priya",
                 "Dr. Deepak", "Prof. Sowmya"]
    }
}

LAB_FLOORS = ["Lab 1", "Lab 2", "Lab 3", "Lab 4", "Lab 5"]
CLASSROOMS = ["C1", "C2", "C3", "C4", "C5"]

# -------------------------------------------------
# PRE-DEFINED SUBJECTS (DEPARTMENT-SPECIFIC)
# -------------------------------------------------
PREDEFINED_SUBJECTS = {
    "R2025": {
        "ECE": {
            "I": {
                "theory": [
                    {"name": "Applied Calculas", "code": "MA25C01", "credit": 4, "periods": 4},
                    {"name": "Applied Physics-I", "code": "PH25C01", "credit": 3, "periods": 1},
                    {"name": "Applied Chemistry-I", "code": "CY25C01", "credit": 3, "periods": 4},
                    {"name": "computer programming C", "code": "CS25C01", "credit": 3, "periods": 4},
                    {"name": "Engineering Drawing", "code": "ME25C01", "credit": 4, "periods": 6},
                    {"name": "Introduction to Mechanical Engineering", "code": "ME25C03", "credit": 3, "periods": 2},
                    {"name": "தமிழர்மரபு / Heritage of Tamils", "code": "UC25H01", "credit": 1, "periods": 1},
                    {"name": "English Essentials – I s", "code": "EN25C01", "credit": 2, "periods": 2},
                ],
                "lab": [
                    {"name": "Makerspace", "code": "UC25A01 "},
                    {"name": "Physical Education – I", "code": "UC25A02 "},
                    {"name": "Physics Lab/Chemistry Lab", "code": "PH1022"},
                ]
            },
            "II": {
                "theory": [
                    {"name": "Engineering Mathematics II", "code": "MA2021", "credit": 4, "periods": 4},
                    {"name": "Physics for Electronics", "code": "PH2021", "credit": 3, "periods": 3},
                    {"name": "Programming in C", "code": "CS2021", "credit": 3, "periods": 3},
                    {"name": "Circuit Theory", "code": "EC2021", "credit": 4, "periods": 4},
                    {"name": "English Communication", "code": "EN2021", "credit": 2, "periods": 2},
                    {"name": "Professional English II", "code": "EN2022", "credit": 2, "periods": 2},
                    {"name": "Basic Electronics", "code": "EC2023", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Physics Lab", "code": "PH2022"},
                    {"name": "C Programming Lab", "code": "CS2022"},
                    {"name": "Circuit Theory Lab", "code": "EC2022"},
                    {"name": "Communication Lab", "code": "EN2023"},
                ]
            },
            "III": {
                "theory": [
                    {"name": "Transforms and Partial Differential Equations", "code": "MA3021", "credit": 4,
                     "periods": 4},
                    {"name": "Electronic Devices and Circuits", "code": "EC3021", "credit": 3, "periods": 3},
                    {"name": "Digital System Design", "code": "EC3022", "credit": 3, "periods": 3},
                    {"name": "Data Structures", "code": "CS3021", "credit": 4, "periods": 4},
                    {"name": "Environmental Science", "code": "GE3021", "credit": 2, "periods": 2},
                    {"name": "Object Oriented Programming", "code": "CS3023", "credit": 3, "periods": 3},
                    {"name": "Engineering Mechanics", "code": "ME3021", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Electronic Devices Lab", "code": "EC3023"},
                    {"name": "Digital System Lab", "code": "EC3024"},
                    {"name": "Data Structures Lab", "code": "CS3022"},
                    {"name": "OOP Lab", "code": "CS3024"},
                ]
            },
            "IV": {
                "theory": [
                    {"name": "Digital Electronics", "code": "EC4021", "credit": 4, "periods": 4},
                    {"name": "Signals and Systems", "code": "EC4022", "credit": 4, "periods": 4},
                    {"name": "Linear Algebra", "code": "MA4021", "credit": 3, "periods": 3},
                    {"name": "Network Theory", "code": "EC4023", "credit": 3, "periods": 3},
                    {"name": "Electronic Devices", "code": "EC4024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Digital Electronics Lab", "code": "EC4025"},
                    {"name": "Signals Lab", "code": "EC4026"},
                    {"name": "Network Theory Lab", "code": "EC4027"},
                ]
            },
            "V": {
                "theory": [
                    {"name": "Probability and Random Processes", "code": "MA5021", "credit": 4, "periods": 4},
                    {"name": "Analog Communication", "code": "EC5021", "credit": 3, "periods": 3},
                    {"name": "Linear Integrated Circuits", "code": "EC5022", "credit": 3, "periods": 3},
                    {"name": "Microprocessor and Microcontroller", "code": "EC5023", "credit": 4, "periods": 4},
                    {"name": "Control Systems", "code": "EC5024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Analog Communication Lab", "code": "EC5025"},
                    {"name": "Linear IC Lab", "code": "EC5026"},
                    {"name": "Microprocessor Lab", "code": "EC5027"},
                ]
            },
            "VI": {
                "theory": [
                    {"name": "Digital Communication", "code": "EC6021", "credit": 4, "periods": 4},
                    {"name": "VLSI Design", "code": "EC6022", "credit": 3, "periods": 3},
                    {"name": "Communication Systems", "code": "EC6023", "credit": 4, "periods": 4},
                    {"name": "Electromagnetic Fields", "code": "EC6024", "credit": 3, "periods": 3},
                    {"name": "Computer Networks", "code": "EC6025", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Digital Communication Lab", "code": "EC6026"},
                    {"name": "VLSI Lab", "code": "EC6027"},
                    {"name": "Communication Systems Lab", "code": "EC6028"},
                ]
            },
            "VII": {
                "theory": [
                    {"name": "Wireless Communication", "code": "EC7021", "credit": 3, "periods": 3},
                    {"name": "Optical Communication", "code": "EC7022", "credit": 3, "periods": 3},
                    {"name": "Microwave Engineering", "code": "EC7023", "credit": 4, "periods": 4},
                    {"name": "Digital Signal Processing", "code": "EC7024", "credit": 4, "periods": 4},
                    {"name": "Professional Elective I", "code": "EC7025", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Wireless Communication Lab", "code": "EC7026"},
                    {"name": "DSP Lab", "code": "EC7027"},
                    {"name": "Microwave Lab", "code": "EC7028"},
                ]
            },
            "VIII": {
                "theory": [
                    {"name": "Embedded Systems", "code": "EC8021", "credit": 3, "periods": 3},
                    {"name": "IoT Systems", "code": "EC8022", "credit": 3, "periods": 3},
                    {"name": "Project Management", "code": "MG8021", "credit": 2, "periods": 2},
                    {"name": "Professional Elective II", "code": "EC8023", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Project Work", "code": "EC8024"},
                ]
            }
        },
        "Mechanical": {
            "I": {
                "theory": [
                    {"name": "Applied Calculas", "code": "MA25C01", "credit": 4, "periods": 4},
                    {"name": "Applied Physics-I", "code": "PH25C01", "credit": 3, "periods": 1},
                    {"name": "Applied Chemistry-I", "code": "CY25C01", "credit": 3, "periods": 4},
                    {"name": "Problem Solving and Python Programming", "code": "CS25C02", "credit": 3, "periods": 4},
                    {"name": "Engineering Drawing", "code": "ME25C01", "credit": 4, "periods": 6},
                    {"name": "Introduction to Mechanical Engineering", "code": "ME25C03", "credit": 3, "periods": 2},
                    {"name": "தமிழர்மரபு / Heritage of Tamils", "code": "UC25H01", "credit": 1, "periods": 1},
                    {"name": "English Essentials – I s", "code": "EN25C01", "credit": 2, "periods": 2},
                ],
                "lab": [
                    {"name": "Makerspace", "code": "UC25A01 "},
                    {"name": "Physical Education – I", "code": "UC25A02 "},
                    {"name": "Physics Lab/Chemistry Lab", "code": "PH1022"},
                    {"name": "Engineering Graphics Lab", "code": "GE1022"},
                ]
            },
            "II": {
                "theory": [
                    {"name": " Linear Algebra ", "code": "MA25C02", "credit": 4, "periods": 4},
                    {"name": "Engineering Mechanics", "code": "ME25C02", "credit": 4, "periods": 4},
                    {"name": "Basic Electrical and Electronics Engineering", "code": "EE25C01", "credit": 3, "periods": 3},
                    {"name": "Applied Physics (ME) – II", "code": "PH25C05", "credit": 3, "periods": 3},
                    {"name": "Applied Chemistry (ME) – II ", "code": "CY25C03", "credit": 2, "periods": 2},
                    {"name": "தமிழர்களும் ததொழில்நுட்பமும் /Tamils and Technology", "code": "UC25H02", "credit": 1, "periods": 1},
                    {"name": "English Essentials – II", "code": "EN25C02", "credit": 2, "periods": 3},
                ],
                "lab": [
                    {"name": "Re-Engineering for Innovation", "code": "ME25C05"},
                    {"name": "Physical Education – II", "code": "UC25A04 "},
                ]
            },
            "III": {
                "theory": [
                    {"name": "Computational Differential Equations ", "code": "ME3021", "credit": 4, "periods": 4},
                    {"name": " Applied Engineering Mechanics ", "code": "ME3022", "credit": 3, "periods": 3},
                    {"name": "Engineering Thermodynamics", "code": "ME3023", "credit": 4, "periods": 4},
                    {"name": "Embedded Systems", "code": "ME3024", "credit": 3, "periods": 3},
                    {"name": "Engineering Mathematics III", "code": "MA3021", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Fluid Mechanics Lab", "code": "ME3025"},
                    {"name": "Manufacturing Lab", "code": "ME3026"},
                    {"name": "Materials Lab", "code": "ME3027"},
                ]
            },
            "IV": {
                "theory": [
                    {"name": "Heat Transfer", "code": "ME4021", "credit": 4, "periods": 4},
                    {"name": "Dynamics of Machinery", "code": "ME4022", "credit": 4, "periods": 4},
                    {"name": "Machine Design I", "code": "ME4023", "credit": 3, "periods": 3},
                    {"name": "Metrology and Measurements", "code": "ME4024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Heat Transfer Lab", "code": "ME4025"},
                    {"name": "Dynamics Lab", "code": "ME4026"},
                    {"name": "Metrology Lab", "code": "ME4027"},
                ]
            },
            "V": {
                "theory": [
                    {"name": "Design of Machine Elements", "code": "ME5021", "credit": 4, "periods": 4},
                    {"name": "Thermal Engineering", "code": "ME5022", "credit": 3, "periods": 3},
                    {"name": "Hydraulic Machines", "code": "ME5023", "credit": 3, "periods": 3},
                    {"name": "CAD/CAM", "code": "ME5024", "credit": 4, "periods": 4},
                    {"name": "Operations Research", "code": "ME5025", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Thermal Engineering Lab", "code": "ME5026"},
                    {"name": "Hydraulics Lab", "code": "ME5027"},
                    {"name": "CAD Lab", "code": "ME5028"},
                ]
            },
            "VI": {
                "theory": [
                    {"name": "Automobile Engineering", "code": "ME6021", "credit": 4, "periods": 4},
                    {"name": "Refrigeration and Air Conditioning", "code": "ME6022", "credit": 3, "periods": 3},
                    {"name": "Industrial Engineering", "code": "ME6023", "credit": 3, "periods": 3},
                    {"name": "Mechatronics", "code": "ME6024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Automobile Lab", "code": "ME6025"},
                    {"name": "RAC Lab", "code": "ME6026"},
                    {"name": "Mechatronics Lab", "code": "ME6027"},
                ]
            },
            "VII": {
                "theory": [
                    {"name": "Robotics", "code": "ME7021", "credit": 3, "periods": 3},
                    {"name": "Finite Element Analysis", "code": "ME7022", "credit": 3, "periods": 3},
                    {"name": "Power Plant Engineering", "code": "ME7023", "credit": 4, "periods": 4},
                    {"name": "Professional Elective I", "code": "ME7024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Robotics Lab", "code": "ME7025"},
                    {"name": "FEA Lab", "code": "ME7026"},
                    {"name": "Power Plant Lab", "code": "ME7027"},
                ]
            },
            "VIII": {
                "theory": [
                    {"name": "Total Quality Management", "code": "ME8021", "credit": 3, "periods": 3},
                    {"name": "Green Manufacturing", "code": "ME8022", "credit": 3, "periods": 3},
                    {"name": "Professional Elective II", "code": "ME8023", "credit": 2, "periods": 2},
                ],
                "lab": [
                    {"name": "Project Work", "code": "ME8024"},
                ]
            }
        },
        "CSE": {
            "I": {
                "theory": [
                    {"name": "Engineering Mathematics I", "code": "MA1021", "credit": 4, "periods": 4},
                    {"name": "Engineering Physics", "code": "PH1021", "credit": 3, "periods": 3},
                    {"name": "Engineering Chemistry", "code": "CH1021", "credit": 3, "periods": 3},
                    {"name": "Problem Solving and Python Programming", "code": "CS1021", "credit": 3, "periods": 3},
                    {"name": "Professional English I", "code": "EN1021", "credit": 2, "periods": 2},
                    {"name": "Digital Fundamentals", "code": "CS1022", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Physics Lab", "code": "PH1022"},
                    {"name": "Chemistry Lab", "code": "CH1022"},
                    {"name": "Python Programming Lab", "code": "CS1023"},
                    {"name": "Digital Lab", "code": "CS1024"},
                ]
            },
            "II": {
                "theory": [
                    {"name": "Engineering Mathematics II", "code": "MA2021", "credit": 4, "periods": 4},
                    {"name": "Data Structures", "code": "CS2021", "credit": 4, "periods": 4},
                    {"name": "Computer Organization", "code": "CS2022", "credit": 3, "periods": 3},
                    {"name": "Object Oriented Programming", "code": "CS2023", "credit": 3, "periods": 3},
                    {"name": "Professional English II", "code": "EN2022", "credit": 2, "periods": 2},
                ],
                "lab": [
                    {"name": "Data Structures Lab", "code": "CS2024"},
                    {"name": "Computer Organization Lab", "code": "CS2025"},
                    {"name": "OOP Lab", "code": "CS2026"},
                ]
            },
            "III": {
                "theory": [
                    {"name": "Discrete Mathematics", "code": "MA3021", "credit": 4, "periods": 4},
                    {"name": "Database Management Systems", "code": "CS3021", "credit": 4, "periods": 4},
                    {"name": "Design and Analysis of Algorithms", "code": "CS3022", "credit": 3, "periods": 3},
                    {"name": "Operating Systems", "code": "CS3023", "credit": 3, "periods": 3},
                    {"name": "Computer Networks", "code": "CS3024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "DBMS Lab", "code": "CS3025"},
                    {"name": "Algorithm Lab", "code": "CS3026"},
                    {"name": "OS Lab", "code": "CS3027"},
                ]
            },
            "IV": {
                "theory": [
                    {"name": "Theory of Computation", "code": "CS4021", "credit": 4, "periods": 4},
                    {"name": "Software Engineering", "code": "CS4022", "credit": 4, "periods": 4},
                    {"name": "Web Technologies", "code": "CS4023", "credit": 3, "periods": 3},
                    {"name": "Microprocessors", "code": "CS4024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Software Engineering Lab", "code": "CS4025"},
                    {"name": "Web Technologies Lab", "code": "CS4026"},
                    {"name": "Microprocessor Lab", "code": "CS4027"},
                ]
            },
            "V": {
                "theory": [
                    {"name": "Artificial Intelligence", "code": "CS5021", "credit": 4, "periods": 4},
                    {"name": "Compiler Design", "code": "CS5022", "credit": 3, "periods": 3},
                    {"name": "Computer Graphics", "code": "CS5023", "credit": 3, "periods": 3},
                    {"name": "Information Security", "code": "CS5024", "credit": 4, "periods": 4},
                ],
                "lab": [
                    {"name": "AI Lab", "code": "CS5025"},
                    {"name": "Compiler Lab", "code": "CS5026"},
                    {"name": "Graphics Lab", "code": "CS5027"},
                ]
            },
            "VI": {
                "theory": [
                    {"name": "Machine Learning", "code": "CS6021", "credit": 4, "periods": 4},
                    {"name": "Cloud Computing", "code": "CS6022", "credit": 3, "periods": 3},
                    {"name": "Mobile Application Development", "code": "CS6023", "credit": 3, "periods": 3},
                    {"name": "Big Data Analytics", "code": "CS6024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Machine Learning Lab", "code": "CS6025"},
                    {"name": "Cloud Computing Lab", "code": "CS6026"},
                    {"name": "Mobile Development Lab", "code": "CS6027"},
                ]
            },
            "VII": {
                "theory": [
                    {"name": "Deep Learning", "code": "CS7021", "credit": 3, "periods": 3},
                    {"name": "Internet of Things", "code": "CS7022", "credit": 3, "periods": 3},
                    {"name": "Blockchain Technology", "code": "CS7023", "credit": 4, "periods": 4},
                    {"name": "Professional Elective I", "code": "CS7024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Deep Learning Lab", "code": "CS7025"},
                    {"name": "IoT Lab", "code": "CS7026"},
                    {"name": "Blockchain Lab", "code": "CS7027"},
                ]
            },
            "VIII": {
                "theory": [
                    {"name": "Natural Language Processing", "code": "CS8021", "credit": 3, "periods": 3},
                    {"name": "Professional Ethics", "code": "GE8021", "credit": 2, "periods": 2},
                    {"name": "Professional Elective II", "code": "CS8022", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Project Work", "code": "CS8023"},
                ]
            }
        },
        "EEE": {
            "I": {
                "theory": [
                    {"name": "Engineering Mathematics I", "code": "MA1021", "credit": 4, "periods": 4},
                    {"name": "Engineering Physics", "code": "PH1021", "credit": 3, "periods": 3},
                    {"name": "Engineering Chemistry", "code": "CH1021", "credit": 3, "periods": 3},
                    {"name": "Problem Solving and Python Programming", "code": "CS1021", "credit": 3, "periods": 3},
                    {"name": "Professional English I", "code": "EN1021", "credit": 2, "periods": 2},
                    {"name": "Basic Electrical Engineering", "code": "EE1021", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Physics Lab", "code": "PH1022"},
                    {"name": "Chemistry Lab", "code": "CH1022"},
                    {"name": "Python Programming Lab", "code": "CS1022"},
                    {"name": "Electrical Engineering Lab", "code": "EE1022"},
                ]
            },
            "II": {
                "theory": [
                    {"name": "Engineering Mathematics II", "code": "MA2021", "credit": 4, "periods": 4},
                    {"name": "Circuit Analysis", "code": "EE2021", "credit": 4, "periods": 4},
                    {"name": "Electronic Devices", "code": "EE2022", "credit": 3, "periods": 3},
                    {"name": "Electrical Machines I", "code": "EE2023", "credit": 3, "periods": 3},
                    {"name": "Professional English II", "code": "EN2022", "credit": 2, "periods": 2},
                ],
                "lab": [
                    {"name": "Circuit Analysis Lab", "code": "EE2024"},
                    {"name": "Electronics Lab", "code": "EE2025"},
                    {"name": "Electrical Machines Lab I", "code": "EE2026"},
                ]
            },
            "III": {
                "theory": [
                    {"name": "Electromagnetic Fields", "code": "EE3021", "credit": 4, "periods": 4},
                    {"name": "Electrical Machines II", "code": "EE3022", "credit": 4, "periods": 4},
                    {"name": "Signals and Systems", "code": "EE3023", "credit": 3, "periods": 3},
                    {"name": "Digital Electronics", "code": "EE3024", "credit": 3, "periods": 3},
                    {"name": "Engineering Mathematics III", "code": "MA3021", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Electrical Machines Lab II", "code": "EE3025"},
                    {"name": "Signals Lab", "code": "EE3026"},
                    {"name": "Digital Electronics Lab", "code": "EE3027"},
                ]
            },
            "IV": {
                "theory": [
                    {"name": "Power Systems I", "code": "EE4021", "credit": 4, "periods": 4},
                    {"name": "Control Systems", "code": "EE4022", "credit": 4, "periods": 4},
                    {"name": "Power Electronics", "code": "EE4023", "credit": 3, "periods": 3},
                    {"name": "Microprocessors", "code": "EE4024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Power Systems Lab I", "code": "EE4025"},
                    {"name": "Control Systems Lab", "code": "EE4026"},
                    {"name": "Power Electronics Lab", "code": "EE4027"},
                ]
            },
            "V": {
                "theory": [
                    {"name": "Power Systems II", "code": "EE5021", "credit": 4, "periods": 4},
                    {"name": "Electrical Measurements", "code": "EE5022", "credit": 3, "periods": 3},
                    {"name": "Electric Drives", "code": "EE5023", "credit": 3, "periods": 3},
                    {"name": "Protection and Switchgear", "code": "EE5024", "credit": 4, "periods": 4},
                ],
                "lab": [
                    {"name": "Power Systems Lab II", "code": "EE5025"},
                    {"name": "Measurements Lab", "code": "EE5026"},
                    {"name": "Drives Lab", "code": "EE5027"},
                ]
            },
            "VI": {
                "theory": [
                    {"name": "High Voltage Engineering", "code": "EE6021", "credit": 4, "periods": 4},
                    {"name": "Renewable Energy Systems", "code": "EE6022", "credit": 3, "periods": 3},
                    {"name": "Power System Operation", "code": "EE6023", "credit": 3, "periods": 3},
                    {"name": "FACTS Devices", "code": "EE6024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "HV Lab", "code": "EE6025"},
                    {"name": "Renewable Energy Lab", "code": "EE6026"},
                    {"name": "Power System Operation Lab", "code": "EE6027"},
                ]
            },
            "VII": {
                "theory": [
                    {"name": "Smart Grid Technology", "code": "EE7021", "credit": 3, "periods": 3},
                    {"name": "HVDC Transmission", "code": "EE7022", "credit": 3, "periods": 3},
                    {"name": "Energy Management", "code": "EE7023", "credit": 4, "periods": 4},
                    {"name": "Professional Elective I", "code": "EE7024", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Smart Grid Lab", "code": "EE7025"},
                    {"name": "HVDC Lab", "code": "EE7026"},
                    {"name": "Energy Management Lab", "code": "EE7027"},
                ]
            },
            "VIII": {
                "theory": [
                    {"name": "Electric Vehicles", "code": "EE8021", "credit": 3, "periods": 3},
                    {"name": "Professional Ethics", "code": "GE8021", "credit": 2, "periods": 2},
                    {"name": "Professional Elective II", "code": "EE8022", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Project Work", "code": "EE8023"},
                ]
            }
        }
    },
    "R2023": {
        "ECE": {
            # Copy similar structure for R2023 - abbreviated for file size
            "I": {
                "theory": [
                    {"name": "Mathematics I", "code": "MA1301", "credit": 4, "periods": 4},
                    {"name": "Applied Physics", "code": "PH1301", "credit": 3, "periods": 3},
                    {"name": "Applied Chemistry", "code": "CH1301", "credit": 3, "periods": 3},
                    {"name": "Programming for Problem Solving", "code": "CS1301", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Physics Lab", "code": "PH1302"},
                    {"name": "Chemistry Lab", "code": "CH1302"},
                ]
            },
            "VIII": {
                "theory": [
                    {"name": "IoT and Applications", "code": "EC8301", "credit": 3, "periods": 3},
                    {"name": "Professional Ethics", "code": "GE8301", "credit": 2, "periods": 2},
                    {"name": "Elective II", "code": "EC8302", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Project Work", "code": "EC8303"},
                ]
            }
        },
        "Mechanical": {
            "I": {
                "theory": [
                    {"name": "Mathematics I", "code": "MA1301", "credit": 4, "periods": 4},
                    {"name": "Applied Physics", "code": "PH1301", "credit": 3, "periods": 3},
                    {"name": "Applied Chemistry", "code": "CH1301", "credit": 3, "periods": 3},
                    {"name": "Engineering Drawing", "code": "ME1301", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Physics Lab", "code": "PH1302"},
                    {"name": "Chemistry Lab", "code": "CH1302"},
                ]
            },
            "VIII": {
                "theory": [
                    {"name": "Quality Management", "code": "ME8301", "credit": 3, "periods": 3},
                    {"name": "Professional Ethics", "code": "GE8301", "credit": 2, "periods": 2},
                    {"name": "Elective II", "code": "ME8302", "credit": 3, "periods": 3},
                ],
                "lab": [
                    {"name": "Project Work", "code": "ME8303"},
                ]
            }
        }
    }
}


# -------------------------------------------------
# ENHANCED TEACHER ASSIGNMENT TRACKING
# -------------------------------------------------
def init_teacher_assignments():
    """Initialize teacher assignment tracking"""
    if "teacher_assignments" not in st.session_state:
        st.session_state.teacher_assignments = {}


def get_teacher_assignment_info(teacher):
    """Get assignment information for a teacher"""
    if teacher not in st.session_state.teacher_assignments:
        return {"count": 0, "subjects": [], "types": []}
    return st.session_state.teacher_assignments[teacher]


def can_teacher_take_subject(teacher, subject_type):
    """
    Check if teacher can take another subject
    Rules:
    - Can have max 2 subjects
    - Valid combinations: 1 theory + 1 lab, 2 theory, 2 lab, or just 1 subject
    """
    info = get_teacher_assignment_info(teacher)

    # No subjects yet - can take any
    if info["count"] == 0:
        return True

    # Already has 2 subjects - cannot take more
    if info["count"] >= 2:
        return False

    # Has 1 subject - check if can take another
    if info["count"] == 1:
        existing_type = info["types"][0]
        # Can take any second subject (theory+lab, theory+theory, or lab+lab all allowed)
        return True

    return False


def assign_teacher_to_subject(teacher, subject_name, subject_type):
    """Assign a teacher to a subject"""
    if teacher not in st.session_state.teacher_assignments:
        st.session_state.teacher_assignments[teacher] = {
            "count": 0,
            "subjects": [],
            "types": []
        }

    st.session_state.teacher_assignments[teacher]["count"] += 1
    st.session_state.teacher_assignments[teacher]["subjects"].append(subject_name)
    st.session_state.teacher_assignments[teacher]["types"].append(subject_type)


def unassign_teacher_from_subject(teacher, subject_name, subject_type):
    """Remove a teacher assignment"""
    if teacher in st.session_state.teacher_assignments:
        info = st.session_state.teacher_assignments[teacher]
        if subject_name in info["subjects"]:
            idx = info["subjects"].index(subject_name)
            info["count"] -= 1
            info["subjects"].pop(idx)
            info["types"].pop(idx)

            # Clean up if no more assignments
            if info["count"] == 0:
                del st.session_state.teacher_assignments[teacher]


def get_available_teachers_for_subject(teachers, subject_type):
    """Get list of teachers who can take a subject of given type"""
    available = []
    for teacher in teachers:
        if can_teacher_take_subject(teacher, subject_type):
            available.append(teacher)
    return available


def get_teacher_status_display(teacher):
    """Get display string for teacher's current assignments"""
    info = get_teacher_assignment_info(teacher)
    if info["count"] == 0:
        return "Available (0/2)"
    elif info["count"] == 1:
        subject_type = "Theory" if info["types"][0] == "theory" else "Lab"
        return f"Assigned 1 ({subject_type}) - Can take 1 more"
    else:
        types_str = " + ".join(["Theory" if t == "theory" else "Lab" for t in info["types"]])
        return f"Fully assigned (2/2) - {types_str}"


# NEW FUNCTION: Format teacher options with availability status
def format_teacher_options_with_status(teachers, subject_type):
    """Format teacher options to show their availability status"""
    options = ["Select"]
    for teacher in teachers:
        if can_teacher_take_subject(teacher, subject_type):
            info = get_teacher_assignment_info(teacher)
            if info["count"] == 0:
                options.append(f"{teacher} ✓ (Available)")
            elif info["count"] == 1:
                assigned_type = "T" if info["types"][0] == "theory" else "L"
                options.append(f"{teacher} ⚡ ({assigned_type} assigned, 1 slot left)")
            else:
                options.append(f"{teacher} ✗ (Full)")
    return options


def extract_teacher_name_from_option(option_text):
    """Extract actual teacher name from formatted option text"""
    if option_text == "Select":
        return "Select"
    # Split by first space and emoji to get teacher name
    parts = option_text.split(" ✓")
    if len(parts) > 1:
        return parts[0]
    parts = option_text.split(" ⚡")
    if len(parts) > 1:
        return parts[0]
    parts = option_text.split(" ✗")
    if len(parts) > 1:
        return parts[0]
    return option_text


# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------
def calculate_teacher_workload(timetable, subject_teacher_map):
    """Calculate workload for each teacher"""
    workload = defaultdict(int)
    for day in DAYS:
        for period in PERIODS:
            subject = timetable.loc[day, period]
            if subject and subject != "" and subject != "Library" and subject != "BREAK":
                teacher = subject_teacher_map.get(subject)
                if teacher:
                    workload[teacher] += 1
    return dict(workload)


def calculate_utilization_score(timetable):
    """Calculate how well the timetable is utilized"""
    total_slots = len(DAYS) * len(PERIODS)
    filled_slots = 0
    library_slots = 0

    for day in DAYS:
        for period in PERIODS:
            cell = timetable.loc[day, period]
            if cell and cell != "":
                if cell == "Library":
                    library_slots += 1
                else:
                    filled_slots += 1

    utilization = (filled_slots / total_slots) * 100
    return utilization, filled_slots, library_slots


def validate_constraints(timetable, confirmed_theory):
    """Validate all constraints and return violations"""
    violations = []

    # Check max 2 periods per subject per day
    for subject in confirmed_theory:
        subject_name = subject["name"]
        for day in DAYS:
            count = sum(1 for period in PERIODS if timetable.loc[day, period] == subject_name)
            if count > 2:
                violations.append({
                    "type": "max_per_day",
                    "subject": subject_name,
                    "day": day,
                    "count": count,
                    "message": f"{subject_name} appears {count} times on {day} (max: 2)"
                })

    # Check same session for 2 periods
    for subject in confirmed_theory:
        subject_name = subject["name"]
        for day in DAYS:
            periods_on_day = [p for p in PERIODS if timetable.loc[day, p] == subject_name]
            if len(periods_on_day) == 2:
                sess1 = "FN" if periods_on_day[0] in PERIODS_FN else "AN"
                sess2 = "FN" if periods_on_day[1] in PERIODS_FN else "AN"
                if sess1 != sess2:
                    violations.append({
                        "type": "session_split",
                        "subject": subject_name,
                        "day": day,
                        "message": f"{subject_name} on {day} spans both sessions"
                    })

    return violations


def export_to_excel(timetable, summary_data, timetable_name, workload_data=None):
    """Export timetable to Excel with multiple sheets"""
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Timetable sheet
        display_timetable = create_display_timetable(timetable)
        display_timetable.to_excel(writer, sheet_name='Timetable', index=True)

        # Summary sheet
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

        # Workload sheet
        if workload_data:
            workload_df = pd.DataFrame([
                {"Teacher": k, "Periods per Week": v}
                for k, v in workload_data.items()
            ])
            workload_df.to_excel(writer, sheet_name='Teacher Workload', index=False)

    return output.getvalue()


def create_display_timetable(timetable):
    """Create display version with break column"""
    display_columns = PERIODS_FN + ["BREAK"] + PERIODS_AN
    display_timetable = pd.DataFrame("", index=DAYS, columns=display_columns)

    for day in DAYS:
        for period in PERIODS_FN:
            display_timetable.loc[day, period] = timetable.loc[day, period]
        display_timetable.loc[day, "BREAK"] = "BREAK"
        for period in PERIODS_AN:
            display_timetable.loc[day, period] = timetable.loc[day, period]

    return display_timetable


# -------------------------------------------------
# ADVANCED TIMETABLE GENERATION WITH SCORING
# -------------------------------------------------
def generate_timetable_with_optimization(confirmed_theory, confirmed_lab, max_iterations=100):
    """
    Generate timetable with optimization scoring
    Tries multiple iterations and returns the best one
    """
    best_timetable = None
    best_score = -1
    best_unallocated = None

    for iteration in range(max_iterations):
        timetable, unallocated = generate_single_timetable(confirmed_theory, confirmed_lab)

        if timetable is not None:
            score = calculate_timetable_score(timetable, confirmed_theory, unallocated)

            if score > best_score:
                best_score = score
                best_timetable = timetable.copy()
                best_unallocated = unallocated.copy() if unallocated else []

                # If perfect score, stop early
                if score >= 95 and not unallocated:
                    break

    return best_timetable, best_unallocated, best_score


def calculate_timetable_score(timetable, confirmed_theory, unallocated):
    """
    Calculate quality score of timetable
    Factors:
    - Allocation completeness (40%)
    - Distribution quality (30%)
    - Constraint satisfaction (30%)
    """
    score = 0

    # 1. Allocation completeness (40 points)
    total_periods_needed = sum(s["periods"] for s in confirmed_theory)
    if total_periods_needed > 0:
        unallocated_periods = sum(u["remaining"] for u in unallocated) if unallocated else 0
        allocated_periods = total_periods_needed - unallocated_periods
        allocation_score = (allocated_periods / total_periods_needed) * 40
        score += allocation_score
    else:
        score += 40

    # 2. Distribution quality (30 points)
    distribution_penalties = 0
    for subject in confirmed_theory:
        subject_name = subject["name"]
        day_counts = []
        for day in DAYS:
            count = sum(1 for period in PERIODS if timetable.loc[day, period] == subject_name)
            day_counts.append(count)

        # Penalize uneven distribution
        if day_counts:
            max_count = max(day_counts)
            min_count = min([c for c in day_counts if c > 0] or [0])
            if max_count - min_count > 1:
                distribution_penalties += 5

    distribution_score = max(0, 30 - distribution_penalties)
    score += distribution_score

    # 3. Constraint satisfaction (30 points)
    violations = validate_constraints(timetable, confirmed_theory)
    constraint_score = max(0, 30 - (len(violations) * 5))
    score += constraint_score

    return min(100, score)


def generate_single_timetable(confirmed_theory, confirmed_lab):
    """Generate a single timetable attempt"""
    timetable = pd.DataFrame("", index=DAYS, columns=PERIODS)
    lab_sessions = {}

    # Check lab conflicts
    lab_conflicts = []
    for i, lab1 in enumerate(confirmed_lab):
        for j, lab2 in enumerate(confirmed_lab):
            if i < j:
                if lab1["day"] == lab2["day"] and lab1["session"] == lab2["session"]:
                    lab_conflicts.append((lab1["name"], lab2["name"], lab1["day"], lab1["session"]))

    if lab_conflicts:
        return None, lab_conflicts

    # Get teacher preferences (free periods)
    teacher_free_periods = st.session_state.get("teacher_preferences", {})

    # Allocate labs
    for lab in confirmed_lab:
        day = lab["day"]
        session = lab["session"]
        lab_sessions[day] = session

        slots = PERIODS_FN if session == "FN" else PERIODS_AN

        for slot in slots:
            timetable.loc[day, slot] = lab["name"]

    # Sort subjects by periods (descending) for better allocation
    sorted_subjects = sorted(confirmed_theory, key=lambda x: x["periods"], reverse=True)

    subject_day_count = defaultdict(lambda: defaultdict(int))
    subject_day_session = defaultdict(lambda: defaultdict(str))

    unallocated = []

    # Allocate theory subjects
    for subject in sorted_subjects:
        periods_needed = subject["periods"]
        subject_name = subject["name"]
        teacher = subject.get("teacher")
        allocated_count = 0

        # Get all available slots
        all_slots = []
        for day in DAYS:
            if day in lab_sessions:
                lab_session = lab_sessions[day]
                available_periods = PERIODS_AN if lab_session == "FN" else PERIODS_FN
            else:
                available_periods = PERIODS[:]

            for period in available_periods:
                if timetable.loc[day, period] == "":
                    # Check if teacher has a free period at this time
                    if teacher and teacher in teacher_free_periods:
                        if (day, period) not in teacher_free_periods[teacher]:
                            all_slots.append((day, period))
                    else:
                        all_slots.append((day, period))

        random.shuffle(all_slots)

        attempts = 0
        max_attempts = len(all_slots) * 3

        while allocated_count < periods_needed and attempts < max_attempts:
            attempts += 1

            valid_slots = []
            for day, period in all_slots:
                # Check max 2 per day
                if subject_day_count[subject_name][day] >= 2:
                    continue

                if timetable.loc[day, period] != "":
                    continue

                current_session = "FN" if period in PERIODS_FN else "AN"

                # If already allocated on this day, must be same session
                if subject_day_count[subject_name][day] > 0:
                    required_session = subject_day_session[subject_name][day]
                    if current_session != required_session:
                        continue

                valid_slots.append((day, period, current_session))

            if not valid_slots:
                break

            # Prefer days with fewer allocations for this subject
            valid_slots.sort(key=lambda x: subject_day_count[subject_name][x[0]])

            day, period, session = valid_slots[0]

            timetable.loc[day, period] = subject_name
            subject_day_count[subject_name][day] += 1
            subject_day_session[subject_name][day] = session
            allocated_count += 1

            all_slots = [(d, p) for d, p in all_slots if not (d == day and p == period)]

        if allocated_count < periods_needed:
            unallocated.append({
                "subject": subject_name,
                "needed": periods_needed,
                "allocated": allocated_count,
                "remaining": periods_needed - allocated_count
            })

    # Fill empty slots with Library
    for day in DAYS:
        for period in PERIODS:
            if timetable.loc[day, period] == "":
                timetable.loc[day, period] = "Library"

    return timetable, unallocated


# -------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------
def init_state():
    defaults = {
        "theory_subjects": [],
        "lab_subjects": [],
        "timetable_generated": False,
        "predefined_loaded": False,
        "current_regulation": None,
        "current_semester": None,
        "current_dept": None,
        "deleted_theory_subjects": [],
        "deleted_lab_subjects": [],
        "timetable": None,
        "unallocated": None,
        "timetable_score": 0,
        "history": [],
        "teacher_preferences": {},
        "generation_count": 0,
        "teacher_assignments": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()
init_teacher_assignments()


# -------------------------------------------------
# HELPER FUNCTIONS FOR EXPORT
# -------------------------------------------------
def get_subject_teacher_map():
    """Create a mapping of subjects to teachers"""
    mapping = {}
    for s in st.session_state.theory_subjects:
        if s["confirmed"]:
            mapping[s["name"]] = s["teacher"]
    for l in st.session_state.lab_subjects:
        if l["confirmed"]:
            mapping[l["name"]] = l["teacher"]
    return mapping


def prepare_summary_data(timetable):
    """Prepare summary data for export"""
    summary_data = []
    sno = 1

    for s in st.session_state.theory_subjects:
        if s["confirmed"]:
            actual_periods = sum(1 for day in DAYS for period in PERIODS
                                 if timetable.loc[day, period] == s["name"])
            subject_type = "Theory (Pre-defined)" if s.get("is_predefined", False) else "Theory (Custom)"
            summary_data.append({
                "S.No": sno,
                "Subject Code": s["code"],
                "Subject Name": s["name"],
                "Teacher": s["teacher"],
                "Credit": s["credit"],
                "Type": subject_type,
                "Periods per Week": s["periods"],
                "Allocated": actual_periods
            })
            sno += 1

    for l in st.session_state.lab_subjects:
        if l["confirmed"]:
            subject_type = "Lab (Pre-defined)" if l.get("is_predefined", False) else "Lab (Custom)"
            summary_data.append({
                "S.No": sno,
                "Subject Code": l["code"],
                "Subject Name": l["name"],
                "Teacher": l["teacher"],
                "Credit": l.get("credit", 2),
                "Type": f"{subject_type} ({l.get('floor', 'N/A')})",
                "Periods per Week": 4,
                "Allocated": 4
            })
            sno += 1

    return summary_data


# -------------------------------------------------
# SIDEBAR CONFIGURATION
# -------------------------------------------------
with st.sidebar:
    st.markdown("### Configuration")

    # Quick Stats
    if st.session_state.theory_subjects or st.session_state.lab_subjects:
        st.markdown("#### Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Theory", len([s for s in st.session_state.theory_subjects if s["confirmed"]]))
        with col2:
            st.metric("Labs", len([l for l in st.session_state.lab_subjects if l["confirmed"]]))

        total_periods = sum(s["periods"] for s in st.session_state.theory_subjects if s["confirmed"])
        total_periods += len([l for l in st.session_state.lab_subjects if l["confirmed"]]) * 4
        st.metric("Total Periods", f"{total_periods}/40")

        # Show teacher assignment summary
        num_teachers_used = len(st.session_state.teacher_assignments)
        if num_teachers_used > 0:
            st.metric("Teachers Used", num_teachers_used)

    st.markdown("---")

    # Export Options
    if st.session_state.timetable_generated and st.session_state.timetable is not None:
        st.markdown("#### Export Options")

        dept = st.session_state.get("current_dept", "")
        regulation = st.session_state.get("current_regulation", "")
        semester = st.session_state.get("current_semester", "")
        section = st.session_state.get("current_section", "")

        if dept and regulation and semester and section:
            timetable_name = f"{dept}_{regulation}_{semester}_Timetable_{section}"

            try:
                display_tt = create_display_timetable(st.session_state.timetable)
                st.download_button(
                    "Download CSV",
                    display_tt.to_csv().encode("utf-8"),
                    f"{timetable_name}.csv",
                    "text/csv",
                    use_container_width=True
                )

                summary_data = prepare_summary_data(st.session_state.timetable)
                subject_teacher_map = get_subject_teacher_map()
                workload_data = calculate_teacher_workload(st.session_state.timetable, subject_teacher_map)

                excel_data = export_to_excel(
                    st.session_state.timetable,
                    summary_data,
                    timetable_name,
                    workload_data
                )

                st.download_button(
                    "Download Excel",
                    excel_data,
                    f"{timetable_name}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error preparing export: {str(e)}")
                st.info("Please generate a timetable first.")

    st.markdown("---")

    # Reset Options
    st.markdown("#### Reset Options")
    if st.button("Clear All Data", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# -------------------------------------------------
# MAIN HEADER
# -------------------------------------------------
st.markdown('<h1 class="main-header">Intelligent Timetable Scheduler</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">created by CODE BLOODED | Intelligent Scheduling System</p>', unsafe_allow_html=True)

# -------------------------------------------------
# MAIN TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Setup",
    "Subjects",
    "Preferences",
    "Generate",
    "Analytics"
])

# -------------------------------------------------
# TAB 1: SETUP
# -------------------------------------------------
with tab1:
    st.markdown("### Basic Configuration")

    col1, col2 = st.columns(2)

    with col1:
        dept = st.selectbox("Department", ["Select"] + list(TEACHERS_BY_DEPT_SEMESTER.keys()), key="dept_select")
        if dept == "Select":
            st.warning("Please select a department to continue")
            st.stop()

        st.session_state.current_dept = dept

        semester_type = st.radio("Semester Type", ["Odd", "Even"], horizontal=True)

        section = st.selectbox("Class Room", CLASSROOMS)
        st.session_state.current_section = section

    with col2:
        regulation = st.selectbox("Regulation", ["R2025", "R2023", "R2021", "R2019"])

        semester = st.selectbox(
            "Semester",
            ["I", "III", "V", "VII"] if semester_type == "Odd" else ["II", "IV", "VI", "VIII"],
        )

    # Get semester-specific teachers
    teachers = TEACHERS_BY_DEPT_SEMESTER.get(dept, {}).get(semester, [])

    if not teachers:
        st.error(f"No teachers defined for {dept} - Semester {semester}")
        st.stop()

    # Display selection summary
    st.success(
        f"Configuration: **{dept}** | **{regulation}** | **{semester_type} Semester {semester}** | **{section}**")

    # Load pre-defined subjects when configuration changes
    if (not st.session_state.predefined_loaded or
            st.session_state.current_regulation != regulation or
            st.session_state.current_semester != semester or
            st.session_state.current_dept != dept):

        st.session_state.theory_subjects = []
        st.session_state.lab_subjects = []
        st.session_state.deleted_theory_subjects = []
        st.session_state.deleted_lab_subjects = []
        st.session_state.teacher_assignments = {}

        # MODIFIED: Load department-specific subjects
        if regulation in PREDEFINED_SUBJECTS:
            if dept in PREDEFINED_SUBJECTS[regulation]:
                if semester in PREDEFINED_SUBJECTS[regulation][dept]:
                    for sub in PREDEFINED_SUBJECTS[regulation][dept][semester]["theory"]:
                        st.session_state.theory_subjects.append({
                            "name": sub["name"],
                            "code": sub["code"],
                            "credit": sub["credit"],
                            "periods": sub["periods"],
                            "teacher": None,
                            "confirmed": False,
                            "is_predefined": True
                        })

                    for lab in PREDEFINED_SUBJECTS[regulation][dept][semester]["lab"]:
                        st.session_state.lab_subjects.append({
                            "name": lab["name"],
                            "code": lab["code"],
                            "credit": 2,
                            "day": None,
                            "session": None,
                            "floor": None,
                            "teacher": None,
                            "confirmed": False,
                            "is_predefined": True,
                            "needs_schedule": True
                        })

        st.session_state.predefined_loaded = True
        st.session_state.current_regulation = regulation
        st.session_state.current_semester = semester
        st.session_state.current_dept = dept
        st.rerun()

    st.markdown("---")

    # Department Teachers Overview
    st.markdown(f"### Available Teachers for {dept} - Semester {semester}")
    st.info(f"Total: {len(teachers)} teachers available for this semester")

    teacher_cols = st.columns(4)
    for idx, teacher in enumerate(teachers):
        with teacher_cols[idx % 4]:
            status = get_teacher_status_display(teacher)
            if "0/2" in status:
                st.markdown(f"🟢 {teacher}")
                st.caption(status)
            elif "1 more" in status:
                st.markdown(f"🟡 {teacher}")
                st.caption(status)
            else:
                st.markdown(f"🔴 {teacher}")
                st.caption(status)

# -------------------------------------------------
# TAB 2: SUBJECTS
# -------------------------------------------------
with tab2:
    subjects_tab1, subjects_tab2 = st.tabs(["Theory Subjects", "Lab Subjects"])

    # THEORY SUBJECTS
    with subjects_tab1:
        st.markdown("### Theory Subjects Management")

        # Show pre-defined subjects
        predefined_theory = [s for s in st.session_state.theory_subjects if s.get("is_predefined", False)]

        if predefined_theory:
            st.markdown("#### Pre-defined Theory Subjects")

            for i, sub in enumerate(predefined_theory):
                with st.expander(f"{sub['name']} ({sub['code']})", expanded=not sub["confirmed"]):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.metric("Periods/Week", sub["periods"])
                        st.metric("Credit", sub["credit"])

                    with col2:
                        actual_index = st.session_state.theory_subjects.index(sub)

                        if not sub["confirmed"]:
                            # MODIFIED: Get formatted teacher options with availability status
                            teacher_options = format_teacher_options_with_status(teachers, "theory")

                            teacher_selected = st.selectbox(
                                "Select Teacher",
                                teacher_options,
                                key=f"t_teacher_pre_{actual_index}",
                                help="Shows availability: ✓ (Available), ⚡ (1 slot left), ✗ (Full)"
                            )

                            # Extract actual teacher name from selection
                            teacher = extract_teacher_name_from_option(teacher_selected)

                            # Show teacher's current load if selected
                            if teacher != "Select":
                                info = get_teacher_assignment_info(teacher)
                                if info["count"] > 0:
                                    st.caption(f"📚 Currently teaching: {', '.join(info['subjects'])}")

                            if st.button("Assign Teacher", key=f"t_confirm_pre_{actual_index}",
                                         use_container_width=True) and teacher != "Select":
                                sub["teacher"] = teacher
                                sub["confirmed"] = True
                                assign_teacher_to_subject(teacher, sub["name"], "theory")
                                st.rerun()
                        else:
                            st.success(f"✅ Assigned to: **{sub['teacher']}**")
                            teacher_info = get_teacher_assignment_info(sub['teacher'])
                            st.caption(f"Teacher load: {teacher_info['count']}/2 subjects")

                            if st.button("Change Teacher", key=f"t_cancel_pre_{actual_index}",
                                         use_container_width=True):
                                unassign_teacher_from_subject(sub["teacher"], sub["name"], "theory")
                                sub["teacher"] = None
                                sub["confirmed"] = False
                                st.rerun()

                    with col3:
                        if st.button("Delete", key=f"t_delete_pre_{actual_index}",
                                     use_container_width=True, type="secondary"):
                            deleted_sub = sub.copy()
                            st.session_state.deleted_theory_subjects.append(deleted_sub)
                            if sub["confirmed"]:
                                unassign_teacher_from_subject(sub["teacher"], sub["name"], "theory")
                            st.session_state.theory_subjects.remove(sub)
                            st.rerun()

        # Restore deleted subjects
        if st.session_state.deleted_theory_subjects:
            with st.expander("Restore Deleted Subjects", expanded=False):
                for i, deleted_sub in enumerate(st.session_state.deleted_theory_subjects):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(
                            f"**{deleted_sub['name']}** ({deleted_sub['code']}) - {deleted_sub['periods']} periods")
                    with col2:
                        if st.button("Restore", key=f"restore_theory_{i}", use_container_width=True):
                            restored_sub = deleted_sub.copy()
                            restored_sub["teacher"] = None
                            restored_sub["confirmed"] = False
                            st.session_state.theory_subjects.append(restored_sub)
                            st.session_state.deleted_theory_subjects.pop(i)
                            st.rerun()

        st.markdown("---")

        # Add custom theory subject
        st.markdown("#### Add Custom Theory Subject")
        with st.form("theory_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                t_name = st.text_input("Subject Name")
                t_credit = st.number_input("Credit", min_value=1, max_value=4, step=1, value=3)
            with col2:
                t_code = st.text_input("Subject Code")
                t_periods = st.number_input("Periods per Week", min_value=1, max_value=8, step=1, value=3)

            add_theory = st.form_submit_button("Add Custom Theory Subject", use_container_width=True)

        if add_theory:
            if not t_name or not t_code:
                st.error("Please fill all required fields")
            elif any(s["name"] == t_name or s["code"] == t_code for s in st.session_state.theory_subjects):
                st.error("Subject already exists")
            else:
                st.session_state.theory_subjects.append({
                    "name": t_name,
                    "code": t_code,
                    "credit": t_credit,
                    "periods": t_periods,
                    "teacher": None,
                    "confirmed": False,
                    "is_predefined": False
                })
                st.success(f"Added: {t_name}")
                st.rerun()

        # Show custom subjects
        custom_theory = [s for s in st.session_state.theory_subjects if not s.get("is_predefined", False)]
        if custom_theory:
            st.markdown("#### Custom Theory Subjects")
            for i, sub in enumerate(custom_theory):
                with st.expander(f"{sub['name']} ({sub['code']})", expanded=not sub["confirmed"]):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.metric("Periods/Week", sub["periods"])
                        st.metric("Credit", sub["credit"])

                    with col2:
                        actual_index = st.session_state.theory_subjects.index(sub)

                        if not sub["confirmed"]:
                            # MODIFIED: Get formatted teacher options with availability status
                            teacher_options = format_teacher_options_with_status(teachers, "theory")

                            teacher_selected = st.selectbox(
                                "Select Teacher",
                                teacher_options,
                                key=f"t_teacher_custom_{actual_index}",
                                help="Shows availability: ✓ (Available), ⚡ (1 slot left), ✗ (Full)"
                            )

                            teacher = extract_teacher_name_from_option(teacher_selected)

                            if teacher != "Select":
                                info = get_teacher_assignment_info(teacher)
                                if info["count"] > 0:
                                    st.caption(f"📚 Currently teaching: {', '.join(info['subjects'])}")

                            if st.button("Assign Teacher", key=f"t_confirm_custom_{actual_index}",
                                         use_container_width=True) and teacher != "Select":
                                sub["teacher"] = teacher
                                sub["confirmed"] = True
                                assign_teacher_to_subject(teacher, sub["name"], "theory")
                                st.rerun()
                        else:
                            st.success(f"✅ Assigned to: **{sub['teacher']}**")
                            teacher_info = get_teacher_assignment_info(sub['teacher'])
                            st.caption(f"Teacher load: {teacher_info['count']}/2 subjects")

                            if st.button("Change Teacher", key=f"t_cancel_custom_{actual_index}",
                                         use_container_width=True):
                                unassign_teacher_from_subject(sub["teacher"], sub["name"], "theory")
                                sub["teacher"] = None
                                sub["confirmed"] = False
                                st.rerun()

                    with col3:
                        if st.button("Delete", key=f"t_delete_custom_{actual_index}",
                                     use_container_width=True, type="secondary"):
                            if sub["confirmed"]:
                                unassign_teacher_from_subject(sub["teacher"], sub["name"], "theory")
                            st.session_state.theory_subjects.remove(sub)
                            st.rerun()

    # LAB SUBJECTS
    with subjects_tab2:
        st.markdown("### Lab Subjects Management")

        # Labs needing schedule
        predefined_labs_needing_schedule = [l for l in st.session_state.lab_subjects
                                            if l.get("is_predefined", False) and l.get("needs_schedule", False)]

        if predefined_labs_needing_schedule:
            st.markdown("#### Schedule Pre-defined Labs")
            st.info("Set day and session for each lab")

            for i, lab in enumerate(predefined_labs_needing_schedule):
                actual_index = st.session_state.lab_subjects.index(lab)

                with st.expander(f"{lab['name']} ({lab['code']})", expanded=True):
                    with st.form(f"predefined_lab_schedule_{actual_index}"):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            l_day = st.selectbox("Day", DAYS, key=f"pre_lab_day_{actual_index}")
                        with col2:
                            l_session = st.radio("Session", ["FN", "AN"], horizontal=True,
                                                 key=f"pre_lab_session_{actual_index}")
                        with col3:
                            l_floor = st.selectbox("Lab Floor", LAB_FLOORS,
                                                   key=f"pre_lab_floor_{actual_index}")
                        with col4:
                            schedule_lab = st.form_submit_button("Set Schedule", use_container_width=True)

                        if schedule_lab:
                            conflict = False
                            for existing_lab in st.session_state.lab_subjects:
                                if (existing_lab != lab and
                                        existing_lab.get("day") == l_day and
                                        existing_lab.get("session") == l_session):
                                    st.error(f"Conflict with {existing_lab['name']} on {l_day} {l_session}")
                                    conflict = True
                                    break

                            if not conflict:
                                lab["day"] = l_day
                                lab["session"] = l_session
                                lab["floor"] = l_floor
                                lab["needs_schedule"] = False
                                st.success("Schedule set!")
                                st.rerun()

        # Scheduled labs
        scheduled_predefined_labs = [l for l in st.session_state.lab_subjects
                                     if l.get("is_predefined", False) and not l.get("needs_schedule", False)]

        if scheduled_predefined_labs:
            st.markdown("#### Pre-defined Labs (Scheduled)")

            with st.container():
                st.markdown("**Lab Schedule Overview:**")
                schedule_df = pd.DataFrame([
                    {"Lab": l["name"], "Day": l["day"], "Session": l["session"], "Floor": l.get("floor", "N/A")}
                    for l in scheduled_predefined_labs
                ])
                st.dataframe(schedule_df, use_container_width=True, hide_index=True)

            st.markdown("---")

            for i, lab in enumerate(scheduled_predefined_labs):
                actual_index = st.session_state.lab_subjects.index(lab)

                with st.expander(f"{lab['name']} - {lab['day']} {lab['session']}",
                                 expanded=not lab["confirmed"]):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.metric("Schedule", f"{lab['day']} {lab['session']}")
                        st.metric("Floor", lab.get("floor", "N/A"))

                    with col2:
                        if not lab["confirmed"]:
                            # MODIFIED: Get formatted teacher options with availability status
                            teacher_options = format_teacher_options_with_status(teachers, "lab")

                            teacher_selected = st.selectbox(
                                "Select Teacher",
                                teacher_options,
                                key=f"l_teacher_pre_{actual_index}",
                                help="Shows availability: ✓ (Available), ⚡ (1 slot left), ✗ (Full)"
                            )

                            teacher = extract_teacher_name_from_option(teacher_selected)

                            if teacher != "Select":
                                info = get_teacher_assignment_info(teacher)
                                if info["count"] > 0:
                                    st.caption(f"📚 Currently teaching: {', '.join(info['subjects'])}")

                            col2a, col2b = st.columns(2)
                            with col2a:
                                if st.button("Assign", key=f"l_confirm_pre_{actual_index}",
                                             use_container_width=True) and teacher != "Select":
                                    lab["teacher"] = teacher
                                    lab["confirmed"] = True
                                    assign_teacher_to_subject(teacher, lab["name"], "lab")
                                    st.rerun()
                            with col2b:
                                if st.button("Reschedule", key=f"l_reschedule_{actual_index}",
                                             use_container_width=True):
                                    lab["needs_schedule"] = True
                                    st.rerun()
                        else:
                            st.success(f"✅ Assigned to: **{lab['teacher']}**")
                            teacher_info = get_teacher_assignment_info(lab['teacher'])
                            st.caption(f"Teacher load: {teacher_info['count']}/2 subjects")

                            col2a, col2b = st.columns(2)
                            with col2a:
                                if st.button("Change", key=f"l_cancel_pre_{actual_index}",
                                             use_container_width=True):
                                    unassign_teacher_from_subject(lab["teacher"], lab["name"], "lab")
                                    lab["teacher"] = None
                                    lab["confirmed"] = False
                                    st.rerun()
                            with col2b:
                                if st.button("Reschedule", key=f"l_reschedule2_{actual_index}",
                                             use_container_width=True):
                                    lab["needs_schedule"] = True
                                    if lab["confirmed"]:
                                        unassign_teacher_from_subject(lab["teacher"], lab["name"], "lab")
                                        lab["teacher"] = None
                                        lab["confirmed"] = False
                                    st.rerun()

                    with col3:
                        if st.button("Delete", key=f"l_delete_scheduled_{actual_index}",
                                     use_container_width=True, type="secondary"):
                            deleted_lab = lab.copy()
                            st.session_state.deleted_lab_subjects.append(deleted_lab)
                            if lab["confirmed"]:
                                unassign_teacher_from_subject(lab["teacher"], lab["name"], "lab")
                            st.session_state.lab_subjects.remove(lab)
                            st.rerun()

        # Restore deleted labs
        if st.session_state.deleted_lab_subjects:
            with st.expander("Restore Deleted Labs", expanded=False):
                for i, deleted_lab in enumerate(st.session_state.deleted_lab_subjects):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        schedule_info = f" - {deleted_lab.get('day', 'Not scheduled')} {deleted_lab.get('session', '')}" if deleted_lab.get(
                            'day') else " - Not scheduled"
                        st.write(f"**{deleted_lab['name']}** ({deleted_lab['code']}){schedule_info}")
                    with col2:
                        if st.button("Restore", key=f"restore_lab_{i}", use_container_width=True):
                            restored_lab = deleted_lab.copy()
                            restored_lab["teacher"] = None
                            restored_lab["confirmed"] = False
                            if not restored_lab.get("day"):
                                restored_lab["needs_schedule"] = True
                            st.session_state.lab_subjects.append(restored_lab)
                            st.session_state.deleted_lab_subjects.pop(i)
                            st.rerun()

        st.markdown("---")

        # Add custom lab
        st.markdown("#### Add Custom Lab Subject")
        with st.form("lab_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                l_name = st.text_input("Lab Name")
                l_credit = st.number_input("Lab Credit", 1, 3, 2)
                l_day = st.selectbox("Day", DAYS)
            with col2:
                l_code = st.text_input("Lab Code")
                l_session = st.radio("Session", ["FN", "AN"], horizontal=True)
                l_floor = st.selectbox("Lab Floor", LAB_FLOORS)

            add_lab = st.form_submit_button("Add Custom Lab Subject", use_container_width=True)

        if add_lab:
            if not l_name or not l_code:
                st.error("Please fill all required fields")
            elif any(l["name"] == l_name or l["code"] == l_code for l in st.session_state.lab_subjects):
                st.error("Lab already exists")
            else:
                conflict = False
                for existing_lab in st.session_state.lab_subjects:
                    if existing_lab.get("day") == l_day and existing_lab.get("session") == l_session:
                        st.error(f"Conflict with {existing_lab['name']} on {l_day} {l_session}")
                        conflict = True
                        break

                if not conflict:
                    st.session_state.lab_subjects.append({
                        "name": l_name,
                        "code": l_code,
                        "credit": l_credit,
                        "day": l_day,
                        "session": l_session,
                        "floor": l_floor,
                        "teacher": None,
                        "confirmed": False,
                        "is_predefined": False,
                        "needs_schedule": False
                    })
                    st.success(f"Added: {l_name}")
                    st.rerun()

        # Show custom labs
        custom_labs = [l for l in st.session_state.lab_subjects
                       if not l.get("is_predefined", False) and not l.get("needs_schedule", False)]

        if custom_labs:
            st.markdown("#### Custom Lab Subjects")
            for i, lab in enumerate(custom_labs):
                actual_index = st.session_state.lab_subjects.index(lab)

                with st.expander(f"{lab['name']} - {lab['day']} {lab['session']}",
                                 expanded=not lab["confirmed"]):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.metric("Schedule", f"{lab['day']} {lab['session']}")
                        st.metric("Floor", lab.get("floor", "N/A"))

                    with col2:
                        if not lab["confirmed"]:
                            # MODIFIED: Get formatted teacher options with availability status
                            teacher_options = format_teacher_options_with_status(teachers, "lab")

                            teacher_selected = st.selectbox(
                                "Select Teacher",
                                teacher_options,
                                key=f"l_teacher_custom_{actual_index}",
                                help="Shows availability: ✓ (Available), ⚡ (1 slot left), ✗ (Full)"
                            )

                            teacher = extract_teacher_name_from_option(teacher_selected)

                            if teacher != "Select":
                                info = get_teacher_assignment_info(teacher)
                                if info["count"] > 0:
                                    st.caption(f"📚 Currently teaching: {', '.join(info['subjects'])}")

                            if st.button("Assign Teacher", key=f"l_confirm_custom_{actual_index}",
                                         use_container_width=True) and teacher != "Select":
                                lab["teacher"] = teacher
                                lab["confirmed"] = True
                                assign_teacher_to_subject(teacher, lab["name"], "lab")
                                st.rerun()
                        else:
                            st.success(f"✅ Assigned to: **{lab['teacher']}**")
                            teacher_info = get_teacher_assignment_info(lab['teacher'])
                            st.caption(f"Teacher load: {teacher_info['count']}/2 subjects")

                            if st.button("Change Teacher", key=f"l_cancel_custom_{actual_index}",
                                         use_container_width=True):
                                unassign_teacher_from_subject(lab["teacher"], lab["name"], "lab")
                                lab["teacher"] = None
                                lab["confirmed"] = False
                                st.rerun()

                    with col3:
                        if st.button("Delete", key=f"l_delete_custom_{actual_index}",
                                     use_container_width=True, type="secondary"):
                            if lab["confirmed"]:
                                unassign_teacher_from_subject(lab["teacher"], lab["name"], "lab")
                            st.session_state.lab_subjects.remove(lab)
                            st.rerun()

# -------------------------------------------------
# TAB 3: PREFERENCES
# -------------------------------------------------
with tab3:
    st.markdown("### Teacher Preferences")
    st.info("Set free periods for teachers. They won't be assigned classes during these times.")

    # Get all teachers who are assigned to subjects
    assigned_teachers = list(st.session_state.teacher_assignments.keys())

    if not assigned_teachers:
        st.warning("No teachers assigned yet. Please assign teachers to subjects first.")
    else:
        # Select teacher
        selected_teacher = st.selectbox(
            "Select Teacher",
            ["Select a teacher"] + sorted(assigned_teachers),
            key="pref_teacher_select"
        )

        if selected_teacher != "Select a teacher":
            # Show teacher's current assignments
            teacher_info = get_teacher_assignment_info(selected_teacher)
            st.info(f"**{selected_teacher}** is currently assigned to: {', '.join(teacher_info['subjects'])}")

            # Initialize teacher preferences if not exists
            if selected_teacher not in st.session_state.teacher_preferences:
                st.session_state.teacher_preferences[selected_teacher] = []

            # Show current free periods
            current_free = st.session_state.teacher_preferences[selected_teacher]

            if current_free:
                st.markdown("**Current Free Periods:**")
                free_df = pd.DataFrame([
                    {"Day": day, "Period": period}
                    for day, period in current_free
                ])
                st.dataframe(free_df, use_container_width=True, hide_index=True)

                if st.button("Clear All Free Periods", key="clear_all_free"):
                    st.session_state.teacher_preferences[selected_teacher] = []
                    st.success("Cleared all free periods")
                    if st.session_state.timetable_generated:
                        st.session_state.timetable_generated = False
                        st.info("Teacher preferences changed. Please regenerate the timetable.")
                    st.rerun()
            else:
                st.markdown("**Current Free Periods:**")
                st.info("No free periods set for this teacher yet.")

            st.markdown("---")

            # Visual grid to select multiple periods
            st.markdown("**Quick Selection Grid:**")
            st.caption("Click on cells to toggle free periods")

            for day in DAYS:
                st.markdown(f"**{day}:**")
                cols = st.columns(8)

                for i, period in enumerate(PERIODS):
                    with cols[i]:
                        is_free = (day, period) in current_free
                        button_label = "✓" if is_free else period
                        button_type = "secondary" if is_free else "primary"

                        if st.button(
                                button_label,
                                key=f"grid_{selected_teacher}_{day}_{period}",
                                use_container_width=True,
                                type=button_type
                        ):
                            if is_free:
                                st.session_state.teacher_preferences[selected_teacher].remove((day, period))
                            else:
                                st.session_state.teacher_preferences[selected_teacher].append((day, period))

                            if st.session_state.timetable_generated:
                                st.session_state.timetable_generated = False
                                st.info("Teacher preferences changed. Please regenerate the timetable.")
                            st.rerun()

                st.markdown("")

            st.markdown("---")

            # Setting free periods section
            st.markdown(f"#### Setting free periods for: **{selected_teacher}**")
            st.markdown("**Add Free Period:**")

            col1, col2, col3 = st.columns([2, 2, 1])

            if 'prev_free_day' not in st.session_state:
                st.session_state.prev_free_day = DAYS[0]

            with col1:
                free_day = st.selectbox("Day", DAYS, key="free_day_select")

            with col2:
                free_periods = st.multiselect("Periods", PERIODS, key=f"free_periods_select_{free_day}")

            with col3:
                st.markdown("")
                st.markdown("")
                if st.button("Add", key="add_free_period", use_container_width=True):
                    if free_periods:
                        added_count = 0
                        for period in free_periods:
                            if (free_day, period) not in current_free:
                                st.session_state.teacher_preferences[selected_teacher].append((free_day, period))
                                added_count += 1

                        if added_count > 0:
                            st.success(f"Added {added_count} free period(s) for {free_day}")
                            if st.session_state.timetable_generated:
                                st.session_state.timetable_generated = False
                                st.info("Teacher preferences changed. Please regenerate the timetable.")
                            st.rerun()
                        else:
                            st.warning("All selected periods already exist")
                    else:
                        st.warning("Please select at least one period")

            st.session_state.prev_free_day = free_day

            st.markdown("---")

            # Summary statistics
            st.markdown("**Summary:**")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Free Periods Set", len(current_free))

            with col2:
                total_periods = 40
                available_periods = total_periods - len(current_free)
                st.metric("Available Periods", available_periods)

            with col3:
                utilization = ((total_periods - len(current_free)) / total_periods) * 100
                st.metric("Availability", f"{utilization:.0f}%")

    st.markdown("---")

    # Summary of all teacher preferences
    if st.session_state.teacher_preferences:
        with st.expander("All Teacher Preferences Summary", expanded=False):
            for teacher, free_periods in st.session_state.teacher_preferences.items():
                if free_periods:
                    st.markdown(f"**{teacher}**: {len(free_periods)} free period(s)")
                    periods_str = ", ".join([f"{day} {period}" for day, period in free_periods])
                    st.caption(periods_str)

# -------------------------------------------------
# TAB 4: GENERATE TIMETABLE (Remains unchanged)
# -------------------------------------------------
with tab4:
    st.markdown("### Generate Timetable")

    unscheduled_labs = [l for l in st.session_state.lab_subjects if l.get("needs_schedule", False)]
    confirmed_theory = [s for s in st.session_state.theory_subjects if s["confirmed"]]
    confirmed_lab = [l for l in st.session_state.lab_subjects if l["confirmed"] and not l.get("needs_schedule", False)]

    if unscheduled_labs:
        st.warning(f"Please schedule {len(unscheduled_labs)} lab(s) before generating timetable")

    if not confirmed_theory and not confirmed_lab:
        st.error("Please add and confirm at least one subject")

    # Show summary before generation
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Theory Subjects", len(confirmed_theory))
    with col2:
        st.metric("Lab Subjects", len(confirmed_lab))
    with col3:
        theory_periods = sum(s["periods"] for s in confirmed_theory)
        st.metric("Theory Periods", theory_periods)
    with col4:
        lab_periods = len(confirmed_lab) * 4
        st.metric("Lab Periods", lab_periods)

    # Capacity check
    total_periods_needed = theory_periods + lab_periods
    available_slots = 40

    if total_periods_needed > available_slots:
        st.error(f"**Over-capacity**: Need {total_periods_needed} periods but only {available_slots} available!")
        st.error(f"**Deficit**: {total_periods_needed - available_slots} periods")
    elif total_periods_needed > available_slots * 0.9:
        st.warning(
            f"**Near capacity**: Using {total_periods_needed}/{available_slots} slots ({(total_periods_needed / available_slots * 100):.1f}%)")
    else:
        st.success(
            f"**Capacity**: {total_periods_needed}/{available_slots} slots ({(total_periods_needed / available_slots * 100):.1f}%)")

    st.markdown("---")

    # Generation options
    col1, col2 = st.columns([3, 1])
    with col1:
        max_iterations = st.slider("Optimization Iterations", 10, 200, 50,
                                   help="More iterations = better timetable but slower generation")
    with col2:
        st.metric("Expected Time", f"~{max_iterations // 20}s")

    # Generate button
    if st.session_state.generation_count == 0:
        button_label = "Generate Timetable"
    else:
        button_label = f"Re-generate Timetable (Attempt #{st.session_state.generation_count + 1})"

    if st.button(button_label, type="primary", use_container_width=True,
                 disabled=(len(unscheduled_labs) > 0 or (not confirmed_theory and not confirmed_lab))):

        st.session_state.generation_count += 1
        random.seed(st.session_state.generation_count * 42)

        with st.spinner(f"Generating optimal timetable ({max_iterations} iterations)..."):
            result = generate_timetable_with_optimization(confirmed_theory, confirmed_lab, max_iterations)

            if result[0] is None:
                st.error("**Generation Failed - Lab Conflicts Detected!**")
                lab_conflicts = result[1]
                for conflict in lab_conflicts:
                    st.write(f"• **{conflict[0]}** and **{conflict[1]}** both on **{conflict[2]} {conflict[3]}**")
                st.stop()

            timetable, unallocated, score = result
            st.session_state.timetable = timetable
            st.session_state.unallocated = unallocated
            st.session_state.timetable_score = score
            st.session_state.timetable_generated = True

        st.success(f"**Timetable Generated! Quality Score: {score:.1f}/100**")
        st.balloons()

    # Display timetable if generated
    if st.session_state.timetable_generated and st.session_state.timetable is not None:
        st.markdown("---")

        score = st.session_state.timetable_score
        if score >= 90:
            quality_color = "🟢"
            quality_text = "Excellent"
        elif score >= 75:
            quality_color = "🟡"
            quality_text = "Good"
        elif score >= 60:
            quality_color = "🟠"
            quality_text = "Fair"
        else:
            quality_color = "🔴"
            quality_text = "Needs Improvement"

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"### {quality_color} Timetable Quality: {quality_text} ({score:.1f}/100)")

        if st.session_state.generation_count > 1:
            st.info(f"This is generation attempt #{st.session_state.generation_count}")

        display_timetable = create_display_timetable(st.session_state.timetable)


        def style_timetable(val):
            if val == "BREAK":
                return 'background-color: #1a1a1a; color: #fafafa; font-weight: bold; text-align: center'
            if val == "Library":
                return 'background-color: #1a4d2e; color: #fafafa'
            if val == "":
                return 'background-color: #0e1117; color: #fafafa'
            return 'background-color: #262730; color: #fafafa; border: 1px solid #3d3d3d'


        styled_table = display_timetable.style.map(style_timetable)
        st.dataframe(styled_table, use_container_width=True, height=250)

        # Download button
        dept = st.session_state.get("current_dept", "")
        regulation = st.session_state.get("current_regulation", "")
        semester = st.session_state.get("current_semester", "")
        section = st.session_state.get("current_section", "")

        if dept and regulation and semester and section:
            roman_to_suffix = {
                "I": "Ist", "II": "IInd", "III": "IIIrd", "IV": "IVth",
                "V": "Vth", "VI": "VIth", "VII": "VIIth", "VIII": "VIIIth",
            }
            semester_suffix = roman_to_suffix.get(semester, semester)
            timetable_name = f"{dept}_{regulation}_Semester_{semester_suffix}_Timetable_{section}"

            csv_data = display_timetable.to_csv().encode("utf-8")

            st.download_button(
                label="Download Timetable (CSV)",
                data=csv_data,
                file_name=f"{timetable_name}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )

        # Allocation status
        if st.session_state.unallocated:
            st.error("**Partial Allocation:**")
            for item in st.session_state.unallocated:
                st.write(
                    f"- **{item['subject']}**: {item['allocated']}/{item['needed']} allocated, {item['remaining']} remaining")
        else:
            st.success("**All subjects successfully allocated!**")

        # Constraint violations
        with st.expander("Constraint Validation"):
            violations = validate_constraints(st.session_state.timetable, confirmed_theory)

            if violations:
                st.warning(f"Found {len(violations)} constraint violation(s):")
                for v in violations:
                    st.write(f"- {v['message']}")
            else:
                st.success("All constraints satisfied!")

# -------------------------------------------------
# TAB 5: ANALYTICS (Remains unchanged)
# -------------------------------------------------
with tab5:
    st.markdown("### Timetable Analytics")

    if not st.session_state.timetable_generated or st.session_state.timetable is None:
        st.info("Generate a timetable first to see analytics")
    else:
        timetable = st.session_state.timetable

        subject_teacher_map = get_subject_teacher_map()
        workload_data = calculate_teacher_workload(timetable, subject_teacher_map)
        utilization, filled, library = calculate_utilization_score(timetable)

        # Overview metrics
        st.markdown("#### Overview Metrics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Utilization Rate", f"{utilization:.1f}%")
        with col2:
            st.metric("Filled Slots", f"{filled}/40")
        with col3:
            st.metric("Library Periods", library)

        st.markdown("---")

        # Teacher Workload Analysis
        st.markdown("#### Teacher Workload Distribution")

        if workload_data:
            workload_df = pd.DataFrame([
                {"Teacher": k, "Periods per Week": v}
                for k, v in sorted(workload_data.items(), key=lambda x: x[1], reverse=True)
            ])

            fig = px.bar(workload_df, x="Teacher", y="Periods per Week",
                         title="Teacher Workload Distribution",
                         color="Periods per Week",
                         color_continuous_scale="Blues")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Workload", f"{workload_df['Periods per Week'].mean():.1f}")
            with col2:
                st.metric("Max Workload", f"{workload_df['Periods per Week'].max()}")
            with col3:
                st.metric("Min Workload", f"{workload_df['Periods per Week'].min()}")

            with st.expander("Detailed Workload Table"):
                st.dataframe(workload_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Subject Distribution Analysis
        st.markdown("#### Subject Distribution Analysis")

        subject_distribution = defaultdict(lambda: {"FN": 0, "AN": 0, "total": 0})

        for day in DAYS:
            for period in PERIODS:
                subject = timetable.loc[day, period]
                if subject and subject != "" and subject != "Library":
                    session = "FN" if period in PERIODS_FN else "AN"
                    subject_distribution[subject][session] += 1
                    subject_distribution[subject]["total"] += 1

        if subject_distribution:
            dist_df = pd.DataFrame([
                {
                    "Subject": k,
                    "FN Periods": v["FN"],
                    "AN Periods": v["AN"],
                    "Total": v["total"],
                    "Balance": abs(v["FN"] - v["AN"])
                }
                for k, v in subject_distribution.items()
            ])

            fig = go.Figure()
            fig.add_trace(go.Bar(name='Forenoon', x=dist_df['Subject'], y=dist_df['FN Periods']))
            fig.add_trace(go.Bar(name='Afternoon', x=dist_df['Subject'], y=dist_df['AN Periods']))
            fig.update_layout(
                barmode='group',
                title="Subject Distribution: Forenoon vs Afternoon",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Subject Distribution Table"):
                st.dataframe(dist_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Daily Load Analysis
        st.markdown("#### Daily Load Analysis")

        daily_load = {}
        for day in DAYS:
            filled = sum(1 for period in PERIODS
                         if timetable.loc[day, period] not in ["", "Library", "BREAK"])
            daily_load[day] = filled

        daily_df = pd.DataFrame([
            {"Day": k, "Filled Periods": v, "Utilization": f"{(v / 8 * 100):.1f}%"}
            for k, v in daily_load.items()
        ])

        fig = px.line(daily_df, x="Day", y="Filled Periods",
                      title="Daily Period Load",
                      markers=True)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Daily Load Table"):
            st.dataframe(daily_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Session-wise Analysis
        st.markdown("#### Session-wise Analysis")

        fn_filled = sum(1 for day in DAYS for period in PERIODS_FN
                        if timetable.loc[day, period] not in ["", "Library"])
        an_filled = sum(1 for day in DAYS for period in PERIODS_AN
                        if timetable.loc[day, period] not in ["", "Library"])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Forenoon Utilization", f"{(fn_filled / 20 * 100):.1f}%",
                      help=f"{fn_filled}/20 periods filled")
        with col2:
            st.metric("Afternoon Utilization", f"{(an_filled / 20 * 100):.1f}%",
                      help=f"{an_filled}/20 periods filled")

        session_data = pd.DataFrame({
            "Session": ["Forenoon", "Afternoon"],
            "Filled Periods": [fn_filled, an_filled]
        })

        fig = px.pie(session_data, values="Filled Periods", names="Session",
                     title="Session-wise Distribution")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem;'>
    <p><strong>Intelligent Timetable Scheduler</strong></p>
    <p>Created by <strong>CODE BLOODED</strong> | Powered by Streamlit</p>
    <p>Features: Flexible Teacher Assignment (Max 2 subjects) • Intelligent Scheduling • Teacher Preferences • Re-generation • Analytics Dashboard</p>
</div>
""", unsafe_allow_html=True)
