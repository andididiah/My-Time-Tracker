import streamlit as st
import pandas as pd
import time
import pytz
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Time Tracker Samarinda", page_icon="⏱️")

# Setting Zona Waktu Samarinda (WITA)
TZ_SAMARINDA = pytz.timezone('Asia/Makassar')

st.title("⏱️ My Time Tracker")

# --- 2. FUNGSI PENDUKUNG ---
def format_duration(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}m {secs}s"

def save_data(aktivitas, kategori, durasi_detik):
    now = datetime.now(TZ_SAMARINDA)
    tanggal = now.strftime("%Y-%m-%d")
    jam_selesai = now.strftime("%H:%M:%S")
    durasi_teks = format_duration(durasi_detik)
    
    new_data = pd.DataFrame([[tanggal, jam_selesai, aktivitas, kategori, durasi_teks]], 
                            columns=['Tanggal', 'Jam', 'Aktivitas', 'Kategori', 'Durasi'])
    try:
        df = pd.read_csv("time_log.csv")
        df = pd.concat([df, new_data], ignore_index=True)
    except FileNotFoundError:
        df = new_data
    df.to_csv("time_log.csv", index=False)

# --- 3. INPUT AKTIVITAS ---
with st.container():
    nama_tugas = st.text_input("Apa yang mau dikerjakan?", placeholder="Contoh: Belajar Akuntansi")
    kategori = st.selectbox("Kategori:", [
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
    st.info("Stopwatch berjalan... Segera klik 'Berhenti' jika selesai.")

if col_b.button("⏹️ Berhenti & Simpan", use_container_width=True):
    if st.session_state.start_time:
        durasi_akhir = time.time() - st.session_state.start_time
        save_data(nama_tugas, kategori, durasi_akhir)
        st.success(f"Tersimpan! Durasi: {format_duration(durasi_akhir)}")
        st.session_state.start_time = None
        time.sleep(1)
        st.rerun()
    else:
        st.warning("Klik 'Mulai' terlebih dahulu!")

# --- 5. KONTROL DATA (Hanya Hapus & Download) ---
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
    st.dataframe(df_history.iloc[::-1], use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.info("Belum ada data tersimpan. Mulai aktivitas pertamamu!")
