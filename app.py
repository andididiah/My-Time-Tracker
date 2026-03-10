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
    return f"{mins} menit"

def save_data(aktivitas, kategori, start_timestamp, end_timestamp):
    start_time = datetime.fromtimestamp(start_timestamp, TZ_SAMARINDA)
    end_time = datetime.fromtimestamp(end_timestamp, TZ_SAMARINDA)
    
    tanggal = start_time.strftime("%Y-%m-%d")
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

# --- 3. INPUT AKTIVITAS & TARGET ---
nama_tugas = st.text_input("Apa yang sedang dikerjakan?", placeholder="Contoh: Belajar Akuntansi")

col_kat, col_target = st.columns(2)
with col_kat:
    kategori = st.selectbox("Klasifikasi:", [
        "Penting & Spesial ✨", 
        "Mindful 🧘", 
        "Neutral 😐", 
        "Worst Time Waste Ever 🗑️"
    ])
with col_target:
    target_menit = st.number_input("Target Waktu (Menit):", min_value=1, value=25)

# --- 4. LOGIKA TIMER & STOPWATCH ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("▶️ Mulai Sesi", use_container_width=True):
        st.session_state.start_time = time.time()
        st.rerun()

with col_b:
    if st.button("⏹️ Berhenti", use_container_width=True):
        if st.session_state.start_time:
            end_time_val = time.time()
            save_data(nama_tugas, kategori, st.session_state.start_time, end_time_val)
            st.success("Tersimpan!")
            st.session_state.start_time = None
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Mulai dulu!")

with col_c:
    if st.button("⚡ Instan (1m)", use_container_width=True):
        now_ts = time.time()
        save_data(nama_tugas, kategori, now_ts, now_ts + 60)
        st.success("Tercatat!")
        st.rerun()

# --- TAMPILAN STATUS TIMER ---
if st.session_state.start_time:
    current_elapsed = time.time() - st.session_state.start_time
    target_detik = target_menit * 60
    
    if current_elapsed < target_detik:
        sisa_waktu = target_detik - current_elapsed
        st.info(f"⏳ Sisa waktu target: {int(sisa_waktu // 60)}m {int(sisa_waktu % 60)}s")
    else:
        overtime = current_elapsed - target_detik
        st.error(f"⚠️ Melebihi target (Overtime): {int(overtime // 60)}m {int(overtime % 60)}s")
    
    # Tombol Refresh Manual untuk HP (Hemat Baterai)
    if st.button("🔄 Update Waktu"):
        st.rerun()

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

    st.write("### 📜 Riwayat Lengkap")
    st.dataframe(df_history.iloc[::-1], use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.info("Belum ada data.")
