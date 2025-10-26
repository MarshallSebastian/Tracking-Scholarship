import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import json, os, shutil

# ======================================
# ⚙️ PAGE CONFIG
# ======================================
st.set_page_config(page_title="🎓 Scholarship Tracker 5.0", page_icon="🎓", layout="wide")

# ======================================
# 💾 FILE CONFIG
# ======================================
SCHOLAR_FILE = "data_scholarship.json"
PROGRESS_FILE = "data_progress.json"

def get_empty_scholar_df():
    return pd.DataFrame(columns=[
        "Nama User", "Negara", "Beasiswa", "Link Beasiswa", "IELTS", "GPA",
        "Other Requirements", "Benefit Scholarship",
        "Periode Pendaftaran (Mulai)", "Periode Pendaftaran (Selesai)",
        "Periode Dokumen (Mulai)", "Periode Dokumen (Selesai)",
        "Periode Wawancara (Mulai)", "Periode Wawancara (Selesai)",
        "Periode Tes (Mulai)", "Periode Tes (Selesai)",
        "Tanggal Pengumuman"
    ])

def get_empty_progress_df():
    return pd.DataFrame(columns=[
        "Nama User", "Beasiswa", "Status Pendaftaran", "Status Dokumen",
        "Status Wawancara", "Status Tes", "Status Pengumuman", "Catatan", "Terakhir Diperbarui"
    ])

def load_json(file, empty_func):
    if not os.path.exists(file):
        return empty_func()
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return pd.DataFrame(data)
    except Exception:
        shutil.copy(file, file + "_backup.json")
        return empty_func()

