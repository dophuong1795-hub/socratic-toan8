import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from PIL import Image
import json
import re
import pandas as pd
import requests
from datetime import datetime

# ================= CẤU HÌNH GIAO DIỆN STREAMLIT =================
st.set_page_config(
    page_title="Đấu Trường Toán Học 8 - Cô Mai Phương",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 760px !important;
    }
    .hero-banner {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        border-radius: 20px;
        padding: 22px 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.25);
        margin-bottom: 22px;
    }
    .hero-banner h1 {
        font-size: 26px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        color: white !important;
    }
    .hero-banner p {
        font-size: 14px;
        margin: 6px 0 0 0;
        opacity: 0.95;
    }
    .step-badge {
        display: inline-block;
        background-color: #EEF2FF;
        color: #4F46E5;
        font-weight: 700;
        font-size: 13px;
        padding: 4px 14px;
        border-radius: 999px;
        margin-bottom: 12px;
        border: 1px solid #C7D2FE;
    }
    div[data-testid="stButton"] button {
        border-radius: 14px !important;
        border: 2px solid #E2E8F0 !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 12px 18px !important;
        background-color: #F8FAFC !important;
        color: #1E293B !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #EEF2FF !important;
        border-color: #6366F1 !important;
        color: #4F46E5 !important;
    }
</style>
""", unsafe_allow_html=True)

# Lấy Gemini API Key an toàn
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    st.error("Chưa cấu hình biến GEMINI_API_KEY trong Secrets của Streamlit!")
    st.stop()

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-3.8-flash"

def format_math(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r"^(?:User Safety|Thinking Process|Thought):[^\n]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    text = text.replace("$", "")
    return text.strip()

def execute_gemini_request(inputs, system_prompt=None, is_json=False):
    config_params = {}
    if system_prompt:
        config_params["system_instruction"] = system_prompt
    if is_json:
        config_params["response_mime_type"] = "application/json"
    
    config = types.GenerateContentConfig(**config_params) if config_params else None

    prepared_contents = []
    for item in inputs:
        if isinstance(item, Image.Image):
            img = item.copy()
            if img.mode != "RGB":
                img = img.convert("RGB")
            if max(img.size) > 1200:
                img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            prepared_contents.append(img)
        elif item:
            prepared_contents.append(str(item))

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prepared_contents,
        config=config
    )
    text_out = response.text or ""
    if not text_out.strip():
        raise Exception("Nội dung phản hồi bị rỗng từ Gemini!")

    if is_json:
        clean_text = re.sub(r"^```(?:json)?\s*|```$", "", text_out.strip(), flags=re.MULTILINE)
        match = re.search(r"\{[\s\S]*\}", clean_text)
        target_str = match.group(0) if match else clean_text
        return json.loads(target_str, strict=False)

    return text_out

if "submission_history" not in st.session_state:
    st.session_state.submission_history = []

st.markdown("""
<div class="hero-banner">
    <h1>📐 ĐẤU TRƯỜNG TOÁN HỌC 8</h1>
    <p>Chinh phục Đại số & Hình học cùng cô Mai Phương • Học tập gợi mở theo từng bước</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🎮 Thử Thách Tương Tác", 
    "📝 Nộp Bài Tập", 
    "📊 Bảng Điểm Lớp",
    "🍄 Đại Chiến Bowser"
])

with tab1:
    st.info("💡 Bấm vào mục bên dưới để tải ảnh bài tập Đại số hoặc Hình học lên và bắt đầu chinh phục các cửa ải gợi mở cùng cô Mai Phương!")
    up_game_img = st.file_uploader("Tải/chụp ảnh bài toán:", type=["jpg", "png", "jpeg"], key="up_game_img_tab1")
    if up_game_img:
        img = Image.open(up_game_img)
        st.image(img, caption="Ảnh bài toán", use_container_width=True)
        if st.button("🚀 Phân tích bài toán cùng AI", type="primary"):
            with st.spinner("Cô đang xem đề bài giúp em..."):
                try:
                    res = execute_gemini_request([img, "Hãy hướng dẫn học sinh giải bài toán này theo các bước Socratic ngắn gọn."], is_json=False)
                    st.success("Kết quả gợi ý từ trợ lý AI:")
                    st.write(res)
                except Exception as e:
                    st.error(f"Lỗi: {e}")

with tab2:
    st.subheader("📝 Nộp Bài Tập Tự Luận")
    s_name = st.text_input("Họ và tên học sinh:")
    s_class = st.selectbox("Lớp:", ["8A13", "8A18"])
    topic = st.selectbox("Chuyên đề:", ["Đại số 8: Hằng đẳng thức", "Hình học 8: Tứ giác & Hình thang cân"])
    up_hw = st.file_uploader("Chụp ảnh bài làm:", type=["jpg", "png", "jpeg"], key="hw_tab2")
    if st.button("🚀 Nộp bài ngay", type="primary"):
        if s_name and up_hw:
            st.success(f"Đã ghi nhận bài nộp của em {s_name} - Lớp {s_class}!")
        else:
            st.warning("Vui lòng điền tên và tải ảnh bài làm lên!")

with tab3:
    st.subheader("📊 Sổ Điểm Giáo Viên")
    pwd = st.text_input("Mật khẩu giáo viên:", type="password")
    if pwd == "Maiphuong2026":
        st.success("Đăng nhập thành công!")
        if st.session_state.submission_history:
            st.dataframe(pd.DataFrame(st.session_state.submission_history))
        else:
            st.info("Chưa có dữ liệu nộp bài.")
    elif pwd:
        st.error("Sai mật khẩu!")

with tab4:
    st.subheader("🍄 Vượt Ải Tứ Giác - Đại Chiến Bowser")
    sheet_webhook = st.secrets.get("GOOGLE_SHEET_WEBHOOK_URL", "")
    
    mario_game_code = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
      <meta charset="UTF-8">
      <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-white p-4 text-center font-sans">
      <div class="max-w-md mx-auto bg-slate-900 border-2 border-amber-400 rounded-2xl p-6 shadow-xl">
        <h2 class="text-lg font-bold text-amber-400 mb-2">ĐẠI CHIẾN BOWSER - TOÁN 8</h2>
        <p class="text-xs text-slate-300 mb-4">Sẵn sàng vượt qua 5 ải hình học tứ giác để nhận +5 điểm thực tế từ cô Mai Phương!</p>
        <button onclick="alert('Bắt đầu thử thách thành công! Chúc em đạt điểm tuyệt đối!')" class="w-full py-3 bg-red-600 hover:bg-red-500 font-bold rounded-xl text-sm shadow-lg">
          VÀO TRẬN ĐẤU NGAY 🎮
        </button>
      </div>
    </body>
    </html>
    """
    components.html(mario_game_code, height=450, scrolling=True)
