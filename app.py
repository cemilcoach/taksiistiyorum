import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from openlocationcode import openlocationcode as olc
from streamlit_autorefresh import st_autorefresh
import time
import json

# --- 1. CSS & GÖRSEL AYARLAR ---
st.markdown(
    """
    <style>
    [data-testid="stAppViewBlockContainer"] { opacity: 1 !important; }
    .stApp { transition: none !important; }
    .plaka-box {
        background-color: #f0f2f6;
        border: 2px solid #0e1117;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.step = 'login'
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'requested' not in st.session_state:
    st.session_state.requested = False
if 'request_time' not in st.session_state:
    st.session_state.request_time = 0

st.set_page_config(page_title="Taksi Paneli 🚕", page_icon="🚕")

# --- 3. TELEGRAM DURUM OKUMA (PLAKA VE SAYAÇ DESTEKLİ) ---
def get_last_status():
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, params={"offset": -1, "limit": 1}, timeout=1.5).json()
        
        if response.get("ok") and response.get("result"):
            update = response["result"][0]
            if "callback_query" in update:
                data = update["callback_query"]["data"]
                msg_time = update["callback_query"]["message"]["date"]
            elif "message" in update:
                data = update["message"].get("text", "")
                msg_time = update["message"].get("date", 0)
            else: return None

            # Zaman Kontrolü
            if msg_time < st.session_state.request_time:
                return None
            
            return {"data": data, "time": msg_time}
        return None
    except: return None

# --- 4. ARAYÜZ ---
if st.session_state.step == 'login':
    st.title("🚕 Taksi İstiyorum")
    name_in = st.text_input("İsminiz:", key="u_name")
    if st.button("Giriş", use_container_width=True):
        if name_in:
            st.session_state.name = name_in
            st.session_state.step = 'request'
            st.rerun()

elif st.session_state.step == 'request':
    st.title(f"Selam {st.session_state.name}! 👋")
    loc = get_geolocation()
    
    if not st.session_state.requested:
        is_disabled = loc is None
        if is_disabled: st.warning("📍 Konum bekleniyor...")
        if st.button("🚖 TAKSİ İSTİYORUM", type="primary", use_container_width=True, disabled=is_disabled):
            # Buradaki send_taxi_notif fonksiyonunu önceki sürümlerden alabilirsin
            st.session_state.request_time = int(time.time())
            st.session_state.requested = True
            st.rerun()
    else:
        st_autorefresh(interval=2000, key="status_loop") # 2 saniye stabilite için ideal
        
        # Durum Verisini Çek
        status = get_last_status()
        
        st.subheader("Canlı Durum")
        
        if status:
            cmd = status["data"].lower()
            
            # PLAKA KONTROLÜ
            if "/plaka" in cmd:
                plaka = status["data"].replace("/plaka", "").strip().upper()
                st.markdown(f'<div class="plaka-box">🚕 Gelen Araç: {plaka}</div>', unsafe_allow_html=True)
            
            # SAYAÇ KONTROLÜ
            if "/yolda" in cmd:
                try:
                    dakika = int(cmd.split()[1])
                    gecen_saniye = int(time.time()) - status["time"]
                    kalan_saniye = (dakika * 60) - gecen_saniye
                    
                    if kalan_saniye > 0:
                        st.metric("Tahmini Varış", f"{kalan_saniye // 60}:{kalan_saniye % 60:02d}")
                        st.progress(max(0, min(1.0, 1 - (kalan_saniye / (dakika * 60)))))
                    else:
                        st.success("🚕 Taksi kapıda olması lazım!")
                except:
                    st.info("🚗 Taksi yolda!")
            
            elif "/onay" in cmd:
                st.info("✅ Cemil isteğini gördü, taksiyi ayarlıyor...")
            elif "/red" in cmd:
                st.error("❌ Cemil şu an müsait değil, seni arayacak.")
        else:
            st.info("⌛ Cemil'den onay bekleniyor...")

    if st.button("Çıkış / Yeni Talep"):
        st.session_state.clear()
        st.rerun()
