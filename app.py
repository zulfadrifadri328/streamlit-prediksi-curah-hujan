import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ======================================
# KONFIGURASI HALAMAN
# ======================================
st.set_page_config(
    page_title="Dashboard Prediksi Curah Hujan",
    page_icon="🌧️",
    layout="wide"
)

# ======================================
# FUNGSI KATEGORI HUJAN
# ======================================
def kategori_hujan(nilai):
    if nilai < 5:
        return "Rendah"
    elif nilai < 20:
        return "Sedang"
    else:
        return "Tinggi"

# ======================================
# HEADER
# ======================================
st.markdown(
    """
    <h1 style='text-align: center;'>🌧️ Dashboard Hasil Prediksi Curah Hujan</h1>
    <p style='text-align: center; color: grey; font-size: 16px;'>
        Visualisasi hasil prediksi ConvLSTM dalam bentuk numerik dan kategori
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ======================================
# LOAD DATA
# ======================================
@st.cache_data
def load_hasil():
    return pd.read_csv("hasil_prediksi_kategori_convlstm.csv")

data = load_hasil()

# ======================================
# SIDEBAR
# ======================================
st.sidebar.header("⚙️ Pengaturan Tampilan")

jumlah_data = st.sidebar.slider(
    "Jumlah data ditampilkan",
    min_value=5,
    max_value=200,
    value=30
)

hari_prediksi = st.sidebar.slider(
    "Jumlah hari prediksi ke depan",
    min_value=1,
    max_value=7,
    value=3
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Dashboard ini menampilkan hasil prediksi **ConvLSTM** "
    "yang dikategorikan menjadi **Rendah, Sedang, dan Tinggi**."
)

# ======================================
# METRIK UTAMA
# ======================================
st.subheader("📊 Ringkasan Kategori Prediksi")

col1, col2, col3 = st.columns(3)

col1.metric("🌤️ Rendah", int((data["Kategori_Prediksi"] == "Rendah").sum()))
col2.metric("🌦️ Sedang", int((data["Kategori_Prediksi"] == "Sedang").sum()))
col3.metric("🌧️ Tinggi", int((data["Kategori_Prediksi"] == "Tinggi").sum()))

st.markdown("---")

# ======================================
# GRAFIK AKTUAL VS PREDIKSI
# ======================================
st.subheader("📉 Perbandingan Curah Hujan Aktual vs Prediksi")

fig1, ax1 = plt.subplots(figsize=(20, 6))

ax1.plot(
    data["Aktual_Rain"].values,
    label="Aktual",
    linewidth=3
)
ax1.plot(
    data["Prediksi_Rain"].values,
    linestyle="--",
    label="Prediksi",
    linewidth=3
)

ax1.set_xlabel("Urutan Waktu")
ax1.set_ylabel("Curah Hujan (mm)")
ax1.set_title("Tren Curah Hujan Aktual vs Prediksi")
ax1.legend()
ax1.grid(alpha=0.3)

st.pyplot(fig1)

st.markdown("---")

# ======================================
# DISTRIBUSI KATEGORI (ANTI ERROR)
# ======================================
st.subheader("📊 Distribusi Kategori Curah Hujan (Prediksi)")

kategori_order = ["Rendah", "Sedang", "Tinggi"]
kategori_count = (
    data["Kategori_Prediksi"]
    .value_counts()
    .reindex(kategori_order)
    .fillna(0)
    .astype(int)
)

fig2, ax2 = plt.subplots(figsize=(12, 5))
bars = ax2.bar(kategori_count.index, kategori_count.values)

ax2.set_xlabel("Kategori")
ax2.set_ylabel("Jumlah Data")
ax2.set_title("Distribusi Kategori Prediksi")
ax2.grid(axis="y", alpha=0.3)

for bar in bars:
    height = bar.get_height()
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height}",
        ha="center",
        va="bottom"
    )

st.pyplot(fig2)

st.markdown("---")

# ======================================
# PERBANDINGAN KATEGORI
# ======================================
st.subheader("🔁 Perbandingan Kategori Aktual vs Prediksi")

compare = pd.crosstab(
    data["Kategori_Aktual"],
    data["Kategori_Prediksi"]
)

st.dataframe(compare, use_container_width=True, height=300)

st.markdown("---")

# ======================================
# PREDIKSI HARIAN 1–7 HARI KE DEPAN
# ======================================
st.subheader("📅 Prediksi Curah Hujan Harian ke Depan")

prediksi_ke_depan = data["Prediksi_Rain"].tail(hari_prediksi).values

df_prediksi_harian = pd.DataFrame({
    "Hari": [f"Hari +{i+1}" for i in range(hari_prediksi)],
    "Prediksi Curah Hujan (mm)": prediksi_ke_depan
})

df_prediksi_harian["Kategori"] = df_prediksi_harian[
    "Prediksi Curah Hujan (mm)"
].apply(kategori_hujan)

st.dataframe(
    df_prediksi_harian,
    use_container_width=True,
    height=250
)

# Grafik prediksi harian
fig3, ax3 = plt.subplots(figsize=(12, 4))

ax3.plot(
    df_prediksi_harian["Hari"],
    df_prediksi_harian["Prediksi Curah Hujan (mm)"],
    marker="o",
    linewidth=3
)

ax3.set_xlabel("Hari")
ax3.set_ylabel("Curah Hujan (mm)")
ax3.set_title("Prediksi Curah Hujan 1–7 Hari ke Depan")
ax3.grid(alpha=0.3)

st.pyplot(fig3)

st.info(
    "Prediksi harian dilakukan secara simulatif berdasarkan "
    "hasil model ConvLSTM dengan window 7 hari."
)

st.markdown("---")

# ======================================
# TABEL DATA UTAMA
# ======================================
st.subheader("📋 Data Hasil Prediksi")

st.dataframe(
    data.head(jumlah_data),
    use_container_width=True,
    height=500
)

st.markdown("---")

# ======================================
# DOWNLOAD CSV
# ======================================
st.subheader("⬇️ Unduh Data Hasil Prediksi")

csv = data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="hasil_prediksi_kategori_convlstm.csv",
    mime="text/csv"
)

# ======================================
# FOOTER
# ======================================
st.markdown(
    """
    <hr>
    <p style='text-align: center; color: grey; font-size: 13px;'>
        Model: ConvLSTM | Output: Prediksi Curah Hujan (Numerik & Kategori)
    </p>
    """,
    unsafe_allow_html=True
)
