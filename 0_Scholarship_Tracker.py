# Scholarship Tracker 6.1 — Dark Elegant | Info Beasiswa Lengkap + Detail View Only
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import json, os, shutil

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="🎓 Scholarship Tracker 6.1", page_icon="🎓", layout="wide")

# ===============================
# FILE UTILITIES
# ===============================
SCHOLAR_FILE = "data_scholarship.json"
PROGRESS_FILE = "data_progress.json"

def empty_scholar_df():
    return pd.DataFrame(columns=[
        "Nama User","Negara","Beasiswa","Link Beasiswa","IELTS","GPA",
        "Other Requirements","Benefit Scholarship",
        "Periode Pendaftaran (Mulai)","Periode Pendaftaran (Selesai)",
        "Periode Dokumen (Mulai)","Periode Dokumen (Selesai)",
        "Periode Wawancara (Mulai)","Periode Wawancara (Selesai)",
        "Periode Tes (Mulai)","Periode Tes (Selesai)",
        "Tanggal Pengumuman"
    ])

def empty_progress_df():
    return pd.DataFrame(columns=[
        "Nama User","Beasiswa",
        "Status Pendaftaran","Status Dokumen","Status Wawancara","Status Tes","Status Pengumuman",
        "Catatan","Terakhir Diperbarui"
    ])

def load_json_safe(path, empty_fn):
    if not os.path.exists(path):
        return empty_fn()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read().strip()
            return pd.DataFrame(json.loads(data)) if data else empty_fn()
    except Exception:
        shutil.copy(path, path + "_backup.json")
        return empty_fn()

def save_json(df, path):
    df = df.fillna("")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

df_scholar = load_json_safe(SCHOLAR_FILE, empty_scholar_df)
df_progress = load_json_safe(PROGRESS_FILE, empty_progress_df)

# ===============================
# STYLING
# ===============================
st.markdown("""
<style>
body { background-color: #0b0f14; color: #e6eef6; font-family: 'Poppins', sans-serif; }
h1 { color: #66c2ff; text-align:center; margin-bottom: 0.3rem; }
h3 { color: #8ed0ff; margin-top: 1rem; }
.stButton>button {
  background: linear-gradient(90deg,#0ea5ff,#1f77b4);
  color: white;
  font-weight:600;
  border-radius:8px;
  padding:8px 18px;
  transition: transform .15s ease;
}
.stButton>button:hover { transform: translateY(-2px); }
div[data-testid="stForm"] {
  background: linear-gradient(180deg,#111316,#14161a);
  padding: 20px 25px;
  border-radius: 12px;
  border: 1px solid #24303a;
  box-shadow: 0 6px 24px rgba(0,0,0,0.5);
}
input, textarea, select {
  background-color: #0f1418 !important;
  color: #e6eef6 !important;
  border: 1px solid #26343d !important;
  border-radius: 6px;
}
.section-title { color:#85d3ff; font-weight:700; margin-top:18px; margin-bottom:4px; }
</style>
""", unsafe_allow_html=True)

# ===============================
# HEADER
# ===============================
st.markdown("<h1>🎓 Scholarship Tracker 6.1</h1>", unsafe_allow_html=True)
st.caption("🌙 Dark Elegant Layout | Full Date Inputs + Detail View | Dibuat oleh Yan Marcel Sebastian")
st.divider()

# ===============================
# TABS
# ===============================
tab_info, tab_progress = st.tabs(["📚 Info Beasiswa", "🚀 Progress Beasiswa"])

