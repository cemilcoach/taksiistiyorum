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

st.set_page_config(page_title="Taksi İstiyorum 🚕", page_icon="🚕")

# --- 3. TELEGRAM DURUM OKUMA (RED KOMUTU EKLENDİ) ---
def get_last_status():
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, params={"offset": -1, "limit": 1}, timeout=1.5).json()
        
        if response.get("ok") and response.get("result"):
            update = response["result"][0]
            
            # Callback (Buton) veya normal mesaj kontrolü
            if "callback_query" in update:
                last_msg = update["callback_query"]["data"].lower()
                msg_time = update["callback_query"]["message"]["date"]
            elif "message" in update:
                last_msg = update["message"].get("text", "").lower()
                msg_time = update["message"].get("date", 0)
            else:
                return "⌛ Cemil'den onay bekleniyor..."

            # Zaman kontrolü
            if msg_time < st.session_state.request_time:
                return "⌛ Cemil'den onay bekleniyor..."
            
            # KOMUTLAR
            if "/onay" in last_msg:
                return "✅ Cemil gördü, Uber'i açıyor!"
            elif "/red" in last_msg:
                return "❌ Cemil şu an müsait değil veya taksi yok, seni arayacak."
            elif "/yolda" in last_msg:
                parts = last_msg.split()
                dk = parts[1] if len(parts) > 1 else "?"
                return f"🚗 Taksi yolda! ({dk} dk içinde yanında)"
        
        return "⌛ Cemil'den onay bekleniyor..."
    except:
        return "⌛ Durum kontrol ediliyor..."

# --- 4. BİLDİRİM GÖNDERME (RED BUTONU DAHİL) ---
def send_taxi_notif(user, location=None):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        loc_info = "📍 Konum paylaşılamadı."
        
        if location:
            lat, lon = location['coords']['latitude'], location['coords']['longitude']
            plus_code = olc.encode(lat, lon)
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            uber_url = f"uber://?action=setPickup&pickup[latitude]={lat}&pickup[longitude]={lon}"
            loc_info = f"📍 [Harita]({maps_url}) | [Uber'de Aç]({uber_url})\n🔢 Code: `{plus_code}`"

        # INLINE KEYBOARD (Red butonu eklendi)
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Onayla", "callback_data": "/onay"},
                    {"text": "❌ Red (Taksi Yok)", "callback_data": "/red"}
                ],
                [
                    {"text": "🚗 5 Dakika", "callback_data": "/yolda 5"},
                    {"text": "🚗 10 Dakika", "callback_data": "/yolda 10"}
                ]
            ]
        }

        payload = {
            "chat_id": chat_id,
            "text": f"🚕 *YENİ TALEP!*\n👤 *Müşteri:* {user}\n\n{loc_info}",
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(keyboard)
        }
        
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data=payload, timeout=2)
        return True
    except: return False

# --- 5. ARAYÜZ ---
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
        if st.button("🚖 TAKSİ İSTİYORUM", type="primary", use_container_width=True):
            if send_taxi_notif(st.session_state.name, loc):
                st.session_state.request_time = int(time.time())
                st.session_state.requested = True
                st.balloons()
                st.rerun()
    else:
        st.success("Talebin Cemil'e iletildi! ❤️")
        st_autorefresh(interval=1000, key="status_loop")
        
        st.divider()
        st.subheader("Canlı Durum")
        status_msg = get_last_status()
        
        # Eğer red gelirse kırmızı, diğerleri mavi görünsün
        if "❌" in status_msg:
            st.error(status_msg)
        else:
            st.info(status_msg)

    if st.button("Çıkış / Yeni Talep"):
        st.session_state.clear()
        st.rerun()
