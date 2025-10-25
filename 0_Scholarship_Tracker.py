import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import json, os

# ================================
# ⚙️ PAGE CONFIG
# ================================
st.set_page_config(page_title="🎓 Scholarship Tracker 3.0", page_icon="🎓", layout="wide")

# ================================
# 💾 PERSISTENT DATA
# ================================
DATA_FILE = "data_scholarship.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "Nama User", "Negara", "Beasiswa", "Link Beasiswa", "IELTS", "GPA",
            "Other Requirements", "Benefit Scholarship",
            "Periode Pendaftaran (Mulai)", "Periode Pendaftaran (Selesai)",
            "Periode Dokumen (Mulai)", "Periode Dokumen (Selesai)",
            "Periode Wawancara (Mulai)", "Periode Wawancara (Selesai)",
            "Periode Tes (Mulai)", "Periode Tes (Selesai)",
            "Tanggal Pengumuman"
        ])

def save_data(df):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

df = load_data()

# ================================
# 🎨 STYLING
# ================================
st.markdown("""
<style>
    body {
        background-color: #f8fafc;
        font-family: "Poppins", sans-serif;
    }
    .stTextInput, .stTextArea, .stDateInput {
        border-radius: 8px !important;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 25px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #135a8d;
    }
    .dataframe td {
        white-space: normal !important;
        word-wrap: break-word !important;
        font-size: 13px !important;
    }
    table {
        border-collapse: collapse;
        border: 1px solid #ddd;
    }
    tr:nth-child(even) {background-color: #f9f9f9;}
    tr:hover {background-color: #eaf2f8;}
</style>
""", unsafe_allow_html=True)

# ================================
# 🎓 HEADER
# ================================
st.markdown("<h1 style='text-align:center;'>🎓 Scholarship Tracker 3.0</h1>", unsafe_allow_html=True)
st.caption("📍 Data tersimpan otomatis secara lokal (JSON) — tetap aman walau direfresh 🔒")
st.divider()

# ================================
# ➕ FORM INPUT
# ================================
st.subheader("➕ Tambahkan / Update Data Beasiswa")

with st.form("form_beasiswa", clear_on_submit=True):
    st.markdown("Masukkan detail lengkap beasiswa di bawah ini:")

    c1, c2 = st.columns(2)
    nama_user = c1.text_input("👤 Nama User")
    negara = c2.text_input("🌍 Negara Tujuan")

    beasiswa = c1.text_input("🎯 Nama Beasiswa")
    link = c2.text_input("🔗 Link Beasiswa")

    c3, c4 = st.columns(2)
    ielts = c3.text_input("📘 IELTS Requirement", placeholder="contoh: 6.5 overall")
    gpa = c4.text_input("🎓 GPA Requirement", placeholder="contoh: 3.5 / 4.0")

    c5, c6 = st.columns(2)
    other = c5.text_area("🧾 Other Requirements", height=100)
    benefit = c6.text_area("💰 Benefit Scholarship", height=100)

    st.markdown("#### ⏰ Periode & Deadline Penting")

    st.markdown("**🗓️ Pendaftaran**")
    p1, p2 = st.columns(2)
    start_reg = p1.date_input("Mulai Pendaftaran")
    end_reg = p2.date_input("Selesai Pendaftaran")

    st.markdown("**📂 Dokumen**")
    d1, d2 = st.columns(2)
    start_doc = d1.date_input("Mulai Pengumpulan Dokumen")
    end_doc = d2.date_input("Selesai Pengumpulan Dokumen")

    st.markdown("**🎤 Wawancara**")
    w1, w2 = st.columns(2)
    start_interview = w1.date_input("Mulai Wawancara")
    end_interview = w2.date_input("Selesai Wawancara")

    st.markdown("**🧪 Tes Beasiswa**")
    t1, t2 = st.columns(2)
    start_test = t1.date_input("Mulai Tes")
    end_test = t2.date_input("Selesai Tes")

    st.markdown("**📢 Pengumuman**")
    pengumuman = st.date_input("Tanggal Pengumuman")

    submitted = st.form_submit_button("💾 Simpan Data Beasiswa")

    if submitted:
        if not nama_user or not beasiswa:
            st.warning("⚠️ Isi minimal Nama User dan Nama Beasiswa!")
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
                "Periode Pendaftaran (Mulai)": str(start_reg),
                "Periode Pendaftaran (Selesai)": str(end_reg),
                "Periode Dokumen (Mulai)": str(start_doc),
                "Periode Dokumen (Selesai)": str(end_doc),
                "Periode Wawancara (Mulai)": str(start_interview),
                "Periode Wawancara (Selesai)": str(end_interview),
                "Periode Tes (Mulai)": str(start_test),
                "Periode Tes (Selesai)": str(end_test),
                "Tanggal Pengumuman": str(pengumuman)
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan!")
            st.rerun()

# ================================
# 🔔 REMINDER
# ================================
st.divider()
st.markdown("## 🔔 Reminder Beasiswa yang Akan Tutup dalam 7 Hari")

if not df.empty:
    today = date.today()
    df["Periode Pendaftaran (Selesai)"] = pd.to_datetime(df["Periode Pendaftaran (Selesai)"], errors="coerce").dt.date
    df["Days Left"] = (df["Periode Pendaftaran (Selesai)"] - today).apply(lambda x: x.days if pd.notnull(x) else None)
    soon = df[df["Days Left"].between(0, 7, inclusive="both")]

    if not soon.empty:
        st.success(f"🎯 Ada {len(soon)} beasiswa yang akan tutup dalam 7 hari!")
        st.dataframe(
            soon[["Nama User", "Beasiswa", "Negara", "Periode Pendaftaran (Selesai)", "Days Left"]],
            use_container_width=True, hide_index=True
        )
    else:
        st.info("✅ Tidak ada beasiswa yang akan tutup dalam 7 hari.")
else:
    st.info("Belum ada data untuk reminder.")

# ================================
# 📊 GANTT CHART
# ================================
st.divider()
st.markdown("## 🗓️ Timeline Gantt Chart (Berdasarkan Negara)")

if not df.empty:
    selected_country = st.selectbox("🌍 Pilih Negara", sorted(df["Negara"].dropna().unique()))
    df_country = df[df["Negara"] == selected_country]

    if not df_country.empty:
        events = []
        for _, row in df_country.iterrows():
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
                color="Tahapan", title=f"📅 Timeline Beasiswa ({selected_country})",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada periode yang lengkap untuk ditampilkan.")
    else:
        st.warning("Tidak ada data untuk negara ini.")
else:
    st.info("Belum ada data untuk ditampilkan.")

# ================================
# 📋 DATABASE
# ================================
st.divider()
st.markdown("## 📋 Database Beasiswa (Editable)")

if not df.empty:
    st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="db_table"
    )
else:
    st.info("Belum ada data yang bisa ditampilkan.")

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Scholarship Tracker 3.0 | Streamlit + JSON Persistent")
