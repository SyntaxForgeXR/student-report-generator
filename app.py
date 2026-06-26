import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from parser import parse_lms_file
from report_pdf import generate_pdf

# --------------------------------------------------------
# Page Configuration
# --------------------------------------------------------
st.set_page_config(
    page_title="Student Report Card Generator", page_icon="🎓", layout="wide"
)

# --------------------------------------------------------
# Theme Colors
# --------------------------------------------------------

PRIMARY = "#2563EB"
SECONDARY = "#4F46E5"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
DANGER = "#EF4444"

BG = "#F8FAFC"
CARD = "#FFFFFF"
TEXT = "#0F172A"
TEXT_LIGHT = "#64748B"

# --------------------------------------------------------
# Modern CSS
# --------------------------------------------------------

st.markdown(
    f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background:{BG};
}}

.block-container {{
    padding-top:2rem;
    padding-bottom:2rem;
    max-width:1400px;
}}

header {{
    visibility:hidden;
}}

footer {{
    visibility:hidden;
}}

#MainMenu {{
    visibility:hidden;
}}

div[data-testid="stVerticalBlock"]>div:has(.metric-card){{
    margin-bottom:0px;
}}

.hero{{
    background:linear-gradient(135deg,#2563EB,#4F46E5);
    padding:35px;
    border-radius:22px;
    color:white;
    margin-bottom:25px;
    box-shadow:0 15px 40px rgba(37,99,235,.18);
}}

.hero-title{{
    font-size:38px;
    font-weight:800;
}}

.hero-sub{{
    opacity:.9;
    margin-top:8px;
    font-size:15px;
}}

.card{{
    background:white;
    border-radius:20px;
    padding:24px;
    border:1px solid #E5E7EB;
    box-shadow:0 8px 30px rgba(15,23,42,.05);
}}

.metric-card{{
    background:white;
    border-radius:18px;
    padding:20px;
    border:1px solid #E5E7EB;
    text-align:center;
    box-shadow:0 8px 25px rgba(0,0,0,.05);
}}

.metric-title{{
    font-size:13px;
    color:{TEXT_LIGHT};
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:.08em;
}}

.metric-value{{
    font-size:34px;
    color:{TEXT};
    font-weight:800;
    margin-top:8px;
}}

.metric-sub{{
    color:{TEXT_LIGHT};
    font-size:13px;
}}

.student-name{{
    font-size:30px;
    font-weight:800;
    color:{TEXT};
}}

.label{{
    color:{TEXT_LIGHT};
    font-size:12px;
    text-transform:uppercase;
    letter-spacing:.08em;
    font-weight:700;
}}

.value{{
    color:{TEXT};
    font-size:16px;
    font-weight:600;
    margin-bottom:18px;
}}

.section-title{{
    font-size:22px;
    font-weight:700;
    margin-bottom:20px;
    color:{TEXT};
}}

div.stButton>button,
div.stDownloadButton>button{{
    width:100%;
    height:52px;
    border-radius:14px;
    border:none;
    background:linear-gradient(135deg,#2563EB,#4F46E5);
    color:white;
    font-weight:700;
    transition:.25s;
}}

div.stButton>button:hover,
div.stDownloadButton>button:hover{{
    transform:translateY(-2px);
}}

.stSelectbox>div>div{{
    border-radius:14px;
}}

[data-testid="stFileUploader"]{{
    border-radius:16px;
    border:2px dashed #CBD5E1;
    padding:12px;
}}

</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------
# Hero Header
# --------------------------------------------------------

st.markdown(
    """
<div class="hero">

<div class="hero-title">
📊 Student Report Card Generator
</div>

<div class="hero-sub">
Your all-in-one report card generator.
</div>

</div>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------
# Upload + Student Selection Row
# --------------------------------------------------------

upload_col, selector_col = st.columns([1, 1])

with upload_col:
    uploaded = st.file_uploader("Upload LMS CSV / XLSX", type=["csv", "xlsx"])

if uploaded is None:

    st.markdown(
        """
    <div class="card" style="text-align:center;padding:70px;">

    <h2>📂 Upload Student's Data</h2>

    <p style="color:#64748B;font-size:16px;">
    Upload a CSV or Excel file to generate professional report cards.
    </p>

    </div>
    """,
        unsafe_allow_html=True,
    )

    st.stop()

# --------------------------------------------------------
# Parse File
# --------------------------------------------------------

try:
    df, exercise, course = parse_lms_file(uploaded)

except Exception as e:

    st.error(e)
    st.stop()

if df.empty:

    st.warning("No student records found.")
    st.stop()

student_names = df["Name"].tolist()

with selector_col:

    selected = st.selectbox("Select Student", student_names)

row = df[df["Name"] == selected].iloc[0]

# --------------------------------------------------------
# Grade Colors
# --------------------------------------------------------

GRADE_COLORS = {
    "A+": "#10B981",
    "A": "#22C55E",
    "B": "#3B82F6",
    "C": "#F59E0B",
    "D": "#F97316",
    "F": "#EF4444",
}


def grade_color(grade):

    grade = str(grade).upper().strip()

    for g in GRADE_COLORS:
        if grade.startswith(g):
            return GRADE_COLORS[g]

    return "#64748B"


# --------------------------------------------------------
# Gauge Chart
# --------------------------------------------------------


def gauge_chart(value, grade):

    color = grade_color(grade)

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "%", "font": {"size": 40, "color": "#0F172A"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": color, "thickness": 0.28},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "#FEE2E2"},
                    {"range": [40, 60], "color": "#FEF3C7"},
                    {"range": [60, 80], "color": "#DBEAFE"},
                    {"range": [80, 100], "color": "#D1FAE5"},
                ],
            },
        )
    )

    fig.update_layout(
        height=300,
        margin=dict(l=15, r=15, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
    )

    return fig


# --------------------------------------------------------
# Donut Chart
# --------------------------------------------------------


def donut_chart(obtained, total, grade):

    color = grade_color(grade)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Obtained", "Remaining"],
                values=[obtained, total - obtained],
                hole=0.72,
                marker=dict(colors=[color, "#E5E7EB"]),
                textinfo="none",
            )
        ]
    )

    fig.update_layout(
        height=300,
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
        margin=dict(l=10, r=10, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


# --------------------------------------------------------
# Performance Bar
# --------------------------------------------------------


def performance_chart(obtained, total, grade):

    color = grade_color(grade)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=["Obtained"],
            y=[obtained],
            marker_color=color,
            text=[obtained],
            textposition="outside",
        )
    )

    fig.add_trace(
        go.Bar(
            x=["Remaining"],
            y=[total - obtained],
            marker_color="#CBD5E1",
            text=[total - obtained],
            textposition="outside",
        )
    )

    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(range=[0, total], gridcolor="#E5E7EB"),
        xaxis=dict(showgrid=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


# --------------------------------------------------------
# Progress Ring
# --------------------------------------------------------


def progress_ring(percent):

    st.progress(percent / 100)

    st.caption(f"{percent:.2f}% Completed")

    # --------------------------------------------------------


# Report Card UI
# --------------------------------------------------------


def render_report_card(row, exercise, course):

    grade = str(row["Grade"])
    gradeClr = grade_color(grade)

    # =====================================================
    # STUDENT DETAILS
    # =====================================================

    left, right = st.columns([2.2, 1])

    with left:

        st.markdown(
            f"""
        <div class="card">

        <div class="student-name">
        {row['Name']}
        </div>

        <br>

        <div class="section-title">
        Student Information
        </div>

        """,
            unsafe_allow_html=True,
        )

        info1, info2 = st.columns(2)

        with info1:

            st.markdown(
                f"""
            <div class="label">Registration Number</div>
            <div class="value">{row['Registration Number']}</div>

            <div class="label">Username</div>
            <div class="value">{row['UserName']}</div>

            <div class="label">Email</div>
            <div class="value">{row['Email']}</div>
            """,
                unsafe_allow_html=True,
            )

        with info2:

            st.markdown(
                f"""
            <div class="label">Course</div>
            <div class="value">{course}</div>

            <div class="label">Exercise</div>
            <div class="value">{exercise}</div>

            <div class="label">Contact</div>
            <div class="value">{row['Contact Number']}</div>
            """,
                unsafe_allow_html=True,
            )

        if "Section" in row:

            st.markdown(
                f"""
            <div class="label">Section</div>
            <div class="value">{row['Section']}</div>
            """,
                unsafe_allow_html=True,
            )

        if "Standards" in row:

            st.markdown(
                f"""
            <div class="label">Standard</div>
            <div class="value">{row['Standards']}</div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown(
            f"""
        <div class="card" style="text-align:center;">

        <div class="section-title">
        Final Grade
        </div>

        <div style="
            font-size:72px;
            font-weight:800;
            color:{gradeClr};
            margin-top:25px;
            margin-bottom:25px;
        ">
        {grade}
        </div>

        <div style="
            background:{gradeClr};
            color:white;
            padding:12px;
            border-radius:12px;
            font-weight:700;
        ">
        {row['Percentage']:.2f}% Overall
        </div>

        </div>
        """,
            unsafe_allow_html=True,
        )

    st.write("")

    # =====================================================
    # KPI CARDS
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(
            f"""
        <div class="metric-card">

        <div class="metric-title">
        📈 Score
        </div>

        <div class="metric-value">
        {row['Marks Obtained']}
        </div>

        <div class="metric-sub">
        out of {row['Total Marks']}
        </div>

        </div>
        """,
            unsafe_allow_html=True,
        )

    with c2:

        st.markdown(
            f"""
        <div class="metric-card">

        <div class="metric-title">
        🏆 Rank
        </div>

        <div class="metric-value">
        #{row['Rank']}
        </div>

        <div class="metric-sub">
        Class Position
        </div>

        </div>
        """,
            unsafe_allow_html=True,
        )

    with c3:

        st.markdown(
            f"""
        <div class="metric-card">

        <div class="metric-title">
        🎯 Percentage
        </div>

        <div class="metric-value">
        {row['Percentage']:.1f}%
        </div>

        <div class="metric-sub">
        Performance
        </div>

        </div>
        """,
            unsafe_allow_html=True,
        )

    with c4:

        st.markdown(
            f"""
        <div class="metric-card">

        <div class="metric-title">
        🔁 Attempts
        </div>

        <div class="metric-value">
        {row['Total Attempts']}
        </div>

        <div class="metric-sub">
        Total Attempts
        </div>

        </div>
        """,
            unsafe_allow_html=True,
        )

    st.write("")

    # =====================================================
    # CHARTS
    # =====================================================

    chart1, chart2, chart3 = st.columns([1, 1, 1])

    with chart1:

        st.markdown(
            '<div class="card"><div class="section-title">Performance Gauge</div>',
            unsafe_allow_html=True,
        )

        st.plotly_chart(
            gauge_chart(row["Percentage"], row["Grade"]),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with chart2:

        st.markdown(
            '<div class="card"><div class="section-title">Marks Distribution</div>',
            unsafe_allow_html=True,
        )

        st.plotly_chart(
            donut_chart(row["Marks Obtained"], row["Total Marks"], row["Grade"]),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with chart3:

        st.markdown(
            '<div class="card"><div class="section-title">Score Breakdown</div>',
            unsafe_allow_html=True,
        )

        st.plotly_chart(
            performance_chart(row["Marks Obtained"], row["Total Marks"], row["Grade"]),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    progress_ring(row["Percentage"])


# ============================================================
# Render Report
# ============================================================

render_report_card(row, exercise, course)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# Download Section
# ============================================================

st.markdown(
    """
<div class="card">

<h3 style="
margin-bottom:15px;
font-weight:700;
color:#0F172A;
">
📄 Export Report Card
</h3>

<p style="
color:#64748B;
margin-bottom:20px;
">
Generate and download a professional PDF report card for this student.
</p>

</div>
""",
    unsafe_allow_html=True,
)

pdf_bytes = generate_pdf(row, exercise, course)

st.download_button(
    label="⬇ Download PDF Report Card",
    data=pdf_bytes,
    file_name=f"{row['Name'].replace(' ','_')}_ReportCard.pdf",
    mime="application/pdf",
    use_container_width=True,
)

st.write("")

# ============================================================
# Summary
# ============================================================

left, right = st.columns([2, 1])

with left:

    st.success(f"""
Student **{row['Name']}** scored **{row['Marks Obtained']} / {row['Total Marks']}**
with an overall percentage of **{row['Percentage']:.2f}%** and secured
**Rank #{row['Rank']}**.
""")

with right:

    st.metric("Overall Grade", row["Grade"])

st.write("")

# ============================================================
# Footer
# ============================================================

st.markdown(
    """

<hr style="margin-top:40px;margin-bottom:20px;">


""",
    unsafe_allow_html=True,
)
