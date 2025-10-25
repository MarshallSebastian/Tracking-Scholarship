import streamlit as st
import pandas as pd
import plotly.express as px
import json, os
from datetime import datetime

st.set_page_config(page_title="🧠 IELTS Tracker", page_icon="🧠", layout="wide")

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

    df_melt = df_ielts.melt(
        id_vars=["Tanggal Tes"], 
        value_vars=["Listening", "Reading", "Writing", "Speaking"],
        var_name="Skill", 
        value_name="Score"
    )

    fig_line = px.line(df_melt, x="Tanggal Tes", y="Score", color="Skill",
                       markers=True, title="📈 Tren Skor per Skill")
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("### 🚀 Progress vs Target")
    progress = latest["Overall"] / latest["Target"]
    st.progress(min(progress, 1.0))
    st.caption(f"{latest['Overall']} / {latest['Target']}")

    st.markdown("### 📋 Database IELTS (Editable)")
    edited_df = st.data_editor(df_ielts, use_container_width=True, hide_index=True)
    if not edited_df.equals(df_ielts):
        save_ielts_data(edited_df)
        st.success("✅ Perubahan disimpan otomatis.")
        st.rerun()

    avg_scores = df_ielts[["Listening", "Reading", "Writing", "Speaking"]].mean()
    weakest = avg_scores.idxmin()
    strongest = avg_scores.idxmax()
    st.info(f"Skill terbaik kamu: **{strongest} ({avg_scores[strongest]:.1f})**, "
            f"dan perlu fokus di **{weakest} ({avg_scores[weakest]:.1f})**.")
else:
    st.info("Belum ada data IELTS.")
