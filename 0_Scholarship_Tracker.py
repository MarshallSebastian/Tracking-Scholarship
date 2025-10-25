import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import json, os

# ================================
# ⚙️ PAGE CONFIG
# ================================
st.set_page_config(page_title="🎓 Scholarship Tracker 3.5", page_icon="🎓", layout="wide")

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

def convert_dates_to_str(df):
    """Konversi semua kolom tanggal ke string sebelum disimpan ke JSON"""
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: x.isoformat() if isinstance(x, (date, datetime)) else x
        )
    return df

def save_data(df):
    df = convert_dates_to_str(df)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

df = load_data()
required_cols = [
    "Nama User", "Negara", "Beasiswa", "Link Beasiswa", "IELTS", "GPA",
    "Other Requirements", "Benefit Scholarship",
    "Periode Pendaftaran (Mulai)", "Periode Pendaftaran (Selesai)",
    "Periode Dokumen (Mulai)", "Periode Dokumen (Selesai)",
    "Periode Wawancara (Mulai)", "Periode Wawancara (Selesai)",
    "Periode Tes (Mulai)", "Periode Tes (Selesai)", "Tanggal Pengumuman"
]
for c in required_cols:
    if c not in df.columns:
        df[c] = ""

# ================================
# 🎨 STYLING
# ================================
st.markdown("""
<style>
body { background-color: #f8fafc; font-family: 'Poppins', sans-serif; }
h1, h2, h3, h4 { color: #1f4e79; }
</style>
""", unsafe_allow_html=True)

# ================================
# 🎓 HEADER
# ================================
st.markdown("<h1 style='text-align:center;'>🎓 Scholarship Tracker 3.5</h1>", unsafe_allow_html=True)
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
            try:
                return st.date_input(label, value=None, key=label)
            except:
                return None

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
# 📋 DATABASE (Editable + Clickable Link)
# ================================
st.divider()
st.markdown("## 📋 Database Beasiswa (Editable & Clickable Link)")

if not df.empty:
    df_edit = df.copy()

    # Pastikan tanggal bisa diubah
    date_cols = [
        "Periode Pendaftaran (Mulai)", "Periode Pendaftaran (Selesai)",
        "Periode Dokumen (Mulai)", "Periode Dokumen (Selesai)",
        "Periode Wawancara (Mulai)", "Periode Wawancara (Selesai)",
        "Periode Tes (Mulai)", "Periode Tes (Selesai)", "Tanggal Pengumuman"
    ]
    for c in date_cols:
        df_edit[c] = pd.to_datetime(df_edit[c], errors="coerce").dt.date

    edited_df = st.data_editor(
        df_edit,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        height=420,
        column_config={
            "Link Beasiswa": st.column_config.TextColumn("Link Beasiswa (klik di bawah untuk akses)"),
        }
    )

    # Convert tanggal ke string sebelum save
    if not edited_df.equals(df):
        save_data(edited_df)
        st.success("✅ Perubahan disimpan otomatis.")
        st.rerun()

    # Tambahkan versi clickable link di bawah tabel
    st.markdown("### 🌐 Link Beasiswa Aktif")
    df_links = df[["Beasiswa", "Link Beasiswa"]].dropna()
    if not df_links.empty:
        df_links["Link Beasiswa"] = df_links["Link Beasiswa"].apply(
            lambda x: f'<a href="{x}" target="_blank" style="color:#1f77b4;text-decoration:none;">🌐 Buka Link</a>' if x else "-"
        )
        st.markdown(df_links.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.info("Belum ada data yang bisa ditampilkan.")

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Scholarship Tracker 3.5 | Streamlit + JSON Persistent | Editable Dates + Clickable Links")
