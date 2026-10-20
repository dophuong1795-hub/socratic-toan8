import streamlit as str_module
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from PIL import Image
import json
import random
import re
import pandas as pd
import requests
from datetime import datetime

# ================= CẤU HÌNH GIAO DIỆN STREAMLIT =================
st.set_page_config(
    page_title="Phi Hành Gia Toán Học 8 - Cô Mai Phương",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CSS TÙY CHỈNH GIAO DIỆN PHONG CÁCH VŨ TRỤ =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    /* NỀN TOÀN TRANG: Giữ bức ảnh cô giáo sáng rõ ở phía sau */
    .stApp {
        background: linear-gradient(rgba(11, 15, 25, 0.15), rgba(11, 15, 25, 0.3)), 
                    url('https://raw.githubusercontent.com/dophuong1795-hub/socratic-toan8/main/teacher_bg.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #ffffff;
    }
    
    /* KHUNG NỘI DUNG CHÍNH: Kính mờ cao cấp */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 780px !important;
        background: rgba(11, 15, 25, 0.82) !important;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius: 24px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.7);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    /* XỬ LÝ CÁC KHUNG NHẬP LIỆU (INPUT, SELECTBOX, UPLOAD) THÀNH MÀU TỐI DỄ ĐỌC */
    
    /* 1. Ô nhập text (Text Input) và Selectbox */
    input[type="text"], .stSelectbox [data-baseweb="select"] > div {
        background-color: rgba(30, 41, 59, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        border-radius: 12px !important;
    }
    
    /* Màu chữ bên trong ô selectbox và input */
    .stSelectbox span, input[type="text"] {
        color: #ffffff !important;
    }

    /* 2. Khung Upload ảnh */
    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.85) !important;
        border: 2px dashed rgba(56, 189, 248, 0.6) !important;
        border-radius: 16px;
        padding: 15px;
    }
    
    /* Chữ hướng dẫn trong khung upload (như 200MB per file...) đổi sang màu sáng dễ đọc */
    [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span {
        color: #cbd5e1 !important;
    }

    /* Nút Browse files trong khung upload */
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #4f46e5, #06b6d4) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
    }

    /* XỬ LÝ THANH EXPANDER */
    [data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.65) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    [data-testid="stExpander"] summary {
        background: rgba(15, 23, 42, 0.75) !important;
        border-radius: 14px !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    [data-testid="stExpander"] details {
        border: none !important;
    }

    .hero-banner {
        background: linear-gradient(135deg, rgba(49, 46, 129, 0.85) 0%, rgba(67, 56, 202, 0.85) 50%, rgba(219, 39, 119, 0.85) 100%);
        border: 2px solid rgba(245, 158, 11, 0.7);
        border-radius: 20px;
        padding: 24px 22px;
        color: white;
        text-align: center;
        box-shadow: 0 12px 35px rgba(67, 56, 202, 0.6);
        margin-bottom: 24px;
    }
    .hero-banner h1 {
        font-size: 28px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        color: #fef08a !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.6);
    }
    .hero-banner p {
        font-size: 14px;
        margin: 8px 0 0 0;
        color: #f1f5f9;
        font-weight: 600;
    }
    .step-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.25);
        color: #38bdf8;
        font-weight: 700;
        font-size: 13px;
        padding: 6px 16px;
        border-radius: 999px;
        margin-bottom: 14px;
        border: 1px solid rgba(56, 189, 248, 0.7);
    }
    
    /* NÚT BẤM CHÍNH */
    div[data-testid="stButton"] button {
        border-radius: 14px !important;
        border: 1px solid rgba(99, 102, 241, 0.6) !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 12px 20px !important;
        background-color: rgba(15, 23, 42, 0.85) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: rgba(67, 56, 202, 0.9) !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
        transform: translateY(-2px) !important;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5, #06b6d4) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.6) !important;
    }
    
    .reward-box {
        background: rgba(6, 78, 59, 0.85);
        border: 2px solid rgba(52, 211, 153, 0.8);
        border-radius: 18px;
        padding: 20px;
        margin-top: 18px;
    }
    .geogebra-container {
        display: flex;
        justify-content: center;
        align-items: center;
        background: rgba(15, 23, 42, 0.9);
        border: 2px solid rgba(56, 189, 248, 0.7);
        border-radius: 16px;
        padding: 12px;
        margin: 18px 0;
    }
    
    /* TAB MENU */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.85) !important;
        padding: 10px;
        border-radius: 16px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        box-shadow: 0 10px 25px rgba(0,0,0,0.6);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #ffffff !important;
        font-weight: 700;
        background-color: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5, #ec4899) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 0 20px rgba(236, 72, 153, 0.6);
    }
    
    label, .stRadio label, .stTextInput label, .stSelectbox label, p, span {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)
# Lấy Gemini API Key
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("Chưa cấu hình biến GEMINI_API_KEY trong Secrets của Streamlit!")
    st.stop()

# Khởi tạo Gemini Client
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-3.8-flash"

# ================= BỘ LỌC CHUẨN HÓA KÝ HIỆU TOÁN HỌC TOÁN 8 =================
def format_math(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""

    text = re.sub(r"^(?:User Safety|Thinking Process|Thought):[^\n]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    text = text.replace("$", "")

    text = re.sub(r"\\(?:widehat|hat)\s*[\{\[]\s*([A-Za-z0-9]{1,3})\s*[\}\]]", r"∠\1", text)
    text = re.sub(r"\\(?:angle)\s+([A-Za-z0-9]{1,3})\b", r"∠\1", text)
    text = re.sub(r"\\(?:Delta|triangle)\s*([A-Za-z]{3})", r"Δ \1", text)
    text = re.sub(r"Δ([A-Za-z]{3})", r"Δ \1", text)
    
    text = re.sub(r"\\perp|£", " ⊥ ", text)
    text = re.sub(r"\\parallel", " // ", text)
    text = re.sub(r"\\in", " ∈ ", text)
    text = re.sub(r"\\notin", " ∉ ", text)
    text = re.sub(r"\^?\\circ", "°", text)
    text = re.sub(r"\\degree", "°", text)
    text = text.replace("°°", "°")

    text = re.sub(r"\\(?:Leftrightarrow|iff)|<=>", " ⇔ ", text)
    text = re.sub(r"\\(?:Rightarrow|implies)|=>", " ⇒ ", text)
    text = re.sub(r"\\le(?:q)?|<=|≤", " ≤ ", text)
    text = re.sub(r"\\ge(?:q)?|>=|≥", " ≥ ", text)
    text = re.sub(r"\\ne(?:q)?|!=|≠", " ≠ ", text)
    text = re.sub(r"\\pm|±", " ± ", text)
    text = re.sub(r"\\times|\\cdot|\*", " · ", text)

    text = re.sub(r"\\sqrt\[3\]\{([^{}]+)\}", r"∛(\1)", text)
    text = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", text)
    text = re.sub(r"\\sqrt\s*([0-9a-zA-Z]+)", r"√\1", text)

    super_digits = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "n": "ⁿ"}
    def replace_power(match):
        power_str = match.group(1) or match.group(2) or match.group(3)
        return "".join(super_digits.get(c, c) for c in power_str)

    text = re.sub(r"\^([0-9n]+)|\^\(([^)]+)\)|\^\{([^}]+)\}", replace_power, text)
    text = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1 / \2)", text)
    
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def format_solution_step_by_step(raw_text: str) -> str:
    if not raw_text:
        return ""
    text = raw_text.replace("Lời giải chi tiết:", "").replace("Bài giải chi tiết:", "").strip()
    text = re.sub(r"(?m)^\s*([a-d]\))\s*", r"\n\n### **\1** ", text)
    text = re.sub(r"(?m)^\s*(Câu\s+\d+[\:\.]?)\s*", r"\n\n### **\1** ", text)
    
    super_digits = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "n": "ⁿ"}
    text = re.sub(r"\^([0-9n]+)|\^\(([^)]+)\)|\^\{([^}]+)\}", lambda m: "".join(super_digits.get(c, c) for c in (m.group(1) or m.group(2) or m.group(3))), text)

    text = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1 / \2)", text)
    text = re.sub(r"Δ\s*([A-Za-z]{3})", r"Δ \1", text)
    text = re.sub(r"\\(?:widehat|hat)\s*[\{\[]\s*([A-Za-z0-9]{1,3})\s*[\}\]]", r"∠\1", text)
    text = re.sub(r"(?<=\.)\s*-\s*", r"\n- ", text)
    text = re.sub(r"\s*(?:=>|⇒|\\Rightarrow)\s*", r"\n  - ⇒ ", text)
    text = re.sub(r"\s*(?:<=>|⇔|\\Leftrightarrow)\s*", r"\n  - ⇔ ", text)
    
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if l:
            l = re.sub(r"\${2,}", "", l)
            l = re.sub(r"\$\s*\$", "", l)
            cleaned_lines.append(l)
    return "\n\n".join(cleaned_lines)

