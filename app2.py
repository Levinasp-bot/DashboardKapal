import os
import json
import streamlit as st
st.set_page_config(page_icon="🚢", layout="wide")
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from PIL import Image
import pandas as pd
from datetime import datetime, timedelta

# --- INISIALISASI FIREBASE ---
try:
    # Ambil kredensial dari secrets
    cred = credentials.Certificate(st.secrets["firebase_cred"])
    
    # Inisialisasi Firebase Admin jika belum terinisialisasi
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    # Inisialisasi Firestore
    db = firestore.client()
except Exception as e:
    st.error(f"Gagal menginisialisasi Firebase: {e}")

# --- STYLE DASHBOARD ---

st.markdown(
    """
    <style>
        .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    /* Hilangkan ruang header utama jika ada */
    header[data-testid="stHeader"] {
        height: 0rem !important;
        visibility: hidden;
    }

    /* Hapus margin atas dari elemen pertama */
    main > div:first-child, .main > div:first-child {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }
    
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
    menu_options = ["Input Kegiatan", "Input Biaya", "Input Pendapatan", "Dashboard Operasional Kapal", "Dashboard Pembiayaan"]

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

elif st.session_state.menu == "Input Biaya":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>Input Pembiayaan</h2>", unsafe_allow_html=True)
    st.write("Isi form berikut untuk mencatat pembiayaan:")

    try:
        kegiatan_docs = list(db.collection("kegiatan_operasional").stream())
        if not kegiatan_docs:
            st.warning("Belum ada data kegiatan operasional. Tambahkan dulu di halaman Input Kegiatan.")
            st.stop()

        kegiatan_list = [
            {
                "label": f"{doc.to_dict().get('ppk', '')} - {doc.to_dict().get('kapal', '')}",
                "ppk": doc.to_dict().get("ppk", ""),
                "kapal": doc.to_dict().get("kapal", "")
            }
            for doc in kegiatan_docs if "ppk" in doc.to_dict() and "kapal" in doc.to_dict()
        ]
    except Exception as e:
        st.error(f"Gagal mengambil data kegiatan operasional: {e}")
        st.stop()

    with st.form(key="input_pembiayaan"):
        selected_label = st.selectbox("Pilih PPK - Kapal", options=[k["label"] for k in kegiatan_list])
        selected_data = next(item for item in kegiatan_list if item["label"] == selected_label)

        # Jenis Jasa dan Tarif
        jenis_jasa_1 = st.text_input("Jenis Jasa 1")
        tarif_1 = st.number_input("Tarif 1 (Rp)", min_value=0.0, step=1000.0)
        jenis_jasa_2 = st.text_input("Jenis Jasa 2")
        tarif_2 = st.number_input("Tarif 2 (Rp)", min_value=0.0, step=1000.0)
        jenis_jasa_3 = st.text_input("Jenis Jasa 3")
        tarif_3 = st.number_input("Tarif 3 (Rp)", min_value=0.0, step=1000.0)
        jenis_jasa_4 = st.text_input("Jenis Jasa 4")
        tarif_4 = st.number_input("Tarif 4 (Rp)", min_value=0.0, step=1000.0)

        nota_keluar = st.text_input("Nota Keluar (isi 'ya' jika ada, kosongkan jika tidak)")
        pertanggungjawaban = st.text_input("Pertanggungjawaban (isi jika nota keluar)")

        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            # Proses validasi dan penyimpanan data
            if not jenis_jasa_1 or not tarif_1:
                st.error("Semua jenis jasa dan tarif wajib diisi.")
            else:
                data = {
                    'ppk': selected_data["ppk"],
                    'kapal': selected_data["kapal"],
                    'jenis_jasa_1': jenis_jasa_1,
                    'tarif_1': tarif_1,
                    'jenis_jasa_2': jenis_jasa_2,
                    'tarif_2': tarif_2,
                    'jenis_jasa_3': jenis_jasa_3,
                    'tarif_3': tarif_3,
                    'jenis_jasa_4': jenis_jasa_4,
                    'tarif_4': tarif_4,
                    'nota_keluar': nota_keluar,
                    'pertanggungjawaban': pertanggungjawaban,
                    'timestamp_created': datetime.now()
                }
                db.collection('pembiayaan').add(data)
                st.success("Data pembiayaan berhasil disimpan! ✅")

elif st.session_state.menu == "Input Pendapatan":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>Input Pendapatan</h2>", unsafe_allow_html=True)
    st.write("Isi form berikut untuk mencatat Pendapatan:")

    try:
        kegiatan_docs = list(db.collection("kegiatan_operasional").stream())
        if not kegiatan_docs:
            st.warning("Belum ada data kegiatan operasional. Tambahkan dulu di halaman Input Kegiatan.")
            st.stop()

        kegiatan_list = [
            {
                "label": f"{doc.to_dict().get('ppk', '')} - {doc.to_dict().get('kapal', '')}",
                "ppk": doc.to_dict().get("ppk", ""),
                "kapal": doc.to_dict().get("kapal", "")
            }
            for doc in kegiatan_docs if "ppk" in doc.to_dict() and "kapal" in doc.to_dict()
        ]
    except Exception as e:
        st.error(f"Gagal mengambil data kegiatan operasional: {e}")
        st.stop()

    with st.form(key="input_pendapatan"):
        selected_label = st.selectbox("Pilih PPK - Kapal", options=[k["label"] for k in kegiatan_list])
        selected_data = next(item for item in kegiatan_list if item["label"] == selected_label)

        # Input manual jenis jasa dan tarif
        jenis_jasa_1 = st.text_input("Jenis Jasa 1")
        tarif_1 = st.number_input("Tarif 1 (Rp)", min_value=0.0, step=1000.0)
        
        jenis_jasa_2 = st.text_input("Jenis Jasa 2")
        tarif_2 = st.number_input("Tarif 2 (Rp)", min_value=0.0, step=1000.0)
        
        jenis_jasa_3 = st.text_input("Jenis Jasa 3")
        tarif_3 = st.number_input("Tarif 3 (Rp)", min_value=0.0, step=1000.0)
        
        jenis_jasa_4 = st.text_input("Jenis Jasa 4")
        tarif_4 = st.number_input("Tarif 4 (Rp)", min_value=0.0, step=1000.0)

        # Menghitung pendapatan (produksi * tarif)
        produksi = st.number_input("Produksi", min_value=0, step=1)
        if produksi > 0:
            total_pendapatan = (produksi * tarif_1) + (produksi * tarif_2) + (produksi * tarif_3) + (produksi * tarif_4)
            st.write(f"Pendapatan Total: Rp {total_pendapatan:,.0f}")

        nota_keluar = st.text_input("Nota Keluar (isi 'ya' jika ada, kosongkan jika tidak)")
        pertanggungjawaban = st.text_input("Pertanggungjawaban (isi jika nota keluar)")

        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            if total_pendapatan > 0 and not nota_keluar:
                st.error("Nota harus keluar jika pendapatan sudah dikeluarkan.")
            elif nota_keluar and not pertanggungjawaban:
                st.warning("Pertanggungjawaban belum diisi meskipun nota sudah keluar.")
            else:
                data = {
                    'ppk': selected_data["ppk"],
                    'kapal': selected_data["kapal"],
                    'jenis_jasa_1': jenis_jasa_1,
                    'tarif_1': tarif_1,
                    'jenis_jasa_2': jenis_jasa_2,
                    'tarif_2': tarif_2,
                    'jenis_jasa_3': jenis_jasa_3,
                    'tarif_3': tarif_3,
                    'jenis_jasa_4': jenis_jasa_4,
                    'tarif_4': tarif_4,
                    'pendapatan': total_pendapatan,
                    'nota_keluar': nota_keluar,
                    'pertanggungjawaban': pertanggungjawaban,
                    'timestamp_created': datetime.now()
                }
                db.collection('pendapatan').add(data)
                st.success("Data pendapatan berhasil disimpan! ✅")

elif st.session_state.menu == "Dashboard Operasional Kapal":
    # Layout dua kolom: kiri 60%, kanan 40%
    left_col, right_col = st.columns([3.5, 2])

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
            .stDateInput {
                margin-bottom: -50px;
            }
            h4 {
                margin-bottom: 0.2rem;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

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
                        
                        # Mengonversi data ke format DataFrame untuk ditampilkan dengan st.dataframe
                        df_data = []
                        for row in items:
                            mulai = row.get("tanggal_mulai")
                            selesai = row.get("tanggal_selesai")
                            df_data.append({
                                "PPK": row.get("ppk", "-"),
                                "Nama Kapal": row.get("nama_kapal", "-"),
                                "Mulai": mulai.strftime("%d-%m-%Y %H:%M") if mulai else "-",
                                "Selesai": selesai.strftime("%d-%m-%Y %H:%M") if selesai else "Belum selesai"
                            })
                        
                        # Membuat DataFrame dan menampilkannya
                        df = pd.DataFrame(df_data)
                        st.dataframe(df, use_container_width=True)

            else:
                st.markdown("<br>", unsafe_allow_html=True)
                st.info("Belum ada data kegiatan.")
        except Exception as e:
            st.error(f"Gagal mengambil data kegiatan: {e}")


elif st.session_state.menu == "Dashboard Pembiayaan":
    st.markdown("<h4>Laporan Pembiayaan Kapal</h4>", unsafe_allow_html=True)
    
    # Default filter tanggal: awal dan akhir bulan ini
    today = datetime.now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month % 12 + 1, day=1) - timedelta(days=1))

    col1, col2 = st.columns(2)
    with col1:
        pembiayaan_mulai_filter = st.date_input("Mulai tanggal", value=first_day_of_month, key="pembiayaan_mulai")
    with col2:
        pembiayaan_selesai_filter = st.date_input("Sampai tanggal", value=last_day_of_month, key="pembiayaan_selesai")

    st.markdown("""
        <style>
        .stDateInput {
            margin-bottom: -50px;
        }
        h4 {
            margin-bottom: 0.2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    try:
        kegiatan_docs = db.collection("kegiatan_operasional") \
            .order_by("timestamp_created", direction=firestore.Query.DESCENDING).stream()

        pembiayaan_data = []
        for doc in kegiatan_docs:
            item = doc.to_dict()
            mulai = item.get("tanggal_mulai")
            if mulai and pembiayaan_mulai_filter <= mulai.date() <= pembiayaan_selesai_filter:
                pembiayaan_data.append({
                    "PPK": item.get("ppk", "-"),
                    "Nama Kapal": item.get("nama_kapal", "-"),
                    "Mulai": mulai.strftime("%d-%m-%Y %H:%M") if mulai else "-",
                    "Selesai": item.get("tanggal_selesai").strftime("%d-%m-%Y %H:%M") if item.get("tanggal_selesai") else "-",
                    "Produksi": item.get("produksi_ton", "-"),
                    "Pendapatan": item.get("pendapatan", "-"),
                    "Biaya": item.get("biaya", "-"),
                    "Nota": item.get("nota", "-"),
                    "Pertanggungjawaban": item.get("pertanggungjawaban", "-")
                })

        if pembiayaan_data:
            df = pd.DataFrame(pembiayaan_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Tidak ada data pembiayaan untuk rentang tanggal ini.")
    except Exception as e:
        st.error(f"Gagal memuat data pembiayaan: {e}")

    # PYMAD Section (judul placeholder)
    col_pendapatan, col_biaya = st.columns(2)
    with col_pendapatan:
        st.markdown("<h4>PYMAD Pendapatan</h4>", unsafe_allow_html=True)
        # Tabel pendapatan akan ditambahkan di sini nanti

    with col_biaya:
        st.markdown("<h4>PYMAD Biaya</h4>", unsafe_allow_html=True)
        # Tabel biaya akan ditambahkan di sini nanti