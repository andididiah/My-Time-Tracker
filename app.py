import streamlit as st
import pandas as pd
import time
import pytz
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Time Tracker Samarinda", page_icon="⏱️")
TZ_SAMARINDA = pytz.timezone('Asia/Makassar')

st.title("⏱️ My Time Tracker")
st.write(f"Zona Waktu: **Samarinda (WITA)**")

# --- 2. FUNGSI PENDUKUNG ---
def format_duration_simple(seconds):
    mins = int(seconds // 60)
    # Menampilkan hanya menit saja
    return f"{mins} menit"

def save_data(aktivitas, kategori, start_timestamp, end_timestamp):
    # Mengonversi timestamp ke waktu Samarinda
    start_time = datetime.fromtimestamp(start_timestamp, TZ_SAMARINDA)
    end_time = datetime.fromtimestamp(end_timestamp, TZ_SAMARINDA)
    
    tanggal = start_time.strftime("%Y-%m-%d")
    
    # Format Jam: Menampilkan Jam Start - Jam Selesai (tanpa detik)
    jam_range = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
    
    durasi_detik = end_timestamp - start_timestamp
    durasi_teks = format_duration_simple(durasi_detik)
    
    new_data = pd.DataFrame([[tanggal, jam_range, aktivitas, kategori, durasi_teks]], 
                            columns=['Tanggal', 'Jam', 'Aktivitas', 'Klasifikasi', 'Durasi'])
    try:
        df = pd.read_csv("time_log.csv")
        df = pd.concat([df, new_data], ignore_index=True)
    except FileNotFoundError:
        df = new_data
    df.to_csv("time_log.csv", index=False)

# --- 3. INPUT AKTIVITAS ---
nama_tugas = st.text_input("Apa yang sedang dikerjakan?", placeholder="Contoh: Belajar Akuntansi")
kategori = st.selectbox("Klasifikasi Aktivitas:", [
        "Personal Care 🌸",
        "Spiritual ✨", 
        "Health 💪", 
        "Development 💡",
        "Work 💼"
])

# --- 4. LOGIKA STOPWATCH ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

col_a, col_b = st.columns(2)

if col_a.button("▶️ Mulai Sesi", use_container_width=True):
    st.session_state.start_time = time.time()
    st.info("Stopwatch berjalan...")

if col_b.button("⏹️ Berhenti & Simpan", use_container_width=True):
    if st.session_state.start_time:
        end_time_val = time.time()
        save_data(nama_tugas, kategori, st.session_state.start_time, end_time_val)
        
        st.success("Tersimpan!")
        st.session_state.start_time = None
        time.sleep(1)
        st.rerun()
    else:
        st.warning("Klik 'Mulai' terlebih dahulu!")

# --- 5. KONTROL DATA ---
st.divider()
try:
    df_history = pd.read_csv("time_log.csv")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Hapus Baris Terakhir", use_container_width=True):
            if len(df_history) > 0:
                df_history = df_history[:-1]
                df_history.to_csv("time_log.csv", index=False)
                st.rerun()
    with c2:
        csv_data = df_history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv_data, file_name="my_time_log.csv", use_container_width=True)

    # --- 6. TABEL RIWAYAT ---
    st.write("### 📜 Riwayat Lengkap")
    # Menampilkan tabel dengan kolom yang sudah diperbarui
    st.dataframe(df_history.iloc[::-1], use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.info("Belum ada data tersimpan.")
