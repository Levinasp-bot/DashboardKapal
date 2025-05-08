import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from PIL import Image
import pandas as pd
from datetime import datetime, timedelta

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

st.set_page_config(page_icon="🚢", layout="wide")

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

with st.sidebar:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        logo = Image.open("assets/Logo_PLMT_c.png")
        st.image(logo, width=150)
    except Exception as e:
        st.warning("Logo tidak ditemukan.")
    st.markdown('</div>', unsafe_allow_html=True)

    if "menu" not in st.session_state:
        st.session_state.menu = "Input Kegiatan"

    menu_options = ["Input Kegiatan", "Input Pembiayaan", "Input Pendapatan", "Dashboard Operasional Kapal", "Dashboard Pendapatan & Biaya"]

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

    dermaga_map = {
        "Terminal Mirah": ["Selatan (324)", "Timur (320)", "Kade Intan (100)", "Benoa Kade (75)"],
        "Terminal Nilam Timur": ["Sisi Selatan (250)", "Sisi Utara (280)", "Bogasari (160)", "Pinda Asen (120)"],
        "Terminal Nilam Utara": ["Sisi Dalam (66)", "Sisi Luar (156)"]
    }

    terminal = st.selectbox("Terminal", list(dermaga_map.keys()), key="terminal_selected")

    dermaga_options = dermaga_map.get(terminal, [])

    with st.form(key="input_kegiatan"):
        dermaga = st.selectbox("Dermaga", dermaga_options, key="dermaga_selected")
        ppk = st.text_input("PPK")
        nama_kapal = st.text_input("Nama Kapal")
        produksi_ton = st.number_input("Produksi (Ton)", min_value=0.0, step=0.1)
        
        submit_button = st.form_submit_button(label="Submit")

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
    st.write("Isi form berikut untuk mencatat pembiayaan:")

    try:
        kegiatan_docs = list(
            db.collection("kegiatan_operasional")
            .where("tanggal_selesai", "!=", None)
            .stream()
        )

        # Filter hanya yang belum punya field tarif_1 (pembiayaan)
        ppk_list = []
        for doc in kegiatan_docs:
            data = doc.to_dict()
            if "ppk" in data and "tarif_1" not in data:
                ppk_list.append({
                    "label": data.get("ppk", ""),
                    "ppk": data.get("ppk", ""),
                    "nama_kapal": data.get("nama_kapal", ""),
                    "produksi_ton": data.get("produksi_ton", 0),
                    "doc_id": doc.id
                })

        if not ppk_list:
            st.warning("Tidak ada PPK yang memenuhi kriteria (selesai dan belum punya data pembiayaan).")
            st.stop()
        else:
            st.warning(f"⚠️ {len(ppk_list)} kapal belum diinput pembiayaannya!!!")

    except Exception as e:
        st.error(f"Gagal mengambil data kegiatan operasional: {e}")
        st.stop()

    selected_label = st.selectbox("Pilih PPK", options=[k["label"] for k in ppk_list])
    selected_data = next(item for item in ppk_list if item["label"] == selected_label)

    st.write(f"**Nama Kapal:** {selected_data['nama_kapal']}")
    st.write(f"**Produksi:** {selected_data['produksi_ton']}")

    with st.form(key="input_pembiayaan"):
        st.markdown("### Jenis Jasa dan Tarif")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            jenis_jasa_1 = st.text_input("Jenis Jasa 1")
            tarif_1 = st.number_input("Tarif 1", min_value=0.0, step=1000.0)
        with col2:
            jenis_jasa_2 = st.text_input("Jenis Jasa 2")
            tarif_2 = st.number_input("Tarif 2", min_value=0.0, step=1000.0)
        with col3:
            jenis_jasa_3 = st.text_input("Jenis Jasa 3")
            tarif_3 = st.number_input("Tarif 3", min_value=0.0, step=1000.0)
        with col4:
            jenis_jasa_4 = st.text_input("Jenis Jasa 4")
            tarif_4 = st.number_input("Tarif 4", min_value=0.0, step=1000.0)

        nota_keluar_value = "belum"
        pertanggungjawaban_value = "belum"

        submit_button = st.form_submit_button(label="Submit")
        total_tarif = (tarif_1 or 0) + (tarif_2 or 0) + (tarif_3 or 0) + (tarif_4 or 0)
        biaya = total_tarif * selected_data["produksi_ton"]

        if submit_button:
            try:
                data_update = {
                    'jenis_jasa_1': jenis_jasa_1,
                    'tarif_1': tarif_1,
                    'jenis_jasa_2': jenis_jasa_2,
                    'tarif_2': tarif_2,
                    'jenis_jasa_3': jenis_jasa_3,
                    'tarif_3': tarif_3,
                    'jenis_jasa_4': jenis_jasa_4,
                    'tarif_4': tarif_4,
                    'biaya': biaya,
                    'nota': nota_keluar_value,
                    'pertanggungjawaban': pertanggungjawaban_value,
                    'timestamp_pembiayaan': datetime.now()
                }

                doc_ref = db.collection("kegiatan_operasional").document(selected_data["doc_id"])
                doc_ref.update(data_update)
                st.success("Data pembiayaan berhasil diperbarui ✅")

            except Exception as e:
                st.error(f"Gagal menyimpan data: {e}")

