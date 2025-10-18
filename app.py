import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# =====================================
# 🎨 PAGE CONFIGURATION
# =====================================
st.set_page_config(
    page_title="🎓 Scholarship Tracker Dashboard",
    page_icon="🎓",
    layout="wide"
)

# =====================================
# 💾 DATABASE IN MEMORY
# =====================================
COLUMNS = [
    "Nama User", "Negara", "Beasiswa", "Link Beasiswa",
    "IELTS", "GPA", "Other Requirements", "Benefit Scholarship",
    "Deadline Pendaftaran", "Deadline Tes 1", "Deadline Tes 2", "Pengumuman"
]

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=COLUMNS)

df = st.session_state.data

# =====================================
# ✨ HEADER
# =====================================
st.markdown("""
    <style>
        body { background-color: #f8fafc; }
        .main-title {
            text-align: center; color: #1a5276; font-size: 38px;
            font-weight: 700; margin-bottom: -5px;
        }
        .sub-title {
            text-align: center; color: #5f6368; font-size: 16px; margin-bottom: 40px;
        }
        [data-testid="stDataEditor"] {
            border-radius: 12px;
            box-shadow: 0 0 10px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎓 Scholarship Tracker Dashboard 2025</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Kelola, pantau, dan visualisasikan progress beasiswa kamu dalam satu halaman ✨</p>", unsafe_allow_html=True)

# =====================================
# 🧾 FORM INPUT
# =====================================
st.markdown("### ➕ Tambahkan Beasiswa Baru")

with st.form("add_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    nama_user = col1.text_input("Nama User")
    negara = col2.text_input("Negara")
    beasiswa = col1.text_input("Nama Beasiswa")
    link = col2.text_input("Link Beasiswa (URL)")
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
        if not nama_user or not beasiswa:
            st.warning("⚠️ Harap isi minimal *Nama User* dan *Nama Beasiswa*.")
        else:
            new_entry = pd.DataFrame([{
                "Nama User": nama_user, "Negara": negara, "Beasiswa": beasiswa, "Link Beasiswa": link,
                "IELTS": ielts, "GPA": gpa, "Other Requirements": other, "Benefit Scholarship": benefit,
                "Deadline Pendaftaran": deadline, "Deadline Tes 1": tes1, "Deadline Tes 2": tes2, "Pengumuman": pengumuman
            }])
            st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
            st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan!")
            st.rerun()  # AUTO REFRESH SAAT SAVE

st.divider()

# =====================================
# 📊 VISUALIZATION SECTION
# =====================================
if not df.empty:
    st.markdown("## 📈 Statistik dan Progress")

    col1, col2 = st.columns(2)

    # Bar Chart by Country
    if df["Negara"].notna().any():
        fig_country = px.bar(
            df.groupby("Negara").size().reset_index(name="Jumlah"),
            x="Negara", y="Jumlah", text_auto=True,
            color_discrete_sequence=["#1a5276"], title="📍 Jumlah Beasiswa per Negara"
        )
        col1.plotly_chart(fig_country, use_container_width=True)

    # Pie Chart by User
    if df["Nama User"].notna().any():
        fig_user = px.pie(df, names="Nama User", title="👥 Distribusi Beasiswa per User")
        col2.plotly_chart(fig_user, use_container_width=True)
else:
    st.info("Belum ada data beasiswa. Tambahkan data di atas dulu ya!")

# =====================================
# 🔔 REMINDER SECTION
# =====================================
st.divider()
st.markdown("## 🔔 Reminder Beasiswa yang Akan Segera Deadline")

if not df.empty:
    today = datetime.now().date()
    df["Deadline Pendaftaran"] = pd.to_datetime(df["Deadline Pendaftaran"]).dt.date
    df["Days Left"] = (df["Deadline Pendaftaran"] - today).apply(lambda x: x.days if pd.notnull(x) else None)
    upcoming = df[df["Days Left"].between(0, 7, inclusive="both")]

    if not upcoming.empty:
        st.success(f"🎯 Ada {len(upcoming)} beasiswa yang akan tutup dalam 7 hari!")
        st.dataframe(
            upcoming[["Nama User", "Beasiswa", "Negara", "Deadline Pendaftaran", "Days Left"]],
            use_container_width=True, hide_index=True
        )
    else:
        st.info("✅ Tidak ada beasiswa yang akan tutup dalam 7 hari.")
else:
    st.info("Belum ada data untuk reminder.")

# =====================================
# 🗓️ CALENDAR STYLE TIMELINE
# =====================================
st.divider()
st.markdown("## 📅 Timeline Kegiatan Beasiswa")

if not df.empty:
    events = []
    for _, row in df.iterrows():
        if pd.notnull(row["Deadline Pendaftaran"]):
            events.append({"Tanggal": row["Deadline Pendaftaran"], "Event": "Deadline", "Beasiswa": row["Beasiswa"]})
        if pd.notnull(row["Deadline Tes 1"]):
            events.append({"Tanggal": row["Deadline Tes 1"], "Event": "Tes 1", "Beasiswa": row["Beasiswa"]})
        if pd.notnull(row["Deadline Tes 2"]):
            events.append({"Tanggal": row["Deadline Tes 2"], "Event": "Tes 2", "Beasiswa": row["Beasiswa"]})
        if pd.notnull(row["Pengumuman"]):
            events.append({"Tanggal": row["Pengumuman"], "Event": "Pengumuman", "Beasiswa": row["Beasiswa"]})

    cal_df = pd.DataFrame(events)
    if not cal_df.empty:
        cal_df["Tanggal"] = pd.to_datetime(cal_df["Tanggal"])
        cal_df = cal_df.sort_values("Tanggal")

        fig_timeline = px.timeline(
            cal_df, x_start="Tanggal", x_end="Tanggal", y="Beasiswa",
            color="Event", title="🗓️ Timeline Beasiswa",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_timeline.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("Belum ada tanggal kegiatan yang diisi.")
else:
    st.info("Belum ada data untuk menampilkan kalender.")

# =====================================
# 📋 DATA TABLE (Editable)
# =====================================
st.divider()
st.markdown("## 📋 Database Beasiswa (Langsung Bisa Diedit)")

if not df.empty:
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Link Beasiswa": st.column_config.LinkColumn("Link Beasiswa"),
            "Benefit Scholarship": st.column_config.TextColumn("Benefit Scholarship", width="medium"),
            "Other Requirements": st.column_config.TextColumn("Other Requirements", width="medium")
        }
    )
    st.session_state.data = edited_df
else:
    st.info("Tambahkan data untuk melihat tabel.")

# =====================================
# 🗑️ DELETE SECTION
# =====================================
st.divider()
st.markdown("## 🗑️ Hapus Beasiswa")

if not df.empty:
    del_name = st.selectbox("Pilih Beasiswa yang akan dihapus", [""] + df["Beasiswa"].tolist())
    if st.button("Hapus Data"):
        if del_name:
            st.session_state.data = st.session_state.data[df["Beasiswa"] != del_name]
            st.success(f"❌ Beasiswa '{del_name}' berhasil dihapus.")
else:
    st.info("Belum ada data yang bisa dihapus.")

# =====================================
# 📦 FOOTER
# =====================================
st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Stylish, interactive, one-page scholarship tracker dashboard ✨")
