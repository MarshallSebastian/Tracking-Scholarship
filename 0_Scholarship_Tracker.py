import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import json, os, shutil

# ================================
# ⚙️ PAGE CONFIG
# ================================
st.set_page_config(page_title="🎓 Scholarship Tracker 4.2", page_icon="🎓", layout="wide")

# ================================
# 💾 DATA HANDLING
# ================================
DATA_FILE = "data_scholarship.json"
BACKUP_FILE = "data_scholarship_backup.json"

def get_empty_df():
    return pd.DataFrame(columns=[
        "Nama User", "Negara", "Beasiswa", "Link Beasiswa", "IELTS", "GPA",
        "Other Requirements", "Benefit Scholarship",
        "Periode Pendaftaran (Mulai)", "Periode Pendaftaran (Selesai)",
        "Periode Dokumen (Mulai)", "Periode Dokumen (Selesai)",
        "Periode Wawancara (Mulai)", "Periode Wawancara (Selesai)",
        "Periode Tes (Mulai)", "Periode Tes (Selesai)", "Tanggal Pengumuman"
    ])

def load_data():
    if not os.path.exists(DATA_FILE):
        return get_empty_df()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return get_empty_df()
            return pd.DataFrame(json.loads(content))
    except json.JSONDecodeError:
        shutil.copy(DATA_FILE, BACKUP_FILE)
        st.warning("⚠️ File JSON rusak. Backup disimpan dan file baru dibuat.")
        return get_empty_df()

def convert_dates_to_str(df):
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x.isoformat() if isinstance(x, (date, datetime)) else x)
    return df

def save_data(df):
    df = convert_dates_to_str(df)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

df = load_data()
for c in get_empty_df().columns:
    if c not in df.columns:
        df[c] = ""

# ================================
# 🎨 DARK ELEGANT CSS
# ================================
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #e0e6ed;
    font-family: 'Poppins', sans-serif;
}

/* HEADER */
h1, h2, h3 {
    color: #4db8ff;
    text-align: center;
    font-weight: 700;
}

/* SUBHEADER & CAPTION */
h2, h3 {
    color: #c7d5e0;
}
p, label, span, div {
    color: #d1d5db !important;
}

/* FORM CARD */
div[data-testid="stForm"] {
    background: #1a1d25;
    padding: 25px 35px;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    border: 1px solid #2c2f36;
}

/* INPUTS */
input, textarea, select {
    background-color: #2b2f3a !important;
    color: #f0f3f8 !important;
    border: 1px solid #3b4252 !important;
    border-radius: 6px;
}
input::placeholder, textarea::placeholder {
    color: #9ca3af !important;
}

