import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

# --- SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.step = 'login'
if 'name' not in st.session_state:
    st.session_state.name = ""

st.set_page_config(page_title="Taksi İstiyorum 🚕", page_icon="🚕")

# --- HIZLI MESAJ FONKSİYONU ---
def send_taxi_notif(user, location=None):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        
        loc_text = "📍 Konum Paylaşılmadı"
        if location:
            lat = location['coords']['latitude']
            lon = location['coords']['longitude']
            # Google Haritalar linki oluşturuyoruz ki tek tıkla Uber'e girebilesin
            loc_text = f"📍 Konum: https://www.google.com/maps?q={lat},{lon}"

        message = f"🚕 *Taksi Talebi!*\n\n👤 {user}\n{loc_text}"
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        
        requests.post(url, data=payload, timeout=1.5)
        return True
    except:
        return False

# --- UI ---
if st.session_state.step == 'login':
    st.title("🚕 Taksi İstiyorum")
    name_input = st.text_input("İsim:", key="name_in")
    if st.button("Giriş Yap", key="btn_l"):
        if name_input:
            st.session_state.name = name_input
            st.session_state.step = 'request'
            st.rerun()

elif st.session_state.step == 'request':
    st.title(f"Selam {st.session_state.name}! 👋")
    
    # Arka planda konumu almaya başla (Kullanıcıdan izin isteyecek)
    loc = get_geolocation()
    
    if st.button("🚖 TAKSİ İSTİYORUM", key="btn_t", type="primary", use_container_width=True):
        with st.status("Mesaj ve konum gönderiliyor...") as status:
            if send_taxi_notif(st.session_state.name, loc):
                status.update(label="Bildirim ve konum iletildi! ❤️", state="complete")
                st.balloons()
            else:
                status.update(label="Hata oluştu!", state="error")

    if st.button("İsim Değiştir", key="btn_b"):
        st.session_state.step = 'login'
        st.rerun()