GAME_PROMPT = """
Bạn là Trợ lý Sư phạm Toán 8 của Cô Mai Phương theo chuẩn chương trình GDPT 2018 (Kết nối tri thức).
QUY TẮC BẮT BUỘC TUÂN THỦ VỀ KIẾN THỨC TOÁN 8:
1. TUYỆT ĐỐI KHÔNG SỬ DỤNG KIẾN THỨC VỀ ĐƯỜNG TRÒN (như đường tròn ngoại tiếp, tâm O cách đều các đỉnh, bán kính...) vì đây là kiến thức hình học lớp 9.
2. ĐỐI VỚI HÌNH HỌC: Chỉ sử dụng định nghĩa, tính chất tứ giác, hình bình hành, hình chữ nhật, hình thoi, hình vuông, định lý Pythagore hoặc tam giác đồng dạng.
3. ĐỐI VỚI is_finished = true:
   - full_solution: Bài giải chi tiết chuẩn mực đúng tiến độ SGK 8.
   - ggb_commands: Mảng các chuỗi lệnh GeoGebra (tiếng Anh) để tự động dựng hình chính xác đúng với đề bài trong ảnh (Ví dụ: ["A = (0, 4)", "B = (-3, 0)", "C = (3, 0)", "Polygon(A, B, C)", "H = (0, 1)"]).

TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON:
{
  "total_steps": 3,
  "subject_type": "algebra" HOẶC "geometry",
  "feedback": "Khen ngợi/động viên ngắn 1 câu",
  "question": "Câu hỏi gợi mở ngắn",
  "options": [
    "Phương án 1",
    "Phương án 2",
    "Phương án 3",
    "Phương án 4"
  ],
  "correct_index": 0,
  "explanation": "Giải thích ngắn theo định lý hình học lớp 8",
  "is_finished": false,
  "full_solution": "",
  "ggb_commands": []
}
"""

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
        raise Exception("Nội dung phản hồi bị rỗng, vui lòng thử lại!")

    if is_json:
        clean_text = re.sub(r"^```(?:json)?\s*|```$", "", text_out.strip(), flags=re.MULTILINE)
        match = re.search(r"\{[\s\S]*\}", clean_text)
        target_str = match.group(0) if match else clean_text
        try:
            data = json.loads(target_str, strict=False)
        except Exception:
            fixed_str = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', target_str)
            data = json.loads(fixed_str, strict=False)
        
        if "options" in data and isinstance(data["options"], list) and len(data["options"]) > 1:
            opts = data["options"]
            corr_idx = data.get("correct_index", 0)
            if 0 <= corr_idx < len(opts):
                indexed_opts = list(enumerate(opts))
                random.shuffle(indexed_opts)
                new_opts = []
                new_corr_idx = 0
                for new_i, (old_i, val) in enumerate(indexed_opts):
                    new_opts.append(val)
                    if old_i == corr_idx:
                        new_corr_idx = new_i
                data["options"] = new_opts
                data["correct_index"] = new_corr_idx

        return data

    return text_out

if "submission_history" not in st.session_state:
    st.session_state.submission_history = []

