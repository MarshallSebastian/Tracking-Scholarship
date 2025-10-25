import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import json, os

# ================================
# ⚙️ PAGE CONFIG
# ================================
st.set_page_config(page_title="🎓 Scholarship Tracker 3.1", page_icon="🎓", layout="wide")

# ================================
# 💾 PERSISTENT DATA
# ================================
DATA_FILE = "data_scholarship.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "Nama User", "Negara", "Beasiswa", "Link Beasiswa", "IELTS", "GPA",
            "Other Requirements", "Benefit Scholarship",
            "Periode Pendaftaran (Mulai)", "Periode Pendaftaran (Selesai)",
            "Periode Dokumen (Mulai)", "Periode Dokumen (Selesai)",
            "Periode Wawancara (Mulai)", "Periode Wawancara (Selesai)",
            "Periode Tes (Mulai)", "Periode Tes (Selesai)",
            "Tanggal Pengumuman"
        ])

def save_data(df):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

df = load_data()

# Tambah kolom jika belum ada
required_columns = [
    "Nama User", "Negara", "Beasiswa", "Link Beasiswa", "IELTS", "GPA",
    "Other Requirements", "Benefit Scholarship",
    "Periode Pendaftaran (Mulai)", "Periode Pendaftaran (Selesai)",
    "Periode Dokumen (Mulai)", "Periode Dokumen (Selesai)",
    "Periode Wawancara (Mulai)", "Periode Wawancara (Selesai)",
    "Periode Tes (Mulai)", "Periode Tes (Selesai)", "Tanggal Pengumuman"
]
for col in required_columns:
    if col not in df.columns:
        df[col] = ""

# ================================
# 🎨 STYLING
# ================================
st.markdown("""
<style>
    body {
        background-color: #f8fafc;
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
    table.dataframe {
        border-collapse: collapse;
        border: 1px solid #ddd;
        width: 100%;
    }
    .dataframe th {
        background-color: #1f77b4;
        color: white;
        padding: 8px;
        text-align: center;
    }
    .dataframe td {
        padding: 6px;
        font-size: 13px;
        vertical-align: top;
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    tr:nth-child(even) {background-color: #f9f9f9;}
    tr:hover {background-color: #eaf2f8;}
</style>
""", unsafe_allow_html=True)

# ================================
# 🎓 HEADER
# ================================
st.markdown("<h1 style='text-align:center;'>🎓 Scholarship Tracker 3.1</h1>", unsafe_allow_html=True)
st.caption("📍 Data tersimpan otomatis secara lokal (JSON) — tetap aman walau direfresh 🔒")
st.divider()

# ================================
# ➕ FORM INPUT
# ================================
st.subheader("➕ Tambahkan / Update Data Beasiswa")

