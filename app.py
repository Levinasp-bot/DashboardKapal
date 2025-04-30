import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from PIL import Image

# --- SETUP FIREBASE (support lokal dan cloud) ---
try:
    firebase_json = st.secrets["firebase_cred"]
    cred_dict = json.loads(firebase_json)
    cred = credentials.Certificate(cred_dict)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    st.error(f"Gagal menginisialisasi Firebase: {e}")

db = firestore.client()

# --- STYLE DASHBOARD ---
st.set_page_config(page_icon="🚢", layout="wide")

st.markdown(
    """
    <style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f7f7f7;
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

    /* Button */
    button[kind="primary"] {
        background-color: #0066cc !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }

    button[kind="primary"]:hover {
        background-color: #005bb5 !important;
        color: white !important;
    }

    /* Input fields (text/number/etc.) */
    .stTextInput > div > input,
    .stNumberInput > div > input {
        border: 1px solid #0066cc;
        border-radius: 5px;
    }

    .stTextInput > div > input:focus,
    .stNumberInput > div > input:focus {
        border: 2px solid #0066cc;
        box-shadow: 0 0 0 0.2rem rgba(0,102,204,.25);
        outline: none;
    }

    /* Headings */
    h2 {
        color: #0066cc;
    }

    /* Other tweaks */
    .stButton>button {
        background-color: #0066cc;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }

    .stButton>button:hover {
        background-color: #005bb5;
        color: white;
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
    menu_options = ["Input Kegiatan", "Input Pembiayaan", "Dashboard Laporan"]

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

    with st.form(key="input_kegiatan"):  # key pada form
        ppk = st.text_input("PPK")
        nama_kapal = st.text_input("Nama Kapal")
        produksi_ton = st.number_input("Produksi (Ton)", min_value=0.0, step=0.1)  # <-- inputan produksi
        terminal = st.selectbox("Terminal", ["Terminal Nilam", "Terminal Mirah"])
        dermaga = st.selectbox("Dermaga", ["1", "2", "3"])  # Dummy dermaga
        
        submit_button = st.form_submit_button(label="Submit")  # Tidak perlu key di sini

        if submit_button:
            if ppk and nama_kapal:
                data = {
                    'ppk': ppk,
                    'nama_kapal': nama_kapal,
                    'produksi_ton': produksi_ton,
                    'terminal': terminal,
                    'dermaga': dermaga,
                    'tanggal_mulai': datetime.now(),
                    'timestamp_created': datetime.now()
                }
                db.collection('kegiatan_operasional').add(data)
                st.success("Data kegiatan kapal berhasil disimpan! ✅")
            else:
                st.error("Mohon isi semua field sebelum submit.")

elif st.session_state.menu == "Input Pembiayaan":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>Input Pembiayaan</h2>", unsafe_allow_html=True)

elif st.session_state.menu == "Dashboard Laporan":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>Dashboard Laporan</h2>", unsafe_allow_html=True)

    # Layout dua kolom: kiri 60%, kanan 40%
    left_col, right_col = st.columns([3, 2])

    with right_col:
        st.subheader("📋 Laporan Kegiatan (Terbaru)")

        try:
            kegiatan_docs = db.collection("kegiatan_operasional") \
                              .order_by("timestamp_created", direction=firestore.Query.DESCENDING).stream()

            kegiatan_data = [doc.to_dict() for doc in kegiatan_docs]

            if kegiatan_data:
                # Kelompokkan berdasarkan terminal -> dermaga
                grouped = {}
                for item in kegiatan_data:
                    terminal = item.get("terminal", "Tidak Diketahui")
                    dermaga = item.get("dermaga", "Tidak Diketahui")
                    grouped.setdefault(terminal, {}).setdefault(dermaga, []).append(item)

                # Tampilkan per kelompok
                for terminal, dermaga_data in grouped.items():
                    st.markdown(f"### Terminal {terminal}")
                    for dermaga, items in dermaga_data.items():
                        st.markdown(f"**Dermaga {dermaga}**")

                        # Siapkan data untuk tabel
                        table_rows = []
                        for row in items:
                            mulai = row.get("tanggal_mulai")
                            selesai = row.get("tanggal_selesai", None)
                            table_rows.append({
                                "PPK": row.get("ppk", "-"),
                                "Nama Kapal": row.get("nama_kapal", "-"),
                                "Mulai": mulai.strftime("%d-%m-%Y %H:%M") if mulai else "-",
                                "Selesai": selesai.strftime("%d-%m-%Y %H:%M") if selesai else "—"
                            })
                        st.dataframe(table_rows, use_container_width=True)
            else:
                st.info("Belum ada data kegiatan.")

        except Exception as e:
            st.error(f"Gagal mengambil data kegiatan: {e}")
