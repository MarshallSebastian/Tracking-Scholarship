import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# =====================================
# ⚙️ Setup Page
# =====================================
st.set_page_config(page_title="Scholarship Progress & Reminder", page_icon="📈", layout="wide")

st.markdown("<h1 style='text-align:center; color:#1a5276;'>📈 Scholarship Tracking & Reminders</h1>", unsafe_allow_html=True)
st.caption("Pantau progress beasiswa kamu lewat grafik, kalender, dan reminder otomatis 🔔")
st.divider()

# =====================================
# 🧠 Load Data dari Session
# =====================================
if "data" not in st.session_state or st.session_state.data.empty:
    st.warning("⚠️ Belum ada data. Silakan tambahkan data beasiswa di halaman utama (📋 Scholarship Database).")
    st.stop()

df = st.session_state.data.copy()

# =====================================
# 🔍 Filter Input
# =====================================
col1, col2 = st.columns(2)
user_input = col1.text_input("Filter berdasarkan Nama User (kosongkan untuk semua):")
country_input = col2.text_input("Filter berdasarkan Negara (kosongkan untuk semua):")

filtered_df = df.copy()
if user_input:
    filtered_df = filtered_df[filtered_df["Nama User"].str.contains(user_input, case=False, na=False)]
if country_input:
    filtered_df = filtered_df[filtered_df["Negara"].str.contains(country_input, case=False, na=False)]

# =====================================
# 📊 Chart Progress
# =====================================
if not filtered_df.empty:
    col1, col2 = st.columns(2)

    fig_country = px.bar(
        filtered_df.groupby("Negara").size().reset_index(name="Jumlah"),
        x="Negara", y="Jumlah",
        title="📍 Jumlah Beasiswa per Negara",
        text_auto=True, color_discrete_sequence=["#1a5276"]
    )
    col1.plotly_chart(fig_country, use_container_width=True)

    fig_user = px.pie(
        filtered_df,
        names="Nama User",
        title="👥 Proporsi Beasiswa per User"
    )
    col2.plotly_chart(fig_user, use_container_width=True)
else:
    st.warning("Tidak ada data yang cocok dengan filter.")
    st.stop()

st.divider()

# =====================================
# 🔔 Reminder System (Deadline)
# =====================================
st.subheader("🔔 Reminder Beasiswa yang Akan Segera Deadline")

today = datetime.now().date()
soon_df = filtered_df.copy()

soon_df["Deadline Pendaftaran"] = pd.to_datetime(soon_df["Deadline Pendaftaran"]).dt.date
soon_df["Days Left"] = (soon_df["Deadline Pendaftaran"] - today).dt.days

# Filter beasiswa yang deadline-nya dalam 7 hari
upcoming = soon_df[soon_df["Days Left"].between(0, 7)]

if not upcoming.empty:
    st.success(f"🎯 Ada {len(upcoming)} beasiswa yang akan tutup dalam 7 hari!")
    st.dataframe(
        upcoming[["Nama User", "Beasiswa", "Negara", "Deadline Pendaftaran", "Days Left"]],
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("✅ Tidak ada beasiswa yang akan tutup dalam 7 hari ke depan.")

# =====================================
# 🗓️ Calendar-style Tracking
# =====================================
st.divider()
st.subheader("📅 Calendar Style: Timeline Beasiswa")

if not filtered_df.empty:
    # Gabungkan event dari deadline, tes, dan pengumuman
    events = []
    for _, row in filtered_df.iterrows():
        if pd.notnull(row["Deadline Pendaftaran"]):
            events.append({"Tanggal": row["Deadline Pendaftaran"], "Event": "Deadline Pendaftaran", "Beasiswa": row["Beasiswa"], "User": row["Nama User"]})
        if pd.notnull(row["Deadline Tes 1"]):
            events.append({"Tanggal": row["Deadline Tes 1"], "Event": "Tes 1", "Beasiswa": row["Beasiswa"], "User": row["Nama User"]})
        if pd.notnull(row["Deadline Tes 2"]):
            events.append({"Tanggal": row["Deadline Tes 2"], "Event": "Tes 2", "Beasiswa": row["Beasiswa"], "User": row["Nama User"]})
        if pd.notnull(row["Pengumuman"]):
            events.append({"Tanggal": row["Pengumuman"], "Event": "Pengumuman", "Beasiswa": row["Beasiswa"], "User": row["Nama User"]})

    cal_df = pd.DataFrame(events)
    cal_df["Tanggal"] = pd.to_datetime(cal_df["Tanggal"])

    if not cal_df.empty:
        cal_df = cal_df.sort_values("Tanggal")

        # Chart timeline style
        fig_timeline = px.timeline(
            cal_df,
            x_start="Tanggal",
            x_end="Tanggal",
            y="Beasiswa",
            color="Event",
            hover_data=["User"],
            title="🗓️ Timeline Kegiatan Beasiswa"
        )
        fig_timeline.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_timeline, use_container_width=True)

        st.caption("📌 Warna menunjukkan jenis event: Deadline, Tes, atau Pengumuman.")
    else:
        st.info("Belum ada tanggal kegiatan yang diisi di data beasiswa.")
else:
    st.info("Belum ada data untuk ditampilkan dalam kalender.")

# =====================================
# 📦 Footer
# =====================================
st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Real-time tracking, reminder, dan calendar view")
