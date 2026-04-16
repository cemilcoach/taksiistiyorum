import streamlit as st
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Taksi İstiyorum 🚕",
    page_icon="🚕",
    layout="centered"
)

# --- TELEGRAM FONKSİYONU ---
def taxi_request_sent(user_name):
    """Telegram botu üzerinden bildirim gönderir."""
    try:
        # Secrets'tan bilgileri çekiyoruz
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        
        message = f"🚕 *Taksi Talebi Geldi!*\n\n{user_name} şu an taksi bekliyor. Uber üzerinden aracı yönlendirebilirsin. ✨"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Sistemsel bir hata oluştu: {e}")
        return False

# --- SESSION STATE KONTROLÜ ---
if 'step' not in st.session_state:
    st.session_state.step = 'login'
if 'name' not in st.session_state:
    st.session_state.name = ""

# --- ARAYÜZ (UI) ---

# 1. ADIM: İSİM GİRİŞİ
if st.session_state.step == 'login':
    st.title("🚕 Taksi İstiyorum")
    st.write("Lütfen devam etmek için ismini yaz.")
    
    name_input = st.text_input("İsim:", placeholder="Adın nedir?")
    
    if st.button("Giriş Yap", use_container_width=True):
        if name_input.strip():
            st.session_state.name = name_input
            st.session_state.step = 'request'
            st.rerun()
        else:
            st.warning("Lütfen geçerli bir isim gir.")

# 2. ADIM: TAKSİ ÇAĞIRMA
elif st.session_state.step == 'request':
    st.title(f"Selam {st.session_state.name}! 👋")
    st.info("Aşağıdaki butona bastığında bana bildirim gelecek ve senin için bir Uber çağıracağım.")
    
    # Büyük Taksi Butonu
    if st.button("🚖 TAKSİ İSTİYORUM", use_container_width=True, type="primary"):
        with st.spinner("Bana haber veriliyor..."):
            success = taxi_request_sent(st.session_state.name)
            
            if success:
                st.balloons()
                st.success("Talebin bana ulaştı! Hemen Uber'i ayarlıyorum. ❤️")
            else:
                st.error("Mesaj gönderilirken bir sorun oluştu. Lütfen tekrar dene.")

    # Geri Dönüş/Sıfırlama Butonu
    if st.button("İsmi Değiştir", type="secondary"):
        st.session_state.step = 'login'
        st.session_state.name = ""
        st.rerun()

# --- ALT BİLGİ ---
st.divider()
st.caption("Bu panel sadece senin ve benim aramda özeldir. 🔒")