/* BUTTONS */
.stButton>button {
    background: linear-gradient(90deg, #007acc, #1f77b4);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 10px 25px;
    width: 100%;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #0095ff, #2da9e3);
    transform: scale(1.02);
}

/* TABLE */
.data-table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 10px;
    overflow: hidden;
    font-size: 14px;
    background: #1a1d25;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.data-table th {
    background: #1f4e79;
    color: #e0f0ff;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
}
.data-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #2c2f36;
    color: #e3e9f0;
}
.data-table tr:nth-child(even) {
    background-color: #222733;
}
.data-table tr:hover {
    background-color: #2d3242;
    transition: 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# ================================
# 🎓 HEADER
# ================================
st.markdown("<h1>🎓 Scholarship Tracker 4.2</h1>", unsafe_allow_html=True)
st.caption("🌙 Dark Elegant Edition | Smart Reminder | Filter | Gantt Chart | Dibuat oleh Yan Marcel Sebastian")

# ================================
# 🔍 FILTER SECTION
# ================================
if not df.empty:
    st.subheader("🔍 Filter Data Beasiswa")
    colf1, colf2, colf3 = st.columns(3)

    user_filter = colf1.selectbox("Filter berdasarkan User", ["Semua"] + sorted(df["Nama User"].dropna().unique().tolist()))
    country_filter = colf2.selectbox("Filter berdasarkan Negara", ["Semua"] + sorted(df["Negara"].dropna().unique().tolist()))

    today = date.today()
    df["Deadline Date"] = pd.to_datetime(df["Periode Pendaftaran (Selesai)"], errors="coerce").dt.date
    df["Days Left"] = (df["Deadline Date"] - today).apply(lambda x: x.days if pd.notnull(x) else None)
    df["Status"] = df["Days Left"].apply(
        lambda x: "🟢 Masih Dibuka" if x and x > 15 else "🟡 Segera Tutup" if x and 0 <= x <= 15 else "🔴 Selesai"
    )

    status_filter = colf3.selectbox("Filter berdasarkan Status", ["Semua", "🟢 Masih Dibuka", "🟡 Segera Tutup", "🔴 Selesai"])

    df_filtered = df.copy()
    if user_filter != "Semua":
        df_filtered = df_filtered[df_filtered["Nama User"] == user_filter]
    if country_filter != "Semua":
        df_filtered = df_filtered[df_filtered["Negara"] == country_filter]
    if status_filter != "Semua":
        df_filtered = df_filtered[df_filtered["Status"] == status_filter]
else:
    df_filtered = df

# ================================
# 🧾 FORM INPUT (TOGGLE)
# ================================
if "show_form" not in st.session_state:
    st.session_state.show_form = False

if st.button("➕ Tambah Beasiswa Baru"):
    st.session_state.show_form = not st.session_state.show_form

if st.session_state.show_form:
    with st.form("form_beasiswa", clear_on_submit=True):
        st.subheader("📝 Tambahkan Data Beasiswa Baru")

        c1, c2 = st.columns(2)
        nama_user = c1.text_input("👤 Nama User")
        negara = c2.text_input("🌍 Negara Tujuan")
        beasiswa = c1.text_input("🎯 Nama Beasiswa")
        link = c2.text_input("🔗 Link Beasiswa (optional)")
        ielts = c1.text_input("📘 IELTS Requirement")
        gpa = c2.text_input("🎓 GPA Requirement")
        other = st.text_area("🧾 Other Requirements", height=100)
        benefit = st.text_area("💰 Benefit Scholarship", height=100)

        st.markdown("#### ⏰ Periode & Deadline Penting")
        def opt_date(label): return st.date_input(label, value=None, key=label)

        p1, p2 = st.columns(2)
        start_reg, end_reg = opt_date("Mulai Pendaftaran"), opt_date("Selesai Pendaftaran")
        d1, d2 = st.columns(2)
        start_doc, end_doc = opt_date("Mulai Pengumpulan Dokumen"), opt_date("Selesai Pengumpulan Dokumen")
        w1, w2 = st.columns(2)
        start_int, end_int = opt_date("Mulai Wawancara"), opt_date("Selesai Wawancara")
        t1, t2 = st.columns(2)
        start_test, end_test = opt_date("Mulai Tes"), opt_date("Selesai Tes")
        pengumuman = opt_date("📢 Tanggal Pengumuman")

        if st.form_submit_button("💾 Simpan Beasiswa"):
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
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan!")
                st.rerun()

# ================================
# 📊 REMINDER CHART
# ================================
st.divider()
st.markdown("## ⏰ Reminder Beasiswa (30 Hari ke Depan)")

if not df_filtered.empty:
    upcoming = df_filtered[df_filtered["Days Left"].between(0, 30, inclusive="both")]
    if not upcoming.empty:
        df_chart = upcoming.groupby("Beasiswa", as_index=False)["Days Left"].mean()
        fig = px.bar(df_chart, x="Beasiswa", y="Days Left", text_auto=True,
                     title="📆 Sisa Waktu Pendaftaran (Hari)",
                     color="Days Left", color_continuous_scale="tealrose")
        fig.update_layout(showlegend=False, yaxis_title="Hari", xaxis_title="Beasiswa",
                          paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                          font_color="#e0e6ed", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("✅ Tidak ada beasiswa yang akan tutup dalam 30 hari.")
else:
    st.info("Belum ada data untuk reminder.")

# ================================
# 📅 GANTT CHART
# ================================
st.divider()
st.markdown("## 🗓️ Timeline (Gantt Chart)")

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
        fig = px.timeline(gantt_df, x_start="Mulai", x_end="Selesai", y="Beasiswa", color="Tahapan",
                          color_discrete_sequence=px.colors.qualitative.Safe,
                          title="📅 Timeline Beasiswa")
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font_color="#e0e6ed", height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data timeline lengkap.")
else:
    st.info("Belum ada data yang bisa ditampilkan.")

# ================================
# 📋 DATA TABLE (READ ONLY)
# ================================
st.divider()
st.markdown("## 📋 Data Beasiswa (Klik Link untuk Membuka)")

if not df_filtered.empty:
    df_show = df_filtered.copy()
    df_show["Link Beasiswa"] = df_show["Link Beasiswa"].apply(
        lambda x: f'<a href="{x}" target="_blank" style="color:#4db8ff;">🌐 Buka</a>' if x else "-"
    )
    st.markdown(df_show.to_html(escape=False, index=False, classes="data-table"), unsafe_allow_html=True)
else:
    st.info("Belum ada data untuk ditampilkan.")

# ================================
# 🗑️ DELETE DATA
# ================================
st.divider()
st.markdown("## 🗑️ Hapus Data Beasiswa")

if not df.empty:
    to_delete = st.selectbox("Pilih beasiswa untuk dihapus", [""] + df["Beasiswa"].tolist())
    if st.button("❌ Hapus Beasiswa Ini"):
        if to_delete:
            df = df[df["Beasiswa"] != to_delete]
            save_data(df)
            st.success(f"Beasiswa '{to_delete}' berhasil dihapus.")
            st.rerun()
else:
    st.info("Belum ada data yang bisa dihapus.")

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Scholarship Tracker 4.2 | Dark Elegant UI 🎓")
