import streamlit as st
import pandas as pd
import os

# ========== 🗂️ Setup Awal ==========
DATA_PATH = "data/scholarships.csv"

# Pastikan folder & file ada
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_PATH):
    df_init = pd.DataFrame(columns=["Scholarship Name", "Country", "Degree", "Deadline", "Link"])
    df_init.to_csv(DATA_PATH, index=False)

# ========== 📥 Load Data ==========
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

df = load_data()

# ========== 🎓 Header ==========
st.set_page_config(page_title="Scholarship Tracker", layout="wide")
st.title("🎓 Scholarship Tracker 2025")
st.caption("Tambah, lihat, dan kelola data beasiswa secara langsung!")

# ========== 🧾 Form Input ==========
with st.expander("➕ Tambahkan Beasiswa Baru"):
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Nama Beasiswa")
        country = col2.text_input("Negara")
        degree = col1.selectbox("Jenjang", ["S1", "S2", "S3", "Postdoc", "Short Course"])
        deadline = col2.date_input("Deadline")
        link = st.text_input("Tautan Resmi (URL)")

        submitted = st.form_submit_button("💾 Simpan Beasiswa")
        if submitted:
            if name and country and degree and link:
                new_row = {"Scholarship Name": name, "Country": country,
                           "Degree": degree, "Deadline": deadline, "Link": link}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"✅ '{name}' berhasil ditambahkan!")
            else:
                st.warning("⚠️ Lengkapi semua kolom dulu ya!")

# ========== 🔍 Filter Data ==========
st.subheader("📊 Daftar Beasiswa")
col1, col2 = st.columns(2)
filter_degree = col1.selectbox("Filter Jenjang", ["Semua"] + sorted(df["Degree"].unique().tolist()))
filter_country = col2.selectbox("Filter Negara", ["Semua"] + sorted(df["Country"].unique().tolist()))

filtered_df = df.copy()
if filter_degree != "Semua":
    filtered_df = filtered_df[filtered_df["Degree"] == filter_degree]
if filter_country != "Semua":
    filtered_df = filtered_df[filtered_df["Country"] == filter_country]

# ========== 📋 Tampilkan Data ==========
st.dataframe(filtered_df, use_container_width=True)

# ========== 🗑️ Hapus Data ==========
with st.expander("🗑️ Hapus Beasiswa"):
    del_name = st.selectbox("Pilih Beasiswa yang ingin dihapus", [""] + df["Scholarship Name"].tolist())
    if st.button("Hapus Data"):
        if del_name:
            df = df[df["Scholarship Name"] != del_name]
            save_data(df)
            st.success(f"❌ '{del_name}' berhasil dihapus!")
        else:
            st.warning("Pilih dulu beasiswa yang mau dihapus!")

# ========== 📦 Footer ==========
st.caption("Dibuat dengan ❤️ oleh kamu, powered by Streamlit & GitHub.")
