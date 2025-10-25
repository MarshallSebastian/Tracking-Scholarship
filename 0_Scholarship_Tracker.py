import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import json, os

# ================================
# ⚙️ PAGE CONFIG
# ================================
st.set_page_config(page_title="🎓 Scholarship Tracker 3.2", page_icon="🎓", layout="wide")

# ================================
# 💾 DATA HANDLING
# ================================
DATA_FILE = "data_scholarship.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    else:
        return pd.DataFrame(columns=[
            "Nama User", "Negara", "Beasiswa", "Link Beasiswa", "IELTS", "GPA",
            "Other Requirements", "Benefit Scholarship",
            "Periode Pendaftaran (Mulai)", "Periode Pendaftaran (Selesai)",
            "Periode Dokumen (Mulai)", "Periode Dokumen (Selesai)",
            "Periode Wawancara (Mulai)", "Periode Wawancara (Selesai)",
            "Periode Tes (Mulai)", "Periode Tes (Selesai)", "Tanggal Pengumuman"
        ])

def save_data(df):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

df = load_data()
for col in [
    "Nama User", "Negara", "Beasiswa", "Link Beasiswa", "IELTS", "GPA",
    "Other Requirements", "Benefit Scholarship",
    "Periode Pendaftaran (Mulai)", "Periode Pendaftaran (Selesai)",
    "Periode Dokumen (Mulai)", "Periode Dokumen (Selesai)",
    "Periode Wawancara (Mulai)", "Periode Wawancara (Selesai)",
    "Periode Tes (Mulai)", "Periode Tes (Selesai)", "Tanggal Pengumuman"
]:
    if col not in df.columns:
        df[col] = ""

# ================================
# 🎨 STYLING
# ================================
st.markdown("""
<style>
body { background-color: #f8fafc; font-family: 'Poppins', sans-serif; }
h1, h2, h3, h4 { color: #1f4e79; }
.dataframe th {
    background-color: #1f4e79 !important;
    color: white !important;
    text-align: center !important;
    padding: 8px !important;
}
.dataframe td {
    background-color: #fdfefe !important;
    padding: 8px !important;
    border: 1px solid #ddd !important;
    word-wrap: break-word !important;
    white-space: normal !important;
}
tr:nth-child(even) td { background-color: #f8f9fa !important; }
tr:hover td { background-color: #eaf2f8 !important; }
</style>
""", unsafe_allow_html=True)

# ================================
# 🎓 HEADER
# ================================
st.markdown("<h1 style='text-align:center;'>🎓 Scholarship Tracker 3.2</h1>", unsafe_allow_html=True)
st.caption("📍 Data tersimpan otomatis secara lokal (JSON) — tetap aman walau direfresh 🔒")
st.divider()

# ================================
# 🧾 FORM HIDE/UNHIDE
# ================================
if "show_form" not in st.session_state:
    st.session_state.show_form = False

if st.button("✏️ Tampilkan/Sembunyikan Form Input Beasiswa"):
    st.session_state.show_form = not st.session_state.show_form

