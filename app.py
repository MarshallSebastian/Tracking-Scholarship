import streamlit as st
import pandas as pd

# =====================================
# 🧠 Session Database (tanpa CSV)
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
st.set_page_config(page_title="Scholarship Data", page_icon="📋", layout="wide")

st.markdown("<h1 style='text-align:center; color:#1a5276;'>📋 Scholarship Database</h1>", unsafe_allow_html=True)
st.caption("Tambah, edit, dan kelola data beasiswa kamu langsung di sini.")
st.divider()

# =====================================
# ➕ Form Tambah Data
# =====================================
with st.expander("➕ Tambahkan Beasiswa Baru"):
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nama_user = col1.text_input("Nama User")
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
            if nama_user and beasiswa:
                new_row = pd.DataFrame([{
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
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                st.success(f"✅ Beasiswa '{beasiswa}' berhasil ditambahkan!")
                st.session_state.refresh = True
            else:
                st.warning("Isi minimal nama user dan nama beasiswa!")

# =====================================
# 📋 Tabel Data (Editable)
# =====================================
st.divider()
st.subheader("📋 Data Beasiswa (Langsung Bisa Diedit)")

if not df.empty:
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        key="editable_table",
        num_rows="fixed",
        column_config={
            "Link Beasiswa": st.column_config.LinkColumn("Link Beasiswa"),
            "Benefit Scholarship": st.column_config.TextColumn("Benefit Scholarship", width="medium"),
            "Other Requirements": st.column_config.TextColumn("Other Requirements", width="medium")
        }
    )
    st.session_state.data = edited_df
else:
    st.info("Belum ada data beasiswa. Tambahkan data di atas dulu ya!")

# =====================================
# 🗑️ Hapus Data
# =====================================
st.divider()
with st.expander("🗑️ Hapus Beasiswa"):
    if not df.empty:
        del_name = st.selectbox("Pilih Beasiswa yang akan dihapus", [""] + df["Beasiswa"].tolist())
        if st.button("Hapus Data"):
            if del_name:
                st.session_state.data = st.session_state.data[df["Beasiswa"] != del_name]
                st.success(f"❌ Beasiswa '{del_name}' berhasil dihapus.")
    else:
        st.info("Belum ada data yang bisa dihapus.")

st.caption("💡 Dibuat oleh Yan Marcel Sebastian | Editable Data Dashboard tanpa file CSV")

if st.session_state.refresh:
    st.session_state.refresh = False
    st.experimental_rerun()
