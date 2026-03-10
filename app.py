import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="My Time Tracker", page_icon="⏱️")

st.title("⏱️ My Personal Time Tracker")
st.subheader("Kelola waktumu dengan lebih bermakna")

# --- DATABASE SEDERHANA (File CSV) ---
# Ini akan menyimpan data kamu secara gratis di folder yang sama
def save_data(aktivitas, kategori, durasi):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, aktivitas, kategori, durasi]], 
                            columns=['Waktu', 'Aktivitas', 'Klasifikasi', 'Durasi (Detik)'])
    try:
        df = pd.read_csv("time_log.csv")
        df = pd.concat([df, new_data], ignore_index=True)
    except FileNotFoundError:
        df = new_data
    df.to_csv("time_log.csv", index=False)

# --- BAGIAN INPUT ---
col1, col2 = st.columns(2)
with col1:
    nama_tugas = st.text_input("Apa yang sedang kamu kerjakan?", placeholder="Contoh: Belajar Excel")
with col2:
    kategori = st.selectbox("Klasifikasi Aktivitas:", [
        "Personal Care 🌸"
        "Spiritual ✨", 
        "Health 💪", 
        "Development 💡"
    ])

# --- LOGIKA STOPWATCH ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

col_a, col_b = st.columns(2)

if col_a.button("▶️ Mulai", use_container_width=True):
    st.session_state.start_time = time.time()
    st.info(f"Stopwatch dimulai untuk: {nama_tugas}")

if col_b.button("⏹️ Berhenti & Simpan", use_container_width=True):
    if st.session_state.start_time:
        end_time = time.time()
        durasi_detik = round(end_time - st.session_state.start_time)
        durasi_menit = round(durasi_detik / 60, 2)
        
        # Simpan ke file
        save_data(nama_tugas, kategori, durasi_detik)
        
        st.success(f"Berhasil dicatat! Durasi: {durasi_menit} menit.")
        st.session_state.start_time = None
    else:
        st.warning("Klik 'Mulai' terlebih dahulu!")

# --- RIWAYAT AKTIVITAS ---
st.divider()
st.write("### 📜 Riwayat Waktumu")
try:
    history_df = pd.read_csv("time_log.csv")
    st.dataframe(history_df.tail(10), use_container_width=True) # Tampilkan 10 data terakhir
except:
    st.info("Belum ada data yang tersimpan. Mulai aktivitas pertamamu!")
