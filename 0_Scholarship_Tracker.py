import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json, os

# ================================
# ⚙️ PAGE CONFIG
# ================================
st.set_page_config(
    page_title="🎓 Scholarship Tracker",
    page_icon="🎓",
    layout="wide"
)

# ================================
# 💾 DATA STORAGE
# ================================
DATA_FILE = "data_scholarship.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "Nama User", "Negara", "Beasiswa", "Link Beasiswa",
            "IELTS", "GPA", "Other Requirements", "Benefit Scholarship",
            "Periode Pendaftaran (Dari)", "Periode Pendaftaran (Sampai)",
            "Deadline Dokumen", "Deadline Wawancara",
            "Deadline Tes 1", "Deadline Tes 2", "Tanggal Pengumuman"
        ])

def save_data(df):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

df = load_data()

# ================================
# 🎨 STYLING
# ================================
st.markdown("""
<style>
    body {
        background-color: #f7f9fc;
        font-family: "Poppins", sans-serif;
    }
    .stTextInput, .stTextArea, .stDateInput, .stSelectbox {
        border-radius: 8px !important;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 25px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #135a8d;
    }
    .dataframe td {
        white-space: normal !important;
        word-wrap: break-word !important;
        font-size: 13px !important;
    }
    table {
        border-collapse: collapse;
        border: 1px solid #ccc;
    }
    tr:nth-child(even) {background-color: #f9f9f9;}
    tr:hover {background-color: #eaf2f8;}
</style>
""", unsafe_allow_html=True)

# ================================
# 🎓 HEADER
# ================================
st.markdown("<h1 style='text-align:center;'>🎓 Scholarship Tracker 2.0</h1>", unsafe_allow_html=True)
st.caption("📍 Data tersimpan otomatis di file lokal (JSON) — tetap aman walau direfresh 🔒")
st.divider()

# ================================
# ➕ FORM INPUT
# ================================
st.subheader("➕ Tambahkan / Update Data Beasiswa")

with st.form("form_beasiswa", clear_on_submit=True):
    st.markdown("Masukkan detail lengkap beasiswa di bawah ini:")

    # Dropdown auto-fill
    user_list = df["Nama User"].dropna().unique().tolist()
    country_list = df["Negara"].dropna().unique().tolist()
    scholarship_list = df["Beasiswa"].dropna().unique().tolist()

    c1, c2, c3 = st.columns(3)
    nama_user = c1.selectbox("👤 Nama User", options=[""] + user_list, index=0)
    if not nama_user:
        nama_user = c1.text_input("Atau ketik User baru")

    negara = c2.selectbox("🌍 Negara Tujuan", options=[""] + country_list, index=0)
    if not negara:
        negara = c2.text_input("Atau ketik Negara baru")

    beasiswa = c3.selectbox("🎯 Nama Beasiswa", options=[""] + scholarship_list, index=0)
    if not beasiswa:
        beasiswa = c3.text_input("Atau ketik Beasiswa baru")

    link = st.text_input("🔗 Link Beasiswa")
    ielts, gpa = st.columns(2)
    ielts_val = ielts.text_input("📘 IELTS Requirement", placeholder="contoh: 6.5 overall")
    gpa_val = gpa.text_input("🎓 GPA Requirement", placeholder="contoh: 3.5 / 4.0")

    other = st.text_area("🧾 Other Requirements", height=100)
    benefit = st.text_area("💰 Benefit Scholarship", height=100)

    st.markdown("#### ⏰ Periode & Deadline Penting")
    d1, d2 = st.columns(2)
    periode_start = d1.date_input("📅 Periode Pendaftaran (Mulai)")
    periode_end = d2.date_input("📅 Periode Pendaftaran (Selesai)")

    d3, d4 = st.columns(2)
    dokumen = d3.date_input("📂 Deadline Dokumen", value=None)
    wawancara = d4.date_input("🎤 Deadline Wawancara", value=None)

    d5, d6, d7 = st.columns(3)
    tes1 = d5.date_input("📝 Deadline Tes 1", value=None)
    tes2 = d6.date_input("📝 Deadline Tes 2", value=None)
    pengumuman = d7.date_input("📢 Tanggal Pengumuman", value=None)

    submitted = st.form_submit_button("💾 Simpan Data Beasiswa")
    if submitted:
        if not nama_user or not beasiswa:
            st.warning("Isi minimal Nama User dan Nama Beasiswa!")
        else:
            new_row = {
                "Nama User": nama_user,
                "Negara": negara,
                "Beasiswa": beasiswa,
                "Link Beasiswa": link,
                "IELTS": ielts_val,
                "GPA": gpa_val,
                "Other Requirements": other,
                "Benefit Scholarship": benefit,
                "Periode Pendaftaran (Dari)": str(periode_start),
                "Periode Pendaftaran (Sampai)": str(periode_end),
                "Deadline Dokumen": str(dokumen) if dokumen else "",
                "Deadline Wawancara": str(wawancara) if wawancara else "",
                "Deadline Tes 1": str(tes1) if tes1 else "",
                "Deadline Tes 2": str(tes2) if tes2 else "",
                "Tanggal Pengumuman": str(pengumuman) if pengumuman else ""
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan!")
            st.rerun()

# ================================
# 🔍 FILTERING & VISUAL
# ================================
st.divider()
st.markdown("## 🔍 Filter & Statistik")

if not df.empty:
    c1, c2, c3 = st.columns(3)
    f_user = c1.selectbox("Filter User", options=["All"] + df["Nama User"].unique().tolist())
    f_negara = c2.selectbox("Filter Negara", options=["All"] + df["Negara"].unique().tolist())
    f_beasiswa = c3.selectbox("Filter Beasiswa", options=["All"] + df["Beasiswa"].unique().tolist())

    df_filtered = df.copy()
    if f_user != "All":
        df_filtered = df_filtered[df_filtered["Nama User"] == f_user]
    if f_negara != "All":
        df_filtered = df_filtered[df_filtered["Negara"] == f_negara]
    if f_beasiswa != "All":
        df_filtered = df_filtered[df_filtered["Beasiswa"] == f_beasiswa]

    if df_filtered.empty:
        st.warning("Tidak ada data sesuai filter.")
    else:
        col1, col2 = st.columns(2)
        fig1 = px.bar(df_filtered.groupby("Negara").size().reset_index(name="Jumlah"),
                      x="Negara", y="Jumlah", text_auto=True, title="🌍 Beasiswa per Negara")
        col1.plotly_chart(fig1, use_container_width=True)

        fig2 = px.pie(df_filtered, names="Nama User", title="👥 Distribusi per User")
        col2.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Belum ada data untuk ditampilkan.")

# ================================
# 📋 DATABASE TABEL
# ================================
st.divider()
st.markdown("## 📋 Database Beasiswa (Editable + Text Wrap)")

if not df.empty:
    st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="db_table"
    )
else:
    st.info("Belum ada data yang bisa ditampilkan.")

st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Scholarship Tracker 2.0 | Local JSON Persistent")
