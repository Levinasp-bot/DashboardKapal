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
    /* Ukuran sidebar */
    section[data-testid="stSidebar"] {
        width: 200px !important;
    }
    div[data-testid="stSidebarContent"] {
        width: 100% !important;
        padding: 0 10px;
    }

    /* Logo container */
    .logo-container {
        text-align: center;
        padding: 10px 0;
    }

    /* Tombol sidebar seragam */
    div[data-testid="stSidebar"] button {
        width: 100% !important;
        background-color: white !important;
        color: #0066cc !important;
        border: 2px solid #0066cc !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        padding: 12px 16px !important;
        margin-top: 10px !important;
        transition: all 0.3s ease;
        text-align: center !important;
    }

    /* Hover efek */
    div[data-testid="stSidebar"] button:hover {
        background-color: #e6f0ff !important;
        color: #0066cc !important;
        border: 2px solid #0066cc !important;
    }

    /* Tombol aktif */
    div[data-testid="stSidebar"] button:focus {
        background-color: #0066cc !important;
        color: white !important;
        border: 2px solid #0066cc !important;
    }
.kegiatan-header, .kegiatan-row {
        display: flex;
        border: 1px solid #cccccc;
    }
    .kegiatan-cell {
        flex: 1;
        padding: 8px;
        border-right: 1px solid #cccccc;
    }
    .kegiatan-cell:last-child {
        border-right: none;
    }
    .kegiatan-header {
        background-color: #f0f2f6;
        font-weight: bold;
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
        logo = Image.open("assets/Logo_PLMT_c.png")
        st.image(logo, width=150)
    except Exception as e:
        st.warning("Logo tidak ditemukan.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Inisialisasi menu
    if "menu" not in st.session_state:
        st.session_state.menu = "Input Kegiatan"

    # Tombol navigasi
    menu_options = ["Input Kegiatan", "Input Pembiayaan", "Dashboard Laporan"]

    for option in menu_options:
        active = st.session_state.menu == option
        button_id = option.replace(" ", "_")

        button_style = f"""
            <style>
            div[data-testid="stSidebar"] div[data-testid="stButton"] > button#{button_id} {{
                background-color: {"#0066cc" if active else "white"};
                color: {"white" if active else "#0066cc"};
                border: 2px solid #0066cc;
                border-radius: 12px;
                width: 100%;
                padding: 12px 16px;
                margin-top: 10px;
                font-weight: bold;
            }}
            div[data-testid="stSidebar"] div[data-testid="stButton"] > button#{button_id}:hover {{
                background-color: #e6f0ff;
                color: #0066cc;
            }}
            </style>
        """
        st.markdown(button_style, unsafe_allow_html=True)
        if st.button(option, key=button_id):
            st.session_state.menu = option

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
        st.markdown("<h4>Kegiatan Operasional Kapal</h4>", unsafe_allow_html=True)
        # Filter rentang tanggal
        today = datetime.now().date()
        col1, col2 = st.columns(2)
        with col1:
            tanggal_mulai_filter = st.date_input("Mulai tanggal", value=today, key="filter_mulai")
        with col2:
            tanggal_selesai_filter = st.date_input("Sampai tanggal", value=today, key="filter_selesai")

        st.markdown("""
        <style>
        .kegiatan-header, .kegiatan-row {
            display: flex;
            border: 1px solid #cccccc;
        }
        .kegiatan-cell {
            flex: 1;
            padding: 8px;
            border-right: 1px solid #cccccc;
        }
        .kegiatan-cell:last-child {
            border-right: none;
        }
        .kegiatan-header {
            background-color: #f0f2f6;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

        try:
            kegiatan_docs = db.collection("kegiatan_operasional") \
                              .order_by("timestamp_created", direction=firestore.Query.DESCENDING).stream()

            kegiatan_data = []
            for doc in kegiatan_docs:
                item = doc.to_dict()
                item["doc_id"] = doc.id
                mulai = item.get("tanggal_mulai")
                if mulai and tanggal_mulai_filter <= mulai.date() <= tanggal_selesai_filter:
                    kegiatan_data.append(item)


            if kegiatan_data:
                # Kelompokkan berdasarkan terminal dan dermaga
                grouped = {}
                for item in kegiatan_data:
                    terminal = item.get("terminal", "Tidak Diketahui")
                    dermaga = item.get("dermaga", "Tidak Diketahui")
                    grouped.setdefault(terminal, {}).setdefault(dermaga, []).append(item)

                # Tampilkan data
                for terminal, dermaga_data in grouped.items():
                    st.markdown(f"<h5 style='margin-top: 20px;'>{terminal}</h5>", unsafe_allow_html=True)
                    for dermaga, items in dermaga_data.items():
                        st.markdown(f"**Dermaga {dermaga}**")

                        # Header tabel manual
                        header_cols = st.columns([1.5, 2, 2, 2])
                        with header_cols[0]: st.markdown("**PPK**")
                        with header_cols[1]: st.markdown("**Nama Kapal**")
                        with header_cols[2]: st.markdown("**Mulai**")
                        with header_cols[3]: st.markdown("**Selesai**")

                        for idx, row in enumerate(items):
                            mulai = row.get("tanggal_mulai")
                            selesai = row.get("tanggal_selesai")
                            doc_id = row.get("doc_id")

                            # Baris data
                            cols = st.columns([1.5, 2, 2, 2])
                            with cols[0]:
                                st.write(row.get("ppk", "-"))
                            with cols[1]:
                                st.write(row.get("nama_kapal", "-"))
                            with cols[2]:
                                st.write(mulai.strftime("%d-%m-%Y %H:%M") if mulai else "-")
                            with cols[3]:
                                if selesai:
                                    st.write(selesai.strftime("%d-%m-%Y %H:%M"))
                                else:
                                    unique_key = f"selesai_{terminal}_{dermaga}_{idx}"
                                    if st.button("Tandai Selesai", key=unique_key):
                                        db.collection("kegiatan_operasional").document(doc_id).update({
                                            "tanggal_selesai": datetime.now()
                                        })
                                        st.rerun()
            else:
                st.info("Belum ada data kegiatan.")
        except Exception as e:
            st.error(f"Gagal mengambil data kegiatan: {e}")