def save_json(df, file):
    df = df.fillna("")
    with open(file, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

df_scholar = load_json(SCHOLAR_FILE, get_empty_scholar_df)
df_progress = load_json(PROGRESS_FILE, get_empty_progress_df)

# ======================================
# 🎨 DARK ELEGANT CSS
# ======================================
st.markdown("""
<style>
body { background-color: #0e1117; color: #e0e6ed; font-family: 'Poppins', sans-serif; }
h1, h2, h3 { color: #4db8ff; text-align: center; font-weight: 700; }
div[data-testid="stForm"] {
    background: #1a1d25; padding: 25px 35px; border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5); border: 1px solid #2c2f36;
}
input, textarea, select {
    background-color: #2b2f3a !important; color: #f0f3f8 !important;
    border: 1px solid #3b4252 !important; border-radius: 6px;
}
.stButton>button {
    background: linear-gradient(90deg, #007acc, #1f77b4); color: white; font-weight: 600;
    border-radius: 8px; padding: 10px 25px; width: 100%; transition: all 0.3s ease;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #0095ff, #2da9e3); transform: scale(1.02);
}
.data-table {
    width: 100%; border-collapse: collapse; border-radius: 10px;
    overflow: hidden; font-size: 14px; background: #1a1d25;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.data-table th {
    background: #1f4e79; color: #e0f0ff; padding: 10px 12px;
    text-align: left; font-weight: 600;
}
.data-table td {
    padding: 10px 12px; border-bottom: 1px solid #2c2f36; color: #e3e9f0;
}
.data-table tr:nth-child(even) { background-color: #222733; }
.data-table tr:hover { background-color: #2d3242; transition: 0.3s ease; }
</style>
""", unsafe_allow_html=True)

# ======================================
# 🎓 HEADER
# ======================================
st.markdown("<h1>🎓 Scholarship Tracker 5.0</h1>", unsafe_allow_html=True)
st.caption("🌙 Dark Elegant Edition | Beasiswa + Progress Tracker | Dibuat oleh Yan Marcel Sebastian")

# ======================================
# 🧾 FORM INPUT DATA BEASISWA
# ======================================
st.divider()
st.subheader("📘 Tambahkan Data Beasiswa")

with st.form("form_beasiswa", clear_on_submit=True):
    c1, c2 = st.columns(2)
    nama_user = c1.text_input("👤 Nama User")
    negara = c2.text_input("🌍 Negara Tujuan")
    beasiswa = c1.text_input("🎯 Nama Beasiswa")
    link = c2.text_input("🔗 Link Beasiswa")
    ielts = c1.text_input("📘 IELTS Requirement")
    gpa = c2.text_input("🎓 GPA Requirement")

    st.markdown("#### 🧾 Detail Tambahan")
    other = st.text_area("Other Requirements", height=100)
    benefit = st.text_area("Benefit Scholarship", height=100)

    st.markdown("#### ⏰ Timeline Beasiswa")
    def opt_date(label): return st.date_input(label, value=None, key=label)
    p1, p2 = st.columns(2)
    start_reg, end_reg = opt_date("Mulai Pendaftaran"), opt_date("Selesai Pendaftaran")
    d1, d2 = st.columns(2)
    start_doc, end_doc = opt_date("Mulai Dokumen"), opt_date("Selesai Dokumen")
    w1, w2 = st.columns(2)
    start_int, end_int = opt_date("Mulai Wawancara"), opt_date("Selesai Wawancara")
    t1, t2 = st.columns(2)
    start_test, end_test = opt_date("Mulai Tes"), opt_date("Selesai Tes")
    pengumuman = opt_date("Tanggal Pengumuman")

    if st.form_submit_button("💾 Simpan Data Beasiswa"):
        if not nama_user or not beasiswa:
            st.warning("⚠️ Isi minimal Nama User dan Nama Beasiswa!")
        else:
            new_row = {
                "Nama User": nama_user, "Negara": negara, "Beasiswa": beasiswa,
                "Link Beasiswa": link, "IELTS": ielts, "GPA": gpa,
                "Other Requirements": other, "Benefit Scholarship": benefit,
                "Periode Pendaftaran (Mulai)": str(start_reg),
                "Periode Pendaftaran (Selesai)": str(end_reg),
                "Periode Dokumen (Mulai)": str(start_doc),
                "Periode Dokumen (Selesai)": str(end_doc),
                "Periode Wawancara (Mulai)": str(start_int),
                "Periode Wawancara (Selesai)": str(end_int),
                "Periode Tes (Mulai)": str(start_test),
                "Periode Tes (Selesai)": str(end_test),
                "Tanggal Pengumuman": str(pengumuman)
            }
            df_scholar = pd.concat([df_scholar, pd.DataFrame([new_row])], ignore_index=True)
            save_json(df_scholar, SCHOLAR_FILE)
            st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan!")
            st.rerun()

# ======================================
# 🧩 FORM INPUT PROGRESS
# ======================================
st.divider()
st.subheader("🚀 Tambahkan Progress Beasiswa")

with st.form("form_progress", clear_on_submit=True):
    nama_user = st.text_input("👤 Nama User")
    beasiswa = st.selectbox("🎓 Pilih Beasiswa", [""] + df_scholar["Beasiswa"].unique().tolist())
    c1, c2, c3 = st.columns(3)
    status_pendaftaran = c1.selectbox("📨 Pendaftaran", ["Belum", "Proses", "Selesai"])
    status_dokumen = c2.selectbox("📂 Dokumen", ["Belum", "Proses", "Selesai"])
    status_interview = c3.selectbox("🎤 Wawancara", ["Belum", "Proses", "Selesai"])
    c4, c5 = st.columns(2)
    status_tes = c4.selectbox("🧪 Tes", ["Belum", "Proses", "Selesai"])
    status_pengumuman = c5.selectbox("📢 Pengumuman", ["Belum", "Proses", "Selesai"])
    catatan = st.text_area("🧾 Catatan Tambahan")
    
    if st.form_submit_button("💾 Simpan Progress"):
        if not nama_user or not beasiswa:
            st.warning("⚠️ Lengkapi Nama User dan Pilih Beasiswa!")
        else:
            new_progress = {
                "Nama User": nama_user,
                "Beasiswa": beasiswa,
                "Status Pendaftaran": status_pendaftaran,
                "Status Dokumen": status_dokumen,
                "Status Wawancara": status_interview,
                "Status Tes": status_tes,
                "Status Pengumuman": status_pengumuman,
                "Catatan": catatan,
                "Terakhir Diperbarui": str(date.today())
            }
            df_progress = pd.concat([df_progress, pd.DataFrame([new_progress])], ignore_index=True)
            save_json(df_progress, PROGRESS_FILE)
            st.success(f"✅ Progress '{beasiswa}' berhasil disimpan!")
            st.rerun()

# ======================================
# 📋 DATA TABLES
# ======================================
st.divider()
st.markdown("## 📊 Data Beasiswa dan Progress")

if not df_scholar.empty:
    df_scholar_show = df_scholar.copy()
    df_scholar_show["Link Beasiswa"] = df_scholar_show["Link Beasiswa"].apply(
        lambda x: f'<a href="{x}" target="_blank" style="color:#4db8ff;">🌐 Buka</a>' if x else "-"
    )
    st.markdown("### 🎯 Data Beasiswa")
    st.markdown(df_scholar_show.to_html(escape=False, index=False, classes="data-table"), unsafe_allow_html=True)
else:
    st.info("Belum ada data beasiswa.")

if not df_progress.empty:
    st.markdown("### 🚀 Data Progress Beasiswa")
    st.markdown(df_progress.to_html(escape=False, index=False, classes="data-table"), unsafe_allow_html=True)
else:
    st.info("Belum ada data progress.")

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Scholarship Tracker 5.0 | Beasiswa + Progress Tracker 🎓")
