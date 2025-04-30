import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from PIL import Image

# --- SETUP FIREBASE (support lokal dan cloud) ---
firebase_json = st.secrets["firebase_cred"]
cred_dict = json.loads(firebase_json)

# Inisialisasi Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- STYLE DASHBOARD ---
st.set_page_config(page_icon="🚢", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #f7f7f7;  /* Abu-abu sangat muda */
        padding: 0 10px;
    }

    .sidebar-btn {
        background-color: white;
        color: #0066cc;
        font-weight: bold;
        border: 2px solid #0066cc;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 10px auto;
        width: 90%;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .sidebar-btn:hover {
        background-color: #e6f0ff;
    }

    .sidebar-btn.active {
        background-color: #0066cc;
        color: white;
    }

    .logo-container {
        text-align: center;
        padding: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR ---
with st.sidebar:
    # Logo
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        logo = Image.open("assets/Logo_PLMT_c.png")  # Gunakan "/" bukan "\"
        st.image(logo, width=150)
    except Exception as e:
        st.warning("Logo tidak ditemukan.")  # Supaya tidak crash kalau logo tidak ada
    st.markdown('</div>', unsafe_allow_html=True)

    # Inisialisasi menu
    if "menu" not in st.session_state:
        st.session_state.menu = "Input Kegiatan"

    # Tombol navigasi
    menu_options = ["Input Kegiatan", "Input Pembiayaan", "Laporan Kegiatan", "Laporan Pembiayaan"]

    for option in menu_options:
        active = "active" if st.session_state.menu == option else ""
        st.markdown(
            f"""
            <div class="sidebar-btn {active}" onclick="window.parent.postMessage({{type: 'streamlit:setSessionState', key: 'menu', value: '{option}' }}, '*')">
                {option}
            </div>
            """, unsafe_allow_html=True
        )

PRIMARY_COLOR = "#0066cc" 

if st.session_state.menu == "Input Kegiatan":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>Input Kegiatan Operasional Kapal</h2>", unsafe_allow_html=True)
    st.write("Isi form berikut untuk mencatat kegiatan kapal:")

    with st.form("input_kegiatan"):
        ppk = st.text_input("PPK")
        nama_kapal = st.text_input("Nama Kapal")
        tanggal_mulai = datetime.now()

        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            if ppk and nama_kapal:
                data = {
                    'ppk': ppk,
                    'nama_kapal': nama_kapal,
                    'tanggal_mulai': tanggal_mulai,
                    'timestamp_created': datetime.now()
                }
                db.collection('kegiatan_operasional').add(data)
                st.success("Data kegiatan kapal berhasil disimpan! ✅")
            else:
                st.error("Mohon isi semua field sebelum submit.")

elif st.session_state.menu == "Input Pembiayaan":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>Input Pembiayaan</h2>", unsafe_allow_html=True)

elif st.session_state.menu == "Laporan Kegiatan":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>Laporan Kegiatan</h2>", unsafe_allow_html=True)

elif st.session_state.menu == "Laporan Pembiayaan":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>Laporan Pembiayaan</h2>", unsafe_allow_html=True)