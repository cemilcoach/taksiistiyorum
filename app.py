import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from openlocationcode import openlocationcode as olc

# --- SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.step = 'login'
if 'name' not in st.session_state:
    st.session_state.name = ""

st.set_page_config(page_title="Taksi İstiyorum 🚕", page_icon="🚕")

# --- MESAJ FONKSİYONU ---
def send_taxi_notif(user, location=None):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        
        loc_info = "📍 Konum paylaşılamadı."
        
        if location:
            lat = location['coords']['latitude']
            lon = location['coords']['longitude']
            
            # Plus Code Hesaplama
            plus_code = olc.encode(lat, lon)
            
            # Google Maps Linki
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            
            # Telegram için kopyalanabilir format (Markdown V2 veya klasik backtick)
            loc_info = (
                f"📍 *Harita:* [Buraya Tıkla]({maps_url})\n"
                f"🔢 *Plus Code (Kopyala):*\n`{plus_code}`"
            )

        message = f"🚕 *YENİ TAKSİ TALEBİ!*\n\n👤 *Kimden:* {user}\n\n{loc_info}"
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": message, 
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        
        requests.post(url, data=payload, timeout=2)
        return True
    except Exception as e:
        print(f"Hata: {e}")
        return False

# --- UI ---
if st.session_state.step == 'login':
    st.title("🚕 Taksi İstiyorum")
    name_input = st.text_input("Lütfen ismini yaz:", key="u_name")
    if st.button("Giriş Yap", key="l_btn", use_container_width=True):
        if name_input:
            st.session_state.name = name_input
            st.session_state.step = 'request'
            st.rerun()

elif st.session_state.step == 'request':
    st.title(f"Selam {st.session_state.name}! 👋")
    st.write("Butona bastığında konumunla birlikte bana haber gidecek.")
    
    # Konumu arka planda hazırla
    loc = get_geolocation()
    
    if st.button("🚖 TAKSİ İSTİYORUM", key="t_btn", type="primary", use_container_width=True):
        if not loc:
            st.warning("Konum izni alınamadı. Lütfen tarayıcıdan konum izni verdiğinden emin ol!")
        
        with st.status("Gönderiliyor...") as status:
            if send_taxi_notif(st.session_state.name, loc):
                status.update(label="Haberim oldu, yoldayım! ❤️", state="complete")
                st.balloons()
            else:
                status.update(label="Bir hata oluştu!", state="error")

    if st.button("İsim Değiştir", key="b_btn"):
        st.session_state.step = 'login'
        st.rerun()
