import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from PIL import Image

# --- SETUP FIREBASE ---
if not firebase_admin._apps:
    cred = credentials.Certificate('dashboard-monitoring-kapal-firebase-adminsdk-fbsvc-4dcc10b399.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- STYLE DASHBOARD ---
st.set_page_config(page_title="Monitoring Kegiatan Kapal", page_icon="🚢", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: white;
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
        padding: 0px 0 0px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR ---
with st.sidebar:
    # Logo
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    logo = Image.open("assets\Logo_PLMT_c.png")
    st.image(logo, width=150)
    st.markdown('</div>', unsafe_allow_html=True)

    # Inisialisasi menu jika belum ada
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

# --- WARNA TEMA UTAMA ---
PRIMARY_COLOR = "#0066cc"  # Biru Pelindo

# Remove the header line below to avoid the extra title
# st.header(st.session_state.menu)

if st.session_state.menu == "Input Kegiatan":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>Input Kegiatan Operasional Kapal</h2>", unsafe_allow_html=True)
    st.write("Isi form berikut untuk mencatat kegiatan kapal:")

    # FORM INPUT
    with st.form("input_kegiatan"):
        ppk = st.text_input("PPK")
        nama_kapal = st.text_input("Nama Kapal")
        tanggal_mulai = datetime.now()

        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            if ppk and nama_kapal:
                # Simpan ke Firestore
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