elif st.session_state.menu == "Input Pendapatan":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>Input Pendapatan</h2>", unsafe_allow_html=True)
    st.write("Isi form berikut untuk mencatat pendapatan:")

    try:
        kegiatan_docs = list(
            db.collection("kegiatan_operasional")
            .where("tanggal_selesai", "!=", None)  # hanya yang selesai-nya tidak null
            .stream()
        )

        # Filter hanya yang belum punya field tarif_1_pendapatan
        ppk_list = []
        for doc in kegiatan_docs:
            data = doc.to_dict()
            if "ppk" in data and "tarif_1_pendapatan" not in data:
                ppk_list.append({
                    "label": data.get("ppk", ""),
                    "ppk": data.get("ppk", ""),
                    "nama_kapal": data.get("nama_kapal", ""),
                    "produksi_ton": data.get("produksi_ton", 0),
                    "doc_id": doc.id
                })

        if not ppk_list:
            st.warning("Tidak ada PPK yang memenuhi kriteria (selesai dan belum punya data pendapatan).")
            st.stop()
        else:
            st.warning(f"⚠️ {len(ppk_list)} kapal belum di input pendapatannya!!!")


    except Exception as e:
        st.error(f"Gagal mengambil data kegiatan operasional: {e}")
        st.stop()

    selected_label = st.selectbox("Pilih PPK", options=[k["label"] for k in ppk_list])
    selected_data = next(item for item in ppk_list if item["label"] == selected_label)

    st.write(f"**Nama Kapal:** {selected_data['nama_kapal']}")
    st.write(f"**Produksi:** {selected_data['produksi_ton']}")
        
    with st.form(key="input_pendapatan"):
        st.markdown("### Jenis Jasa dan Tarif")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            jenis_jasa_1 = st.text_input("Jenis Jasa 1")
            tarif_1 = st.number_input("Tarif 1", min_value=0.0, step=1000.0)
        with col2:
            jenis_jasa_2 = st.text_input("Jenis Jasa 2")
            tarif_2 = st.number_input("Tarif 2", min_value=0.0, step=1000.0)
        with col3:
            jenis_jasa_3 = st.text_input("Jenis Jasa 3")
            tarif_3 = st.number_input("Tarif 3", min_value=0.0, step=1000.0)
        with col4:
            jenis_jasa_4 = st.text_input("Jenis Jasa 4")
            tarif_4 = st.number_input("Tarif 4", min_value=0.0, step=1000.0)

        submit_button = st.form_submit_button(label="Submit")
        total_tarif = (tarif_1 or 0) + (tarif_2 or 0) + (tarif_3 or 0) + (tarif_4 or 0)
        pendapatan = total_tarif * selected_data["produksi_ton"]

        if submit_button:
            try:
                data_update = {
                    'jenis_jasa_1_pendapatan': jenis_jasa_1,
                    'tarif_1_pendapatan': tarif_1,
                    'jenis_jasa_2_pendapatan': jenis_jasa_2,
                    'tarif_2_pendapatan': tarif_2,
                    'jenis_jasa_3_pendapatan': jenis_jasa_3,
                    'tarif_3_pendapatan': tarif_3,
                    'jenis_jasa_4_pendapatan': jenis_jasa_4,
                    'tarif_4_pendapatan': tarif_4,
                    'nota': 'belum',
                    'pendapatan': pendapatan,
                    'pertanggung_jawaban': 'belum',
                    'timestamp_pendapatan': datetime.now()
                }

                doc_ref = db.collection("kegiatan_operasional").document(selected_data["doc_id"])
                doc_ref.update(data_update)
                st.success("Data pendapatan berhasil diperbarui ✅")

            except Exception as e:
                st.error(f"Gagal menyimpan data: {e}")

