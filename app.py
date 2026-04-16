import streamlit as st
import requests

def taxi_request_sent(user_name):
    """Hızlandırılmış mesaj gönderimi."""
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        
        message = f"🚕 *Taksi Talebi!* \n\n{user_name} bekliyor."
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        # timeout=2 ekleyerek bağlantının askıda kalmasını önlüyoruz. 
        # Genelde Telegram milisaniyeler içinde yanıt verir.
        response = requests.post(url, data=payload, timeout=2)
        return response.status_code == 200
    except Exception:
        # Hız için hatayı loglamak yerine sessizce geçebilir veya basit bir uyarı verebilirsin
        return False

# Buton kısmında kullanımı:
if st.button("🚖 TAKSİ İSTİYORUM", use_container_width=True, type="primary"):
    # Spinner'ı kaldırıp direkt işlemi başlatıyoruz ki kullanıcı beklediğini hissetmesin
    success = taxi_request_sent(st.session_state.name)
    if success:
        st.balloons()
        st.success("Hemen ayarlıyorum! ❤️")
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
