import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from openlocationcode import openlocationcode as olc
from streamlit_autorefresh import st_autorefresh

# --- 1. GÖRSEL DÜZENLEME (ŞEFFAFLAŞMAYI ENGELLER) ---
st.markdown(
    """
    <style>
    [data-testid="stAppViewBlockContainer"] { opacity: 1 !important; }
    .stApp { transition: none !important; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
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

st.set_page_config(page_title="Taksi İstiyorum 🚕", page_icon="🚕")

# --- 3. TELEGRAM DURUM OKUMA (GÜNCELLENDİ) ---
def get_last_status():
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        # offset=-1 ve limit=1 ile sadece en son atılan mesajı çekiyoruz
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, params={"offset": -1, "limit": 1}, timeout=1.5).json()
        
        if response.get("ok") and response.get("result"):
            # En son gelen mesajın içeriği
            last_msg = response["result"][0].get("message", {}).get("text", "").lower()
            
            if "/onay" in last_msg:
                return "✅ Cemil gördü, Uber'i açıyor!"
            elif "/yolda" in last_msg:
                parts = last_msg.split()
                dk = parts[1] if len(parts) > 1 else "?"
                return f"🚗 Taksi yolda! ({dk} dk içinde yanında)"
            elif "/iptal" in last_msg:
                return "❌ Cemil şu an uygun değil, seni arayacak."
        
        return "⌛ Cemil'den onay bekleniyor..."
    except Exception as e:
        return f"⌛ Durum kontrol ediliyor..."

# --- 4. TELEGRAM BİLDİRİM GÖNDERME ---
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
            loc_info = f"📍 [Harita]({maps_url}) | [Uber'de Aç]({uber_url})\n🔢 Plus Code: `{plus_code}`"

        msg = f"🚕 *YENİ TALEP!*\n👤 *Müşteri:* {user}\n\n{loc_info}\n\nOnay için: `/onay`\nSüre için: `/yolda 5`"
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=2)
        return True
    except: return False

# --- 5. ARAYÜZ ---

if st.session_state.step == 'login':
    st.title("🚕 Taksi İstiyorum")
    name_in = st.text_input("Lütfen ismini yaz:", key="u_name")
    if st.button("Giriş Yap", use_container_width=True, key="l_btn"):
        if name_in:
            st.session_state.name = name_in
            st.session_state.step = 'request'
            st.rerun()

elif st.session_state.step == 'request':
    st.title(f"Selam {st.session_state.name}! 👋")
    
    # Konumu arka planda hep güncel tut
    loc = get_geolocation()
    
    if not st.session_state.requested:
        if st.button("🚖 TAKSİ İSTİYORUM", type="primary", use_container_width=True, key="t_btn"):
            if send_taxi_notif(st.session_state.name, loc):
                st.session_state.requested = True
                st.balloons()
                st.rerun()
    
    else:
        # TALEP GİTTİKTEN SONRA BURASI ÇALIŞIR
        st.success("Talebin Cemil'e iletildi! ❤️")
        st.divider()
        st.subheader("Canlı Durum")
        
        # 1 Saniye Yenileme
        st_autorefresh(interval=1000, key="status_loop")
        
        status_msg = get_last_status()
        st.info(status_msg)

    if st.button("Çıkış / İptal", key="exit_btn"):
        st.session_state.clear()
        st.rerun()