with st.form("form_beasiswa", clear_on_submit=True):
    st.markdown("Masukkan detail lengkap beasiswa di bawah ini:")

    c1, c2 = st.columns(2)
    nama_user = c1.text_input("👤 Nama User")
    negara = c2.text_input("🌍 Negara Tujuan")
    beasiswa = c1.text_input("🎯 Nama Beasiswa")
    link = c2.text_input("🔗 Link Beasiswa (optional)")
    ielts = c1.text_input("📘 IELTS Requirement", placeholder="contoh: 6.5 overall")
    gpa = c2.text_input("🎓 GPA Requirement", placeholder="contoh: 3.5 / 4.0")
    other = st.text_area("🧾 Other Requirements", height=100)
    benefit = st.text_area("💰 Benefit Scholarship", height=100)

    st.markdown("#### ⏰ Periode & Deadline Penting")

    def optional_date(label):
        """Biarkan kosong kalau tidak diisi"""
        try:
            return st.date_input(label, value=None, key=label)
        except Exception:
            return None

    st.markdown("**🗓️ Pendaftaran**")
    p1, p2 = st.columns(2)
    start_reg = optional_date("Mulai Pendaftaran")
    end_reg = optional_date("Selesai Pendaftaran")

    st.markdown("**📂 Dokumen**")
    d1, d2 = st.columns(2)
    start_doc = optional_date("Mulai Pengumpulan Dokumen")
    end_doc = optional_date("Selesai Pengumpulan Dokumen")

    st.markdown("**🎤 Wawancara**")
    w1, w2 = st.columns(2)
    start_interview = optional_date("Mulai Wawancara")
    end_interview = optional_date("Selesai Wawancara")

    st.markdown("**🧪 Tes Beasiswa**")
    t1, t2 = st.columns(2)
    start_test = optional_date("Mulai Tes")
    end_test = optional_date("Selesai Tes")

    pengumuman = optional_date("📢 Tanggal Pengumuman")

    submitted = st.form_submit_button("💾 Simpan Data Beasiswa")

    if submitted:
        if not nama_user or not beasiswa:
            st.warning("⚠️ Isi minimal Nama User dan Nama Beasiswa!")
        else:
            new_row = {
                "Nama User": nama_user,
                "Negara": negara,
                "Beasiswa": beasiswa,
                "Link Beasiswa": link,
                "IELTS": ielts,
                "GPA": gpa,
                "Other Requirements": other,
                "Benefit Scholarship": benefit,
                "Periode Pendaftaran (Mulai)": str(start_reg) if start_reg else "",
                "Periode Pendaftaran (Selesai)": str(end_reg) if end_reg else "",
                "Periode Dokumen (Mulai)": str(start_doc) if start_doc else "",
                "Periode Dokumen (Selesai)": str(end_doc) if end_doc else "",
                "Periode Wawancara (Mulai)": str(start_interview) if start_interview else "",
                "Periode Wawancara (Selesai)": str(end_interview) if end_interview else "",
                "Periode Tes (Mulai)": str(start_test) if start_test else "",
                "Periode Tes (Selesai)": str(end_test) if end_test else "",
                "Tanggal Pengumuman": str(pengumuman) if pengumuman else ""
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan!")
            st.rerun()

# ================================
# 🔔 REMINDER (30 Hari)
# ================================
st.divider()
st.markdown("## 🔔 Reminder Beasiswa yang Akan Tutup dalam 30 Hari")

if not df.empty:
    today = date.today()
    df["Periode Pendaftaran (Selesai)"] = pd.to_datetime(df["Periode Pendaftaran (Selesai)"], errors="coerce").dt.date
    df["Days Left"] = (df["Periode Pendaftaran (Selesai)"] - today).apply(lambda x: x.days if pd.notnull(x) else None)
    soon = df[df["Days Left"].between(0, 30, inclusive="both")]

    if not soon.empty:
        st.success(f"🎯 Ada {len(soon)} beasiswa yang akan tutup dalam 30 hari!")
        soon_display = soon.copy()
        soon_display["Link Beasiswa"] = soon_display["Link Beasiswa"].apply(
            lambda x: f"[Klik di sini]({x})" if x else "-"
        )
        st.markdown(soon_display[["Nama User", "Beasiswa", "Negara", "Periode Pendaftaran (Selesai)", "Days Left", "Link Beasiswa"]].to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.info("✅ Tidak ada beasiswa yang akan tutup dalam 30 hari.")
else:
    st.info("Belum ada data untuk reminder.")

# ================================
# 📊 GANTT CHART (Filter Negara & User)
# ================================
st.divider()
st.markdown("## 🗓️ Timeline Gantt Chart")

if not df.empty:
    col1, col2 = st.columns(2)
    selected_user = col1.selectbox("👤 Pilih User", sorted(df["Nama User"].dropna().unique()))
    selected_country = col2.selectbox("🌍 Pilih Negara", sorted(df["Negara"].dropna().unique()))
    df_filtered = df[(df["Negara"] == selected_country) & (df["Nama User"] == selected_user)]

    if not df_filtered.empty:
        events = []
        for _, row in df_filtered.iterrows():
            for phase, start_col, end_col in [
                ("Pendaftaran", "Periode Pendaftaran (Mulai)", "Periode Pendaftaran (Selesai)"),
                ("Dokumen", "Periode Dokumen (Mulai)", "Periode Dokumen (Selesai)"),
                ("Wawancara", "Periode Wawancara (Mulai)", "Periode Wawancara (Selesai)"),
                ("Tes", "Periode Tes (Mulai)", "Periode Tes (Selesai)"),
                ("Pengumuman", "Tanggal Pengumuman", "Tanggal Pengumuman")
            ]:
                if row[start_col] and row[end_col]:
                    events.append({
                        "Beasiswa": row["Beasiswa"],
                        "Tahapan": phase,
                        "Mulai": pd.to_datetime(row[start_col]),
                        "Selesai": pd.to_datetime(row[end_col])
                    })
        gantt_df = pd.DataFrame(events)
        if not gantt_df.empty:
            fig = px.timeline(
                gantt_df, x_start="Mulai", x_end="Selesai", y="Beasiswa",
                color="Tahapan", title=f"📅 Timeline {selected_user} - {selected_country}",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data periode lengkap untuk Gantt Chart.")
    else:
        st.warning("Tidak ada data sesuai filter user & negara.")
else:
    st.info("Belum ada data yang bisa ditampilkan.")

# ================================
# 📋 DATABASE TABEL CANTIK
# ================================
st.divider()
st.markdown("## 📋 Database Beasiswa (Clickable Links)")

if not df.empty:
    df_display = df.copy()
    df_display["Link Beasiswa"] = df_display["Link Beasiswa"].apply(lambda x: f"[🌐 Buka Link]({x})" if x else "-")
    st.markdown(df_display.to_markdown(index=False), unsafe_allow_html=True)
else:
    st.info("Belum ada data yang bisa ditampilkan.")

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Scholarship Tracker 3.1 | Streamlit + JSON Persistent")
