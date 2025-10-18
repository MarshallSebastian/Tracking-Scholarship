import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# 🧠 Session-based database (tanpa CSV)
# =====================================
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

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=COLUMNS)
if "refresh" not in st.session_state:
    st.session_state.refresh = False

df = st.session_state.data

# =====================================
# 🎨 Setup UI
# =====================================
st.set_page_config(page_title="Scholarship Tracker 2025", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
        .block-container {padding-top: 2rem; padding-bottom: 1rem;}
        h1, h2, h3 {color: #1a5276;}
        [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 0 8px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🎓 Scholarship Tracker 2025</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#5f6368;'>Kelola dan pantau semua beasiswa kamu langsung dari satu dashboard ✨</p>", unsafe_allow_html=True)
st.divider()

# =====================================
# 🔍 Filter Sidebar
# =====================================
st.sidebar.header("🔍 Filter Data")

user_list = sorted(df["Nama User"].dropna().unique().tolist()) if not df.empty else []
user_filter = st.sidebar.selectbox("👤 Pilih User", ["Semua"] + user_list)

country_list = sorted(df["Negara"].dropna().unique().tolist()) if not df.empty else []
country_filter = st.sidebar.selectbox("🌍 Filter Negara", ["Semua"] + country_list)

# =====================================
# ➕ Input Data
# =====================================
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
            st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
            st.session_state.refresh = True
            st.success(f"✅ Beasiswa '{beasiswa}' berhasil ditambahkan!")

# =====================================
# 📊 Statistik Beasiswa
# =====================================
st.divider()
st.subheader("📈 Statistik Beasiswa")

filtered_df = st.session_state.data.copy()
if user_filter != "Semua":
    filtered_df = filtered_df[filtered_df["Nama User"] == user_filter]
if country_filter != "Semua":
    filtered_df = filtered_df[filtered_df["Negara"] == country_filter]

if not filtered_df.empty:
    col1, col2 = st.columns(2)
    fig_country = px.bar(
        filtered_df.groupby("Negara").size().reset_index(name="Jumlah"),
        x="Negara", y="Jumlah", title="📍 Jumlah Beasiswa per Negara", text_auto=True
    )
    fig_country.update_traces(marker_color="#1a5276")
    col1.plotly_chart(fig_country, use_container_width=True)

    fig_user = px.pie(filtered_df, names="Nama User", title="👥 Proporsi Beasiswa per User")
    col2.plotly_chart(fig_user, use_container_width=True)
else:
    st.info("Belum ada data untuk ditampilkan di grafik.")

# =====================================
# 📋 Database Langsung (Auto Refresh)
# =====================================
st.divider()
st.subheader("📋 Database Beasiswa (Langsung Bisa Diedit)")

if not filtered_df.empty:
    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="editable_table",
        column_config={
            "Link Beasiswa": st.column_config.LinkColumn("Link Beasiswa"),
            "Benefit Scholarship": st.column_config.TextColumn("Benefit Scholarship", width="medium"),
            "Other Requirements": st.column_config.TextColumn("Other Requirements", width="medium")
        }
    )
    # Simpan perubahan langsung ke session_state
    st.session_state.data.loc[edited_df.index, :] = edited_df
else:
    st.warning("Belum ada data beasiswa. Tambahkan data di atas dulu ya!")

# =====================================
# 🗑️ Hapus Data
# =====================================
st.divider()
with st.expander("🗑️ Hapus Beasiswa"):
    if not df.empty:
        del_name = st.selectbox("Pilih Beasiswa yang akan dihapus", [""] + df["Beasiswa"].tolist())
        if st.button("Hapus Data"):
            if del_name:
                st.session_state.data = st.session_state.data[st.session_state.data["Beasiswa"] != del_name]
                st.success(f"❌ Beasiswa '{del_name}' berhasil dihapus.")
    else:
        st.info("Belum ada data yang bisa dihapus.")

st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Real-time editable dashboard tanpa file CSV")

# =====================================
# 🔁 Refresh otomatis setelah Save
# =====================================
if st.session_state.refresh:
    st.session_state.refresh = False
    st.experimental_rerun()
