# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# -----------------------
# CONFIG PAGE
# -----------------------
st.set_page_config(page_title="🎓 Scholarship Tracker Live", page_icon="🎓", layout="wide")

# -----------------------
# READ SECRETS (service account JSON & sheet id)
# -----------------------
# On Streamlit Cloud: add 'service_account' (paste full JSON) and 'sheet_id' in Secrets
if "service_account" not in st.secrets:
    st.error("Service account JSON belum ada di Streamlit Secrets. Tambahkan 'service_account' pada Secrets.")
    st.stop()

if "sheet_id" not in st.secrets:
    st.error("Sheet ID belum ditambahkan ke Streamlit Secrets (key: 'sheet_id').")
    st.stop()

# st.secrets['service_account'] may be already parsed dict or a string
svc = st.secrets["service_account"]
if isinstance(svc, str):
    try:
        svc_dict = json.loads(svc)
    except Exception as e:
        st.error("Gagal parse JSON dari secret 'service_account'. Pastikan kamu paste JSON service account yang valid.")
        st.stop()
else:
    svc_dict = svc  # already a dict

SHEET_ID = st.secrets["sheet_id"]
SHEET_NAME = "Sheet1"  # ganti jika nama sheet berbeda

# -----------------------
# CONNECT TO GOOGLE SHEETS (gspread)
# -----------------------
try:
    # gspread helper: create client from dict
    gc = gspread.service_account_from_dict(svc_dict)
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.worksheet(SHEET_NAME)
except Exception as e:
    st.error("Gagal koneksi ke Google Sheets. Pastikan service account sudah di-share ke Sheet dan secrets benar.")
    st.exception(e)
    st.stop()

# -----------------------
# HELPERS: load & save
# -----------------------
COLUMNS = [
    "Nama User", "Negara", "Beasiswa", "Link Beasiswa",
    "IELTS", "GPA", "Other Requirements", "Benefit Scholarship",
    "Deadline Pendaftaran", "Deadline Tes 1", "Deadline Tes 2", "Pengumuman"
]

def load_data_from_sheet():
    rows = worksheet.get_all_records()
    if not rows:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.DataFrame(rows)
    # Ensure all columns exist (preserve order)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[COLUMNS]
    return df

def save_data_to_sheet(df: pd.DataFrame):
    # Convert datetimes to ISO strings to avoid serialization issues
    df2 = df.copy()
    for col in ["Deadline Pendaftaran", "Deadline Tes 1", "Deadline Tes 2", "Pengumuman"]:
        if col in df2.columns:
            df2[col] = df2[col].apply(lambda x: x.isoformat() if isinstance(x, (pd.Timestamp, datetime)) else x)
    # prepare values (header + rows)
    values = [df2.columns.tolist()] + df2.fillna("").values.tolist()
    worksheet.clear()
    worksheet.update(values)

# -----------------------
# LOAD initial data
# -----------------------
df = load_data_from_sheet()

# put a copy in session_state so data_editor can update and we can compare
if "df" not in st.session_state:
    st.session_state.df = df.copy()

# -----------------------
# UI: header and form
# -----------------------
st.markdown("<h1 style='text-align:center;color:#1a5276;'>🎓 Scholarship Tracker Live</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#5f6368;'>Data tersimpan di Google Sheet — update realtime & permanen.</p>", unsafe_allow_html=True)
st.divider()

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
    pengumuman = col2.date_input("Tanggal Pengumuman", value=None)

    submitted = st.form_submit_button("💾 Simpan Data")
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
                "Deadline Pendaftaran": deadline,
                "Deadline Tes 1": tes1,
                "Deadline Tes 2": tes2,
                "Pengumuman": pengumuman
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            # Save to sheet
            try:
                save_data_to_sheet(st.session_state.df)
                st.success(f"✅ Beasiswa '{beasiswa}' berhasil disimpan ke Google Sheet.")
            except Exception as e:
                st.error("Gagal menyimpan ke Google Sheet.")
                st.exception(e)
            st.experimental_rerun()

st.divider()

# -----------------------
# Visualization / Stats
# -----------------------
# Refresh df from session
df = st.session_state.df.copy()