elif st.session_state.menu == "Dashboard Operasional Kapal":
    left_col, right_col = st.columns([3.2, 2])

    with left_col:
        st.markdown("""
            <div style="border: 2px solid black; height: 500px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                Layout Dermaga Akan Tampil Disini
            </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("<h4>Kegiatan Operasional Kapal</h4>", unsafe_allow_html=True)
        
        today = datetime.now().date()
        col1, col2 = st.columns(2)
        with col1:
            tanggal_mulai_filter = st.date_input("Mulai tanggal", value=today, key="filter_mulai")
        with col2:
            tanggal_selesai_filter = st.date_input("Sampai tanggal", value=today, key="filter_selesai")

        st.markdown("""
        <style>
        div[data-testid="stDateInput"] {
            margin-bottom: -40px;
                    }
        .kegiatan-header, .kegiatan-row {
            display: flex;
            border: 1px solid #cccccc;
        }
        .kegiatan-cell {
            flex: 1;
            padding: 4px;  /* Mengurangi padding */
            border-right: 1px solid #cccccc;
        }
        .kegiatan-cell:last-child {
            border-right: none;
        }
        .kegiatan-header {
            background-color: #f0f2f6;
            font-weight: bold;
        }
        .stButton>button {
            font-size: 12px;  /* Ukuran tombol yang lebih kecil */
            padding: 4px 8px;  /* Mengurangi padding tombol */
        }
        .stColumn {
            padding-left: 0rem;  /* Mengurangi padding kiri kolom */
            padding-right: 0rem;  /* Mengurangi padding kanan kolom */
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
                if mulai and tanggal_mulai_filter <= mulai.date() <= tanggal_selesai_filter and item.get("tanggal_selesai") is None:
                    kegiatan_data.append(item)

            if kegiatan_data:
                grouped = {}
                for item in kegiatan_data:
                    terminal = item.get("terminal", "Tidak Diketahui")
                    dermaga = item.get("dermaga", "Tidak Diketahui")
                    grouped.setdefault(terminal, {}).setdefault(dermaga, []).append(item)

                for terminal, dermaga_data in grouped.items():
                    st.markdown(f"<h5 style='margin-top: 20px;'>{terminal}</h5>", unsafe_allow_html=True)
                    for dermaga, items in dermaga_data.items():
                        st.markdown(f"**Dermaga {dermaga}**")

                        header_cols = st.columns([1.5, 2, 2, 2])
                        with header_cols[0]: st.markdown("**PPK**")
                        with header_cols[1]: st.markdown("**Nama Kapal**")
                        with header_cols[2]: st.markdown("**Mulai**")
                        with header_cols[3]: st.markdown("**Selesai**")

                        for idx, row in enumerate(items):
                            mulai = row.get("tanggal_mulai")
                            selesai = row.get("tanggal_selesai")
                            doc_id = row.get("doc_id")

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

elif st.session_state.menu == "Dashboard Pendapatan & Biaya":
    st.markdown("<h4>Laporan Pendapatan & Biaya Kapal</h4>", unsafe_allow_html=True)

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
        pymad_auto_data = []

        first_day_last_month = (first_day_of_month - timedelta(days=1)).replace(day=1)
        last_day_last_month = first_day_of_month - timedelta(days=1)

        for doc in kegiatan_docs:
            item = doc.to_dict()
            doc_id = doc.id
            mulai = item.get("tanggal_mulai")
            selesai = item.get("tanggal_selesai")
            nota = str(item.get("nota", "")).lower()

            if mulai and selesai and pembiayaan_mulai_filter <= mulai.date() <= pembiayaan_selesai_filter:
                pembiayaan_data.append({
                    "doc_id": doc_id,
                    "PPK": item.get("ppk", "-"),
                    "Nama Kapal": item.get("nama_kapal", "-"),
                    "Mulai": mulai.strftime("%d-%m-%Y %H:%M") if mulai else "-",
                    "Selesai": selesai.strftime("%d-%m-%Y %H:%M") if selesai else "-",
                    "Produksi": item.get("produksi_ton", "-"),
                    "Pendapatan": item.get("pendapatan", "-"),
                    "Biaya": item.get("biaya", "-"),
                    "Nota": item.get("nota", "-"),
                    "Pertanggungjawaban": item.get("pertanggungjawaban", "-")
                })

            if mulai and selesai and first_day_last_month <= mulai.date() <= last_day_last_month and nota != "done":
                pymad_auto_data.append({
                    "PPK": item.get("ppk", "-"),
                    "Nama Kapal": item.get("nama_kapal", "-"),
                    "Mulai": mulai.strftime("%d-%m-%Y %H:%M") if mulai else "-",
                    "Selesai": selesai.strftime("%d-%m-%Y %H:%M") if selesai else "-",
                    "Pendapatan": item.get("pendapatan", "-"),
                    "Biaya": item.get("biaya", "-")
                })

        if pembiayaan_data:
            st.markdown("### Data Pembiayaan")
            for i, row in enumerate(pembiayaan_data):
                with st.expander(f"{row['PPK']} - {row['Nama Kapal']}"):
                    st.write(f"**Mulai:** {row['Mulai']}")
                    st.write(f"**Selesai:** {row['Selesai']}")
                    st.write(f"**Produksi:** {row['Produksi']}")
                    st.write(f"**Pendapatan:** {row['Pendapatan']}")
                    st.write(f"**Biaya:** {row['Biaya']}")

                    nota_key = f"nota_{i}"
                    ptj_key = f"ptj_{i}"
                    nota_default = row["Nota"].lower() == "done"
                    ptj_default = row["Pertanggungjawaban"].lower() == "done"

                    nota_checked = st.checkbox("Nota", value=nota_default, key=nota_key)
                    ptj_checked = st.checkbox("Pertanggungjawaban", value=ptj_default, key=ptj_key)

                    # Update ke Firestore jika checkbox berubah dan belum "done"
                    if nota_checked and row["Nota"].lower() != "done":
                        db.collection("kegiatan_operasional").document(row["doc_id"]).update({"nota": "done"})
                        st.success("✅ Nota diperbarui menjadi 'done'")

                    if ptj_checked and row["Pertanggungjawaban"].lower() != "done":
                        db.collection("kegiatan_operasional").document(row["doc_id"]).update({"pertanggungjawaban": "done"})
                        st.success("✅ Pertanggungjawaban diperbarui menjadi 'done'")

        else:
            st.info("Tidak ada data pembiayaan untuk rentang tanggal ini.")

        col_pendapatan, col_biaya = st.columns(2)

        with col_pendapatan:
            st.markdown("<h4>PYMAD</h4>", unsafe_allow_html=True)
            if pymad_auto_data:
                df_pendapatan = pd.DataFrame(pymad_auto_data)[["PPK", "Nama Kapal", "Pendapatan"]]
                st.dataframe(df_pendapatan, use_container_width=True)
            else:
                st.info("Tidak ada data PYMAD.")

        with col_biaya:
            st.markdown("<h4>BYMAD</h4>", unsafe_allow_html=True)
            if pymad_auto_data:
                df_biaya = pd.DataFrame(pymad_auto_data)[["PPK", "Nama Kapal", "Biaya"]]
                st.dataframe(df_biaya, use_container_width=True)
            else:
                st.info("Tidak ada data BYMAD.")

    except Exception as e:
        st.error(f"Gagal memuat data pembiayaan: {e}")
