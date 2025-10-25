import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json, os
import warnings
warnings.filterwarnings("ignore")

# =====================================
# ⚙️ PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="🎓 Scholarship Tracker (Offline Mode)",
    page_icon="🎓",
    layout="wide"
)

# =====================================
# 💾 PERSISTENT STORAGE
# =====================================
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
            "Deadline Pendaftaran", "Deadline Tes 1", "Deadline Tes 2", "Pengumuman"
        ])

def save_data(df):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

df = load_data()

# =====================================
# 🎨 STYLING
# =====================================
st.markdown("""
<style>
    .main {
        background-color: #f9fafc;
    }
    h1, h2, h3 {
        color: #1a5276;
        font-family: 'Poppins', sans-serif;
    }
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stDataFrame {
        border-radius: 10px;
    }
    [data-testid="stMetricValue"] {
        color: #1a5276;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# 🎓 HEADER
# =====================================
st.markdown("""
<h1 style='text-align:center;'>🎓 Scholarship Tracker Dashboard</h1>
<p style='text-align:center; color:#5f6368;'>
Tanpa GSheet, tanpa database — data kamu tersimpan otomatis di <b>local JSON</b> ✨
</p>
""", unsafe_allow_html=True)
st.divider()

# =====================================
# ➕ INPUT FORM
# =====================================
with st.expander("➕ Tambahkan Beasiswa Baru", expanded=True):
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nama_user = col1.text_input("Nama User")
        negara = col2.text_input("Negara")
        beasiswa = col1.text_input("Nama Beasiswa")
        link = col2.text_input("Link Beasiswa")
        ielts = col1.text_input("IELTS Requirement")
        gpa = col2.text_input("GPA Requirement")
        other = col1.text_area("Other Requirements")
        benefit = col2.text_area("Benefit Scholarship")
        deadline = col1.date_input("Deadline Pendaftaran")
        tes1 = col2.date_input("Deadline Tes 1", value=None)
        tes2 = col1.date_input("Deadline Tes 2", value=None)
        pengumuman = col1.date_input("Tanggal Pengumuman", value=None)

        submitted = st.form_submit_button("💾 Simpan Data", use_container_width=True)

        if submitted:
            if not nama_user or not beasiswa:
                st.warning("Isi minimal Nama User dan Nama Beasiswa.")
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
                    "Deadline Pendaftaran": str(deadline),
                    "Deadline Tes 1": str(tes1) if tes1 else "",
                    "Deadline Tes 2": str(tes2) if tes2 else "",
                    "Pengumuman": str(pengumuman) if pengumuman else ""
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan!")
                st.rerun()

# =====================================
# 📊 CHART SECTION
# =====================================
st.divider()
if not df.empty:
    st.markdown("## 📊 Statistik Beasiswa")
    col1, col2 = st.columns(2)
    if df["Negara"].notna().any():
        fig_country = px.bar(df.groupby("Negara").size().reset_index(name="Jumlah"),
                             x="Negara", y="Jumlah", text_auto=True,
                             title="📍 Jumlah Beasiswa per Negara")
        col1.plotly_chart(fig_country, use_container_width=True)
    if df["Nama User"].notna().any():
        fig_user = px.pie(df, names="Nama User", title="👥 Distribusi Beasiswa per User")
        col2.plotly_chart(fig_user, use_container_width=True)
else:
    st.info("Belum ada data untuk ditampilkan.")

# =====================================
# 🔔 REMINDER
# =====================================
st.divider()
st.markdown("## 🔔 Reminder Beasiswa yang Akan Segera Tutup")
if not df.empty:
    today = datetime.now().date()
    df["Deadline Pendaftaran"] = pd.to_datetime(df["Deadline Pendaftaran"], errors="coerce").dt.date
    df["Days Left"] = (df["Deadline Pendaftaran"] - today).apply(lambda x: x.days if pd.notnull(x) else None)
    soon = df[df["Days Left"].between(0, 7, inclusive="both")]
    if not soon.empty:
        st.success(f"🎯 Ada {len(soon)} beasiswa yang akan tutup dalam 7 hari!")
        st.dataframe(soon[["Nama User", "Beasiswa", "Negara", "Deadline Pendaftaran", "Days Left"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("✅ Tidak ada beasiswa yang akan tutup dalam 7 hari.")

# =====================================
# 🗓️ TIMELINE
# =====================================
st.divider()
st.markdown("## 📅 Timeline Kegiatan Beasiswa")
if not df.empty:
    events = []
    for _, row in df.iterrows():
        for col, label in [("Deadline Pendaftaran", "Deadline"),
                           ("Deadline Tes 1", "Tes 1"),
                           ("Deadline Tes 2", "Tes 2"),
                           ("Pengumuman", "Pengumuman")]:
            if pd.notnull(row[col]) and str(row[col]) != "":
                events.append({"Tanggal": row[col], "Event": label, "Beasiswa": row["Beasiswa"]})
    if events:
        cal_df = pd.DataFrame(events)
        cal_df["Tanggal"] = pd.to_datetime(cal_df["Tanggal"], errors="coerce")
        cal_df = cal_df.sort_values("Tanggal")
        fig_timeline = px.timeline(cal_df, x_start="Tanggal", x_end="Tanggal", y="Beasiswa",
                                   color="Event", title="🗓️ Timeline Beasiswa",
                                   color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_timeline.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("Belum ada tanggal kegiatan yang diisi.")

# =====================================
# 📋 DATABASE (EDITABLE)
# =====================================
st.divider()
st.markdown("## 📋 Database Beasiswa (Editable)")

if not df.empty:
    edited_df = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="fixed")
    if not edited_df.equals(df):
        save_data(edited_df)
        st.success("✅ Perubahan disimpan otomatis.")
        st.rerun()
else:
    st.info("Belum ada data yang bisa ditampilkan.")

# =====================================
# 🗑️ DELETE
# =====================================
st.divider()
st.markdown("## 🗑️ Hapus Beasiswa")

if not df.empty:
    del_name = st.selectbox("Pilih Beasiswa untuk dihapus", [""] + df["Beasiswa"].tolist())
    if st.button("🗑️ Hapus Data", use_container_width=True):
        if del_name:
            df = df[df["Beasiswa"] != del_name]
            save_data(df)
            st.success(f"❌ Beasiswa '{del_name}' berhasil dihapus.")
            st.rerun()

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Data tersimpan lokal di JSON ✨")
