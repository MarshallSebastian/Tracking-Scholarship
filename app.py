import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json, os

# ================================
# ⚙️ PAGE CONFIG
# ================================
st.set_page_config(
    page_title="🎓 Scholarship Tracker",
    page_icon="🎓",
    layout="wide"
)

# ================================
# 💾 PERSISTENT LOCAL STORAGE
# ================================
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

# ================================
# 🎨 GLOBAL STYLE
# ================================
st.markdown("""
<style>
    body {
        background-color: #f7f9fc;
        font-family: "Poppins", sans-serif;
    }
    .stTextInput, .stTextArea, .stDateInput {
        border-radius: 10px !important;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 25px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #135a8d;
    }
    .main {
        padding: 0rem 2rem;
    }
    h1, h2, h3 {
        color: #1f4e79;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# 🎓 HEADER
# ================================
st.markdown("<h1 style='text-align:center;'>🎓 Scholarship Tracker Dashboard</h1>", unsafe_allow_html=True)
st.caption("Data tersimpan otomatis secara lokal (JSON) — tidak hilang walau direfresh 🔒")
st.divider()

# ================================
# ➕ INPUT FORM (Better UX)
# ================================
st.subheader("➕ Tambah Data Beasiswa")

with st.form("form_beasiswa", clear_on_submit=True):
    st.markdown("Masukkan informasi lengkap beasiswa di bawah ini 👇")

    c1, c2 = st.columns(2)
    nama_user = c1.text_input("👤 Nama User")
    negara = c2.text_input("🌍 Negara Tujuan")
    beasiswa = c1.text_input("🎯 Nama Beasiswa")
    link = c2.text_input("🔗 Link Beasiswa")
    ielts = c1.text_input("📘 IELTS Requirement", placeholder="contoh: 6.5 overall")
    gpa = c2.text_input("🎓 GPA Requirement", placeholder="contoh: 3.5 / 4.0")

    c3, c4 = st.columns(2)
    other = c3.text_area("🧾 Other Requirements")
    benefit = c4.text_area("💰 Benefit Scholarship")

    st.markdown("#### ⏰ Tanggal Penting")
    d1, d2, d3, d4 = st.columns(4)
    deadline = d1.date_input("📅 Deadline Pendaftaran")
    tes1 = d2.date_input("📝 Deadline Tes 1", value=None)
    tes2 = d3.date_input("📝 Deadline Tes 2", value=None)
    pengumuman = d4.date_input("📢 Pengumuman", value=None)

    submitted = st.form_submit_button("💾 Simpan Beasiswa Ini")

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

# ================================
# 📊 VISUALISASI DATA
# ================================
st.divider()
if not df.empty:
    st.markdown("## 📈 Statistik Beasiswa")
    c1, c2 = st.columns(2)

    if df["Negara"].notna().any():
        fig_country = px.bar(df.groupby("Negara").size().reset_index(name="Jumlah"),
                             x="Negara", y="Jumlah", text_auto=True,
                             title="🌍 Jumlah Beasiswa per Negara",
                             color_discrete_sequence=["#1f77b4"])
        c1.plotly_chart(fig_country, use_container_width=True)

    if df["Nama User"].notna().any():
        fig_user = px.pie(df, names="Nama User", title="👥 Distribusi Beasiswa per User",
                          color_discrete_sequence=px.colors.sequential.Blues)
        c2.plotly_chart(fig_user, use_container_width=True)
else:
    st.info("Belum ada data untuk ditampilkan.")

# ================================
# 🔔 REMINDER SECTION
# ================================
st.divider()
st.markdown("## 🔔 Reminder Beasiswa yang Akan Tutup (7 Hari ke Depan)")

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

# ================================
# 📅 GANTT CHART (Timeline)
# ================================
st.divider()
st.markdown("## 🗓️ Timeline Kegiatan (Gantt Chart)")

if not df.empty:
    events = []
    for _, row in df.iterrows():
        for col, label in [("Deadline Pendaftaran", "Pendaftaran"),
                           ("Deadline Tes 1", "Tes 1"),
                           ("Deadline Tes 2", "Tes 2"),
                           ("Pengumuman", "Pengumuman")]:
            if row[col] and str(row[col]).strip():
                events.append({
                    "Beasiswa": row["Beasiswa"],
                    "Event": label,
                    "Tanggal": pd.to_datetime(row[col])
                })
    if events:
        gantt_df = pd.DataFrame(events)
        gantt_df.sort_values(by="Tanggal", inplace=True)
        fig = px.timeline(
            gantt_df,
            x_start="Tanggal",
            x_end="Tanggal",
            y="Beasiswa",
            color="Event",
            title="📅 Gantt Chart Beasiswa",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada tanggal kegiatan yang diisi.")
else:
    st.info("Belum ada data beasiswa yang tersedia.")

# ================================
# 📋 DATABASE (Editable)
# ================================
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

# ================================
# 🗑️ DELETE SECTION
# ================================
st.divider()
st.markdown("## 🗑️ Hapus Beasiswa")

if not df.empty:
    del_name = st.selectbox("Pilih Beasiswa untuk dihapus", [""] + df["Beasiswa"].tolist())
    if st.button("🗑️ Hapus Data Ini", use_container_width=True):
        if del_name:
            df = df[df["Beasiswa"] != del_name]
            save_data(df)
            st.success(f"❌ Beasiswa '{del_name}' berhasil dihapus.")
            st.rerun()

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Data tersimpan lokal (JSON) | Streamlit Offline Mode 🎓")


elif page == "🧠 IELTS Tracker":
    st.title("🧠 IELTS Progress Tracker")

    DATA_FILE_IELTS = "ielts_data.json"

    def load_ielts_data():
        if os.path.exists(DATA_FILE_IELTS):
            with open(DATA_FILE_IELTS, "r", encoding="utf-8") as f:
                data = json.load(f)
            return pd.DataFrame(data)
        else:
            return pd.DataFrame(columns=[
                "Nama User", "Tanggal Tes", "Listening", "Reading", "Writing", "Speaking",
                "Overall", "Target", "Catatan"
            ])

    def save_ielts_data(df):
        with open(DATA_FILE_IELTS, "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    df_ielts = load_ielts_data()

    st.markdown("### ➕ Tambahkan Data Tes IELTS Baru")

    with st.form("ielts_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nama_user = c1.text_input("👤 Nama User")
        tanggal = c2.date_input("📅 Tanggal Tes")

        c3, c4 = st.columns(2)
        listening = c3.number_input("🎧 Listening", 0.0, 9.0, step=0.5)
        reading = c4.number_input("📖 Reading", 0.0, 9.0, step=0.5)

        c5, c6 = st.columns(2)
        writing = c5.number_input("✍️ Writing", 0.0, 9.0, step=0.5)
        speaking = c6.number_input("🗣️ Speaking", 0.0, 9.0, step=0.5)

        overall = round((listening + reading + writing + speaking) / 4, 1)
        target = c1.number_input("🎯 Target Overall", 0.0, 9.0, 7.5, step=0.5)
        catatan = c2.text_area("📝 Catatan Tes")

        st.info(f"**Skor Overall kamu:** {overall}")

        submitted = st.form_submit_button("💾 Simpan Hasil Tes")
        if submitted:
            new_row = {
                "Nama User": nama_user,
                "Tanggal Tes": str(tanggal),
                "Listening": listening,
                "Reading": reading,
                "Writing": writing,
                "Speaking": speaking,
                "Overall": overall,
                "Target": target,
                "Catatan": catatan
            }
            df_ielts = pd.concat([df_ielts, pd.DataFrame([new_row])], ignore_index=True)
            save_ielts_data(df_ielts)
            st.success("✅ Data tes berhasil disimpan!")
            st.rerun()

    st.divider()

    if not df_ielts.empty:
        st.markdown("## 📊 Statistik & Progres IELTS")

        latest = df_ielts.sort_values("Tanggal Tes").iloc[-1]
        st.metric("📘 Latest Overall", latest["Overall"])
        st.metric("🎯 Target", latest["Target"])
        st.metric("📈 Gap", round(latest["Target"] - latest["Overall"], 1))

        # Line chart trend
        df_melt = df_ielts.melt(
            id_vars=["Tanggal Tes"], 
            value_vars=["Listening", "Reading", "Writing", "Speaking"],
            var_name="Skill", 
            value_name="Score"
        )

        fig_line = px.line(df_melt, x="Tanggal Tes", y="Score", color="Skill",
                           markers=True, title="📈 Tren Skor per Skill")
        st.plotly_chart(fig_line, use_container_width=True)

        # Progress bar vs target
        st.markdown("### 🚀 Progress vs Target")
        progress = latest["Overall"] / latest["Target"]
        st.progress(min(progress, 1.0))
        st.caption(f"{latest['Overall']} / {latest['Target']}")

        # Table editable
        st.markdown("### 📋 Database IELTS (Editable)")
        edited_df = st.data_editor(df_ielts, use_container_width=True, hide_index=True)
        if not edited_df.equals(df_ielts):
            save_ielts_data(edited_df)
            st.success("✅ Perubahan disimpan otomatis.")
            st.rerun()

        # Insight sederhana
        st.markdown("### 💡 Insight Otomatis")
        avg_scores = df_ielts[["Listening", "Reading", "Writing", "Speaking"]].mean()
        weakest = avg_scores.idxmin()
        strongest = avg_scores.idxmax()
        st.info(f"Skill terbaik kamu adalah **{strongest} ({avg_scores[strongest]:.1f})**, "
                f"dan perlu fokus lebih di **{weakest} ({avg_scores[weakest]:.1f})**.")
    else:
        st.info("Belum ada data IELTS.")