if st.session_state.show_form:
    with st.form("form_beasiswa", clear_on_submit=True):
        st.subheader("➕ Tambah / Update Data Beasiswa")
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
        def optional_date(label):
            try: return st.date_input(label, value=None, key=label)
            except: return None

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
        start_int = optional_date("Mulai Wawancara")
        end_int = optional_date("Selesai Wawancara")

        st.markdown("**🧪 Tes Beasiswa**")
        t1, t2 = st.columns(2)
        start_test = optional_date("Mulai Tes")
        end_test = optional_date("Selesai Tes")

        pengumuman = optional_date("📢 Tanggal Pengumuman")

        if st.form_submit_button("💾 Simpan Beasiswa"):
            if not nama_user or not beasiswa:
                st.warning("⚠️ Isi minimal Nama User dan Nama Beasiswa!")
            else:
                new_row = {
                    "Nama User": nama_user,
                    "Negara": negara,
                    "Beasiswa": beasiswa,
                    "Link Beasiswa": link,
                    "IELTS": ielts, "GPA": gpa,
                    "Other Requirements": other,
                    "Benefit Scholarship": benefit,
                    "Periode Pendaftaran (Mulai)": str(start_reg) if start_reg else "",
                    "Periode Pendaftaran (Selesai)": str(end_reg) if end_reg else "",
                    "Periode Dokumen (Mulai)": str(start_doc) if start_doc else "",
                    "Periode Dokumen (Selesai)": str(end_doc) if end_doc else "",
                    "Periode Wawancara (Mulai)": str(start_int) if start_int else "",
                    "Periode Wawancara (Selesai)": str(end_int) if end_int else "",
                    "Periode Tes (Mulai)": str(start_test) if start_test else "",
                    "Periode Tes (Selesai)": str(end_test) if end_test else "",
                    "Tanggal Pengumuman": str(pengumuman) if pengumuman else ""
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan!")
                st.rerun()

# ================================
# 📊 REMINDER CHART (30 Hari)
# ================================
st.divider()
st.markdown("## ⏰ Reminder Beasiswa (30 Hari ke Depan)")

if not df.empty:
    today = date.today()
    df["Periode Pendaftaran (Selesai)"] = pd.to_datetime(df["Periode Pendaftaran (Selesai)"], errors="coerce").dt.date
    df["Days Left"] = (df["Periode Pendaftaran (Selesai)"] - today).apply(lambda x: x.days if pd.notnull(x) else None)
    upcoming = df[df["Days Left"].between(0, 30, inclusive="both")]

    if not upcoming.empty:
        df_chart = upcoming.groupby("Beasiswa", as_index=False)["Days Left"].mean()
        df_chart["Color"] = df_chart["Days Left"].apply(lambda x: "#27ae60" if x>15 else "#f1c40f" if x>7 else "#e74c3c")
        fig = px.bar(df_chart, x="Beasiswa", y="Days Left", color="Color", text_auto=True,
                     title="📆 Sisa Waktu Pendaftaran (Hari)",
                     color_discrete_map="identity")
        fig.update_layout(showlegend=False, yaxis_title="Hari Tersisa", xaxis_title="Beasiswa")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("✅ Tidak ada beasiswa yang akan tutup dalam 30 hari.")
else:
    st.info("Belum ada data untuk reminder.")

# ================================
# 📅 GANTT CHART (Filter User & Negara)
# ================================
st.divider()
st.markdown("## 🗓️ Timeline Beasiswa (Gantt Chart)")

if not df.empty:
    c1, c2 = st.columns(2)
    selected_user = c1.selectbox("👤 Pilih User", sorted(df["Nama User"].dropna().unique()))
    selected_country = c2.selectbox("🌍 Pilih Negara", sorted(df["Negara"].dropna().unique()))
    df_filt = df[(df["Nama User"] == selected_user) & (df["Negara"] == selected_country)]

    if not df_filt.empty:
        events = []
        for _, row in df_filt.iterrows():
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
                color="Tahapan", color_discrete_sequence=px.colors.qualitative.Pastel,
                title=f"📅 Timeline {selected_user} - {selected_country}"
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data lengkap untuk Gantt Chart.")
    else:
        st.warning("Tidak ada data untuk user & negara ini.")

# ================================
# 📋 DATABASE MODERN & RESPONSIVE
# ================================
st.divider()
st.markdown("## 📋 Database Beasiswa")

if not df.empty:
    df_display = df.copy()

    # Buat link beasiswa jadi clickable
    df_display["Link Beasiswa"] = df_display["Link Beasiswa"].apply(
        lambda x: f'<a href="{x}" target="_blank" style="color:#1f77b4; text-decoration:none;">🌐 Buka Link</a>' if x else "-"
    )

    # Custom table styling modern
    st.markdown("""
    <style>
    .styled-table {
        border-collapse: collapse;
        width: 100%;
        font-family: "Poppins", sans-serif;
        font-size: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-radius: 10px;
        overflow: hidden;
    }
    .styled-table thead tr {
        background-color: #1f4e79;
        color: #ffffff;
        text-align: left;
    }
    .styled-table th, .styled-table td {
        padding: 10px 15px;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f3f6fa;
    }
    .styled-table tbody tr:hover {
        background-color: #e9f3ff;
    }
    </style>
    """, unsafe_allow_html=True)

    # Convert dataframe ke HTML dengan class custom
    html_table = df_display.to_html(
        escape=False,
        index=False,
        classes="styled-table"
    )

    # Render table
    st.markdown(html_table, unsafe_allow_html=True)

else:
    st.info("Belum ada data yang bisa ditampilkan.")

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Scholarship Tracker 3.3 | Streamlit + JSON Persistent | UI Enhanced")