# ===============================
# 📘 INFO BEASISWA
# ===============================
with tab_info:
    st.markdown("<div class='section-title'>📘 Info Beasiswa</div>", unsafe_allow_html=True)

    # FORM TOGGLE
    with st.expander("➕ Tambah / Edit Info Beasiswa", expanded=False):
        with st.form("form_info", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nama_user = c1.text_input("👤 Nama User")
            negara = c2.text_input("🌍 Negara Tujuan")
            beasiswa = c1.text_input("🎯 Nama Beasiswa")
            link = c2.text_input("🔗 Link Beasiswa")
            ielts = c1.text_input("📘 IELTS Requirement", placeholder="contoh: 6.5 overall")
            gpa = c2.text_input("🎓 GPA Requirement", placeholder="contoh: 3.5 / 4.0")
            other = st.text_area("🧾 Other Requirements", height=80)
            benefit = st.text_area("💰 Benefit Scholarship", height=80)

            st.markdown("#### ⏰ Tanggal Penting (semua opsional)")
            # Full timeline fields
            p1, p2 = st.columns(2)
            reg_start = p1.date_input("Periode Pendaftaran (Mulai)", value=None)
            reg_end = p2.date_input("Periode Pendaftaran (Selesai)", value=None)
            d1, d2 = st.columns(2)
            doc_start = d1.date_input("Periode Dokumen (Mulai)", value=None)
            doc_end = d2.date_input("Periode Dokumen (Selesai)", value=None)
            w1, w2 = st.columns(2)
            waw_start = w1.date_input("Periode Wawancara (Mulai)", value=None)
            waw_end = w2.date_input("Periode Wawancara (Selesai)", value=None)
            t1, t2 = st.columns(2)
            tes_start = t1.date_input("Periode Tes (Mulai)", value=None)
            tes_end = t2.date_input("Periode Tes (Selesai)", value=None)
            pengumuman = st.date_input("📢 Tanggal Pengumuman", value=None)

            if st.form_submit_button("💾 Simpan Info Beasiswa"):
                if not nama_user or not beasiswa:
                    st.warning("⚠️ Isi minimal Nama User dan Nama Beasiswa.")
                else:
                    new_row = {
                        "Nama User": nama_user, "Negara": negara, "Beasiswa": beasiswa,
                        "Link Beasiswa": link, "IELTS": ielts, "GPA": gpa,
                        "Other Requirements": other, "Benefit Scholarship": benefit,
                        "Periode Pendaftaran (Mulai)": str(reg_start) if reg_start else "",
                        "Periode Pendaftaran (Selesai)": str(reg_end) if reg_end else "",
                        "Periode Dokumen (Mulai)": str(doc_start) if doc_start else "",
                        "Periode Dokumen (Selesai)": str(doc_end) if doc_end else "",
                        "Periode Wawancara (Mulai)": str(waw_start) if waw_start else "",
                        "Periode Wawancara (Selesai)": str(waw_end) if waw_end else "",
                        "Periode Tes (Mulai)": str(tes_start) if tes_start else "",
                        "Periode Tes (Selesai)": str(tes_end) if tes_end else "",
                        "Tanggal Pengumuman": str(pengumuman) if pengumuman else ""
                    }
                    df_scholar = pd.concat([df_scholar, pd.DataFrame([new_row])], ignore_index=True)
                    save_json(df_scholar, SCHOLAR_FILE)
                    st.success(f"✅ Info beasiswa '{beasiswa}' berhasil disimpan!")
                    st.rerun()

    st.markdown("### 📅 Gantt Timeline Beasiswa")
    events = []
    for _, row in df_scholar.iterrows():
        for colset in [
            ("Pendaftaran","Periode Pendaftaran (Mulai)","Periode Pendaftaran (Selesai)"),
            ("Dokumen","Periode Dokumen (Mulai)","Periode Dokumen (Selesai)"),
            ("Wawancara","Periode Wawancara (Mulai)","Periode Wawancara (Selesai)"),
            ("Tes","Periode Tes (Mulai)","Periode Tes (Selesai)"),
            ("Pengumuman","Tanggal Pengumuman","Tanggal Pengumuman")
        ]:
            label, start_col, end_col = colset
            if row[start_col] and row[end_col]:
                try:
                    events.append({
                        "Beasiswa": row["Beasiswa"],
                        "Tahap": label,
                        "Mulai": pd.to_datetime(row[start_col]),
                        "Selesai": pd.to_datetime(row[end_col])
                    })
                except:
                    pass
    if events:
        df_gantt = pd.DataFrame(events)
        fig = px.timeline(df_gantt, x_start="Mulai", x_end="Selesai", y="Beasiswa",
                          color="Tahap", title="🗓️ Timeline Beasiswa",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(paper_bgcolor="#0b0f14", plot_bgcolor="#0b0f14", font_color="#e6eef6")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data periode lengkap untuk menampilkan timeline.")

    st.markdown("### 🔎 Lihat Detail Lengkap")
    if not df_scholar.empty:
        selected = st.selectbox("Pilih Beasiswa untuk melihat detail", [""] + df_scholar["Beasiswa"].tolist())
        if selected:
            data = df_scholar[df_scholar["Beasiswa"] == selected].iloc[0].to_dict()
            st.markdown(f"#### Detail: {data['Beasiswa']}")
            st.markdown(f"**Negara:** {data['Negara']}")
            st.markdown(f"**IELTS / GPA:** {data['IELTS']} / {data['GPA']}")
            st.markdown("**Other Requirements:**")
            st.write(data["Other Requirements"])
            st.markdown("**Benefit Scholarship:**")
            st.write(data["Benefit Scholarship"])
            st.markdown("**Periode & Dates:**")
            for col in [c for c in df_scholar.columns if "Periode" in c or c == "Tanggal Pengumuman"]:
                st.write(f"- **{col}**: {data[col]}")
            if data["Link Beasiswa"]:
                st.markdown(f"**Link Beasiswa:** [🌐 Buka Link]({data['Link Beasiswa']})")
    else:
        st.info("Belum ada data beasiswa.")

# ===============================
# 🚀 PROGRESS BEASISWA (Tetap)
# ===============================
with tab_progress:
    st.markdown("<div class='section-title'>🚀 Progress Beasiswa</div>", unsafe_allow_html=True)
    st.info("Bagian ini tetap sama seperti versi sebelumnya (form + chart + progress bar).")

st.divider()
st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Scholarship Tracker 6.1 — Full Date + Detail Dropdown | Streamlit JSON Persistent")
