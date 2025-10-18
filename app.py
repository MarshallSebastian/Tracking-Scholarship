import streamlit as st
import pandas as pd
import os
import plotly.express as px

# ======================================
# 🗂️ Konfigurasi Data
# ======================================
DATA_PATH = "data/scholarships.csv"
COLUMNS = [
    "Nama User",
    "Negara",
    "Beasiswa",
    "Link Beasiswa",
    "IELTS",
    "GPA",
    "Other Requirements",
    "Benefit Scholarship",
    "Deadline Pendaftaran",
    "Deadline Tes 1",
    "Deadline Tes 2",
    "Pengumuman"
]

# Pastikan folder data ada
os.makedirs("data", exist_ok=True)

# ======================================
# 🧠 Load data ke session state
# ======================================
if "df" not in st.session_state:
    if os.path.exists(DATA_PATH):
        st.session_state.df = pd.read_csv(DATA_PATH)
    else:
        st.session_state.df = pd.DataFrame(columns=COLUMNS)

# ======================================
# 🎨 Setup UI
# ======================================
st.set_page_config(page_title="Scholarship Tracker 2025", layout="wide", page_icon="🎓")

st.markdown("<h1 style='text-align:center; color:#1a5276;'>🎓 Scholarship Tracker 2025</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Pantau, tambah, dan kelola semua beasiswa kamu secara langsung 📚</p>", unsafe_allow_html=True)
st.divider()

df = st.session_state.df

# ======================================
# 👥 Filter Sidebar
# ======================================
st.sidebar.header("🔍 Filter Data")
user_filter = st.sidebar.selectbox("Pilih User", ["Semua"] + sorted(df["Nama User"].dropna().unique().tolist()))
country_filter = st.sidebar.selectbox("Filter Negara", ["Semua"] + sorted(df["Negara"].dropna().unique().tolist()))

filtered_df = df.copy()
if user_filter != "Semua":
    filtered_df = filtered_df[filtered_df["Nama User"] == user_filter]
if country_filter != "Semua":
    filtered_df = filtered_df[filtered_df["Negara"] == country_filter]

# ======================================
# ➕ Input Data
# ======================================
with st.expander("➕ Tambahkan Beasiswa Baru"):
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nama_user = col1.selectbox("Nama User", ["Marcel", "Della"])
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
            new_entry = pd.DataFrame([{
                "Nama User": nama_user,
                "Negara": negara,
                "Beasiswa": beasiswa,
                "Link Beasiswa": link,
                "IELTS": ielts,
                "GPA": gpa,
                "Other Requirements": other,
                "Benefit Scholarship": benefit,
                "Deadline Pendaftaran": deadline,
                "Deadline Tes 1": tes1,
                "Deadline Tes 2": tes2,
                "Pengumuman": pengumuman
            }])
            st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
            st.session_state.df.to_csv(DATA_PATH, index=False)
            st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan!")

st.divider()

# ======================================
# 📊 Statistik Beasiswa
# ======================================
st.subheader("📈 Statistik Beasiswa")

if not filtered_df.empty:
    col1, col2 = st.columns(2)

    fig_country = px.bar(
        filtered_df.groupby("Negara").size().reset_index(name="Jumlah"),
        x="Negara", y="Jumlah", title="📍 Jumlah Beasiswa per Negara"
    )
    col1.plotly_chart(fig_country, use_container_width=True)

    fig_user = px.pie(filtered_df, names="Nama User", title="👥 Proporsi Beasiswa per User")
    col2.plotly_chart(fig_user, use_container_width=True)
else:
    st.info("Belum ada data untuk ditampilkan di grafik.")

st.divider()

# ======================================
# 📋 Tabel Data
# ======================================
st.subheader("📋 Database Beasiswa")

if filtered_df.empty:
    st.warning("Belum ada data beasiswa.")
else:
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# ======================================
# 🗑️ Hapus Data
# ======================================
with st.expander("🗑️ Hapus Beasiswa"):
    if not df.empty:
        del_name = st.selectbox("Pilih Beasiswa yang akan dihapus", [""] + df["Beasiswa"].tolist())
        if st.button("Hapus Data"):
            if del_name:
                st.session_state.df = st.session_state.df[st.session_state.df["Beasiswa"] != del_name]
                st.session_state.df.to_csv(DATA_PATH, index=False)
                st.success(f"❌ Beasiswa '{del_name}' berhasil dihapus.")
    else:
        st.info("Belum ada data yang bisa dihapus.")

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Powered by Streamlit & GitHub")
