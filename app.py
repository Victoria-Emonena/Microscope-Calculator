"""
app.py — Microscope Specimen Size Calculator
A production-ready Streamlit application for CSC 442 Project 1.
"""

import os
import sys
import streamlit as st
from PIL import Image

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from database.db import init_db, save_user, save_calculation, get_all_calculations, delete_calculation, delete_all_calculations
from modules.calculator import (
    MICROSCOPE_TYPES, UNIT_LABELS, calculate_real_size,
    format_scientific, build_explanation,
)
from utils.helpers import save_uploaded_image, records_to_csv, validate_username, validate_measured_size

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_ttl="Microscope Size Calculator",
    iconPage="🔬",
    layout_size="wide",
    starting_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 600;
        background: linear-gradient(135deg, #2196F3, #00BCD4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.4rem;
    }
    .subtitle {font-size: 1rem; color: #90CAF9; margin-bottom: 1.5rem;}
    .result-card {
        background: linear-gradient(135deg, #00BCD4 , #0D47A1);
        border-radius: 11px;#1565C0
        padding: 1.4rem;
        margin: 1.1rem 0;
        border: 2px solid #1976D2;
    }
    .result-number {
        font-size: 2.7rem;
        font-weight: 600;
        color: #64B5F6;
    }
    .step-box {
        background: #1565C0;
        border-left: 5px solid #2196F3;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        margin: 0.6rem 0;
    }
    .stat-card {
        background: #3E2723;
        border-radius: 6px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid #2D3250;
    }
    .warning-box {
        background: #1E2130;
        border: 1px solid #FF8F00;
        border-radius: 6px;
        padding: 0.6rem;
        color: #FFD54F;
    }
</style>
""", unsafe_allow_html=True)

# ── Initialise DB ────────────────────────────────────────────────────────────
init_db()

# ── Session state defaults ────────────────────────────────────────────────────
if "username" not in st.session_state:
    st.session_state.username = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## MicroCalc")
    st.markdown("---")

    # Username
    st.markdown("### 👤 User Login")
    username_type = st.text_input(
        "Enter your username",
        value=st.session_state.username,
        placeholder="e.g. john_doe",
        key="username_field",
    )
    if st.button("Set Username", use_container_width=True):
        valid, err = validate_username(username_type)
        if valid:
            st.session_state.username = username_type.strip()
            save_user(st.session_state.username)
            st.success(f"Welcome, **{st.session_state.username}**!")
        else:
            st.error(err)

    if st.session_state.username:
        st.info(f"Logged in as: **{st.session_state.username}**")

    st.markdown("---")
    st.markdown("### Navigation")
    page = st.radio(
        "Go to",
        ["🧮 Calculator", " History & Records"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### Microscope Reference")
    for mtype, mag in MICROSCOPE_TYPES.items():
        st.markdown(f"- **{mtype}**: {mag}×")

if page == " Calculator":
    st.markdown('<div class="main-title"> Microscope Specimen Size Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">CSC 442 — Computational Biology | 400 Level</div>', unsafe_allow_html=True)

    if not st.session_state.username:
        st.markdown('<div class="warning-box"> Please enter your username in the sidebar before performing a calculation.</div>', unsafe_allow_html=True)
        st.stop()

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("#### Upload Specimen Image")
        uploaded_file = st.file_uploader(
            "Select an image of the specimen",
            type=["jpg", "jpeg", "png"],
            help="Upload a JPG or PNG image of the microscope specimen.",
        )

        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, caption=f"Specimen: {uploaded_file.name}", use_container_width=True)

        st.markdown("#### Calculation Inputs")
        microscope_type = st.selectbox(
            "Microscope Type",
            options=list(MICROSCOPE_TYPES.keys()),
            help="Select the type of microscope used.",
        )
        mag_factor = MICROSCOPE_TYPES[microscope_type]
        st.caption(f"Magnification factor: **{mag_factor}×**")

        col_size, col_unit = st.columns([2, 1])
        with col_size:
            measured_size_str = st.text_input(
                "Measured Size",
                value="",
                placeholder="e.g. 5.0",
            )
        with col_unit:
            input_unit = st.selectbox("Input Unit", UNIT_LABELS, index=2)

        output_unit = st.selectbox("Output Unit", UNIT_LABELS, index=1)

        calc_button = st.button("🔭 Calculate Real Size", use_container_width=True, type="primary")

    with col_right:
        st.markdown("#### Results")

        if calc_button:
            valid_size, size_err = validate_measured_size(measured_size_str)
            if not valid_size:
                st.error(size_err)
            else:
                measured_size = float(measured_size_str)
                with st.spinner("Calculating..."):
                    result = calculate_real_size(measured_size, microscope_type, input_unit, output_unit)

                # Save to DB
                image_filename = ""
                if uploaded_file:
                    uploaded_file.seek(0)
                    image_filename = save_uploaded_image(uploaded_file, UPLOAD_DIR)

                save_calculation(
                    username=st.session_state.username,
                    image_filename=image_filename,
                    microscope_type=microscope_type,
                    magnification_factor=mag_factor,
                    measured_size=measured_size,
                    real_size=result["real_size"],
                    input_unit=input_unit,
                    output_unit=output_unit,
                )

                st.session_state.last_result = result
                st.success("Calculation saved to database!")

        if st.session_state.last_result:
            r = st.session_state.last_result
            st.markdown(f"""
            <div class="result-card">
                <div style="color:#90CAF9; font-size:0.9rem; margin-bottom:0.3rem;">REAL SPECIMEN SIZE</div>
                <div class="result-number">{format_scientific(r['real_size'])} {r['output_unit']}</div>
                <div style="color:#BBB; font-size:0.85rem; margin-top:0.5rem;">
                    Measured: {format_scientific(r['measured_size'])} {r['input_unit']} &nbsp;|&nbsp;
                    Microscope: {r['microscope_type']} ({r['magnification']}×)
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### Step-by-Step Breakdown")
            steps = build_explanation(r)
            for step in steps:
                st.markdown(f'<div class="step-box">{step}</div>', unsafe_allow_html=True)

            with st.expander(" Summary Table"):
                st.table({
                    "Field": ["Microscope Type", "Magnification Factor", "Measured Size", "Measured Size (mm)", "Real Size (mm)", "Real Size (output unit)"],
                    "Value": [
                        r["microscope_type"],
                        f"{r['magnification']}×",
                        f"{r['measured_size']} {r['input_unit']}",
                        format_scientific(r["measured_size_mm"]),
                        format_scientific(r["real_size_mm"]),
                        f"{format_scientific(r['real_size'])} {r['output_unit']}",
                    ],
                })
        else:
            st.info("Fill in the form and click **Calculate Real Size** to see results here.")

# ── History page ─────────────────────────────────────────────────────────────
elif page == " History & Records":
    st.markdown('<div class="main-title"> Calculation History</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">View, search, and manage saved calculation records.</div>', unsafe_allow_html=True)

    col_search, col_actions = st.columns([3, 1])
    with col_search:
        search_query = st.text_input(" Search records", placeholder="Search by username, microscope type, or filename...")
    with col_actions:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(" Clear All Records", use_container_width=True):
            delete_all_calculations()
            st.success("All records deleted.")
            st.rerun()

    records = get_all_calculations(search=search_query)

    if not records:
        st.info("No records found.")
    else:
        # Stats row
        total = len(records)
        users = len(set(r["username"] for r in records))
        scope = [r["real_size"] for r in records]
        avg_size = sum(scope) / len(scope) if scope else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-card"><div style="font-size:2rem;font-weight:800;color:#64B5F6">{total}</div><div>Total Calculations</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div style="font-size:2rem;font-weight:800;color:#81C784">{users}</div><div>Unique Users</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div style="font-size:2rem;font-weight:800;color:#FFB74D">{format_scientific(avg_size)}</div><div>Avg Real Size</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # Export CSV
        csv_data = records_to_csv(records)
        st.download_button(
            " Export as CSV",
            data=csv_data,
            file_name="microscope_calculations.csv",
            mime="text/csv",
        )

        st.markdown(f"**{total} record(s) found**")
        st.markdown("")

        for rec in records:
            with st.expander(f"#{rec['id']} | {rec['username']} — {rec['microscope_type']} — {rec['timestamp'][:19]}"):
                cols = st.columns([2, 2, 1])
                with cols[0]:
                    st.markdown(f"**Username:** {rec['username']}")
                    st.markdown(f"**Microscope:** {rec['microscope_type']} ({rec['magnification_factor']}×)")
                    st.markdown(f"**Measured Size:** {format_scientific(rec['measured_size'])} {rec['input_unit']}")
                with cols[1]:
                    st.markdown(f"**Real Size:** {format_scientific(rec['real_size'])} {rec['output_unit']}")
                    st.markdown(f"**Image:** {rec['image_filename'] or 'N/A'}")
                    st.markdown(f"**Timestamp:** {rec['timestamp'][:19]}")
                with cols[2]:
                    if st.button(" Delete", key=f"del_{rec['id']}"):
                        delete_calculation(rec["id"])
                        st.success("Record deleted.")
                        st.rerun()