# ================= BANNER VŨ TRỤ =================
st.markdown("""
<div class="hero-banner">
    <h1>🚀 PHI HÀNH GIA TOÁN HỌC 8</h1>
    <p>Khám phá Vũ trụ Tri thức Đại số & Hình học cùng cô Mai Phương • Học tập gợi mở từng bước</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🪐 Thử Thách Tương Tác", 
    "📝 Nộp Bài Tập", 
    "👾 Đại Chiến Bowser",
    "📊 Bảng Điểm Lớp"
])

# ================= TAB 1: GAME TƯƠNG TÁC =================
with tab1:
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "total_steps" not in st.session_state:
        st.session_state.total_steps = 3
    if "card" not in st.session_state:
        st.session_state.card = None
    if "answered" not in st.session_state:
        st.session_state.answered = False
    if "selected_idx" not in st.session_state:
        st.session_state.selected_idx = None
    if "img_data" not in st.session_state:
        st.session_state.img_data = None
    if "reward" not in st.session_state:
        st.session_state.reward = None
    if "reward_ggb" not in st.session_state:
        st.session_state.reward_ggb = None

    with st.expander("📸 Trạm quét ảnh bài toán (Số học, Đại số hoặc Hình học)", expanded=(st.session_state.card is None)):
        up_game_img = st.file_uploader("Tải/chụp ảnh bài toán:", type=["jpg", "png", "jpeg"], key="up_game_img")
        math_mode = st.radio("Phân loại hệ thống:", ["Tự động nhận diện", "Toán Số (Đại số)", "Toán Hình (Hình học)"], horizontal=True)
        
        if up_game_img:
            st.session_state.img_data = Image.open(up_game_img)
            st.image(st.session_state.img_data, caption="Ảnh đề bài đang xử lý", use_container_width=True)

        if st.session_state.img_data and st.session_state.card is None:
            if st.button("🚀 Khởi động Trạm thử thách Bước 1!", type="primary", use_container_width=True):
                with st.spinner("Phi hành đoàn AI đang phân tích quỹ đạo đề bài theo chuẩn SGK Toán 8..."):
                    try:
                        p_start = f"Tạo câu hỏi thử thách Bước 1 ngắn gọn. Phân loại yêu cầu: {math_mode}. TUYỆT ĐỐI KHÔNG dùng đường tròn."
                        c_data = execute_gemini_request([st.session_state.img_data, p_start], GAME_PROMPT, is_json=True)
                        st.session_state.card = c_data
                        st.session_state.total_steps = c_data.get("total_steps", 3)
                        st.session_state.step = 1
                        st.session_state.answered = False
                        st.session_state.reward = None
                        st.session_state.reward_ggb = None
                        st.rerun()
                    except Exception as err:
                        st.error(f"Lỗi nạp thử thách: {err}")

    card = st.session_state.card
    if card:
        total = st.session_state.total_steps
        curr = st.session_state.step
        progress_val = min(int((curr / max(total, 1)) * 100), 100)
        st.progress(progress_val)

        badge_type = "ĐẠI SỐ" if card.get("subject_type") == "algebra" else "HÌNH HỌC"
        st.markdown(f'<span class="step-badge">[{badge_type}] TRẠM KHÔNG GIAN: BƯỚC {curr} / {total}</span>', unsafe_allow_html=True)
        
        fb = format_math(card.get("feedback", ""))
        if fb:
            st.info(f"💡 {fb}")

        st.markdown(f"#### 🎯 {format_math(card.get('question', ''))}")
        st.write("")

        opts = card.get("options", [])
        correct = card.get("correct_index", 0)

        if not st.session_state.answered:
            st.markdown("**👉 Phi hành gia hãy chọn một tọa độ đáp án đúng nhất:**")
            for idx, opt in enumerate(opts):
                clean_opt = format_math(opt)
                clean_opt = re.sub(r"^[A-D]\s*[\.\:\)]\s*", "", clean_opt)
                label = f"{chr(65+idx)}. {clean_opt}"
                if st.button(label, key=f"btn_choice_{idx}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.selected_idx = idx
                    st.rerun()
        else:
            sel = st.session_state.selected_idx
            sel_text = format_math(opts[sel]) if (sel is not None and sel < len(opts)) else ""
            sel_text = re.sub(r"^[A-D]\s*[\.\:\)]\s*", "", sel_text)

            correct_text = format_math(opts[correct]) if correct < len(opts) else ""
            correct_text = re.sub(r"^[A-D]\s*[\.\:\)]\s*", "", correct_text)

            if sel == correct:
                st.success("🎉 **Chính xác!** Quỹ đạo tư duy chuẩn xác.")
            else:
                st.error("❌ **Chệch quỹ đạo.**")
                st.markdown(f"Đáp án chuẩn: **{chr(65+correct)}. {correct_text}**")

            st.markdown(f"**💡 Trạm phân tích:** {format_math(card.get('explanation', ''))}")

            is_finish = card.get("is_finished") or (curr >= total)

            if is_finish:
                st.balloons()
                st.success("🏆 **HOÀN THÀNH XUẤT SẮC! Chinh phục trọn vẹn hành tinh toán học!**")

                if not st.session_state.reward:
                    sol = card.get("full_solution", "")
                    ggb_cmds = card.get("ggb_commands", [])
                    if (not sol or not ggb_cmds) and st.session_state.img_data:
                        with st.spinner("Đang mở khóa kho báu lời giải và trạm hình học GeoGebra không gian..."):
                            p_sol = """Hãy viết bài giải mẫu mực hoàn chỉnh đúng chuẩn kiến thức SGK Toán 8 (Kết nối tri thức). 
                            TUYỆT ĐỐI KHÔNG dùng kiến thức đường tròn.
                            Nếu là Toán Hình: BẮT BUỘC sinh mảng ggb_commands chứa các lệnh GeoGebra tiếng Anh để dựng đúng hình của đề bài.
                            Trả về JSON: {"full_solution": "...", "ggb_commands": ["..."]}"""
                            try:
                                res_final = execute_gemini_request([st.session_state.img_data, p_sol], is_json=True)
                                sol = res_final.get("full_solution", "")
                                ggb_cmds = res_final.get("ggb_commands", [])
                            except Exception as e:
                                sol = "Đã xảy ra lỗi khi tạo lời giải chi tiết."
                    st.session_state.reward = sol
                    st.session_state.reward_ggb = ggb_cmds

                st.markdown("""
                <div class="reward-box">
                    <h3 style="color: #34d399; margin-top:0;">🎁 KHO BÁU PHẦN THƯỞNG: BÀI GIẢI MẪU HOÀN CHỈNH</h3>
                    <p style="color: #a7f3d0; font-size: 14px;">Hãy ghi chép cẩn thận vào nhật ký học tập nhé!</p>
                </div>
                """, unsafe_allow_html=True)

                if card.get("subject_type") == "geometry":
                    st.markdown("#### 📐 Trạm Hình học không gian động GeoGebra:")
                    cmds = st.session_state.reward_ggb or ["A = (0, 4)", "B = (-3, 0)", "C = (3, 0)", "Polygon(A, B, C)"]
                    commands_js = "".join([f'try {{ api.evalCommand("{cmd}"); }} catch(e) {{}} \n' for cmd in cmds])

                    geogebra_html = f"""
                    <div class="geogebra-container">
                        <script src="https://www.geogebra.org/apps/deployggb.js"></script>
                        <div id="ggb-element"></div>
                        <script>
                        var ggbApp = new GGBApplet({{
                            "ui:design": "simple",
                            "showToolBar": false,
                            "showAlgebraInput": false,
                            "showMenuBar": false,
                            "width": 640,
                            "height": 400,
                            "appletOnLoad": function(api) {{
                                {commands_js}
                            }}
                        }}, true);
                        window.addEventListener("load", function() {{
                            ggbApp.inject('ggb-element');
                        }});
                        </script>
                    </div>
                    """
                    components.html(geogebra_html, height=430, scrolling=False)

                st.markdown("#### 📝 Lời giải chi tiết:")
                formatted_solution = format_solution_step_by_step(st.session_state.reward or "")
                st.markdown(formatted_solution)

                st.write("")
                st.success("📝 **Bước tiếp theo:** Hãy chuyển sang tab **'Nộp Bài Tập'** để truyền tín hiệu bài làm về trạm điều khiển của cô nhé!")
            else:
                st.write("")
                if st.button("➡️ Tiến tới trạm tiếp theo", type="primary", use_container_width=True):
                    with st.spinner("Đang dịch chuyển qua không gian tiếp theo..."):
                        p_next = f"""Học sinh vừa vượt qua bước {curr} với đáp án đúng: {correct_text}. Tạo thử thách trắc nghiệm bước {curr + 1} / {total}. 
                        TUYỆT ĐỐI KHÔNG dùng đường tròn hoặc kiến thức ngoài chương trình lớp 8."""
                        try:
                            st.session_state.card = execute_gemini_request([st.session_state.img_data, p_next], GAME_PROMPT, is_json=True)
                            st.session_state.step += 1
                            st.session_state.answered = False
                            st.session_state.selected_idx = None
                            st.rerun()
                        except Exception as err:
                            st.error(f"Lỗi tải màn: {err}")

        st.write("")
        if st.button("🔄 Khám phá hành tinh bài tập khác", use_container_width=True):
            st.session_state.step = 1
            st.session_state.card = None
            st.session_state.answered = False
            st.session_state.selected_idx = None
            st.session_state.img_data = None
            st.session_state.reward = None
            st.session_state.reward_ggb = None
            st.rerun()

# ================= TAB 2: NỘP BÀI & CHẤM ĐIỂM =================
with tab2:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(56, 189, 248, 0.3); padding: 16px; border-radius: 16px; margin-bottom: 20px;">
        <span style="font-weight: 700; color: #38bdf8;">📋 Trạm truyền dữ liệu bài làm viết tay - AI giám sát theo Rubric chuẩn môn Toán THCS</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        s_name = st.text_input("Tên phi hành gia (Họ và tên):")
    with c2:
        s_class = st.selectbox("Hạm đội lớp:", ["8A13", "8A18"])

    topic = st.selectbox("Chọn hành tinh chuyên đề:", [
        "Đại số 8: Đơn thức và Đa thức nhiều biến",
        "Đại số 8: Các hằng đẳng thức đáng nhớ",
        "Đại số 8: Phân tích đa thức thành nhân tử",
        "Đại số 8: Phân thức đại số và rút gọn phân thức",
        "Đại số 8: Phương trình bậc nhất một ẩn",
        "Đại số 8: Giải bài toán bằng cách lập phương trình",
        "Đại số 8: Hàm số bậc nhất và đồ thị",
        "Hình học 8: Tứ giác và Hình thang cân",
        "Hình học 8: Hình bình hành và Hình chữ nhật",
        "Hình học 8: Hình thoi và Hình vuông",
        "Hình học 8: Định lý Thalès trong tam giác",
        "Hình học 8: Tam giác đồng dạng và định lý liên quan",
        "Hình học 8: Hình chóp tam giác đều & tứ giác đều",
        "Bài kiểm tra tổng hợp vũ trụ (Số và Hình)"
    ])

    up_hw = st.file_uploader("📸 Truyền ảnh nhật ký bài giải viết tay trong vở:", type=["jpg", "png", "jpeg"], key="hw_submit_img")

    if st.button("🚀 Phóng tín hiệu nộp bài và nhận điểm", type="primary", use_container_width=True):
        if not s_name:
            st.warning("Phi hành gia hãy nhập Họ và tên trước khi phóng tín hiệu nhé!")
        elif not up_hw:
            st.warning("Bạn chưa đính kèm ảnh nhật ký bài làm!")
        else:
            with st.spinner("Trạm AI đang quét và chấm điểm chi tiết theo Rubric Vũ trụ Toán..."):
                try:
                    hw_img = Image.open(up_hw)
                    RUBRIC = f"""
Bạn là Giám khảo chấm thi môn Toán THCS tại Việt Nam.
Chuyên đề nộp: "{topic}".
Đọc ảnh bài làm viết tay của học sinh và đánh giá theo Rubric thang điểm 10 đúng chuẩn chương trình KNTT SGK 8 (TUYỆT ĐỐI KHÔNG dùng đường tròn).

ĐỊNH DẠNG BẮT BUỘC TRẢ VỀ:
- Tổng điểm: [Điểm số]/10
1. Kỹ năng nền tảng / Hình vẽ ([Điểm]/2.0 điểm):
   - Ưu điểm: ...
   - Hạn chế: ...
2. Quá trình biến đổi & Lập luận ([Điểm]/6.0 điểm):
   - Ưu điểm: ...
   - Hạn chế: ...
3. Trình bày & Kết luận ([Điểm]/2.0 điểm):
   - Ưu điểm: ...
   - Hạn chế: ...
"""
                    score_res = execute_gemini_request([hw_img, RUBRIC])
                    score_res_clean = format_math(score_res)

                    score_match = re.search(r"(\d+(?:[.,]\d+)?)\s*/\s*10", score_res_clean)
                    extracted_score = score_match.group(1).replace(",", ".") if score_match else "Chưa xác định"

                    sub_record = {
                        "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Họ và tên": s_name,
                        "Lớp": s_class,
                        "Bài tập": topic,
                        "Điểm số": extracted_score,
                        "Nhận xét của AI": score_res_clean.replace("\n", " ")
                    }
                    st.session_state.submission_history.append(sub_record)

                    webhook_url = st.secrets.get("GOOGLE_SHEET_WEBHOOK_URL")
                    if webhook_url:
                        payload = {
                            "time": sub_record["Thời gian"],
                            "name": s_name,
                            "student_class": s_class,
                            "topic": topic,
                            "score": extracted_score,
                            "feedback": sub_record["Nhận xét của AI"]
                        }
                        try:
                            requests.post(webhook_url, json=payload, timeout=5)
                        except Exception:
                            pass

                    st.success("🎉 Tín hiệu đã truyền thành công! Điểm số tự động cập nhật về hạm đội của cô!")
                    st.markdown(f"### Kết quả của phi hành gia: **{s_name}** - Hạm đội **{s_class}**")
                    st.markdown(score_res_clean)
                except Exception as err:
                    st.error(f"Lỗi truyền tín hiệu: {err}")

# ================= TAB 3: MINIGAME ĐẠI CHIẾN BOWSER (VŨ TRỤ TỨ GIÁC) =================
with tab3:
    st.subheader("👾 Trạm Không Gian: Đại Chiến Bowser (Tứ Giác Toán 8)")
    st.caption("Vượt qua 5 ải Tứ giác hệ thống & Tiêu diệt trùm Bowser để nhận +5 điểm cộng thực tế từ Cô Mai Phương!")

    sheet_webhook = st.secrets.get("GOOGLE_SHEET_WEBHOOK_URL", "https://script.google.com/macros/s/AKfycbwYEXAMPLE_REPLACE_HERE/exec")

    mario_game_code = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
      <script src="https://cdn.tailwindcss.com"></script>
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
        .font-pixel { font-family: 'Press Start 2P', monospace; }
        .font-body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .shake {
          animation: shake-anim 0.35s cubic-bezier(.36,.07,.19,.97) both;
        }
        @keyframes shake-anim {
          10%, 90% { transform: translate3d(-2px, 0, 0); }
          20%, 80% { transform: translate3d(4px, 0, 0); }
          30%, 50%, 70% { transform: translate3d(-6px, 0, 0); }
          40%, 60% { transform: translate3d(6px, 0, 0); }
        }
      </style>
    </head>
    <body class="bg-slate-950 text-slate-100 font-body min-h-screen flex flex-col items-center justify-start p-2 select-none">

      <div id="login-modal" class="fixed inset-0 z-50 bg-slate-950/95 backdrop-blur-md flex items-center justify-center p-4">
        <div class="bg-slate-900 border-2 border-amber-400/80 rounded-2xl max-w-md w-full p-6 shadow-2xl text-center">
          <div class="inline-block p-3 bg-indigo-600 rounded-2xl shadow-lg mb-3">
            <span class="font-pixel text-2xl text-white">🚀</span>
          </div>
          <h1 class="text-xl font-extrabold text-amber-400 mb-1">VŨ TRỤ TOÁN HỌC - CÔ MAI PHƯƠNG</h1>
          <p class="text-xs text-slate-400 mb-5">Đại chiến Bowser - Vượt ải Tứ Giác Toán 8</p>
          
          <div class="space-y-3.5 text-left mb-6">
            <div>
              <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Tên Phi Hành Gia:</label>
              <input type="text" id="input-name" placeholder="Ví dụ: Nguyễn Văn An" class="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-400">
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Hạm đội Lớp:</label>
              <input type="text" id="input-class" placeholder="Ví dụ: 8A13" class="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-400">
            </div>
          </div>

          <div class="bg-slate-800/80 border border-slate-700 rounded-xl p-3 text-xs text-slate-300 text-left mb-5 space-y-1">
            <p>• <b>5 Mạng sống (❤️❤️❤️❤️❤️)</b>. Tự động phiêu lưu không gian!</p>
            <p>• Thời gian: <b>15s</b> (Nhận biết), <b>20s</b> (Thông hiểu), <b>30s</b> (Vận dụng).</p>
            <p>• Hạ gục Bowser nhận ngay <b>+5 Điểm cộng thực tế</b> từ Cô Mai Phương!</p>
          </div>

          <button id="btn-start-game" class="w-full py-3.5 bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white font-extrabold text-sm rounded-xl shadow-lg transition transform active:scale-95">
            BẮT ĐẦU PHÓNG VŨ TRỤ NGAY
          </button>
        </div>
      </div>

      <header class="w-full max-w-2xl flex items-center justify-between bg-slate-900/90 border border-slate-800 px-3 py-2 rounded-2xl mb-2 shadow-lg">
        <div class="flex items-center space-x-2">
          <div class="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center font-pixel text-white text-[10px]">🚀</div>
          <div>
            <h2 class="text-xs font-extrabold text-amber-400 leading-tight">PHI HÀNH GIA TOÁN 8</h2>
            <p id="hud-student" class="text-[10px] text-slate-400">Phi hành gia: Đang kết nối...</p>
          </div>
        </div>
        
        <div class="flex items-center space-x-3 text-right">
          <div>
            <div class="text-[9px] text-slate-400 font-bold uppercase">Điểm</div>
            <div id="hud-score" class="font-pixel text-xs text-amber-400">0</div>
          </div>
          <div>
            <div class="text-[9px] text-slate-400 font-bold uppercase">Mạng</div>
            <div id="hud-lives" class="text-xs">❤️❤️❤️❤️❤️</div>
          </div>
          <button id="btn-toggle-sound" class="p-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 text-xs">🔊</button>
        </div>
      </header>

      <main id="game-arena" class="relative w-full max-w-2xl aspect-[16/9] bg-slate-950 rounded-2xl border-2 border-cyan-500/60 shadow-2xl overflow-hidden">
        <canvas id="gameCanvas" width="860" height="484" class="w-full h-full block"></canvas>
      </main>

      <div id="quiz-modal" class="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-sm flex items-center justify-center p-3 hidden">
        <div class="bg-slate-900 border-2 border-sky-400/90 rounded-2xl max-w-xl w-full p-4 shadow-2xl flex flex-col max-h-[92vh] overflow-y-auto">
          
          <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
            <span id="quiz-level-badge" class="px-2.5 py-1 bg-sky-500/20 text-sky-400 border border-sky-500/40 rounded-lg text-xs font-bold uppercase">
              NHẬN BIẾT (15s)
            </span>
            <div class="flex items-center space-x-1.5 font-pixel text-xs text-amber-400">
              <span>⏳</span>
              <span id="quiz-timer-text">15s</span>
            </div>
          </div>

          <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-3">
            <div id="quiz-timer-bar" class="h-full bg-amber-400 transition-all duration-100 ease-linear" style="width: 100%;"></div>
          </div>

          <div id="quiz-question-text" class="text-sm font-bold text-amber-200 mb-3 leading-relaxed">
            Đề bài...
          </div>

          <div id="quiz-options-container" class="space-y-2 mb-2"></div>

          <div id="quiz-short-container" class="space-y-2 mb-2 hidden">
            <input type="text" id="quiz-short-input" placeholder="Nhập đáp số hoặc tên hình..." autocomplete="off" class="w-full bg-slate-800 border-2 border-sky-500/60 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-400">
            <button id="quiz-short-submit" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-md transition">
              XÁC NHẬN TỌA ĐỘ (ENTER)
            </button>
          </div>

          <div id="quiz-feedback" class="mt-2 text-xs font-semibold min-h-[20px]"></div>
        </div>
      </div>

      <div id="stage-clear-modal" class="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-sm flex items-center justify-center p-4 hidden">
        <div class="bg-slate-900 border-2 border-emerald-400 rounded-2xl max-w-md w-full p-6 text-center shadow-2xl">
          <div class="text-3xl mb-2">🌟</div>
          <h3 id="stage-clear-title" class="text-base font-extrabold text-emerald-400 mb-1">VƯỢT TRẠM THÀNH CÔNG!</h3>
          <p class="text-xs text-amber-400 font-bold mb-3">NHẬT KÝ TỪ CÔ MAI PHƯƠNG</p>
          
          <div id="stage-clear-msg" class="bg-slate-800/80 border border-slate-700 rounded-xl p-3.5 text-xs text-slate-200 text-left mb-5 leading-relaxed"></div>

          <button id="btn-continue-next-stage" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl transition shadow-lg">
            TIẾP TỤC KHÁM PHÁ TRẠM TIẾP THEO ⏩
          </button>
        </div>
      </div>

      <div id="summary-modal" class="fixed inset-0 z-50 bg-slate-950/95 backdrop-blur-md flex items-center justify-center p-3 hidden">
        <div class="bg-slate-900 border-2 border-amber-400 rounded-2xl max-w-md w-full p-5 shadow-2xl flex flex-col max-h-[92vh] overflow-y-auto">
          
          <div class="text-center mb-3">
            <span id="summary-badge-icon" class="text-3xl">🏆</span>
            <h2 id="summary-title" class="text-lg font-extrabold text-amber-400 mt-1">VINH DANH VŨ TRỤ!</h2>
            <p id="summary-subtitle" class="text-[11px] text-emerald-400 font-semibold">Đã hoàn thành xuất sắc nhiệm vụ không gian</p>
          </div>

          <div class="bg-slate-800/80 border border-slate-700 rounded-xl p-3 mb-3 grid grid-cols-2 gap-2 text-xs">
            <div><span class="text-slate-400">Phi hành gia:</span> <b id="sum-name" class="text-white">...</b></div>
            <div><span class="text-slate-400">Hạm đội:</span> <b id="sum-class" class="text-white">...</b></div>
            <div><span class="text-slate-400">Mã trạm:</span> <b id="sum-examcode" class="text-amber-300">...</b></div>
            <div><span class="text-slate-400">Tổng điểm:</span> <b id="sum-score" class="text-amber-400 font-pixel">0</b></div>
            <div class="col-span-2 bg-emerald-950/60 border border-emerald-500/40 p-2 rounded-lg text-emerald-300 text-center font-bold">
              🎁 Thưởng trạm: <span id="sum-bonus" class="text-amber-300 font-extrabold">+5 ĐIỂM CỘNG</span> từ Cô Mai Phương!
            </div>
          </div>

          <div id="summary-teacher-note" class="bg-amber-950/30 border border-amber-500/30 rounded-xl p-3 text-xs text-amber-200 mb-3 leading-relaxed"></div>

          <div id="sync-status-box" class="border border-slate-700 bg-slate-950/60 rounded-xl p-2.5 text-center mb-3">
            <div id="sync-status-text" class="text-xs text-yellow-400 font-medium">
              ⏳ Đang truyền kết quả về trạm Google Sheets...
            </div>
            <button id="btn-retry-sync" class="mt-2 hidden px-3 py-1 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-lg transition">
              🔄 Truyền lại dữ liệu
            </button>
          </div>

          <button onclick="location.reload()" class="w-full py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white font-bold text-xs rounded-xl transition">
            PHÓNG LẠI HÀNH TRÌNH MỚI 🔁
          </button>
        </div>
      </div>

      <script>
        const GOOGLE_SCRIPT_WEBAPP_URL = "WEBHOOK_URL_PLACEHOLDER";

        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        let isSoundMuted = false;

        function playTone(freq, type, duration, vol = 0.15) {
          if (isSoundMuted) return;
          if (audioCtx.state === 'suspended') audioCtx.resume();
          try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(vol, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
          } catch(e) {}
        }

        function sndJump() { playTone(220, 'square', 0.12, 0.1); setTimeout(() => playTone(550, 'square', 0.12, 0.1), 60); }
        function sndCoin() { playTone(1046, 'square', 0.08, 0.12); setTimeout(() => playTone(1318, 'square', 0.2, 0.12), 70); }
        function sndFireball() { playTone(350, 'triangle', 0.12, 0.2); setTimeout(() => playTone(150, 'sawtooth', 0.25, 0.2), 80); }
        function sndWrong() { playTone(180, 'sawtooth', 0.2, 0.2); setTimeout(() => playTone(100, 'sawtooth', 0.3, 0.2), 150); }
        function sndRoar() { playTone(90, 'sawtooth', 0.4, 0.25); setTimeout(() => playTone(50, 'sawtooth', 0.45, 0.25), 180); }

        let bgmInterval = null;
        const bgmNotes = [330, 330, 0, 330, 0, 262, 330, 392];
        let noteIdx = 0;
        function startBgm() {
          if (bgmInterval || isSoundMuted) return;
          bgmInterval = setInterval(() => {
            if (!gameState.isPaused && !gameState.isGameOver && bgmNotes[noteIdx] > 0) {
              playTone(bgmNotes[noteIdx], 'square', 0.08, 0.025);
            }
            noteIdx = (noteIdx + 1) % bgmNotes.length;
          }, 240);
        }
        function stopBgm() { if (bgmInterval) { clearInterval(bgmInterval); bgmInterval = null; } }

        document.getElementById("btn-toggle-sound").onclick = () => {
          isSoundMuted = !isSoundMuted;
          document.getElementById("btn-toggle-sound").textContent = isSoundMuted ? "🔇" : "🔊";
          if (isSoundMuted) stopBgm(); else startBgm();
        };

        const rawQuestionPool = {
          stage1: [
            { level: "Nhận biết", time: 15, type: "short", q: "Tổng các góc trong một tứ giác lồi luôn bằng bao nhiêu độ? (Chỉ nhập số)", correctAnswers: ["360", "360 độ", "360°"], explain: "Định lý: Tổng các góc của một tứ giác luôn bằng 360 độ." },
            { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác luôn nằm trong một nửa mặt phẳng có bờ là đường thẳng chứa bất kì cạnh nào gọi là tứ giác gì?", correctAnswers: ["lồi", "tứ giác lồi"], explain: "Định nghĩa: Đó là tứ giác lồi." },
            { level: "Thông hiểu", time: 20, type: "mcq", q: "Một tứ giác lồi có thể có nhiều nhất bao nhiêu góc nhọn?", answers: ["3 góc nhọn", "4 góc nhọn", "2 góc nhọn"], correct: 0, explain: "Nếu có 4 góc nhọn thì tổng 4 góc < 360° (vô lý). Vậy tối đa có 3 góc nhọn." },
            { level: "Vận dụng", time: 30, type: "short", q: "Tứ giác ABCD có góc A = 70°, B = 90°, C = 80°. Tính số đo góc D (nhập số):", correctAnswers: ["120", "120 độ", "120°"], explain: "Góc D = 360° - (70° + 90° + 80°) = 120°." }
          ],
          stage2: [
            { level: "Nhận biết", time: 15, type: "short", q: "Hình thang có hai góc kề một đáy bằng nhau là hình thang gì?", correctAnswers: ["cân", "hình thang cân"], explain: "Định nghĩa SGK: Hình thang có 2 góc kề một đáy bằng nhau là hình thang cân." },
            { level: "Nhận biết", time: 15, type: "mcq", q: "Trong hình thang cân, hai đường chéo có mối quan hệ gì với nhau?", answers: ["Bằng nhau", "Vuông góc với nhau", "Cắt nhau tại trung điểm"], correct: 0, explain: "Tính chất SGK: Trong hình thang cân, hai đường chéo bằng nhau." },
            { level: "Thông hiểu", time: 20, type: "short", q: "Hình thang có hai đường chéo bằng nhau là hình thang gì?", correctAnswers: ["cân", "hình thang cân"], explain: "Dấu hiệu nhận biết: Hình thang có 2 đường chéo bằng nhau là hình thang cân." },
            { level: "Vận dụng", time: 30, type: "short", q: "Hình thang cân ABCD (AB // CD) có góc D = 70°. Tính số đo góc A kề cạnh bên AD (nhập số):", correctAnswers: ["110", "110 độ", "110°"], explain: "Vì AB // CD nên hai góc trong cùng phía bù nhau: Góc A = 180° - 70° = 110°." }
          ],
          stage3: [
            { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có các cạnh đối song song được gọi là hình gì?", correctAnswers: ["hình bình hành", "bình hành"], explain: "Định nghĩa: Hình bình hành là tứ giác có các cạnh đối song song." },
            { level: "Nhận biết", time: 15, type: "mcq", q: "Trong hình bình hành, hai đường chéo có tính chất gì?", answers: ["Cắt nhau tại trung điểm của mỗi đường", "Vuông góc với nhau", "Bằng nhau"], correct: 0, explain: "Tính chất: Hai đường chéo cắt nhau tại trung điểm của mỗi đường." },
            { level: "Thông hiểu", time: 20, type: "short", q: "Tứ giác có hai đường chéo cắt nhau tại trung điểm của mỗi đường là hình gì?", correctAnswers: ["hình bình hành", "bình hành"], explain: "Dấu hiệu nhận biết: Tứ giác có 2 đường chéo cắt nhau tại trung điểm là hình bình hành." },
            { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình thang có hai cạnh bên song song là hình gì?", answers: ["Hình bình hành", "Hình thang cân", "Hình chữ nhật"], correct: 0, explain: "Nhận xét SGK: Hình thang có 2 cạnh bên song song là hình bình hành." },
            { level: "Vận dụng", time: 30, type: "short", q: "Hình bình hành ABCD có góc A = 115°. Tính số đo góc đối C (nhập số):", correctAnswers: ["115", "115 độ", "115°"], explain: "Tính chất: Hai góc đối bằng nhau nên góc C = góc A = 115°." }
          ],
          stage4: [
            { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có bốn góc vuông được gọi là hình gì?", correctAnswers: ["hình chữ nhật", "chữ nhật"], explain: "Định nghĩa: Hình chữ nhật là tứ giác có bốn góc vuông." },
            { level: "Thông hiểu", time: 20, type: "short", q: "Hình bình hành có hai đường chéo bằng nhau là hình gì?", correctAnswers: ["hình chữ nhật", "chữ nhật"], explain: "Dấu hiệu nhận biết: Hình bình hành có 2 đường chéo bằng nhau là hình chữ nhật." },
            { level: "Thông hiểu", time: 20, type: "short", q: "Hình thang cân có một góc vuông là hình gì?", correctAnswers: ["hình chữ nhật", "chữ nhật"], explain: "Dấu hiệu: Hình thang cân có 1 góc vuông là hình chữ nhật." },
            { level: "Thông hiểu", time: 20, type: "mcq", q: "Trong tam giác vuông, đường trung tuyến ứng với cạnh huyền có độ dài bằng mấy phần cạnh huyền?", answers: ["Một nửa cạnh huyền", "Bằng cạnh huyền", "Gấp đôi cạnh huyền"], correct: 0, explain: "Định lý: Đường trung tuyến ứng với cạnh huyền bằng nửa cạnh huyền." },
            { level: "Vận dụng", time: 30, type: "short", q: "Cho tam giác ABC vuông tại A có cạnh huyền BC = 16 cm. Độ dài đường trung tuyến AM bằng mấy cm? (Nhập số):", correctAnswers: ["8", "8 cm", "8cm"], explain: "AM = BC / 2 = 16 / 2 = 8 cm." }
          ],
          stage5: [
            { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có bốn cạnh bằng nhau là hình gì?", correctAnswers: ["hình thoi", "thoi"], explain: "Định nghĩa: Hình thoi là tứ giác có bốn cạnh bằng nhau." },
            { level: "Thông hiểu", time: 20, type: "mcq", q: "Trong hình thoi, hai đường chéo có tính chất đặc trưng nào sau đây?", answers: ["Vuông góc với nhau và là tia phân giác các góc", "Bằng nhau và song song", "Cắt nhau tại 1/3 mỗi đường"], correct: 0, explain: "Tính chất: Hai đường chéo vuông góc và là phân giác các góc của hình thoi." },
            { level: "Thông hiểu", time: 20, type: "short", q: "Hình bình hành có hai đường chéo vuông góc với nhau là hình gì?", correctAnswers: ["hình thoi", "thoi"], explain: "Dấu hiệu: Hình bình hành có 2 đường chéo vuông góc là hình thoi." },
            { level: "Thông hiểu", time: 20, type: "short", q: "Hình chữ nhật có hai đường chéo vuông góc với nhau là hình gì?", correctAnswers: ["hình vuông", "vuông"], explain: "Dấu hiệu: Hình chữ nhật có 2 đường chéo vuông góc là hình vuông." },
            { level: "Vận dụng", time: 30, type: "short", q: "Một hình thoi có chu vi bằng 48 cm. Độ dài một cạnh của hình thoi đó bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["12", "12 cm", "12cm"], explain: "Độ dài 1 cạnh = 48 / 4 = 12 cm." }
          ],
          boss: [
            { level: "Vận dụng cao", time: 30, type: "mcq", q: "Nối trung điểm 4 cạnh của một hình chữ nhật ta luôn nhận được hình gì?", answers: ["Hình thoi", "Hình bình hành thông thường", "Hình vuông"], correct: 0, explain: "Bốn cạnh đều bằng nửa đường chéo HCN => Bằng nhau => Là Hình thoi." },
            { level: "Vận dụng cao", time: 30, type: "mcq", q: "Nối trung điểm 4 cạnh của một hình thoi ta luôn nhận được hình gì?", answers: ["Hình chữ nhật", "Hình vuông", "Hình bình hành góc 60°"], correct: 0, explain: "Vì hai đường chéo hình thoi vuông góc nên các cạnh kề vuông góc => Hình chữ nhật." },
            { level: "Vận dụng cao", time: 30, type: "short", q: "Hình thoi ABCD có cạnh bằng 8 cm và góc A = 60°. Độ dài đường chéo BD bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["8", "8 cm", "8cm"], explain: "Tam giác ABD cân có góc 60° nên là tam giác đều => BD = 8 cm." }
          ]
        };

        function shuffle(arr) {
          const a = [...arr];
          for (let i = a.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [a[i], a[j]] = [a[j], a[i]];
          }
          return a;
        }

        function buildExam() {
          return {
            code: "CMP-SPACE-8-" + Math.floor(1000 + Math.random() * 9000),
            stages: [
              { name: "Trạm 1: Tứ giác lồi", questions: shuffle(rawQuestionPool.stage1).slice(0, 3) },
              { name: "Trạm 2: Hình thang cân", questions: shuffle(rawQuestionPool.stage2).slice(0, 4) },
              { name: "Trạm 3: Hình bình hành", questions: shuffle(rawQuestionPool.stage3).slice(0, 5) },
              { name: "Trạm 4: Hình chữ nhật", questions: shuffle(rawQuestionPool.stage4).slice(0, 5) },
              { name: "Trạm 5: Hình thoi & Hình vuông", questions: shuffle(rawQuestionPool.stage5).slice(0, 5) },
            ],
            bossQuestions: shuffle(rawQuestionPool.boss).slice(0, 3)
          };
        }

        const gameState = {
          studentName: "", studentClass: "", examData: null,
          currentStageIdx: 0, currentQuestionIdx: 0, inBossFight: false,
          bossHp: 3, bossMaxHp: 3, score: 0, lives: 5, correctCount: 0,
          totalAnswered: 0, isPaused: true, isGameOver: false, defeatedBoss: false,
          timerSec: 15, timerMax: 15, timerInterval: null, lastPayload: null
        };

        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const arenaEl = document.getElementById("game-arena");

        const rocket = { x: 120, y: 330, w: 46, h: 28, vy: 0, isJumping: false, exhaustFlame: 0 };
        let worldOffset = 0;
        let meteorBox = { x: 750, y: 230, active: true, bounce: 0 };
        let laserBeam = { active: false, x: 0, y: 0, vx: 0 };

        function triggerShake() {
          arenaEl.classList.add("shake");
          setTimeout(() => arenaEl.classList.remove("shake"), 380);
        }

        function updateWorld() {
          if (gameState.isPaused || gameState.isGameOver) return;
          rocket.exhaustFlame += 0.4;

          if (rocket.isJumping) {
            rocket.y += rocket.vy;
            rocket.vy += 0.8;
            if (rocket.y >= 330) { rocket.y = 330; rocket.isJumping = false; }
          }

          if (laserBeam.active) {
            laserBeam.x += laserBeam.vx;
            if (laserBeam.x >= 680) {
              laserBeam.active = false;
              triggerShake();
              sndFireball();
            }
          }

          if (!gameState.inBossFight) {
            worldOffset += 3.5;
            meteorBox.x -= 3.5;
            if (meteorBox.x <= 220 && meteorBox.active) {
              meteorBox.active = false;
              openNextQuestion();
            }
          }
        }

        function drawWorld() {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          
          // Vẽ nền không gian vũ trụ & các ngôi sao lấp lánh
          ctx.fillStyle = gameState.inBossFight ? "#0f051d" : "#060913";
          ctx.fillRect(0, 0, canvas.width, canvas.height);

          ctx.fillStyle = "#ffffff";
          for(let i=0; i<30; i++) {
            let sx = (i * 37 + worldOffset * 0.3) % canvas.width;
            let sy = (i * 23) % (canvas.height - 50);
            ctx.fillRect(sx, sy, 2, 2);
          }

          // Vẽ bề mặt hành tinh bên dưới
          ctx.fillStyle = gameState.inBossFight ? "#31103f" : "#1e1b4b";
          ctx.fillRect(0, 394, canvas.width, 16);
          ctx.fillStyle = gameState.inBossFight ? "#581c87" : "#312e81";
          ctx.fillRect(0, 410, canvas.width, 74);

          // Vẽ thiên thạch / hộp bí ẩn không gian
          if (!gameState.inBossFight && meteorBox.x > -50) {
            ctx.fillStyle = "#f59e0b";
            ctx.fillRect(meteorBox.x, meteorBox.y, 44, 44);
            ctx.strokeStyle = "#b45309";
            ctx.lineWidth = 3;
            ctx.strokeRect(meteorBox.x, meteorBox.y, 44, 44);
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 24px monospace";
            ctx.fillText("?", meteorBox.x + 14, meteorBox.y + 31);
          }

          // Vẽ Tên lửa (Phi hành gia)
          ctx.fillStyle = "#38bdf8";
          ctx.beginPath();
          ctx.moveTo(rocket.x + rocket.w, rocket.y + rocket.h / 2);
          ctx.lineTo(rocket.x, rocket.y);
          ctx.lineTo(rocket.x + 10, rocket.y + rocket.h / 2);
          ctx.lineTo(rocket.x, rocket.y + rocket.h);
          ctx.closePath();
          ctx.fill();

          // Lửa tên lửa
          let flameSize = 8 + Math.sin(rocket.exhaustFlame) * 5;
          ctx.fillStyle = "#f97316";
          ctx.fillRect(rocket.x - flameSize, rocket.y + 10, flameSize, 8);

          if (laserBeam.active) {
            ctx.fillStyle = "#38bdf8";
            ctx.beginPath();
            ctx.arc(laserBeam.x, laserBeam.y, 14, 0, Math.PI * 2);
            ctx.fill();
          }

          // Vẽ Trùm Bowser Không Gian (Hành tinh độc ác)
          if (gameState.inBossFight && !gameState.defeatedBoss) {
            const bx = 680, by = 285;
            ctx.fillStyle = "#7c2d12";
            ctx.beginPath();
            ctx.arc(bx + 40, by + 45, 48, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = "#b91c1c";
            ctx.fillRect(bx + 10, by + 15, 60, 50);

            ctx.fillStyle = "#000";
            ctx.fillRect(bx - 20, by - 36, 120, 16);
            ctx.fillStyle = "#ef4444";
            const hpW = (gameState.bossHp / gameState.bossMaxHp) * 116;
            ctx.fillRect(bx - 18, by - 34, Math.max(0, hpW), 12);
            ctx.fillStyle = "#fff";
            ctx.font = "bold 10px monospace";
            ctx.fillText("TRÙM BOWSER: " + gameState.bossHp + "/" + gameState.bossMaxHp, bx - 14, by - 42);
          }
        }

        function gameLoop() {
          updateWorld();
          drawWorld();
          requestAnimationFrame(gameLoop);
        }
        gameLoop();

        document.getElementById("btn-start-game").onclick = () => {
          const name = document.getElementById("input-name").value.trim();
          const sClass = document.getElementById("input-class").value.trim();
          if (!name || !sClass) { alert("Em vui lòng nhập đầy đủ Tên và Lớp nhé!"); return; }
          gameState.studentName = name;
          gameState.studentClass = sClass;
          gameState.examData = buildExam();

          document.getElementById("login-modal").classList.add("hidden");
          document.getElementById("hud-student").textContent = name + " (" + sClass + ") • " + gameState.examData.code;
          gameState.isPaused = false;
          startBgm();
        };

        const quizModal = document.getElementById("quiz-modal");
        const badgeEl = document.getElementById("quiz-level-badge");
        const timerTextEl = document.getElementById("quiz-timer-text");
        const timerBarEl = document.getElementById("quiz-timer-bar");
        const questionTextEl = document.getElementById("quiz-question-text");
        const optionsBox = document.getElementById("quiz-options-container");
        const shortBox = document.getElementById("quiz-short-container");
        const shortInput = document.getElementById("quiz-short-input");
        const shortSubmit = document.getElementById("quiz-short-submit");
        const feedbackEl = document.getElementById("quiz-feedback");

        let currentQ = null;

        function openNextQuestion() {
          gameState.isPaused = true;
          feedbackEl.innerHTML = "";

          if (!gameState.inBossFight) {
            const curStage = gameState.examData.stages[gameState.currentStageIdx];
            currentQ = curStage.questions[gameState.currentQuestionIdx];
            badgeEl.textContent = gameState.examData.code + " • " + curStage.name + " (" + (gameState.currentQuestionIdx + 1) + "/" + curStage.questions.length + ")";
          } else {
            currentQ = gameState.examData.bossQuestions[gameState.bossMaxHp - gameState.bossHp];
            sndRoar();
            badgeEl.textContent = "⚔️ TIÊU DIỆT TRÙM HP: " + gameState.bossHp + "/" + gameState.bossMaxHp + " - VẬN DỤNG CAO";
          }

          questionTextEl.textContent = currentQ.q;
          quizModal.classList.remove("hidden");

          gameState.timerSec = currentQ.time;
          gameState.timerMax = currentQ.time;
          timerTextEl.textContent = gameState.timerSec + "s";
          timerBarEl.style.width = "100%";

          if (gameState.timerInterval) clearInterval(gameState.timerInterval);
          gameState.timerInterval = setInterval(() => {
            gameState.timerSec--;
            timerTextEl.textContent = gameState.timerSec + "s";
            const percent = Math.max(0, (gameState.timerSec / gameState.timerMax) * 100);
            timerBarEl.style.width = percent + "%";

            if (gameState.timerSec <= 0) {
              clearInterval(gameState.timerInterval);
              handleAnswer(false, "Đã hết thời gian không gian!");
            }
          }, 1000);

          if (currentQ.type === "mcq") {
            optionsBox.classList.remove("hidden");
            shortBox.classList.add("hidden");
            optionsBox.innerHTML = "";

            currentQ.answers.forEach((ans, idx) => {
              const btn = document.createElement("button");
              btn.className = "w-full text-left bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl p-3 text-xs font-semibold";
              btn.innerHTML = '<span class="text-amber-400 font-bold">' + (idx + 1) + '.</span> ' + ans;
              btn.onclick = () => {
                clearInterval(gameState.timerInterval);
                handleAnswer(idx === currentQ.correct);
              };
              optionsBox.appendChild(btn);
            });
          } else {
            optionsBox.classList.add("hidden");
            shortBox.classList.remove("hidden");
            shortInput.value = "";
            setTimeout(() => shortInput.focus(), 150);
          }
        }

        function submitShortAnswer() {
          const val = shortInput.value.trim().toLowerCase();
          if (!val) return;
          clearInterval(gameState.timerInterval);
          const isOk = currentQ.correctAnswers.some(ans => ans.toLowerCase() === val);
          handleAnswer(isOk);
        }
        shortSubmit.onclick = submitShortAnswer;
        shortInput.onkeydown = (e) => { if (e.key === "Enter") submitShortAnswer(); };

        function handleAnswer(isCorrect, customReason = null) {
          gameState.totalAnswered++;

          if (isCorrect) {
            sndCoin();
            gameState.correctCount++;
            gameState.score += gameState.inBossFight ? 300 : 100;
            document.getElementById("hud-score").textContent = gameState.score;
            feedbackEl.innerHTML = '<span class="text-emerald-400 font-bold">🎉 TỌA ĐỘ CHUẨN XÁC! +' + (gameState.inBossFight ? 300 : 100) + ' Điểm</span>';

            rocket.isJumping = true;
            rocket.vy = -12;

            if (gameState.inBossFight) {
              laserBeam.active = true;
              laserBeam.x = rocket.x + 30;
              laserBeam.y = rocket.y + 14;
              laserBeam.vx = 14;
              gameState.bossHp--;
            }

            setTimeout(() => {
              quizModal.classList.add("hidden");
              advanceProgress();
            }, 1100);
          } else {
            sndWrong();
            gameState.lives--;
            document.getElementById("hud-lives").textContent = "❤️".repeat(Math.max(0, gameState.lives)) || "💀 Hết";
            feedbackEl.innerHTML = '<span class="text-rose-400 font-bold">❌ ' + (customReason || "Sai quỹ đạo!") + '</span><br><span class="text-[11px] text-slate-300">Ghi nhớ: ' + currentQ.explain + '</span>';

            setTimeout(() => {
              quizModal.classList.add("hidden");
              if (gameState.lives <= 0) {
                finishGameSession(false);
              } else {
                advanceProgress();
              }
            }, 3000);
          }
        }

        const stageClearModal = document.getElementById("stage-clear-modal");
        const teacherNotes = [
          "Cô Mai Phương rất tự hào! Em đã nắm vững góc tứ giác lồi. Tiếp tục phóng tới Trạm 2 nhé!",
          "Xuất sắc! Em đã thuộc lòng tính chất hai đường chéo hình thang cân. Tiến lên Trạm 3!",
          "Tuyệt vời! Quỹ đạo hình bình hành đã được chinh phục. Phóng tới Trạm 4 nào!",
          "Quá đỉnh! Em vận dụng hoàn hảo tính chất hình chữ nhật. Trạm 5 đang chờ đón!",
          "Đã vượt qua 5 Trạm không gian! Hãy tập trung tối đa tiêu diệt trùm Bowser để nhận +5 Điểm!"
        ];

        function advanceProgress() {
          if (gameState.inBossFight) {
            if (gameState.bossHp <= 0) {
              gameState.defeatedBoss = true;
              finishGameSession(true);
            } else {
              setTimeout(() => openNextQuestion(), 600);
            }
            return;
          }

          const curStage = gameState.examData.stages[gameState.currentStageIdx];
          gameState.currentQuestionIdx++;

          if (gameState.currentQuestionIdx >= curStage.questions.length) {
            document.getElementById("stage-clear-title").textContent = "HOÀN THÀNH " + curStage.name.toUpperCase() + "!";
            document.getElementById("stage-clear-msg").textContent = teacherNotes[gameState.currentStageIdx];
            stageClearModal.classList.remove("hidden");
          } else {
            meteorBox.x = 760;
            meteorBox.active = true;
            gameState.isPaused = false;
          }
        }

        document.getElementById("btn-continue-next-stage").onclick = () => {
          stageClearModal.classList.add("hidden");
          gameState.currentStageIdx++;
          gameState.currentQuestionIdx = 0;

          if (gameState.currentStageIdx >= gameState.examData.stages.length) {
            gameState.inBossFight = true;
            sndRoar();
            setTimeout(() => openNextQuestion(), 600);
          } else {
            meteorBox.x = 760;
            meteorBox.active = true;
            gameState.isPaused = false;
          }
        };

        function finishGameSession(isVictory) {
          gameState.isGameOver = true;
          gameState.isPaused = true;
          stopBgm();

          document.getElementById("sum-name").textContent = gameState.studentName;
          document.getElementById("sum-class").textContent = gameState.studentClass;
          document.getElementById("sum-examcode").textContent = gameState.examData.code;
          document.getElementById("sum-score").textContent = gameState.score;

          if (isVictory) {
            document.getElementById("summary-badge-icon").textContent = "👑";
            document.getElementById("summary-title").textContent = "CHIẾN THẮNG VŨ TRỤ!";
            document.getElementById("sum-bonus").textContent = "+5 ĐIỂM CỘNG";
            document.getElementById("summary-teacher-note").innerHTML = '🎉 <b>Lời khen từ Cô Mai Phương:</b> Em đã hạ gục trùm Bowser xuất sắc! Cô cộng ngay <b>+5 điểm thực tế</b> vào sổ điểm cho em!';
          } else {
            document.getElementById("summary-badge-icon").textContent = "🛡️";
            document.getElementById("summary-title").textContent = "HOÀN THÀNH NHIỆM VỤ";
            document.getElementById("sum-bonus").textContent = "0 ĐIỂM";
            document.getElementById("summary-teacher-note").innerHTML = '💡 <b>Lời dặn từ Cô Mai Phương:</b> Em đã đạt <b>' + gameState.score + ' điểm</b>. Hãy xem lại kiến thức và phóng lại để đạt điểm tuyệt đối nhé!';
          }

          document.getElementById("summary-modal").classList.remove("hidden");

          const payload = {
            time: new Date().toLocaleString("vi-VN"),
            examCode: gameState.examData.code,
            name: gameState.studentName,
            student_class: gameState.studentClass,
            score: gameState.score,
            topic: "Minigame Vũ Trụ Tứ Giác (Bowser)",
            feedback: isVictory ? "Hạ gục Bowser (+5đ)" : "Chưa diệt Bowser"
          };

          gameState.lastPayload = payload;
          syncToGoogleSheets(payload);
        }

        async function syncToGoogleSheets(payload) {
          const syncStatusText = document.getElementById("sync-status-text");
          const retryBtn = document.getElementById("btn-retry-sync");

          syncStatusText.innerHTML = "⏳ Đang truyền kết quả về trạm Google Sheets của cô...";
          syncStatusText.className = "text-xs text-yellow-400 font-medium";
          retryBtn.classList.add("hidden");

          try {
            await fetch(GOOGLE_SCRIPT_WEBAPP_URL, {
              method: "POST",
              mode: "no-cors",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });

            syncStatusText.innerHTML = "✅ Đã lưu kết quả thành công vào trạm Google Sheets của Cô Mai Phương!";
            syncStatusText.className = "text-xs text-emerald-400 font-bold";
          } catch (err) {
            syncStatusText.innerHTML = '<div class="text-rose-400 font-bold">⚠️ Mất kết nối trạm!</div><div class="text-[10px] text-slate-300 mt-1">Hãy chụp màn hình gửi cô hoặc bấm nút truyền lại:</div>';
            retryBtn.classList.remove("hidden");
          }
        }

        document.getElementById("btn-retry-sync").onclick = () => {
          if (gameState.lastPayload) syncToGoogleSheets(gameState.lastPayload);
        };
      </script>
    </body>
    </html>
    """

    mario_game_code = mario_game_code.replace("WEBHOOK_URL_PLACEHOLDER", sheet_webhook)
    components.html(mario_game_code, height=720, scrolling=True)

# ================= TAB 4: BẢNG ĐIỂM LỚP =================
with tab4:
    st.markdown("### 🔒 Trạm Bảo Mật Sổ Điểm Giáo Viên")
    st.caption("Dữ liệu hạm đội học sinh được mã hóa bảo mật.")

    teacher_password = st.text_input("🔑 Nhập mật khẩu hạm đội để mở sổ điểm:", type="password", key="teacher_pass_tab4")
    ADMIN_PASS = "Maiphuong2026"

    if teacher_password:
        if teacher_password == ADMIN_PASS:
            st.success("🔓 Xác thực trạm thành công! Chào cô Mai Phương.")
            
            if len(st.session_state.submission_history) == 0:
                st.info("Chưa có phi hành gia nào truyền bài nộp trong phiên này.")
            else:
                df = pd.DataFrame(st.session_state.submission_history)
                st.dataframe(df, use_container_width=True)

                csv_data = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

                st.write("---")
                st.download_button(
                    label="📗 Tải file bảng điểm Vũ Trụ (.CSV cho Google Sheets)",
                    data=csv_data,
                    file_name=f"Bang_Diem_VuTru_Toan8_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
        else:
            st.error("⛔ Mật khẩu không chính xác! Khu vực hạn chế truy cập.")
    else:
        st.info("👉 Vui lòng nhập mật khẩu bảo mật để mở trạm theo dõi điểm.")
