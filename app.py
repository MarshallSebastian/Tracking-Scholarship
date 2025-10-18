import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from datetime import datetime, timedelta
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import warnings
warnings.filterwarnings("ignore")

# =====================================
# 🧠 SETUP
# =====================================
st.set_page_config(page_title="Scholarship Tracker (Simple)", page_icon="🎓", layout="wide")

# Google Sheet ID kamu (ambil dari URL)
SHEET_ID = "1xhFX3Jj1opcHP-b1JWz95TZ1gX3tklOOJoLoONeLzMI"
SHEET_NAME = "Sheet1"

# =====================================
# 🔗 CONNECT KE PUBLIC GOOGLE SHEET
# =====================================
try:
    gc = gspread.Client(None)
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.worksheet(SHEET_NAME)
except Exception as e:
    st.error("Gagal connect ke Google Sheet. Pastikan Sheet di-share: Anyone with link → Editor.")
    st.stop()

# =====================================
# 📥 LOAD DATA
# =====================================
def load_data():
    data = worksheet.get_all_records()
    if not data:
        df = pd.DataFrame(columns=[
            "Nama User", "Negara", "Beasiswa", "Link Beasiswa",
            "IELTS", "GPA", "Other Requirements", "Benefit Scholarship",
            "Deadline Pendaftaran", "Deadline Tes 1", "Deadline Tes 2", "Pengumuman"
        ])
    else:
        df = pd.DataFrame(data)
    return df

def save_data(df):
    worksheet.clear()
    set_with_dataframe(worksheet, df)

df = load_data()

# =====================================
# 🎨 HEADER
# =====================================
st.markdown("<h1 style='text-align:center;color:#1a5276;'>🎓 Scholarship Tracker Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#5f6368;'>Data langsung tersimpan ke Google Sheet — tanpa credential JSON ✨</p>", unsafe_allow_html=True)
st.divider()

# =====================================
# ➕ INPUT FORM
# =====================================
st.subheader("➕ Tambahkan Beasiswa Baru")

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

    submitted = st.form_submit_button("💾 Simpan Data")

    if submitted:
        new_data = pd.DataFrame([{
            "Nama User": nama_user, "Negara": negara, "Beasiswa": beasiswa, "Link Beasiswa": link,
            "IELTS": ielts, "GPA": gpa, "Other Requirements": other, "Benefit Scholarship": benefit,
            "Deadline Pendaftaran": deadline, "Deadline Tes 1": tes1,
            "Deadline Tes 2": tes2, "Pengumuman": pengumuman
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan!")
        st.rerun()

# =====================================
# 📊 CHART SECTION
# =====================================
st.divider()
if not df.empty:
    st.markdown("## 📈 Statistik Beasiswa")
    col1, col2 = st.columns(2)
    fig_country = px.bar(df.groupby("Negara").size().reset_index(name="Jumlah"), x="Negara", y="Jumlah",
                         title="📍 Jumlah Beasiswa per Negara", text_auto=True)
    col1.plotly_chart(fig_country, use_container_width=True)
    fig_user = px.pie(df, names="Nama User", title="👥 Distribusi Beasiswa per User")
    col2.plotly_chart(fig_user, use_container_width=True)

# =====================================
# 🔔 REMINDER SECTION
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
            if pd.notnull(row[col]):
                events.append({"Tanggal": row[col], "Event": label, "Beasiswa": row["Beasiswa"]})
    cal_df = pd.DataFrame(events)
    if not cal_df.empty:
        fig_timeline = px.timeline(cal_df, x_start="Tanggal", x_end="Tanggal", y="Beasiswa",
                                   color="Event", title="🗓️ Timeline Beasiswa")
        fig_timeline.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_timeline, use_container_width=True)

# =====================================
# 📋 EDITABLE TABLE
# =====================================
st.divider()
st.markdown("## 📋 Database Beasiswa (Editable)")

if not df.empty:
    edited = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="fixed")
    if not edited.equals(df):
        save_data(edited)
        st.success("✅ Perubahan disimpan otomatis ke Google Sheet.")
        st.rerun()
else:
    st.info("Belum ada data untuk ditampilkan.")

# =====================================
# 🗑️ DELETE
# =====================================
st.divider()
st.markdown("## 🗑️ Hapus Beasiswa")

if not df.empty:
    del_item = st.selectbox("Pilih Beasiswa yang akan dihapus", [""] + df["Beasiswa"].tolist())
    if st.button("Hapus Data"):
        if del_item:
            df = df[df["Beasiswa"] != del_item]
            save_data(df)
            st.success(f"❌ Beasiswa '{del_item}' berhasil dihapus.")
            st.rerun()

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Live Google Sheet Sync tanpa JSON credential 🚀")
