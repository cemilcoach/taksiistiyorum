import streamlit as st
import requests

# --- 1. SESSION STATE BAŞLATMA (Hata Almamak İçin En Üstte Olmalı) ---
if 'step' not in st.session_state:
    st.session_state.step = 'login'
if 'name' not in st.session_state:
    st.session_state.name = ""

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Taksi İstiyorum 🚕", page_icon="🚕")

# --- HIZLANDIRILMIŞ TELEGRAM FONKSİYONU ---
def send_taxi_notif(user):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        payload = {
            "chat_id": chat_id, 
            "text": f"🚕 *Taksi Talebi!* \n\n{user} bekliyor. Uber'i aç!",
            "parse_mode": "Markdown"
        }
        # timeout=1 ve stream=False yaparak en hızlı şekilde isteği bitiriyoruz
        requests.post(url, data=payload, timeout=1.5)
        return True
    except:
        return False

# --- UI MANTIĞI ---

if st.session_state.step == 'login':
    st.title("🚕 Taksi İstiyorum")
    name_input = st.text_input("Lütfen ismini yaz:", key="main_name_input")
    
    # key="login_btn" ekleyerek Duplicate ID hatasını çözüyoruz
    if st.button("Giriş Yap", key="login_btn", use_container_width=True):
        if name_input:
            st.session_state.name = name_input
            st.session_state.step = 'request'
            st.rerun()

elif st.session_state.step == 'request':
    st.title(f"Selam {st.session_state.name}! 👋")
    
    # Ana Taksi Butonu - key="taxi_btn" ile hata engellendi
    if st.button("🚖 TAKSİ İSTİYORUM", key="taxi_btn", type="primary", use_container_width=True):
        # Kullanıcıyı bekletmemek için direkt görsel geri bildirim veriyoruz
        with st.status("Mesaj gönderiliyor...", expanded=False) as status:
            if send_taxi_notif(st.session_state.name):
                status.update(label="Bildirim bana ulaştı! ❤️", state="complete")
                st.balloons()
            else:
                status.update(label="Gönderilemedi, tekrar dene.", state="error")

    # Geri dönme butonu - key="back_btn"
    if st.button("İsim Değiştir", key="back_btn"):
        st.session_state.step = 'login'
        st.rerun()
