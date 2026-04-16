import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from openlocationcode import openlocationcode as olc
from streamlit_autorefresh import st_autorefresh

# --- 1. CSS İLE ŞEFFAFLAŞMAYI (FADE) ENGELLEME ---
# Bu blok, Streamlit'in yenileme sırasındaki "opacity" animasyonunu kapatır.
st.markdown(
    """
    <style>
    [data-testid="stAppViewBlockContainer"] {
        opacity: 1 !important;
    }
    .stApp {
        transition: none !important;
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

st.set_page_config(page_title="Taksi Paneli 🚕", page_icon="🚕")

# --- 3. OTOMATİK YENİLEME (500ms) ---
if st.session_state.requested:
    st_autorefresh(interval=500, key="no_flicker_refresh")

# --- TELEGRAM MESAJ OKUMA ---
def get_last_status():
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        params = {"offset": -1, "limit": 1}
        response = requests.get(url, params=params, timeout=0.4).json() # Timeout daha da düşürüldü
        
        if response["ok"] and response["result"]:
            last_msg = response["result"][0]["message"].get("text", "").lower()
            if "/onay" in last_msg: return "✅ Cemil isteğini gördü, Uber'i açıyor!"
            if "/yolda" in last_msg:
                parts = last_msg.split()
                dakika = parts[1] if len(parts) > 1 else "?"
                return f"🚗 Taksi yolda! Yaklaşık {dakika} dakika içinde yanında olacak."
        return "⌛ Cemil'den onay bekleniyor..."
    except: return "⌛ Güncelleniyor..."

# --- UI AKIŞI ---
if st.session_state.step == 'login':
    st.title("🚕 Taksi İstiyorum")
    name_in = st.text_input("İsminiz:", key="user_z")
    if st.button("Giriş", use_container_width=True):
        if name_in:
            st.session_state.name = name_in
            st.session_state.step = 'request'
            st.rerun()

elif st.session_state.step == 'request':
    st.title(f"Selam {st.session_state.name}! ✨")
    
    loc = get_geolocation()
    
    if st.button("🚖 TAKSİ İSTİYORUM", type="primary", use_container_width=True):
        # Bildirim gönderme fonksiyonunu burada çağırabilirsin (önceki kodlardaki gibi)
        st.session_state.requested = True
        st.balloons()
        st.rerun()

    if st.session_state.requested:
        st.divider()
        st.subheader("Canlı Durum")
        
        # st.empty() kullanarak içeriği aynı alanda sabit tutuyoruz
        placeholder = st.empty()
        status_msg = get_last_status()
        placeholder.info(status_text := status_msg)

    if st.button("Çıkış", type="secondary"):
        st.session_state.clear()
        st.rerun()
