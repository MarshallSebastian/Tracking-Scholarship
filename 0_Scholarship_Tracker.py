# Scholarship Tracker 6.0 — Dark Elegant, Info Beasiswa & Progress (Full)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import json, os, shutil

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="🎓 Scholarship Tracker 6.0", page_icon="🎓", layout="wide")

# ===============================
# FILES / DATA UTIL
# ===============================
SCHOLAR_FILE = "data_scholarship.json"
PROGRESS_FILE = "data_progress.json"
BACKUP_SUFFIX = "_backup.json"

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

def load_json_safely(path, empty_fn):
    if not os.path.exists(path):
        return empty_fn()
    try:
        with open(path, "r", encoding="utf-8") as f:
            s = f.read().strip()
            if not s:
                return empty_fn()
            return pd.DataFrame(json.loads(s))
    except Exception as e:
        # backup corrupt file and return empty DF
        try:
            shutil.copy(path, path + BACKUP_SUFFIX)
        except:
            pass
        st.warning(f"⚠️ File `{os.path.basename(path)}` corrupt — backup dibuat, memulai kosong.")
        return empty_fn()

def save_json_safely(df, path):
    # ensure no datetime objects (json can't serialize dates)
    df_to_save = df.copy()
    for col in df_to_save.columns:
        df_to_save[col] = df_to_save[col].apply(
            lambda x: x.isoformat() if isinstance(x, (date, datetime)) else ("" if pd.isna(x) else x)
        )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(df_to_save.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

# load dataframes
df_scholar = load_json_safely(SCHOLAR_FILE, empty_scholar_df)
df_progress = load_json_safely(PROGRESS_FILE, empty_progress_df)

# ensure columns exist (kitten-safe)
for c in empty_scholar_df().columns:
    if c not in df_scholar.columns:
        df_scholar[c] = ""
for c in empty_progress_df().columns:
    if c not in df_progress.columns:
        df_progress[c] = ""

# ===============================
# STYLES (Dark Elegant)
# ===============================
st.markdown("""
<style>
/* Page */
body { background-color: #0b0f14; color: #e6eef6; font-family: 'Poppins', sans-serif; }

/* Headings */
h1 { color: #66c2ff; text-align:center; margin-bottom: 0.1rem; }
h2 { color: #cfeeff; }
.small-caption { color: #9fb7c9; font-size:12px; margin-top: -8px; }

/* Form card */
div[data-testid="stForm"] {
  background: linear-gradient(180deg, #111316 0%, #14161a 100%);
  padding: 18px 22px;
  border-radius: 12px;
  border: 1px solid #24303a;
  box-shadow: 0 6px 24px rgba(0,0,0,0.6);
}

/* Inputs */
input, textarea, select {
  background-color: #0f1418 !important;
  color: #e6eef6 !important;
  border: 1px solid #26343d !important;
  border-radius: 6px;
}
input::placeholder, textarea::placeholder { color: #94a7b7 !important; }

/* Buttons */
.stButton>button {
  background: linear-gradient(90deg,#0ea5ff,#1f77b4);
  color: white;
  font-weight:600;
  border-radius:8px;
  padding:8px 18px;
  transition: transform .15s ease;
}
.stButton>button:hover { transform: translateY(-2px); }

/* Tables - fixed layout, ellipsis */
.data-table {
  width: 100%;
  border-collapse: collapse;
  border-radius: 10px;
  overflow: hidden;
  font-size: 13px;
  background: #0f1418;
  box-shadow: 0 6px 18px rgba(0,0,0,0.6);
  table-layout: fixed;
}
.data-table th {
  background: linear-gradient(90deg,#0f4a73,#134a6b);
  color: #e8f7ff;
  padding: 10px;
  text-align: left;
  font-weight:600;
}
.data-table td {
  padding: 9px 10px;
  border-bottom: 1px solid #18242a;
  color: #dbeefb;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.data-table tr:nth-child(even) { background: #0d1215; }
.data-table tr:hover { background: #18242a; }

/* small buttons inside table */
.table-btn {
  background: transparent;
  border: 1px solid #2d8fca;
  color: #aee2ff;
  padding: 4px 8px;
  border-radius: 6px;
}
.table-btn:hover { background: rgba(46, 150, 200, 0.08); }

/* section title */
.section-title { color:#85d3ff; font-weight:700; margin-top:18px; margin-bottom:4px; }

/* compact layout for small captions */
.compact { font-size:12px; color:#9fb7c9; }
</style>
""", unsafe_allow_html=True)

# ===============================
# HEADER
# ===============================
st.markdown("<h1>🎓 Scholarship Tracker 6.0</h1>", unsafe_allow_html=True)
st.markdown("<div class='small-caption'>Dark Elegant · Info Beasiswa & Progress · Toggle forms · Gantt · Charts · Read-only tables</div>", unsafe_allow_html=True)
st.divider()

# ===============================
# TABS: Info Beasiswa | Progress
# ===============================
tab_info, tab_progress = st.tabs(["📚 Info Beasiswa", "🚀 Progress Beasiswa"])

# -------------------------------
# TAB: INFO BEASISWA
# -------------------------------
with tab_info:
    st.markdown("<div class='section-title'>📘 Info Beasiswa (Form, Gantt, Detail)</div>", unsafe_allow_html=True)
    st.write("")  # spacing

    # Form toggle using expander (hide/unhide)
    with st.expander("➕ Tambah / Edit Info Beasiswa (klik untuk buka)", expanded=False):
        with st.form("form_info", clear_on_submit=True):
            c1, c2 = st.columns([1,1])
            nama_user = c1.text_input("👤 Nama User", placeholder="Contoh: Yan Marcel")
            negara = c2.text_input("🌍 Negara Tujuan", placeholder="Contoh: UK")
            beasiswa = c1.text_input("🎯 Nama Beasiswa", placeholder="Contoh: Chevening Scholarship")
            link = c2.text_input("🔗 Link Beasiswa (optional)")
            ielts = c1.text_input("📘 IELTS Requirement", placeholder="contoh: 6.5")
            gpa = c2.text_input("🎓 GPA Requirement", placeholder="contoh: 3.5 / 4.0")
            other = st.text_area("🧾 Other Requirements (singkat)", height=80)
            benefit = st.text_area("💰 Benefit Scholarship (singkat)", height=80)

            st.markdown("**⏰ Periode / Deadline (opsional)**")
            p1, p2 = st.columns(2)
            start_reg = p1.date_input("Mulai Pendaftaran", value=None)
            end_reg = p2.date_input("Selesai Pendaftaran", value=None)

            # minimal fields validation on submit
            if st.form_submit_button("💾 Simpan Info Beasiswa"):
                if not nama_user or not beasiswa:
                    st.warning("Isi minimal Nama User dan Nama Beasiswa.")
                else:
                    row = {
                        "Nama User": nama_user, "Negara": negara, "Beasiswa": beasiswa,
                        "Link Beasiswa": link, "IELTS": ielts, "GPA": gpa,
                        "Other Requirements": other, "Benefit Scholarship": benefit,
                        "Periode Pendaftaran (Mulai)": str(start_reg) if start_reg else "",
                        "Periode Pendaftaran (Selesai)": str(end_reg) if end_reg else "",
                        "Periode Dokumen (Mulai)": "", "Periode Dokumen (Selesai)": "",
                        "Periode Wawancara (Mulai)": "", "Periode Wawancara (Selesai)": "",
                        "Periode Tes (Mulai)": "", "Periode Tes (Selesai)": "",
                        "Tanggal Pengumuman": ""
                    }
                    df_scholar = pd.concat([df_scholar, pd.DataFrame([row])], ignore_index=True)
                    save_json_safely(df_scholar, SCHOLAR_FILE)
                    st.success(f"✅ Info beasiswa '{beasiswa}' tersimpan.")
                    st.experimental_rerun()

    st.markdown("### 📅 Gantt Timeline (Beasiswa dengan periode lengkap)")
    # prepare events for Gantt (only if start and end present)
    events = []
    for _, r in df_scholar.iterrows():
        # iterate phases with their columns if present
        phases = [
            ("Pendaftaran","Periode Pendaftaran (Mulai)","Periode Pendaftaran (Selesai)"),
            ("Dokumen","Periode Dokumen (Mulai)","Periode Dokumen (Selesai)"),
            ("Wawancara","Periode Wawancara (Mulai)","Periode Wawancara (Selesai)"),
            ("Tes","Periode Tes (Mulai)","Periode Tes (Selesai)"),
            ("Pengumuman","Tanggal Pengumuman","Tanggal Pengumuman")
        ]
        for phase, sc, ec in phases:
            if r.get(sc) and r.get(ec) and str(r.get(sc)).strip() and str(r.get(ec)).strip():
                try:
                    events.append({
                        "Beasiswa": r["Beasiswa"],
                        "Tahap": phase,
                        "Mulai": pd.to_datetime(r[sc]),
                        "Selesai": pd.to_datetime(r[ec])
                    })
                except:
                    pass
    if events:
        gantt_df = pd.DataFrame(events).sort_values("Mulai")
        fig = px.timeline(gantt_df, x_start="Mulai", x_end="Selesai", y="Beasiswa",
                          color="Tahap", title="🗓️ Gantt Timeline Beasiswa",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(paper_bgcolor="#0b0f14", plot_bgcolor="#0b0f14", font_color="#e6eef6", height=420)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada periode lengkap untuk Gantt. Isi periode di Info Beasiswa agar tampil.")

    st.markdown("<div class='section-title'>📋 Detail Beasiswa (klik View untuk lihat lengkap)</div>", unsafe_allow_html=True)

    # prepare table view: no wrap, ellipsis, View button for full details
    if not df_scholar.empty:
        df_show = df_scholar.copy()
        # clickable link short text
        df_show["Link Beasiswa"] = df_show["Link Beasiswa"].apply(lambda x: f'<a href="{x}" target="_blank" style="color:#66c2ff;">🌐 Link</a>' if x else "-")
        # pick columns to display (compact)
        display_cols = ["Nama User","Negara","Beasiswa","Link Beasiswa","IELTS","GPA","Other Requirements","Benefit Scholarship","Periode Pendaftaran (Selesai)"]
        df_show = df_show[display_cols].fillna("")

        # render table HTML
        html_table = df_show.to_html(escape=False, index=False, classes="data-table")
        st.markdown(html_table, unsafe_allow_html=True)

        # "View" controls under table: select scholarship to view full text
        st.markdown("**🔎 Lihat detail lengkap**")
        options = [""] + df_scholar["Beasiswa"].tolist()
        sel = st.selectbox("Pilih Beasiswa untuk melihat detail", options, key="select_view_info")
        if sel:
            row = df_scholar[df_scholar["Beasiswa"] == sel].iloc[0].to_dict()
            with st.expander(f"Detail: {sel}", expanded=True):
                st.markdown(f"**Negara:** {row.get('Negara','')}")
                st.markdown(f"**IELTS / GPA:** {row.get('IELTS','')} / {row.get('GPA','')}")
                st.markdown("**Other Requirements:**")
                st.write(row.get("Other Requirements",""))
                st.markdown("**Benefit Scholarship:**")
                st.write(row.get("Benefit Scholarship",""))
                st.markdown("**Periode & Dates:**")
                for key in df_scholar.columns:
                    if "Periode" in key or key == "Tanggal Pengumuman":
                        st.write(f"- **{key}**: {row.get(key,'')}")
                st.markdown(f"**Link Beasiswa:** {row.get('Link Beasiswa','')}")
    else:
        st.info("Belum ada data beasiswa.")

# -------------------------------
# TAB: PROGRESS
# -------------------------------
with tab_progress:
    st.markdown("<div class='section-title'>🚀 Progress Beasiswa (Form, Charts, Table)</div>", unsafe_allow_html=True)

    # Form toggle
    with st.expander("➕ Tambah Progress (klik untuk buka)", expanded=False):
        with st.form("form_progress2", clear_on_submit=True):
            p_user = st.text_input("👤 Nama User (progress)")
            p_beasiswa = st.selectbox("🎓 Pilih Beasiswa", [""] + df_scholar["Beasiswa"].tolist())
            c1, c2, c3 = st.columns(3)
            s_daftar = c1.selectbox("📨 Pendaftaran", ["Belum","Proses","Selesai"])
            s_dok = c2.selectbox("📂 Dokumen", ["Belum","Proses","Selesai"])
            s_waw = c3.selectbox("🎤 Wawancara", ["Belum","Proses","Selesai"])
            c4, c5 = st.columns(2)
            s_test = c4.selectbox("🧪 Tes", ["Belum","Proses","Selesai"])
            s_peng = c5.selectbox("📢 Pengumuman", ["Belum","Proses","Selesai"])
            note = st.text_area("🧾 Catatan", height=80)
            if st.form_submit_button("💾 Simpan Progress"):
                if not p_user or not p_beasiswa:
                    st.warning("Lengkapi Nama User dan Pilih Beasiswa.")
                else:
                    newp = {
                        "Nama User": p_user, "Beasiswa": p_beasiswa,
                        "Status Pendaftaran": s_daftar, "Status Dokumen": s_dok,
                        "Status Wawancara": s_waw, "Status Tes": s_test,
                        "Status Pengumuman": s_peng, "Catatan": note,
                        "Terakhir Diperbarui": str(date.today())
                    }
                    df_progress = pd.concat([df_progress, pd.DataFrame([newp])], ignore_index=True)
                    save_json_safely(df_progress, PROGRESS_FILE)
                    st.success("✅ Progress tersimpan.")
                    st.experimental_rerun()

    # Charts area
    st.markdown("### 📈 Progress Overview & Beasiswa Progress")
    if not df_progress.empty:
        # status distribution pie
        melt = df_progress.melt(id_vars=["Beasiswa","Nama User"], value_vars=[
            "Status Pendaftaran","Status Dokumen","Status Wawancara","Status Tes","Status Pengumuman"
        ], var_name="Tahap", value_name="Status")
        dist = melt.groupby("Status").size().reset_index(name="Jumlah")
        fig_pie = px.pie(dist, names="Status", values="Jumlah", title="🔵 Distribusi Status (Semua Tahap)")
        fig_pie.update_layout(paper_bgcolor="#0b0f14", plot_bgcolor="#0b0f14", font_color="#e6eef6")
        st.plotly_chart(fig_pie, use_container_width=True)

        # progress percent per scholarship (average of stages per latest record per scholarship-user)
        # compute percent complete per row
        def pct_complete(row):
            stages = [
                row.get("Status Pendaftaran",""), row.get("Status Dokumen",""),
                row.get("Status Wawancara",""), row.get("Status Tes",""), row.get("Status Pengumuman","")
            ]
            done = sum(1 for s in stages if str(s).lower()=="selesai")
            return int(round(done / len(stages) * 100))
        # for readability compute latest progress per beasiswa
        latest = df_progress.copy()
        latest["Terakhir Diperbarui_dt"] = pd.to_datetime(latest["Terakhir Diperbarui"], errors="coerce")
        latest = latest.sort_values("Terakhir Diperbarui_dt").groupby(["Beasiswa","Nama User"]).tail(1)
        latest["Percent"] = latest.apply(pct_complete, axis=1)
        # avg percent per beasiswa
        avg_pct = latest.groupby("Beasiswa", as_index=False)["Percent"].mean().sort_values("Percent", ascending=False)
        if not avg_pct.empty:
            fig_bar = px.bar(avg_pct, x="Percent", y="Beasiswa", orientation="h",
                             title="📊 Rata-rata Percent Progress per Beasiswa", text="Percent",
                             color="Percent", color_continuous_scale="tealrose")
            fig_bar.update_layout(paper_bgcolor="#0b0f14", plot_bgcolor="#0b0f14", font_color="#e6eef6", height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Belum ada data progress untuk chart.")

    # Progress table (detailed)
    st.markdown("<div class='section-title'>📋 Detail Progress</div>", unsafe_allow_html=True)
    if not df_progress.empty:
        df_prog_show = df_progress.copy()
        df_prog_show = df_prog_show[["Nama User","Beasiswa","Status Pendaftaran","Status Dokumen","Status Wawancara","Status Tes","Status Pengumuman","Terakhir Diperbarui"]]
        st.markdown(df_prog_show.to_html(escape=False, index=False, classes="data-table"), unsafe_allow_html=True)
    else:
        st.info("Belum ada progress yang tercatat.")

# ===============================
# BOTTOM: DELETE utilities
# ===============================
st.divider()
st.markdown("## ⚠️ Delete / Cleanup (Use Carefully)")
c1, c2 = st.columns(2)
with c1:
    if not df_scholar.empty:
        to_del = st.selectbox("Hapus Beasiswa (pilih)", [""] + df_scholar["Beasiswa"].tolist(), key="del1")
        if st.button("❌ Hapus Beasiswa (aman)"):
            if to_del:
                df_scholar = df_scholar[df_scholar["Beasiswa"] != to_del]
                save_json_safely(df_scholar, SCHOLAR_FILE)
                # also remove progress rows for that scholarship
                df_progress = df_progress[df_progress["Beasiswa"] != to_del]
                save_json_safely(df_progress, PROGRESS_FILE)
                st.success(f"Beasiswa '{to_del}' dan progress terkait dihapus.")
                st.experimental_rerun()
with c2:
    if st.button("🔁 Reset All Data (backup dibuat)"):
        if os.path.exists(SCHOLAR_FILE):
            shutil.copy(SCHOLAR_FILE, SCHOLAR_FILE + BACKUP_SUFFIX)
            os.remove(SCHOLAR_FILE)
        if os.path.exists(PROGRESS_FILE):
            shutil.copy(PROGRESS_FILE, PROGRESS_FILE + BACKUP_SUFFIX)
            os.remove(PROGRESS_FILE)
        st.success("Semua data di-reset. Backup dibuat.")
        st.experimental_rerun()

st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Scholarship Tracker 6.0 — Dark Elegant · Info & Progress")
