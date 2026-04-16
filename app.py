import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from openlocationcode import openlocationcode as olc
from streamlit_autorefresh import st_autorefresh

# --- 1. SESSION STATE BAŞLATMA ---
if 'step' not in st.session_state:
    st.session_state.step = 'login'
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'requested' not in st.session_state:
    st.session_state.requested = False

st.set_page_config(page_title="Taksi Paneli 🚕", page_icon="🚕", layout="centered")

# --- GERÇEK ZAMANLI YENİLEME (0.5 Saniye) ---
if st.session_state.requested:
    # 500ms = 0.5 saniye. Gecikme hissini yok eder.
    st_autorefresh(interval=500, key="ultra_fast_refresh")

# --- HIZLANDIRILMIŞ MESAJ OKUMA ---
def get_last_status():
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        # getUpdates'i en hızlı yanıt alacak şekilde optimize ettik
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        params = {"offset": -1, "limit": 1}
        response = requests.get(url, params=params, timeout=0.8).json()
        
        if response["ok"] and response["result"]:
            msg_data = response["result"][0]["message"]
            last_msg = msg_data.get("text", "").lower()
            
            if "/onay" in last_msg:
                return "✅ Cemil isteğini gördü, Uber'i açıyor!"
            elif "/yolda" in last_msg:
                parts = last_msg.split()
                dakika = parts[1] if len(parts) > 1 else "?"
                return f"🚗 Taksi yolda! Yaklaşık {dakika} dakika içinde yanında olacak."
            elif "/iptal" in last_msg:
                return "❌ Bir sorun oluştu, Cemil seninle iletişime geçecek."
        
        return "⌛ Talebin iletildi, Cemil'den onay bekleniyor..."
    except:
        return "⌛ Güncelleniyor..."

# --- TELEGRAM BİLDİRİM GÖNDERME ---
def send_taxi_notif(user, location=None):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        
        loc_info = "📍 Konum alınamadı."
        if location:
            lat, lon = location['coords']['latitude'], location['coords']['longitude']
            plus_code = olc.encode(lat, lon)
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            # Uber Deep Link (Telefonunda Uber'i direkt açar)
            uber_url = f"uber://?action=setPickup&pickup[latitude]={lat}&pickup[longitude]={lon}"
            
            loc_info = (
                f"📍 [Google Maps]({maps_url}) | [Uber'de Aç]({uber_url})\n"
                f"🔢 *Plus Code:* `{plus_code}`"
            )

        message = f"🚕 *YENİ TALEP!*\n👤 *Müşteri:* {user}\n\n{loc_info}\n\n_Hızlı Yanıtlar:_\n`/onay`\n`/yolda 5`"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=1)
        return True
    except: return False

# --- KULLANICI ARAYÜZÜ ---

if st.session_state.step == 'login':
    st.title("🚕 Taksi İstiyorum")
    name_in = st.text_input("İsminiz:", key="user_input")
    if st.button("Giriş", use_container_width=True, key="login_b"):
        if name_in:
            st.session_state.name = name_in
            st.session_state.step = 'request'
            st.rerun()

elif st.session_state.step == 'request':
    st.title(f"Selam {st.session_state.name}! ✨")
    
    # Konum verisini çek
    loc = get_geolocation()
    
    if st.button("🚖 TAKSİ İSTİYORUM", type="primary", use_container_width=True, key="req_b"):
        if send_taxi_notif(st.session_state.name, loc):
            st.session_state.requested = True
            st.balloons()
            st.rerun()

    # CANLI DURUM GÖSTERGESİ
    if st.session_state.requested:
        st.divider()
        st.subheader("Canlı Durum")
        
        # 0.5 saniyede bir burası güncellenir
        status_text = get_last_status()
        st.info(status_text)
        
        st.caption("⚡ Canlı bağlantı aktif.")

    if st.button("Çıkış", type="secondary", key="exit_b"):
        st.session_state.step = 'login'
        st.session_state.name = ""
        st.session_state.requested = False
        st.rerun()