if not df.empty:
    st.markdown("## 📈 Statistik & Progress")
    c1, c2 = st.columns(2)
    if df["Negara"].notna().any():
        fig_country = px.bar(df.groupby("Negara").size().reset_index(name="Jumlah"),
                             x="Negara", y="Jumlah", title="📍 Jumlah Beasiswa per Negara", text_auto=True)
        fig_country.update_traces(marker_color="#1a5276")
        c1.plotly_chart(fig_country, use_container_width=True)
    if df["Nama User"].notna().any():
        fig_user = px.pie(df, names="Nama User", title="👥 Distribusi Beasiswa per User")
        c2.plotly_chart(fig_user, use_container_width=True)
else:
    st.info("Belum ada data untuk ditampilkan.")

# -----------------------
# Reminder (Deadline)
# -----------------------
st.divider()
st.markdown("## 🔔 Reminder: Beasiswa Segera Tutup")
if not df.empty:
    today = datetime.now().date()
    # convert column to date if possible
    df["Deadline Pendaftaran"] = pd.to_datetime(df["Deadline Pendaftaran"], errors="coerce").dt.date
    df["Days Left"] = (df["Deadline Pendaftaran"] - today).apply(lambda x: x.days if pd.notnull(x) else None)
    upcoming = df[df["Days Left"].between(0, 7, inclusive="both")]
    if not upcoming.empty:
        st.success(f"🎯 Ada {len(upcoming)} beasiswa yang akan tutup dalam 7 hari.")
        st.dataframe(upcoming[["Nama User", "Beasiswa", "Negara", "Deadline Pendaftaran", "Days Left"]], use_container_width=True)
    else:
        st.info("Tidak ada yang akan tutup dalam 7 hari.")
else:
    st.info("Belum ada data.")

# -----------------------
# Timeline / Calendar-style
# -----------------------
st.divider()
st.markdown("## 📅 Timeline Beasiswa")
events = []
for _, row in df.iterrows():
    for col, label in [("Deadline Pendaftaran", "Deadline"), ("Deadline Tes 1", "Tes 1"),
                       ("Deadline Tes 2", "Tes 2"), ("Pengumuman", "Pengumuman")]:
        val = row.get(col, None)
        if pd.notnull(val) and val != "":
            events.append({"Tanggal": val, "Event": label, "Beasiswa": row.get("Beasiswa", "")})
if events:
    cal_df = pd.DataFrame(events)
    cal_df["Tanggal"] = pd.to_datetime(cal_df["Tanggal"], errors="coerce")
    cal_df = cal_df.sort_values("Tanggal")
    fig_tl = px.timeline(cal_df, x_start="Tanggal", x_end="Tanggal", y="Beasiswa", color="Event", title="🗓️ Timeline")
    fig_tl.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_tl, use_container_width=True)
else:
    st.info("Belum ada tanggal terdaftar untuk timeline.")

# -----------------------
# Editable data table (save on change)
# -----------------------
st.divider()
st.markdown("## 📋 Database Beasiswa (Editable)")

if not df.empty:
    edited = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="fixed", key="editor")
    # if changed, save back to sheet
    if not edited.equals(df):
        try:
            save_data_to_sheet(edited)
            st.session_state.df = edited
            st.success("✅ Perubahan disimpan ke Google Sheet.")
            st.experimental_rerun()
        except Exception as e:
            st.error("Gagal menyimpan perubahan ke Google Sheet.")
            st.exception(e)
else:
    st.info("Belum ada data. Tambahkan beasiswa di atas.")

# -----------------------
# Delete section
# -----------------------
st.divider()
st.markdown("## 🗑️ Hapus Beasiswa")
if not df.empty:
    del_name = st.selectbox("Pilih beasiswa untuk dihapus", [""] + df["Beasiswa"].tolist())
    if st.button("Hapus"):
        if del_name:
            df2 = df[df["Beasiswa"] != del_name].reset_index(drop=True)
            try:
                save_data_to_sheet(df2)
                st.session_state.df = df2
                st.success(f"✅ Beasiswa '{del_name}' dihapus dari Google Sheet.")
                st.experimental_rerun()
            except Exception as e:
                st.error("Gagal hapus di Google Sheet.")
                st.exception(e)
else:
    st.info("Belum ada data yang bisa dihapus.")

st.divider()
st.caption("💡 Live Google Sheet sync — semua update tersimpan permanen dan realtime.")
