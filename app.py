import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from PIL import Image
import hmac
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

    /* NỀN TOÀN TRANG: Đẩy hẳn hình ảnh sang bên trái màn hình */
    .stApp {
        background: linear-gradient(rgba(11, 15, 25, 0.2), rgba(11, 15, 25, 0.35)),
                    url('https://raw.githubusercontent.com/dophuong1795-hub/socratic-toan8/main/teacher_bg.jpg.jpg');
        background-size: cover;
        background-position: left center; /* Đẩy hẳn hình sang trái */
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

    /* Ô NHẬP LIỆU VÀ SELECTBOX TỐI MÀU DỄ ĐỌC */
    input[type="text"], input[type="password"], .stSelectbox [data-baseweb="select"] > div {
        background-color: rgba(30, 41, 59, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        border-radius: 12px !important;
    }

    .stSelectbox span, input[type="text"], input[type="password"] {
        color: #ffffff !important;
    }

    /* KHUNG UPLOAD ẢNH */
    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.85) !important;
        border: 2px dashed rgba(56, 189, 248, 0.6) !important;
        border-radius: 16px;
        padding: 15px;
    }

    [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span {
        color: #cbd5e1 !important;
    }

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

    /* ===== ẨN MENU, FOOTER, THANH CÔNG CỤ VÀ BIỂU TƯỢNG GITHUB ===== */
    #MainMenu,
    footer,
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stToolbarActions"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stAppDeployButton"],
    [data-testid="manage-app-button"],
    .stDeployButton,
    .stAppDeployButton,
    [class*="viewerBadge"],
    [class*="profileContainer"],
    a[href*="github.com"],
    a[href*="streamlit.io/cloud"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ================= ĐỌC SECRETS AN TOÀN =================
def get_secret(key, default=None):
    """Đọc st.secrets; không bị lỗi khi chưa có file secrets.toml."""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# Lấy Gemini API Key. Thiếu key thì chỉ tắt phần AI (tab 1, 2); game và sổ điểm vẫn dùng được.
API_KEY = get_secret("GEMINI_API_KEY")
# Link Web App Apps Script ghi điểm vào Google Sheet; Secrets GOOGLE_SHEET_WEBHOOK_URL (nếu có) được ưu tiên
DEFAULT_WEBHOOK = "https://script.google.com/macros/s/AKfycbzZ9lzrOGbOUJfalzR3cUH5aYXuOELw94aJvvb0BwVLq7eDYcZ9sLR241l6b9osYgzA/exec"
MODEL_NAME = get_secret("GEMINI_MODEL", "gemini-3.8-flash")


@st.cache_resource
def get_gemini_client(api_key):
    return genai.Client(api_key=api_key)


client = get_gemini_client(API_KEY) if API_KEY else None


# Sổ điểm dùng chung cho mọi học sinh đang mở app (session_state chỉ riêng từng người,
# nên trước đây cô mở tab Bảng điểm sẽ không thấy bài của học sinh nào).
# Lưu ý: danh sách này mất khi app khởi động lại; bản lưu lâu dài là Google Sheets.
@st.cache_resource
def get_shared_history():
    return []


submission_history = get_shared_history()

# ================= BỘ LỌC CHUẨN HÓA KÝ HIỆU TOÁN HỌC TOÁN 8 =================
def format_math(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""

    text = re.sub(r"^(?:User Safety|Thinking Process|Thought):[^\n]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    text = text.replace("$", "")

    # (?![a-zA-Z]) để \left không bị hiểu là \le, \int/\infty không bị hiểu là \in ...
    text = re.sub(r"\\text\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\(?:left|right)(?![a-zA-Z])", "", text)
    text = re.sub(r"\\(?:widehat|hat)\s*[\{\[]\s*([A-Za-z0-9]{1,3})\s*[\}\]]", r"∠\1", text)
    text = re.sub(r"\\(?:angle)\s+([A-Za-z0-9]{1,3})\b", r"∠\1", text)
    text = re.sub(r"\\(?:Delta|triangle)\s*([A-Za-z]{3})", r"Δ \1", text)
    text = re.sub(r"Δ([A-Za-z]{3})", r"Δ \1", text)

    text = re.sub(r"\\perp(?![a-zA-Z])|£", " ⊥ ", text)
    text = re.sub(r"\\parallel(?![a-zA-Z])", " // ", text)
    text = re.sub(r"\\notin(?![a-zA-Z])", " ∉ ", text)
    text = re.sub(r"\\in(?![a-zA-Z])", " ∈ ", text)
    text = re.sub(r"\^?\\circ", "°", text)
    text = re.sub(r"\\degree", "°", text)
    text = text.replace("°°", "°")

    text = re.sub(r"\\(?:Leftrightarrow|iff)(?![a-zA-Z])|<=>", " ⇔ ", text)
    text = re.sub(r"\\(?:Rightarrow|implies)(?![a-zA-Z])|=>", " ⇒ ", text)
    text = re.sub(r"\\leq?(?![a-zA-Z])|<=|≤", " ≤ ", text)
    text = re.sub(r"\\geq?(?![a-zA-Z])|>=|≥", " ≥ ", text)
    text = re.sub(r"\\neq?(?![a-zA-Z])|!=|≠", " ≠ ", text)
    text = re.sub(r"\\pm(?![a-zA-Z])|±", " ± ", text)
    # Chỉ đổi dấu * nằm giữa hai số/chữ (2*3) – không phá chữ in đậm **...** của Markdown
    text = re.sub(r"\\times|\\cdot|(?<=[\w\)\]])\s*\*\s*(?=[\w\(\[])", " · ", text)

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
4. KHÔNG dùng LaTeX (không viết \\frac, \\sqrt, $...$). Viết ký hiệu Unicode: ∠A, Δ ABC, √, ², ⊥, //, °.

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

# Lệnh LaTeX hay gặp trong JSON của AI. Trong JSON, "\frac" bị hiểu thành ký tự form-feed + "rac",
# "\times" thành tab + "imes"... nên phải nhân đôi dấu \ trước khi json.loads.
LATEX_IN_JSON = re.compile(
    r"(?<!\\)\\(?=(?:dfrac|frac|sqrt|times|cdot|circ|degree|angle|widehat|hat|triangle|Delta|perp|parallel"
    r"|leq|le|geq|ge|neq|ne|pm|notin|in|Rightarrow|Leftrightarrow|rightarrow|leftrightarrow|implies|iff"
    r"|left|right|text|alpha|beta|pi|infty)(?![a-zA-Z]))"
)


def execute_gemini_request(inputs, system_prompt=None, is_json=False):
    if client is None:
        raise Exception("Chưa cấu hình GEMINI_API_KEY trong Secrets của Streamlit!")

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
        target_str = LATEX_IN_JSON.sub(r"\\\\", target_str)
        try:
            data = json.loads(target_str, strict=False)
        except Exception:
            fixed_str = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', target_str)
            data = json.loads(fixed_str, strict=False)

        if not isinstance(data, dict):
            raise Exception("AI trả về sai định dạng, vui lòng thử lại!")

        if "options" in data and isinstance(data["options"], list) and len(data["options"]) > 1:
            opts = data["options"]
            corr_idx = to_int(data.get("correct_index", 0), 0)
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

# ================= BANNER VŨ TRỤ =================
st.markdown("""
<div class="hero-banner">
    <h1>🚀 PHI HÀNH GIA TOÁN HỌC 8</h1>
    <p>Khám phá Vũ trụ Tri thức Đại số & Hình học cùng cô Mai Phương • Học tập gợi mở từng bước</p>
</div>
""", unsafe_allow_html=True)

if client is None:
    st.error("Chưa cấu hình biến GEMINI_API_KEY trong Secrets của Streamlit! Tab 1 và Tab 2 tạm thời không dùng được; game Vượt Ải Không Gian vẫn chơi bình thường.")

tab1, tab2, tab3, tab4 = st.tabs([
    "🪐 Thử Thách Tương Tác",
    "📝 Nộp Bài Tập",
    "👾 Vượt Ải Không Gian",
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
    if "img_id" not in st.session_state:
        st.session_state.img_id = None
    if "reward" not in st.session_state:
        st.session_state.reward = None
    if "reward_ggb" not in st.session_state:
        st.session_state.reward_ggb = None

    with st.expander("📸 Trạm quét ảnh bài toán (Số học, Đại số hoặc Hình học)", expanded=(st.session_state.card is None)):
        up_game_img = st.file_uploader("Tải/chụp ảnh bài toán:", type=["jpg", "png", "jpeg"], key="up_game_img")
        math_mode = st.radio("Phân loại hệ thống:", ["Tự động nhận diện", "Toán Số (Đại số)", "Toán Hình (Hình học)"], horizontal=True)

        if up_game_img:
            new_id = getattr(up_game_img, "file_id", f"{up_game_img.name}-{up_game_img.size}")
            if new_id != st.session_state.img_id:
                # Học sinh đổi sang ảnh bài khác -> bỏ thử thách của ảnh cũ
                st.session_state.img_id = new_id
                st.session_state.card = None
                st.session_state.step = 1
                st.session_state.answered = False
                st.session_state.selected_idx = None
                st.session_state.reward = None
                st.session_state.reward_ggb = None
            st.session_state.img_data = Image.open(up_game_img)
            st.image(st.session_state.img_data, caption="Ảnh đề bài đang xử lý", use_container_width=True)

        if st.session_state.img_data and st.session_state.card is None:
            if st.button("🚀 Khởi động Trạm thử thách Bước 1!", type="primary", use_container_width=True):
                with st.spinner("Phi hành đoàn AI đang phân tích quỹ đạo đề bài theo chuẩn SGK Toán 8..."):
                    try:
                        p_start = f"Tạo câu hỏi thử thách Bước 1 ngắn gọn. Phân loại yêu cầu: {math_mode}. TUYỆT ĐỐI KHÔNG dùng đường tròn."
                        c_data = execute_gemini_request([st.session_state.img_data, p_start], GAME_PROMPT, is_json=True)
                        st.session_state.card = c_data
                        st.session_state.total_steps = max(1, to_int(c_data.get("total_steps", 3), 3))
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
        if not isinstance(opts, list):
            opts = []
        correct = to_int(card.get("correct_index", 0), 0)
        if not 0 <= correct < max(len(opts), 1):
            correct = 0

        if not st.session_state.answered:
            st.markdown("**👉 Phi hành gia hãy chọn một tọa độ đáp án đúng nhất:**")
            for idx, opt in enumerate(opts):
                clean_opt = format_math(str(opt))
                clean_opt = re.sub(r"^[A-D]\s*[\.\:\)]\s*", "", clean_opt)
                label = f"{chr(65+idx)}. {clean_opt}"
                if st.button(label, key=f"btn_choice_{idx}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.selected_idx = idx
                    st.rerun()
        else:
            sel = st.session_state.selected_idx
            sel_text = format_math(str(opts[sel])) if (sel is not None and sel < len(opts)) else ""
            sel_text = re.sub(r"^[A-D]\s*[\.\:\)]\s*", "", sel_text)

            correct_text = format_math(str(opts[correct])) if correct < len(opts) else ""
            correct_text = re.sub(r"^[A-D]\s*[\.\:\)]\s*", "", correct_text)

            if sel == correct:
                st.success("🎉 **Chính xác!** Quỹ đạo tư duy chuẩn xác.")
            else:
                st.error("❌ **Chệch quỹ đạo.**")
                st.markdown(f"Đáp án chuẩn: **{chr(65+correct)}. {correct_text}**")

            st.markdown(f"**💡 Trạm phân tích:** {format_math(card.get('explanation', ''))}")

            is_finish = card.get("is_finished") is True or (curr >= total)

            if is_finish:
                st.balloons()
                st.success("🏆 **HOÀN THÀNH XUẤT SẮC! Chinh phục trọn vẹn hành tinh toán học!**")

                # Chỉ gọi AI 1 lần (trước đây lời giải rỗng sẽ gọi lại AI ở mỗi lần trang tải lại)
                if st.session_state.reward is None:
                    sol = card.get("full_solution", "")
                    ggb_cmds = card.get("ggb_commands", [])
                    if (not sol or not ggb_cmds) and st.session_state.img_data:
                        with st.spinner("Đang mở khóa kho báu lời giải và trạm hình học GeoGebra không gian..."):
                            p_sol = """Hãy viết bài giải mẫu mực hoàn chỉnh đúng chuẩn kiến thức SGK Toán 8 (Kết nối tri thức).
                            TUYỆT ĐỐI KHÔNG dùng kiến thức đường tròn. KHÔNG dùng LaTeX, viết ký hiệu Unicode.
                            Nếu là Toán Hình: BẮT BUỘC sinh mảng ggb_commands chứa các lệnh GeoGebra tiếng Anh để dựng đúng hình của đề bài.
                            Trả về JSON: {"full_solution": "...", "ggb_commands": ["..."]}"""
                            try:
                                res_final = execute_gemini_request([st.session_state.img_data, p_sol], is_json=True)
                                sol = res_final.get("full_solution", "") or sol
                                ggb_cmds = res_final.get("ggb_commands", []) or ggb_cmds
                            except Exception:
                                sol = sol or "Đã xảy ra lỗi khi tạo lời giải chi tiết."
                    st.session_state.reward = str(sol or "")
                    st.session_state.reward_ggb = [str(c) for c in ggb_cmds] if isinstance(ggb_cmds, list) else []

                st.markdown("""
                <div class="reward-box">
                    <h3 style="color: #34d399; margin-top:0;">🎁 KHO BÁU PHẦN THƯỞNG: BÀI GIẢI MẪU HOÀN CHỈNH</h3>
                    <p style="color: #a7f3d0; font-size: 14px;">Hãy ghi chép cẩn thận vào nhật ký học tập nhé!</p>
                </div>
                """, unsafe_allow_html=True)

                if card.get("subject_type") == "geometry":
                    st.markdown("#### 📐 Trạm Hình học không gian động GeoGebra:")
                    cmds = st.session_state.reward_ggb or ["A = (0, 4)", "B = (-3, 0)", "C = (3, 0)", "Polygon(A, B, C)"]
                    # json.dumps để lệnh có dấu " hoặc \ không làm hỏng mã JavaScript
                    commands_js = "".join(f"try {{ api.evalCommand({json.dumps(cmd)}); }} catch(e) {{}}\n" for cmd in cmds)

                    geogebra_html = f"""
                    <div style="display:flex;justify-content:center;align-items:center;background:#0f172a;border:2px solid rgba(56,189,248,0.7);border-radius:16px;padding:12px;">
                        <script src="https://www.geogebra.org/apps/deployggb.js"></script>
                        <div id="ggb-element"></div>
                        <script>
                        var ggbApp = new GGBApplet({{
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
                    components.html(geogebra_html, height=440, scrolling=False)

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
        s_name = s_name.strip()
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
KHÔNG dùng LaTeX, viết ký hiệu Unicode.

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

                    # Ưu tiên số sau chữ "Tổng điểm"; không có thì lấy số đầu tiên dạng x/10
                    score_match = (re.search(r"Tổng điểm\W*(\d+(?:[.,]\d+)?)\s*/\s*10", score_res_clean, flags=re.IGNORECASE)
                                   or re.search(r"(\d+(?:[.,]\d+)?)\s*/\s*10(?!\d)", score_res_clean))
                    extracted_score = score_match.group(1).replace(",", ".") if score_match else "Chưa xác định"

                    sub_record = {
                        "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Họ và tên": s_name,
                        "Lớp": s_class,
                        "Bài tập": topic,
                        "Điểm số": extracted_score,
                        "Nhận xét của AI": score_res_clean.replace("\n", " ")
                    }
                    submission_history.append(sub_record)

                    webhook_url = get_secret("GOOGLE_SHEET_WEBHOOK_URL", DEFAULT_WEBHOOK) or DEFAULT_WEBHOOK
                    sheet_ok = False
                    sheet_err = ""
                    if not webhook_url or "EXAMPLE_REPLACE" in webhook_url:
                        sheet_err = "Chưa cấu hình GOOGLE_SHEET_WEBHOOK_URL trong Secrets của Streamlit"
                    else:
                        payload = {
                            "time": sub_record["Thời gian"],
                            "name": s_name,
                            "student_class": s_class,
                            "topic": topic,
                            "score": extracted_score,
                            "feedback": sub_record["Nhận xét của AI"]
                        }
                        try:
                            # Gửi dạng text/plain giống game Vượt Ải Không Gian; Apps Script đọc bằng e.postData.contents
                            resp = requests.post(webhook_url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                                                 headers={"Content-Type": "text/plain;charset=utf-8"}, timeout=15)
                            # Apps Script trả mã 200 cả khi lỗi hoặc bắt đăng nhập, nên phải đọc nội dung trả về
                            sheet_ok = resp.ok and '"ok"' in resp.text
                            if not sheet_ok:
                                sheet_err = f"HTTP {resp.status_code}: {resp.text[:300]}"
                        except Exception as e:
                            sheet_err = str(e)

                    if sheet_ok:
                        st.success("🎉 Tín hiệu đã truyền thành công! Điểm số tự động cập nhật về hạm đội của cô!")
                    else:
                        st.warning("⚠️ Đã chấm xong nhưng chưa gửi được điểm về Google Sheets. Em hãy chụp màn hình kết quả gửi cô nhé!")
                        with st.expander("Chi tiết lỗi (dành cho cô)"):
                            st.code(sheet_err)
                    st.markdown(f"### Kết quả của phi hành gia: **{s_name}** - Hạm đội **{s_class}**")
                    st.markdown(score_res_clean)
                except Exception as err:
                    st.error(f"Lỗi truyền tín hiệu: {err}")


# ================= TAB 3: MINIGAME VƯỢT ẢI KHÔNG GIAN (TỨ GIÁC) =================
SPACE_GAME_HTML = """
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
    .shake { animation: shake-anim 0.35s cubic-bezier(.36,.07,.19,.97) both; }
    html, body { touch-action: manipulation; -webkit-touch-callout: none; -webkit-tap-highlight-color: transparent; }
    .pad-btn { touch-action: none; -webkit-user-select: none; user-select: none; }
    .pad-btn.pressed { transform: scale(0.92); filter: brightness(1.3); }
    @keyframes shake-anim {
      10%, 90% { transform: translate3d(-2px, 0, 0); }
      20%, 80% { transform: translate3d(4px, 0, 0); }
      30%, 50%, 70% { transform: translate3d(-6px, 0, 0); }
      40%, 60% { transform: translate3d(6px, 0, 0); }
    }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 font-body min-h-screen flex flex-col items-center justify-start p-2 select-none">

  <!-- ĐĂNG NHẬP -->
  <div id="login-modal" class="fixed inset-0 z-50 bg-slate-950/95 backdrop-blur-md flex items-start sm:items-center justify-center p-3 sm:p-4 overflow-y-auto">
    <div class="bg-slate-900 border-2 border-amber-400/80 rounded-2xl max-w-md w-full p-6 shadow-2xl text-center">
      <div class="inline-block p-3 bg-indigo-600 rounded-2xl shadow-lg mb-3">
        <span class="text-3xl">🚀</span>
      </div>
      <h1 class="text-xl font-extrabold text-amber-400 mb-1">LỚP TOÁN CÔ MAI PHƯƠNG</h1>
      <p class="text-xs text-slate-400 mb-5">Phi Hành Gia Toán Học: Vượt Ải Không Gian & Chinh Phục Quái Thú Tứ Giác</p>

      <div class="space-y-3.5 text-left mb-6">
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Họ và tên học sinh:</label>
          <input type="text" id="input-name" placeholder="Ví dụ: Nguyễn Văn An" class="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-400">
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Lớp:</label>
          <input type="text" id="input-class" placeholder="Ví dụ: 8A13" class="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-400">
        </div>
      </div>

      <div class="bg-slate-800/80 border border-slate-700 rounded-xl p-3 text-xs text-slate-300 text-left mb-5 space-y-1.5">
        <p>🎮 <b>Máy tính:</b> <b>← / →</b> để chạy, <b>Space / ↑</b> để nhảy.</p>
        <p>📱 <b>Điện thoại:</b> giữ nút <b>◀</b> (bên trái) để lùi, <b>▶</b> (bên phải) để tiến; bấm nút <b>NHẢY</b> bên trái hoặc chạm vào màn hình game để nhảy.</p>
        <p>🧊 Nhảy húc đầu vào các <b>khối năng lượng</b> (Δ, π, √x...): 5 Câu hỏi, 🧪 Bình oxy (+1 mạng), 💎 Tinh thể, ☄️ Thiên thạch (-1 mạng).</p>
        <p>⚠️ Nhảy qua <b>hố đen</b> trên đường đi! Trả lời đủ 5 câu hỏi để qua ải, rồi hạ <b>Quái Thú Tứ Giác</b>.</p>
      </div>

      <button id="btn-start-game" class="w-full py-3.5 bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white font-extrabold text-sm rounded-xl shadow-lg transition transform active:scale-95">
        BẮT ĐẦU VƯỢT ẢI NGAY
      </button>
    </div>
  </div>

  <!-- HUD THÔNG TIN PHI HÀNH GIA -->
  <header class="w-full max-w-3xl flex flex-wrap items-center justify-between gap-x-2 gap-y-1 bg-black border-2 border-slate-800 px-2 sm:px-4 py-2 mb-2 font-pixel text-[9px] sm:text-[11px] text-white rounded-xl shadow-lg">
    <div class="text-center">
      <div class="text-cyan-400 mb-0.5 text-[8px] sm:text-[9px]">SCORE</div>
      <div id="hud-score" class="text-white">000000</div>
    </div>
    <div class="text-center">
      <div class="text-cyan-400 mb-0.5 text-[8px] sm:text-[9px]">GEMS</div>
      <div id="hud-coins" class="text-fuchsia-300">💎 x0</div>
    </div>
    <div class="text-center">
      <div class="text-cyan-400 mb-0.5 text-[8px] sm:text-[9px]">PLANET</div>
      <div id="hud-world" class="text-amber-300">P-1</div>
    </div>
    <div class="text-center">
      <div class="text-cyan-400 mb-0.5 text-[8px] sm:text-[9px]">QUESTIONS</div>
      <div id="hud-quest" class="text-amber-300">0/5</div>
    </div>
    <div class="text-center">
      <div class="text-cyan-400 mb-0.5 text-[8px] sm:text-[9px]">OXYGEN</div>
      <div id="hud-lives" class="text-rose-500 text-xs">❤️❤️❤️❤️❤️</div>
    </div>
    <button id="btn-toggle-sound" class="p-1.5 bg-slate-800 hover:bg-slate-700 rounded border border-slate-700 text-xs font-body">🔊</button>
  </header>

  <!-- MÀN HÌNH GAME CANVAS -->
  <main id="game-arena" class="relative w-full max-w-3xl aspect-[16/9] bg-[#0b1026] rounded-2xl border-4 border-slate-800 shadow-2xl overflow-hidden">
    <canvas id="gameCanvas" width="900" height="506" class="w-full h-full block"></canvas>
  </main>

  <!-- NÚT ĐIỀU KHIỂN CẢM ỨNG: tay trái = lùi + nhảy, tay phải = tiến -->
  <div id="touch-pad" class="w-full max-w-3xl flex items-center justify-between mt-3 px-1">
    <div class="flex items-center gap-3">
      <button id="pad-left" class="pad-btn w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-slate-800 border-4 border-sky-400/80 text-4xl text-white shadow-lg transition-transform">◀</button>
      <button id="pad-jump" class="pad-btn w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-gradient-to-br from-indigo-600 to-cyan-500 border-4 border-cyan-300 font-extrabold text-base sm:text-lg leading-tight text-white shadow-lg transition-transform">NHẢY<br>⤴</button>
    </div>
    <button id="pad-right" class="pad-btn w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-slate-800 border-4 border-sky-400/80 text-4xl text-white shadow-lg transition-transform">▶</button>
  </div>

  <!-- MODAL CÂU HỎI -->
  <div id="quiz-modal" class="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-sm flex items-center justify-center p-3 hidden">
    <div class="bg-slate-900 border-2 border-sky-400/90 rounded-2xl max-w-xl w-full p-4 shadow-2xl flex flex-col max-h-[92vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
        <span id="quiz-level-badge" class="px-2.5 py-1 bg-sky-500/20 text-sky-400 border border-sky-500/40 rounded-lg text-xs font-bold uppercase">NHẬN BIẾT (15s)</span>
        <div class="flex items-center space-x-1.5 font-pixel text-xs text-amber-400">
          <span>⏳</span><span id="quiz-timer-text">15s</span>
        </div>
      </div>

      <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-3">
        <div id="timer-bar" class="h-full bg-amber-400 transition-all duration-100 ease-linear" style="width: 100%;"></div>
      </div>

      <div id="quiz-question-text" class="text-sm font-bold text-amber-200 mb-3 leading-relaxed">Đề bài...</div>

      <div id="quiz-options-container" class="space-y-2 mb-2"></div>

      <div id="quiz-short-container" class="space-y-2 mb-2 hidden">
        <input type="text" id="quiz-short-input" placeholder="Nhập đáp số hoặc tên hình..." autocomplete="off" class="w-full bg-slate-800 border-2 border-sky-500/60 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-400">
        <button id="quiz-short-submit" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-md transition">XÁC NHẬN ĐÁP ÁN (ENTER)</button>
      </div>

      <div id="quiz-feedback" class="mt-2 text-xs font-semibold min-h-[20px]"></div>
    </div>
  </div>

  <!-- MODAL HOÀN THÀNH ẢI -->
  <div id="stage-clear-modal" class="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto hidden">
    <div class="bg-slate-900 border-2 border-emerald-400 rounded-2xl max-w-md w-full p-6 text-center shadow-2xl">
      <div class="text-3xl mb-2">🌟</div>
      <h3 id="stage-clear-title" class="text-base font-extrabold text-emerald-400 mb-1">HOÀN THÀNH ẢI!</h3>
      <p class="text-xs text-amber-400 font-bold mb-3">LỜI DẶN DÒ TỪ CÔ MAI PHƯƠNG</p>
      <div id="stage-clear-msg" class="bg-slate-800/80 border border-slate-700 rounded-xl p-3.5 text-xs text-slate-200 text-left mb-5 leading-relaxed"></div>
      <button id="btn-continue-next-stage" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl transition shadow-lg">TIẾP TỤC TIẾN LÊN ẢI TIẾP THEO ⏩</button>
    </div>
  </div>

  <!-- MODAL TỔNG KẾT -->
  <div id="summary-modal" class="fixed inset-0 z-50 bg-slate-950/95 backdrop-blur-md flex items-center justify-center p-3 hidden">
    <div class="bg-slate-900 border-2 border-amber-400 rounded-2xl max-w-md w-full p-5 shadow-2xl flex flex-col max-h-[92vh] overflow-y-auto">
      <div class="text-center mb-3">
        <span id="summary-badge-icon" class="text-3xl">🏆</span>
        <h2 id="summary-title" class="text-lg font-extrabold text-amber-400 mt-1">VINH DANH CHIẾN THẮNG!</h2>
        <p id="summary-subtitle" class="text-[11px] text-emerald-400 font-semibold">Đã xuất sắc vượt qua 5 Ải & Hạ gục Quái Thú Tứ Giác</p>
      </div>

      <div class="bg-slate-800/80 border border-slate-700 rounded-xl p-3 mb-3 grid grid-cols-2 gap-2 text-xs">
        <div><span class="text-slate-400">Học sinh:</span> <b id="sum-name" class="text-white">...</b></div>
        <div><span class="text-slate-400">Lớp:</span> <b id="sum-class" class="text-white">...</b></div>
        <div><span class="text-slate-400">Mã đề:</span> <b id="sum-examcode" class="text-amber-300">...</b></div>
        <div><span class="text-slate-400">Tổng điểm:</span> <b id="sum-score" class="text-amber-400 font-pixel">0</b></div>
        <div class="col-span-2 bg-emerald-950/60 border border-emerald-500/40 p-2 rounded-lg text-emerald-300 text-center font-bold">
          🎁 Phần thưởng: <span id="sum-bonus" class="text-amber-300 font-extrabold">+5 ĐIỂM CỘNG</span> từ Cô Mai Phương!
        </div>
      </div>

      <div id="summary-teacher-note" class="bg-amber-950/30 border border-amber-500/30 rounded-xl p-3 text-xs text-amber-200 mb-3 leading-relaxed"></div>

      <div id="sync-status-box" class="border border-slate-700 bg-slate-950/60 rounded-xl p-2.5 text-center mb-3">
        <div id="sync-status-text" class="text-xs text-yellow-400 font-medium">⏳ Đang kết nối gửi kết quả về Google Sheets...</div>
        <button id="btn-retry-sync" class="mt-2 hidden px-3 py-1 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-lg transition">🔄 Thử gửi lại dữ liệu</button>
      </div>

      <button onclick="location.reload()" class="w-full py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white font-bold text-xs rounded-xl transition">CHƠI LẠI VỚI BỘ ĐỀ MỚI 🔁</button>
    </div>
  </div>

  <script>
    const GOOGLE_SCRIPT_WEBAPP_URL = "WEBHOOK_URL_PLACEHOLDER";

    // ===== TÀI NGUYÊN ẢNH (tùy chọn) =====
    // Dán "data:image/png;base64,..." hoặc mã <svg>...</svg> hoặc đường dẫn ảnh.
    // Để "" thì game tự vẽ hình pixel mặc định.
    const ASSETS = {
      hero: "",        // phi hành gia, gợi ý 64x88 px, nền trong suốt, quay mặt sang PHẢI
      boss: "",        // Quái Thú Tứ Giác, gợi ý 160x160 px
      box: "",         // khối năng lượng 72x72 px
      background: ""   // hình nền 1280x720 px
    };

    function toSrc(value) {
      if (!value) return "";
      if (value.trim().startsWith("<svg")) return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(value);
      return value;
    }
    function loadImage(src) {
      const img = new Image();
      img.ok = false;
      if (!src) return img;
      img.onload = () => { img.ok = true; };
      img.onerror = () => { img.ok = false; };
      img.src = src;
      return img;
    }
    const IMG = {
      hero: loadImage(toSrc(ASSETS.hero)),
      boss: loadImage(toSrc(ASSETS.boss)),
      box: loadImage(toSrc(ASSETS.box)),
      background: loadImage(toSrc(ASSETS.background))
    };

    // ===== ÂM THANH =====
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

    function sndJump() { playTone(330, 'triangle', 0.12, 0.14); setTimeout(() => playTone(620, 'triangle', 0.14, 0.12), 50); }
    function sndCoin() { playTone(880, 'sine', 0.08, 0.16); setTimeout(() => playTone(1175, 'sine', 0.08, 0.16), 60); setTimeout(() => playTone(1760, 'sine', 0.18, 0.12), 120); }
    function sndPowerup() { playTone(392, 'triangle', 0.12, 0.16); setTimeout(() => playTone(587, 'triangle', 0.12, 0.16), 90); setTimeout(() => playTone(880, 'sine', 0.25, 0.14), 180); }
    function sndTrap() { playTone(150, 'sawtooth', 0.25, 0.25); setTimeout(() => playTone(80, 'sawtooth', 0.3, 0.25), 120); }
    function sndWrong() { playTone(200, 'sawtooth', 0.2, 0.2); setTimeout(() => playTone(120, 'sawtooth', 0.3, 0.2), 150); }
    function sndRoar() { playTone(85, 'sawtooth', 0.45, 0.3); setTimeout(() => playTone(60, 'sawtooth', 0.5, 0.3), 180); }
    function sndBump() { playTone(110, 'square', 0.08, 0.15); }

    let bgmInterval = null;
    const bgmNotes = [220, 0, 329.6, 0, 293.7, 0, 392, 0, 349.2, 0, 293.7, 0, 261.6, 0, 329.6, 0];   // giai điệu vũ trụ tự sáng tác
    let noteIdx = 0;
    function startBgm() {
      if (bgmInterval || isSoundMuted) return;
      bgmInterval = setInterval(() => {
        if (gameState.started && !gameState.isPaused && !gameState.isGameOver && bgmNotes[noteIdx] > 0) {
          playTone(bgmNotes[noteIdx], 'triangle', 0.18, 0.035);
        }
        noteIdx = (noteIdx + 1) % bgmNotes.length;
      }, 220);
    }
    function stopBgm() { if (bgmInterval) { clearInterval(bgmInterval); bgmInterval = null; } }

    document.getElementById("btn-toggle-sound").onclick = (e) => {
      isSoundMuted = !isSoundMuted;
      e.currentTarget.textContent = isSoundMuted ? "🔇" : "🔊";
      e.currentTarget.blur();
      if (isSoundMuted) stopBgm(); else startBgm();
    };

    // ===== NGÂN HÀNG CÂU HỎI =====
    // Mỗi màn có nhiều câu; mỗi lần chơi game bốc ngẫu nhiên 2 Nhận biết + 2 Thông hiểu + 1 Vận dụng.
    // Thêm câu mới: chép một dòng có sẵn rồi sửa. "short" = tự luận (correctAnswers), "mcq" = trắc nghiệm (correct = vị trí đáp án đúng, tính từ 0).
    const rawQuestionPool = {
      stage1: [
        { level: "Nhận biết", time: 15, type: "short", q: "Tổng các góc trong một tứ giác lồi luôn bằng bao nhiêu độ? (Chỉ nhập số)", correctAnswers: ["360"], explain: "Định lý: Tổng các góc của một tứ giác luôn bằng 360 độ." },
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác luôn nằm trong một nửa mặt phẳng có bờ là đường thẳng chứa bất kì cạnh nào gọi là tứ giác gì?", correctAnswers: ["lồi", "tứ giác lồi"], explain: "Định nghĩa: Đó là tứ giác lồi." },
        { level: "Nhận biết", time: 15, type: "short", q: "Một tứ giác lồi có tổng cộng bao nhiêu đường chéo? (Chỉ nhập số)", correctAnswers: ["2"], explain: "Mỗi tứ giác lồi có đúng 2 đường chéo nối các đỉnh đối nhau." },
        { level: "Nhận biết", time: 15, type: "mcq", q: "Trong tứ giác ABCD, các đường chéo là những đoạn thẳng nào?", answers: ["AC và BD", "AB và CD", "AD và BC"], correct: 0, explain: "Đường chéo nối hai đỉnh đối nhau: AC và BD." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Một tứ giác lồi có thể có nhiều nhất bao nhiêu góc nhọn?", answers: ["3 góc nhọn", "4 góc nhọn", "2 góc nhọn"], correct: 0, explain: "Nếu có 4 góc nhọn thì tổng 4 góc < 360° (vô lý). Vậy tối đa có 3 góc nhọn." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Một tứ giác có thể có nhiều nhất bao nhiêu góc tù?", answers: ["3 góc tù", "4 góc tù", "2 góc tù"], correct: 0, explain: "4 góc tù thì tổng > 360° (vô lý). Có thể có 3 góc tù, ví dụ 100°, 100°, 100°, 60°." },
        { level: "Thông hiểu", time: 20, type: "short", q: "Tứ giác có bốn góc bằng nhau thì mỗi góc bằng bao nhiêu độ? (Nhập số)", correctAnswers: ["90"], explain: "Mỗi góc = 360° : 4 = 90°." },
        { level: "Thông hiểu", time: 20, type: "short", q: "Tứ giác ABCD có góc A + góc C = 200°. Tổng góc B + góc D bằng bao nhiêu độ? (Nhập số)", correctAnswers: ["160"], explain: "B + D = 360° - 200° = 160°." },
        { level: "Vận dụng", time: 30, type: "short", q: "Tứ giác ABCD có góc A = 70°, B = 90°, C = 80°. Tính số đo góc D bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["120"], explain: "Góc D = 360° - (70° + 90° + 80°) = 120°." },
        { level: "Vận dụng", time: 30, type: "short", q: "Tứ giác ABCD có góc A = 100°, góc B = 80° và góc C = góc D. Tính góc C bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["90"], explain: "C + D = 360° - 180° = 180°, mà C = D nên C = 90°." },
        { level: "Vận dụng", time: 30, type: "short", q: "Tứ giác MNPQ có các góc M, N, P, Q tỉ lệ với 1 : 2 : 3 : 4. Góc Q bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["144"], explain: "Tổng 10 phần = 360° nên 1 phần = 36°. Góc Q = 4 · 36° = 144°." },
        { level: "Vận dụng", time: 30, type: "short", q: "Tứ giác ABCD có góc B = 90°, C = 100°, D = 70°. Góc ngoài tại đỉnh A bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["80"], explain: "Góc A = 360° - 260° = 100°. Góc ngoài tại A = 180° - 100° = 80°." }
      ],
      stage2: [
        { level: "Nhận biết", time: 15, type: "short", q: "Hình thang có hai góc kề một đáy bằng nhau là hình thang gì?", correctAnswers: ["cân", "hình thang cân", "thang cân"], explain: "Định nghĩa SGK: Hình thang có 2 góc kề một đáy bằng nhau là hình thang cân." },
        { level: "Nhận biết", time: 15, type: "mcq", q: "Trong hình thang cân, hai đường chéo có mối quan hệ gì với nhau?", answers: ["Bằng nhau", "Vuông góc với nhau", "Cắt nhau tại trung điểm mỗi đường"], correct: 0, explain: "Tính chất SGK: Trong hình thang cân, hai đường chéo bằng nhau." },
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có hai cạnh đối song song được gọi là hình gì?", correctAnswers: ["hình thang", "thang"], explain: "Định nghĩa: Hình thang là tứ giác có hai cạnh đối song song." },
        { level: "Nhận biết", time: 15, type: "mcq", q: "Trong hình thang cân, hai cạnh bên có tính chất gì?", answers: ["Bằng nhau", "Song song với nhau", "Vuông góc với nhau"], correct: 0, explain: "Tính chất: Trong hình thang cân, hai cạnh bên bằng nhau." },
        { level: "Thông hiểu", time: 20, type: "short", q: "Hình thang có hai đường chéo bằng nhau là hình thang gì?", correctAnswers: ["cân", "hình thang cân", "thang cân"], explain: "Dấu hiệu nhận biết: Hình thang có 2 đường chéo bằng nhau là hình thang cân." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Cho hình thang cân ABCD (AB // CD). Khẳng định nào sau đây là ĐÚNG?", answers: ["Góc C = góc D và góc A = góc B", "Góc A = góc C", "Góc B = góc D"], correct: 0, explain: "Trong hình thang cân, hai góc kề một đáy có số đo bằng nhau." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình thang ABCD (AB // CD) có góc A và góc D là hai góc kề cạnh bên AD. Hai góc này có quan hệ gì?", answers: ["Bù nhau (tổng 180°)", "Bằng nhau", "Phụ nhau (tổng 90°)"], correct: 0, explain: "AB // CD nên A và D là hai góc trong cùng phía, bù nhau." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình thang có một góc vuông được gọi là hình gì?", answers: ["Hình thang vuông", "Hình thang cân", "Hình chữ nhật"], correct: 0, explain: "Định nghĩa: Hình thang có một góc vuông là hình thang vuông." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình thang cân ABCD (AB // CD) có góc D = 70°. Tính số đo góc A kề cạnh bên AD bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["110"], explain: "Vì AB // CD nên hai góc trong cùng phía bù nhau: Góc A = 180° - 70° = 110°." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình thang cân ABCD (AB // CD) có góc A = 115°. Góc C bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["65"], explain: "D = 180° - 115° = 65°, và hai góc kề đáy CD bằng nhau nên C = D = 65°." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình thang cân ABCD có đường chéo AC = 7 cm. Đường chéo BD dài bao nhiêu cm? (Nhập số):", correctAnswers: ["7"], explain: "Hình thang cân có hai đường chéo bằng nhau nên BD = AC = 7 cm." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình thang cân ABCD (AB // CD) có AB = 4 cm, CD = 10 cm, AH là đường cao (H thuộc CD). Độ dài DH bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["3"], explain: "Trong hình thang cân, DH = (CD - AB) : 2 = (10 - 4) : 2 = 3 cm." }
      ],
      stage3: [
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có các cạnh đối song song được gọi là hình gì?", correctAnswers: ["hình bình hành", "bình hành"], explain: "Định nghĩa: Hình bình hành là tứ giác có các cạnh đối song song." },
        { level: "Nhận biết", time: 15, type: "mcq", q: "Trong hình bình hành, hai đường chéo có tính chất gì?", answers: ["Cắt nhau tại trung điểm của mỗi đường", "Vuông góc với nhau", "Bằng nhau"], correct: 0, explain: "Tính chất: Hai đường chéo cắt nhau tại trung điểm của mỗi đường." },
        { level: "Nhận biết", time: 15, type: "mcq", q: "Trong hình bình hành, các cạnh đối có tính chất gì?", answers: ["Bằng nhau", "Vuông góc với nhau", "Cắt nhau"], correct: 0, explain: "Tính chất: Trong hình bình hành, các cạnh đối bằng nhau." },
        { level: "Nhận biết", time: 15, type: "mcq", q: "Trong hình bình hành, các góc đối có tính chất gì?", answers: ["Bằng nhau", "Bù nhau", "Phụ nhau"], correct: 0, explain: "Tính chất: Trong hình bình hành, các góc đối bằng nhau." },
        { level: "Thông hiểu", time: 20, type: "short", q: "Tứ giác có hai đường chéo cắt nhau tại trung điểm của mỗi đường là hình gì?", correctAnswers: ["hình bình hành", "bình hành"], explain: "Dấu hiệu nhận biết: Tứ giác có 2 đường chéo cắt nhau tại trung điểm là hình bình hành." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình thang có hai cạnh bên song song là hình gì?", answers: ["Hình bình hành", "Hình thang cân", "Hình chữ nhật"], correct: 0, explain: "Nhận xét SGK: Hình thang có 2 cạnh bên song song là hình bình hành." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Tứ giác có một cặp cạnh đối vừa song song vừa bằng nhau là hình gì?", answers: ["Hình bình hành", "Hình thang cân", "Hình thang vuông"], correct: 0, explain: "Dấu hiệu nhận biết: Tứ giác có hai cạnh đối song song và bằng nhau là hình bình hành." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Trong hình bình hành ABCD, hai góc kề một cạnh (ví dụ góc A và góc B) có quan hệ gì?", answers: ["Bù nhau (tổng 180°)", "Bằng nhau", "Phụ nhau (tổng 90°)"], correct: 0, explain: "AD // BC nên góc A và góc B là hai góc trong cùng phía, bù nhau." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình bình hành ABCD có góc A = 115°. Tính số đo góc đối C bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["115"], explain: "Tính chất: Hai góc đối hình bình hành bằng nhau nên góc C = góc A = 115°." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình bình hành ABCD có góc A = 70°. Góc B bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["110"], explain: "Hai góc kề một cạnh bù nhau: B = 180° - 70° = 110°." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình bình hành ABCD có AB = 8 cm, BC = 5 cm. Chu vi hình bình hành bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["26"], explain: "Các cạnh đối bằng nhau nên chu vi = 2 · (8 + 5) = 26 cm." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình bình hành ABCD có hai đường chéo cắt nhau tại O, AC = 12 cm. Độ dài OA bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["6"], explain: "O là trung điểm AC nên OA = 12 : 2 = 6 cm." }
      ],
      stage4: [
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có bốn góc vuông được gọi là hình gì?", correctAnswers: ["hình chữ nhật", "chữ nhật"], explain: "Định nghĩa: Hình chữ nhật là tứ giác có bốn góc vuông." },
        { level: "Nhận biết", time: 15, type: "short", q: "Hình chữ nhật có tất cả bao nhiêu trục đối xứng? (Nhập số)", correctAnswers: ["2"], explain: "Hình chữ nhật có 2 trục đối xứng là hai đường thẳng đi qua trung điểm các cặp cạnh đối." },
        { level: "Nhận biết", time: 15, type: "mcq", q: "Trong hình chữ nhật, hai đường chéo có tính chất gì?", answers: ["Bằng nhau và cắt nhau tại trung điểm mỗi đường", "Vuông góc với nhau", "Là tia phân giác các góc"], correct: 0, explain: "Tính chất: Hai đường chéo hình chữ nhật bằng nhau và cắt nhau tại trung điểm mỗi đường." },
        { level: "Nhận biết", time: 15, type: "short", q: "Mỗi góc của hình chữ nhật bằng bao nhiêu độ? (Nhập số)", correctAnswers: ["90"], explain: "Hình chữ nhật có bốn góc vuông, mỗi góc 90°." },
        { level: "Thông hiểu", time: 20, type: "short", q: "Hình bình hành có hai đường chéo bằng nhau là hình gì?", correctAnswers: ["hình chữ nhật", "chữ nhật"], explain: "Dấu hiệu nhận biết: Hình bình hành có 2 đường chéo bằng nhau là hình chữ nhật." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Trong tam giác vuông, đường trung tuyến ứng với cạnh huyền có độ dài bằng mấy phần cạnh huyền?", answers: ["Một nửa cạnh huyền", "Bằng cạnh huyền", "Gấp đôi cạnh huyền"], correct: 0, explain: "Định lý: Trong tam giác vuông, đường trung tuyến ứng với cạnh huyền bằng nửa cạnh huyền." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình bình hành có một góc vuông là hình gì?", answers: ["Hình chữ nhật", "Hình thoi", "Hình thang cân"], correct: 0, explain: "Dấu hiệu nhận biết: Hình bình hành có một góc vuông là hình chữ nhật." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình thang cân có một góc vuông là hình gì?", answers: ["Hình chữ nhật", "Hình thoi", "Hình vuông"], correct: 0, explain: "Dấu hiệu nhận biết: Hình thang cân có một góc vuông là hình chữ nhật." },
        { level: "Vận dụng", time: 30, type: "short", q: "Cho tam giác ABC vuông tại A có cạnh huyền BC = 18 cm. Độ dài đường trung tuyến AM ứng với cạnh huyền bằng mấy cm? (Nhập số):", correctAnswers: ["9"], explain: "Theo định lý: AM = BC / 2 = 18 / 2 = 9 cm." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình chữ nhật có hai cạnh dài 6 cm và 8 cm. Đường chéo dài bao nhiêu cm? (Nhập số):", correctAnswers: ["10"], explain: "Theo định lý Pythagore: đường chéo² = 6² + 8² = 100, nên đường chéo = 10 cm." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình chữ nhật ABCD có đường chéo AC = 14 cm, O là giao điểm hai đường chéo. Độ dài OB bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["7"], explain: "Hai đường chéo bằng nhau và cắt nhau tại trung điểm: OB = BD : 2 = AC : 2 = 7 cm." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình chữ nhật có chiều dài 9 cm và chu vi 30 cm. Chiều rộng bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["6"], explain: "Nửa chu vi = 15 cm, chiều rộng = 15 - 9 = 6 cm." }
      ],
      stage5: [
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có bốn cạnh bằng nhau được gọi là hình gì?", correctAnswers: ["hình thoi", "thoi"], explain: "Định nghĩa: Hình thoi là tứ giác có bốn cạnh bằng nhau." },
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác vừa là hình chữ nhật vừa là hình thoi là hình gì?", correctAnswers: ["hình vuông", "vuông"], explain: "Định nghĩa: Hình vuông là hình chữ nhật đồng thời là hình thoi." },
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có bốn góc vuông và bốn cạnh bằng nhau là hình gì?", correctAnswers: ["hình vuông", "vuông"], explain: "Định nghĩa: Hình vuông là tứ giác có bốn góc vuông và bốn cạnh bằng nhau." },
        { level: "Nhận biết", time: 15, type: "mcq", q: "Hình thoi có bao nhiêu trục đối xứng?", answers: ["2", "4", "1"], correct: 0, explain: "Hình thoi có 2 trục đối xứng là hai đường chéo của nó." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Trong hình thoi, hai đường chéo có tính chất đặc trưng nào sau đây?", answers: ["Vuông góc với nhau và là tia phân giác các góc", "Bằng nhau và song song", "Cắt nhau tại 1/3 mỗi đường"], correct: 0, explain: "Tính chất: Hai đường chéo hình thoi vuông góc và là phân giác các góc." },
        { level: "Thông hiểu", time: 20, type: "short", q: "Hình bình hành có hai đường chéo vuông góc với nhau là hình gì?", correctAnswers: ["hình thoi", "thoi"], explain: "Dấu hiệu: Hình bình hành có 2 đường chéo vuông góc là hình thoi." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình chữ nhật có hai cạnh kề bằng nhau là hình gì?", answers: ["Hình vuông", "Hình thoi không vuông", "Hình bình hành"], correct: 0, explain: "Dấu hiệu nhận biết: Hình chữ nhật có hai cạnh kề bằng nhau là hình vuông." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình thoi có một góc vuông là hình gì?", answers: ["Hình vuông", "Hình chữ nhật không vuông", "Hình thang cân không vuông"], correct: 0, explain: "Dấu hiệu nhận biết: Hình thoi có một góc vuông là hình vuông." },
        { level: "Vận dụng", time: 30, type: "short", q: "Một hình thoi có chu vi bằng 52 cm. Độ dài một cạnh của hình thoi đó bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["13"], explain: "Hình thoi có 4 cạnh bằng nhau nên độ dài một cạnh = 52 / 4 = 13 cm." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình vuông có cạnh 5 cm. Chu vi hình vuông bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["20"], explain: "Chu vi = 4 · 5 = 20 cm." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình thoi có hai đường chéo dài 6 cm và 8 cm. Cạnh hình thoi dài bao nhiêu cm? (Nhập số):", correctAnswers: ["5"], explain: "Hai đường chéo vuông góc tại trung điểm, tạo tam giác vuông có hai cạnh góc vuông 3 cm và 4 cm. Cạnh = √(3² + 4²) = 5 cm." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình thoi ABCD có góc A = 50°. Góc B bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["130"], explain: "Hình thoi là hình bình hành nên hai góc kề một cạnh bù nhau: B = 180° - 50° = 130°." }
      ],
      boss: [
        { level: "Vận dụng cao", time: 30, type: "mcq", q: "Nối trung điểm 4 cạnh của một hình chữ nhật ta luôn nhận được hình gì?", answers: ["Hình thoi", "Hình bình hành thông thường", "Hình vuông"], correct: 0, explain: "Bốn cạnh của tứ giác mới đều bằng nửa đường chéo hình chữ nhật nên bằng nhau => Là Hình thoi." },
        { level: "Vận dụng cao", time: 30, type: "mcq", q: "Nối trung điểm 4 cạnh của một hình thoi ta luôn nhận được hình gì?", answers: ["Hình chữ nhật", "Hình vuông", "Hình bình hành có góc 60°"], correct: 0, explain: "Vì hai đường chéo hình thoi vuông góc nên các cạnh của tứ giác trung điểm vuông góc với nhau => Hình chữ nhật." },
        { level: "Vận dụng cao", time: 30, type: "mcq", q: "Nối trung điểm 4 cạnh của một tứ giác bất kì ta luôn nhận được hình gì?", answers: ["Hình bình hành", "Hình thang cân", "Hình chữ nhật"], correct: 0, explain: "Mỗi cặp cạnh đối của tứ giác mới đều song song và bằng nửa một đường chéo => Hình bình hành." },
        { level: "Vận dụng cao", time: 30, type: "mcq", q: "Nối trung điểm 4 cạnh của một hình vuông ta luôn nhận được hình gì?", answers: ["Hình vuông", "Hình chữ nhật không vuông", "Hình thoi không vuông"], correct: 0, explain: "Hai đường chéo hình vuông bằng nhau và vuông góc nên tứ giác trung điểm vừa là hình thoi vừa là hình chữ nhật => Hình vuông." },
        { level: "Vận dụng cao", time: 30, type: "short", q: "Hình thoi ABCD có cạnh bằng 10 cm và góc A = 60°. Độ dài đường chéo BD bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["10"], explain: "Tam giác ABD cân có góc A = 60° nên là tam giác đều => BD = AB = 10 cm." },
        { level: "Vận dụng cao", time: 30, type: "short", q: "Hình thoi có cạnh 10 cm và một đường chéo dài 12 cm. Đường chéo còn lại dài bao nhiêu cm? (Nhập số):", correctAnswers: ["16"], explain: "Nửa đường chéo đã biết = 6 cm. Nửa đường chéo còn lại = √(10² - 6²) = 8 cm, nên đường chéo = 16 cm." },
        { level: "Vận dụng cao", time: 30, type: "short", q: "Tam giác ABC vuông tại A có AB = 6 cm, AC = 8 cm. Đường trung tuyến AM ứng với cạnh huyền dài bao nhiêu cm? (Nhập số):", correctAnswers: ["5"], explain: "BC = √(6² + 8²) = 10 cm, AM = BC : 2 = 5 cm." },
        { level: "Vận dụng cao", time: 30, type: "short", q: "Hình vuông có đường chéo dài 8 cm. Diện tích hình vuông bằng bao nhiêu cm²? (Nhập số):", correctAnswers: ["32"], explain: "Hình vuông cũng là hình thoi nên diện tích = (8 · 8) : 2 = 32 cm²." }
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

    // Trộn thứ tự đáp án trắc nghiệm để mỗi lần chơi đáp án đúng không luôn ở vị trí 1
    function prepareQuestion(q) {
      if (q.type !== "mcq") return { ...q };
      const order = shuffle(q.answers.map((_, i) => i));
      return { ...q, answers: order.map(i => q.answers[i]), correct: order.indexOf(q.correct) };
    }

    // Bốc 5 câu/màn theo mức độ, xếp từ dễ đến khó
    const PICK_PLAN = [ ["Nhận biết", 2], ["Thông hiểu", 2], ["Vận dụng", 1] ];

    function pickStageQuestions(pool) {
      const picked = [];
      PICK_PLAN.forEach(([level, n]) => {
        picked.push(...shuffle(pool.filter(q => q.level === level)).slice(0, n));
      });
      // Nếu mức độ nào thiếu câu thì bù bằng câu khác cho đủ 5
      const rest = shuffle(pool.filter(q => !picked.includes(q)));
      while (picked.length < 5 && rest.length) picked.push(rest.shift());
      return picked.map(prepareQuestion);
    }

    function buildExam() {
      return {
        code: "CMP-8A-" + Math.floor(1000 + Math.random() * 9000),
        stages: [
          { name: "Màn 1: Tứ giác lồi", questions: pickStageQuestions(rawQuestionPool.stage1), bg: "#0b1026" },
          { name: "Màn 2: Hình thang cân", questions: pickStageQuestions(rawQuestionPool.stage2), bg: "#1e1035" },
          { name: "Màn 3: Hình bình hành", questions: pickStageQuestions(rawQuestionPool.stage3), bg: "#062a33" },
          { name: "Màn 4: Hình chữ nhật", questions: pickStageQuestions(rawQuestionPool.stage4), bg: "#101d42" },
          { name: "Màn 5: Hình thoi và Hình vuông", questions: pickStageQuestions(rawQuestionPool.stage5), bg: "#2a0f3d" }
        ],
        // Trùm: trộn toàn bộ câu, trả lời sai thì gặp câu khác
        bossQuestions: shuffle(rawQuestionPool.boss).map(prepareQuestion)
      };
    }

    // Chuẩn hóa đáp án tự luận: bỏ hoa/thường, bỏ đơn vị "độ", "°", "cm", gộp khoảng trắng
    function normalizeAnswer(s) {
      return String(s).normalize("NFC").toLowerCase()
        .replace(/°|độ|cm²|cm2|cm/g, "")
        .replace(/\\s+/g, " ")
        .trim();
    }

    // ===== TRẠNG THÁI GAME =====
    const gameState = {
      started: false, studentName: "", studentClass: "", examData: null,
      currentStageIdx: 0, currentQuestionIdx: 0, inBossFight: false,
      bossHp: 3, bossMaxHp: 3, bossQIdx: 0, score: 0, coins: 0, lives: 5,
      isPaused: true, isGameOver: false, defeatedBoss: false, answerLocked: true,
      timerSec: 15, timerMax: 15, timerInterval: null, lastPayload: null
    };

    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const arenaEl = document.getElementById("game-arena");

    // ===== CẤU HÌNH ĐỘ KHÓ (chỉnh ở đây) =====
    const WORLD_W = 3000;
    const GROUND_TOP = 400;
    const HERO_SCALE = 1.5;          // phóng to nhân vật (hình gốc 32x44)
    const HERO_W = 32 * HERO_SCALE, HERO_H = 44 * HERO_SCALE;
    const GROUND_Y = GROUND_TOP - HERO_H;    // y của phi hành gia khi đứng trên mặt đất
    const BOX_SIZE = 52;             // khối năng lượng to hơn
    const BOX_Y = 198;               // độ cao khối năng lượng (nhảy là húc tới)
    const MAX_LIVES = 9;             // số mạng tối đa có thể tích lũy
    const TRAP_PENALTY = 200;        // điểm bị trừ khi mở trúng thiên thạch
    const BOSS_X = 1200, BOSS_Y = 260;
    const STAGE_PITS = [ { start: 1160, width: 70 }, { start: 2220, width: 80 } ];  // hố đen hẹp, dễ nhảy

    const hero = { x: 100, y: GROUND_Y, w: HERO_W, h: HERO_H, vx: 0, vy: 0, isJumping: false, falling: false, fallPit: null, facing: 1, legSwing: 0, speed: 4 };
    let cameraX = 0;
    const keys = { left: false, right: false };

    let mysteryBoxes = [];
    let groundPits = [];
    let floatingCoins = [];
    let popItems = [];               // bình oxy / thiên thạch / tinh thể nhô lên khi mở khối
    const laser = { active: false, x: 0, y: 0, vx: 0 };   // tia năng lượng bắn Quái Thú
    let bossFlash = 0;

    function initLevelBoxes() {
      mysteryBoxes = [
        { x: 300,  type: 'quiz' },
        { x: 460,  type: 'oxygen' },
        { x: 620,  type: 'coin' },
        { x: 790,  type: 'quiz' },
        { x: 960,  type: 'oxygen' },
        { x: 1350, type: 'quiz' },
        { x: 1520, type: 'trap' },
        { x: 1690, type: 'oxygen' },
        { x: 1870, type: 'quiz' },
        { x: 2040, type: 'coin' },
        { x: 2420, type: 'oxygen' },
        { x: 2580, type: 'trap' },
        { x: 2740, type: 'quiz' },
        { x: 2880, type: 'oxygen' }
      ].map(b => ({ ...b, y: BOX_Y, active: true, bump: 0 }));
      groundPits = STAGE_PITS.map(p => ({ ...p }));
      floatingCoins = [];
      popItems = [];
    }

    function resetHero(x) {
      hero.x = x; hero.y = GROUND_Y; hero.vy = 0;
      hero.isJumping = false; hero.falling = false; hero.fallPit = null; hero.facing = 1;
      keys.left = keys.right = false;
    }

    // ===== HUD =====
    function updateHud() {
      document.getElementById("hud-score").textContent = String(gameState.score).padStart(6, '0');
      document.getElementById("hud-coins").textContent = "💎 x" + gameState.coins;
      document.getElementById("hud-lives").textContent = gameState.lives > 0 ? "❤️x" + gameState.lives : "💀";
    }

    // ===== BÀN PHÍM (bỏ qua khi đang gõ vào ô nhập) =====
    function isTyping(e) {
      const t = e.target;
      return t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
    }

    window.addEventListener('keydown', (e) => {
      if (isTyping(e)) return;
      if (e.code === 'ArrowLeft' || e.code === 'KeyA') keys.left = true;
      if (e.code === 'ArrowRight' || e.code === 'KeyD') keys.right = true;
      if (e.code === 'Space' || e.code === 'ArrowUp') {
        e.preventDefault();
        doJump();
      }
    });

    function doJump() {
      if (!hero.isJumping && !hero.falling && !gameState.isPaused && !gameState.isGameOver) {
        hero.isJumping = true;
        hero.vy = -14;
        sndJump();
      }
    }

    window.addEventListener('keyup', (e) => {
      if (e.code === 'ArrowLeft' || e.code === 'KeyA') keys.left = false;
      if (e.code === 'ArrowRight' || e.code === 'KeyD') keys.right = false;
    });

    window.addEventListener('blur', () => { keys.left = keys.right = false; });

    // ===== NÚT CẢM ỨNG: giữ để chạy, chạm để nhảy =====
    function bindHoldButton(id, key) {
      const btn = document.getElementById(id);
      const press = (e) => {
        e.preventDefault();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        keys[key] = true;
        btn.classList.add("pressed");
        if (e.pointerId !== undefined && btn.setPointerCapture) {
          try { btn.setPointerCapture(e.pointerId); } catch (err) {}
        }
      };
      const release = (e) => {
        if (e) e.preventDefault();
        keys[key] = false;
        btn.classList.remove("pressed");
      };
      btn.addEventListener("pointerdown", press);
      btn.addEventListener("pointerup", release);
      btn.addEventListener("pointercancel", release);
      btn.addEventListener("lostpointercapture", () => release());
      btn.addEventListener("contextmenu", (e) => e.preventDefault());
    }
    bindHoldButton("pad-left", "left");
    bindHoldButton("pad-right", "right");

    const jumpBtn = document.getElementById("pad-jump");
    jumpBtn.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      if (audioCtx.state === 'suspended') audioCtx.resume();
      jumpBtn.classList.add("pressed");
      doJump();
    });
    ["pointerup", "pointercancel", "pointerleave"].forEach(ev =>
      jumpBtn.addEventListener(ev, () => jumpBtn.classList.remove("pressed")));
    jumpBtn.addEventListener("contextmenu", (e) => e.preventDefault());

    // Chạm thẳng vào màn hình game cũng nhảy
    canvas.addEventListener("pointerdown", (e) => { e.preventDefault(); doJump(); });
    canvas.style.touchAction = "none";

    function triggerShake() {
      arenaEl.classList.add("shake");
      setTimeout(() => arenaEl.classList.remove("shake"), 380);
    }

    function loseLife() {
      gameState.lives = Math.max(0, gameState.lives - 1);
      updateHud();
      if (gameState.lives <= 0) finishGameSession(false);
    }

    // ===== CẬP NHẬT THẾ GIỚI =====
    function findPitUnderHero() {
      const cx = hero.x + hero.w / 2;
      return groundPits.find(p => cx > p.start + 4 && cx < p.start + p.width - 4) || null;
    }

    // Vật phẩm nhô lên khỏi ô để học sinh thấy mình nhận được gì
    function spawnPopItem(box, kind, label, color) {
      popItems.push({ kind, label, color, x: box.x + BOX_SIZE / 2, baseY: box.y, rise: 0, life: 90 });
    }

    function hitBox(box) {
      box.active = false;
      box.bump = 8;
      if (box.type === 'coin') {
        sndCoin();
        gameState.coins++;
        gameState.score += 200;
        floatingCoins.push({ x: box.x + BOX_SIZE / 2 - 12, y: box.y - 10, vy: -9 });
        spawnPopItem(box, 'text', "+200", "#facc15");
        updateHud();
      } else if (box.type === 'oxygen') {
        sndPowerup();
        const full = gameState.lives >= MAX_LIVES;
        gameState.lives = Math.min(MAX_LIVES, gameState.lives + 1);
        spawnPopItem(box, 'oxygen', full ? "ĐẦY MẠNG" : "+1 MẠNG", "#4ade80");
        updateHud();
      } else if (box.type === 'trap') {
        sndTrap();
        triggerShake();
        gameState.score = Math.max(0, gameState.score - TRAP_PENALTY);
        spawnPopItem(box, 'meteor', "-1 MẠNG", "#f87171");
        loseLife();
      } else {
        openNextQuestion();
      }
    }

    function checkBoxBump() {
      for (const box of mysteryBoxes) {
        const overlapX = hero.x + hero.w - 4 > box.x && hero.x + 4 < box.x + BOX_SIZE;
        const headHit = hero.y <= box.y + BOX_SIZE && hero.y > box.y + BOX_SIZE - 18;
        if (overlapX && headHit) {
          hero.y = box.y + BOX_SIZE;
          hero.vy = 1;
          if (box.active) hitBox(box); else sndBump();
          return;
        }
      }
    }

    function step() {
      if (!gameState.started || gameState.isGameOver) return;
      const active = !gameState.isPaused;

      // Di chuyển ngang (khóa khi đang rơi hố)
      if (active && !hero.falling) {
        if (keys.left)  { hero.x = Math.max(30, hero.x - hero.speed); hero.facing = -1; hero.legSwing += 0.3; }
        if (keys.right) { hero.x = Math.min(WORLD_W - 60, hero.x + hero.speed); hero.facing = 1; hero.legSwing += 0.3; }
        cameraX = Math.max(0, Math.min(WORLD_W - canvas.width, hero.x - 300));
      }

      // Rơi xuống hố
      if (hero.falling) {
        hero.y += 7;
        if (hero.y > canvas.height + 20) {
          sndTrap();
          triggerShake();
          const pit = hero.fallPit;
          loseLife();
          if (!gameState.isGameOver) resetHero(Math.max(60, pit.start - 90));
        }
      } else if (hero.isJumping) {
        hero.y += hero.vy;
        hero.vy += 0.8;
        if (active && hero.vy < 0 && !gameState.inBossFight) checkBoxBump();
        if (hero.y >= GROUND_Y) { hero.y = GROUND_Y; hero.vy = 0; hero.isJumping = false; }
      }

      // Đứng trên miệng hố -> rơi
      if (active && !hero.isJumping && !hero.falling) {
        const pit = findPitUnderHero();
        if (pit) { hero.falling = true; hero.fallPit = pit; }
      }

      // Hiệu ứng: tinh thể bay, khối nảy, tia năng lượng
      floatingCoins.forEach(fc => { fc.y += fc.vy; fc.vy += 0.6; });
      floatingCoins = floatingCoins.filter(fc => fc.vy < 9);
      mysteryBoxes.forEach(b => { if (b.bump > 0) b.bump--; });
      popItems.forEach(p => { if (p.rise < 46) p.rise += 2.5; p.life--; });
      popItems = popItems.filter(p => p.life > 0);

      if (laser.active) {
        laser.x += laser.vx;
        if (laser.x >= BOSS_X + 20) { laser.active = false; bossFlash = 18; sndTrap(); triggerShake(); }
      }
      if (bossFlash > 0) bossFlash--;
    }

    // ===== VẼ =====
    const STARS = Array.from({ length: 90 }, (_, i) => ({
      x: (i * 137.5) % 900, y: (i * 61.3) % 380, r: i % 7 === 0 ? 3 : (i % 3 === 0 ? 2 : 1),
      depth: i % 2 === 0 ? 0.15 : 0.3, c: i % 5 === 0 ? "#a5f3fc" : (i % 4 === 0 ? "#fde68a" : "#ffffff")
    }));
    // các hành tinh xa: [x, y, bán kính, màu, có vành đai?]
    const CUBE_SYMBOLS = ["Δ", "π", "√x", "∑", "∠", "x²", "≅", "∞"];
    const PLANETS = [[260, 120, 46, "#f472b6", true], [1050, 80, 30, "#34d399", false], [1750, 140, 58, "#60a5fa", true], [2550, 90, 38, "#fbbf24", false]];
    // Phi hành gia pixel (nhân vật gốc của dự án): đồ trắng, mũ tròn kính xanh neon, ba lô oxy cam
    function drawHero() {
      ctx.save();
      ctx.translate(hero.x, hero.y);
      if (hero.facing < 0) { ctx.translate(hero.w, 0); ctx.scale(-1, 1); }

      if (IMG.hero.ok) {
        ctx.drawImage(IMG.hero, 0, 0, hero.w, hero.h);
      } else {
        ctx.scale(HERO_SCALE, HERO_SCALE);   // vẽ hình pixel gốc 32x44 rồi phóng to
        const legOffset = (keys.left || keys.right) && !hero.isJumping ? Math.round(Math.sin(hero.legSwing) * 2) : 0;
        // ba lô oxy (sau lưng)
        ctx.fillStyle = "#f97316"; ctx.fillRect(1, 17, 7, 15);
        ctx.fillStyle = "#c2410c"; ctx.fillRect(1, 17, 7, 3);
        // chân + ủng xám
        ctx.fillStyle = "#e2e8f0";
        ctx.fillRect(8, 33 + legOffset, 7, 7);
        ctx.fillRect(18, 33 - legOffset, 7, 7);
        ctx.fillStyle = "#64748b";
        ctx.fillRect(7, 39 + legOffset, 9, 5);
        ctx.fillRect(17, 39 - legOffset, 9, 5);
        // thân áo trắng
        ctx.fillStyle = "#f8fafc"; ctx.fillRect(7, 17, 20, 17);
        ctx.fillStyle = "#cbd5e1"; ctx.fillRect(7, 31, 20, 3);
        // bảng điều khiển trước ngực
        ctx.fillStyle = "#1e293b"; ctx.fillRect(13, 21, 9, 6);
        ctx.fillStyle = "#22d3ee"; ctx.fillRect(14, 22, 2, 2);
        ctx.fillStyle = "#facc15"; ctx.fillRect(17, 22, 2, 2);
        ctx.fillStyle = "#4ade80"; ctx.fillRect(20, 22, 1, 2);
        // tay
        ctx.fillStyle = "#e2e8f0"; ctx.fillRect(25, 19, 5, 9);
        ctx.fillStyle = "#64748b"; ctx.fillRect(25, 27, 5, 3);
        // mũ bảo hiểm tròn
        ctx.fillStyle = "#f8fafc";
        ctx.beginPath(); ctx.arc(17, 10, 11, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = "#94a3b8"; ctx.lineWidth = 1.5; ctx.stroke();
        // kính mũ xanh neon + vệt sáng
        ctx.fillStyle = "#06b6d4"; ctx.fillRect(15, 5, 12, 9);
        ctx.fillStyle = "#67e8f9"; ctx.fillRect(16, 6, 4, 3);
        ctx.strokeStyle = "#0e7490"; ctx.strokeRect(15, 5, 12, 9);
        // ăng-ten nhỏ
        ctx.fillStyle = "#94a3b8"; ctx.fillRect(10, -3, 2, 4);
        ctx.fillStyle = "#facc15"; ctx.fillRect(9, -5, 4, 3);
      }
      ctx.restore();
    }

    // Bình oxy: +1 mạng
    function drawOxygen(cx, bottom) {
      ctx.fillStyle = "#38bdf8";
      ctx.fillRect(cx - 13, bottom - 34, 26, 34);
      ctx.strokeStyle = "#000"; ctx.lineWidth = 2; ctx.strokeRect(cx - 13, bottom - 34, 26, 34);
      ctx.fillStyle = "#e0f2fe"; ctx.fillRect(cx - 10, bottom - 30, 3, 24);
      ctx.fillStyle = "#475569"; ctx.fillRect(cx - 5, bottom - 41, 10, 7);
      ctx.strokeRect(cx - 5, bottom - 41, 10, 7);
      ctx.fillStyle = "#fff";
      ctx.font = "bold 11px 'Plus Jakarta Sans', sans-serif";
      ctx.textAlign = "center"; ctx.fillText("O₂", cx + 2, bottom - 13); ctx.textAlign = "left";
    }

    // Thiên thạch: -1 mạng
    function drawMeteor(cx, bottom, t) {
      const cy = bottom - 20;
      // đuôi lửa
      ctx.fillStyle = t % 8 < 4 ? "rgba(250,204,21,0.8)" : "rgba(249,115,22,0.8)";
      ctx.beginPath(); ctx.moveTo(cx + 10, cy - 14); ctx.lineTo(cx + 34, cy - 34); ctx.lineTo(cx + 18, cy + 4); ctx.closePath(); ctx.fill();
      // khối đá
      ctx.fillStyle = "#57534e";
      ctx.beginPath();
      ctx.moveTo(cx - 18, cy - 4); ctx.lineTo(cx - 8, cy - 19); ctx.lineTo(cx + 12, cy - 16);
      ctx.lineTo(cx + 19, cy + 2); ctx.lineTo(cx + 6, cy + 18); ctx.lineTo(cx - 13, cy + 14);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle = "#f87171"; ctx.lineWidth = 2; ctx.stroke();
      ctx.fillStyle = "#292524";
      [[-6, -4, 5], [7, 6, 4], [5, -9, 3]].forEach(([dx, dy, r]) => {
        ctx.beginPath(); ctx.arc(cx + dx, cy + dy, r, 0, Math.PI * 2); ctx.fill();
      });
    }

    function drawPopItem(p) {
      const bottom = p.baseY - p.rise + BOX_SIZE * 0.2;
      ctx.save();
      ctx.globalAlpha = Math.min(1, p.life / 20);
      if (p.kind === 'oxygen') drawOxygen(p.x, bottom);
      else if (p.kind === 'meteor') drawMeteor(p.x, bottom, p.life);
      ctx.restore();
    }

    function drawPopLabel(p) {
      const y = p.baseY - p.rise - (p.kind === 'text' ? 0 : 52);
      ctx.save();
      ctx.globalAlpha = Math.min(1, p.life / 20);
      ctx.font = "800 20px 'Plus Jakarta Sans', sans-serif";   // font pixel không có dấu tiếng Việt
      ctx.textAlign = "center";
      ctx.lineWidth = 4; ctx.strokeStyle = "#000";
      ctx.strokeText(p.label, p.x, y);
      ctx.fillStyle = p.color;
      ctx.fillText(p.label, p.x, y);
      ctx.restore();
    }

    // Bề mặt hành tinh: đá tím xám có miệng hố nhỏ, hố đen là khoảng trống
    function drawGround() {
      const segments = [];
      let lastX = 0;
      groundPits.forEach(pit => { segments.push([lastX, pit.start]); lastX = pit.start + pit.width; });
      segments.push([lastX, WORLD_W]);
      segments.forEach(([a, b]) => {
        ctx.fillStyle = "#4c4566";
        ctx.fillRect(a, GROUND_TOP, b - a, canvas.height - GROUND_TOP);
        ctx.fillStyle = "#a78bfa";
        ctx.fillRect(a, GROUND_TOP, b - a, 5);          // viền sáng trên mặt đất
        ctx.fillStyle = "#3b3552";
        for (let gx = a + 30; gx < b - 30; gx += 140) {   // miệng hố thiên thạch
          ctx.beginPath(); ctx.ellipse(gx, GROUND_TOP + 34, 22, 7, 0, 0, Math.PI * 2); ctx.fill();
          ctx.beginPath(); ctx.ellipse(gx + 70, GROUND_TOP + 72, 14, 5, 0, 0, Math.PI * 2); ctx.fill();
        }
      });
      // hố đen: viền phát sáng tím
      groundPits.forEach(pit => {
        const g = ctx.createLinearGradient(0, GROUND_TOP, 0, canvas.height);
        g.addColorStop(0, "#000"); g.addColorStop(1, "#1e0b3a");
        ctx.fillStyle = g;
        ctx.fillRect(pit.start, GROUND_TOP, pit.width, canvas.height - GROUND_TOP);
        ctx.fillStyle = "#d946ef";
        ctx.fillRect(pit.start - 3, GROUND_TOP, 3, canvas.height - GROUND_TOP);
        ctx.fillRect(pit.start + pit.width, GROUND_TOP, 3, canvas.height - GROUND_TOP);
      });
    }

    // Quái Thú Tứ Giác (nhân vật gốc): thân là tứ giác ABCD không đều, một mắt to, sừng ở các đỉnh
    function drawBoss() {
      const bx = BOSS_X, by = BOSS_Y;
      const shakeX = bossFlash > 0 ? (bossFlash % 4 < 2 ? -4 : 4) : 0;
      const t = performance.now() / 300;
      if (IMG.boss.ok) {
        ctx.drawImage(IMG.boss, bx + shakeX, by, 90, 140);
      } else {
        const x = bx + shakeX, y = by + Math.sin(t) * 4;       // lơ lửng nhẹ
        const P = { A: [x + 8, y + 22], B: [x + 92, y + 4], C: [x + 82, y + 132], D: [x - 4, y + 116] };
        // sừng tam giác ở mỗi đỉnh
        ctx.fillStyle = "#facc15"; ctx.strokeStyle = "#000"; ctx.lineWidth = 2;
        [["A", -10, -12], ["B", 12, -12], ["C", 12, 12], ["D", -12, 12]].forEach(([k, dx, dy]) => {
          const [px, py] = P[k];
          ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px + dx, py + dy * 0.4); ctx.lineTo(px + dx * 0.4, py + dy); ctx.closePath();
          ctx.fill(); ctx.stroke();
        });
        // thân tứ giác
        ctx.fillStyle = bossFlash > 0 && bossFlash % 4 < 2 ? "#ffffff" : "#7c3aed";
        ctx.beginPath(); ctx.moveTo(...P.A); ctx.lineTo(...P.B); ctx.lineTo(...P.C); ctx.lineTo(...P.D); ctx.closePath();
        ctx.fill(); ctx.lineWidth = 3; ctx.stroke();
        // hai đường chéo mờ
        ctx.strokeStyle = "rgba(255,255,255,0.25)"; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(...P.A); ctx.lineTo(...P.C); ctx.moveTo(...P.B); ctx.lineTo(...P.D); ctx.stroke();
        // một mắt to
        ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(x + 46, y + 52, 17, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = "#000"; ctx.lineWidth = 2; ctx.stroke();
        ctx.fillStyle = "#dc2626"; ctx.beginPath(); ctx.arc(x + 40, y + 54, 8, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#000"; ctx.beginPath(); ctx.arc(x + 38, y + 54, 4, 0, Math.PI * 2); ctx.fill();
        // miệng răng cưa
        ctx.fillStyle = "#1e1b4b"; ctx.fillRect(x + 22, y + 86, 50, 14);
        ctx.fillStyle = "#fff";
        for (let i = 0; i < 5; i++) {
          ctx.beginPath(); ctx.moveTo(x + 22 + i * 10, y + 86); ctx.lineTo(x + 27 + i * 10, y + 94); ctx.lineTo(x + 32 + i * 10, y + 86); ctx.fill();
        }
        // nhãn đỉnh A B C D
        ctx.font = "bold 13px 'Plus Jakarta Sans', sans-serif"; ctx.fillStyle = "#fde047";
        ctx.fillText("A", P.A[0] - 16, P.A[1] - 4); ctx.fillText("B", P.B[0] + 8, P.B[1] - 2);
        ctx.fillText("C", P.C[0] + 8, P.C[1] + 12); ctx.fillText("D", P.D[0] - 16, P.D[1] + 14);
      }
      ctx.fillStyle = "#000";
      ctx.fillRect(bx - 10, by - 32, 100, 16);
      ctx.fillStyle = "#ef4444";
      const hpW = (gameState.bossHp / gameState.bossMaxHp) * 96;
      ctx.fillRect(bx - 8, by - 30, Math.max(0, hpW), 12);
      ctx.fillStyle = "#fff";
      ctx.font = "800 13px 'Plus Jakarta Sans', sans-serif";
      ctx.fillText("QUÁI THÚ TỨ GIÁC", bx - 14, by - 40);
    }

    function drawWorld() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const currentBg = !gameState.examData ? "#0b1026"
        : gameState.inBossFight ? "#1a0420"
        : gameState.examData.stages[Math.min(gameState.currentStageIdx, 4)].bg;
      ctx.fillStyle = currentBg;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      // sao lấp lánh, trôi chậm hơn mặt đất (hiệu ứng chiều sâu)
      STARS.forEach(s => {
        const sx = ((s.x - cameraX * s.depth) % canvas.width + canvas.width) % canvas.width;
        ctx.globalAlpha = 0.5 + 0.5 * Math.abs(Math.sin(performance.now() / 600 + s.x));
        ctx.fillStyle = s.c;
        ctx.fillRect(sx, s.y, s.r, s.r);
      });
      ctx.globalAlpha = 1;
      if (IMG.background.ok && !gameState.inBossFight) {
        ctx.globalAlpha = 0.85;
        ctx.drawImage(IMG.background, 0, 0, canvas.width, canvas.height);
        ctx.globalAlpha = 1;
      }

      ctx.save();
      ctx.translate(-Math.round(cameraX), 0);

      if (!gameState.inBossFight) {
        // Hành tinh phía xa
        PLANETS.forEach(([px, py, pr, pc, ring]) => {
          ctx.fillStyle = pc; ctx.globalAlpha = 0.85;
          ctx.beginPath(); ctx.arc(px, py, pr, 0, Math.PI * 2); ctx.fill();
          ctx.fillStyle = "rgba(0,0,0,0.25)";
          ctx.beginPath(); ctx.arc(px + pr * 0.35, py + pr * 0.2, pr * 0.8, 0, Math.PI * 2); ctx.fill();
          if (ring) {
            ctx.strokeStyle = "rgba(255,255,255,0.6)"; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.ellipse(px, py, pr * 1.6, pr * 0.35, -0.3, 0, Math.PI * 2); ctx.stroke();
          }
          ctx.globalAlpha = 1;
        });

        // Trạm vũ trụ đích cuối màn (cột ăng-ten + đèn hiệu)
        ctx.fillStyle = "#94a3b8"; ctx.fillRect(2970, 230, 10, 170);
        ctx.fillStyle = "#334155"; ctx.fillRect(2950, 380, 50, 20);
        ctx.fillStyle = Math.floor(performance.now() / 400) % 2 ? "#22d3ee" : "#f0abfc";
        ctx.beginPath(); ctx.arc(2975, 224, 9, 0, Math.PI * 2); ctx.fill();

        // Vật phẩm nhô lên (vẽ trước ô để trông như chui ra từ trong ô)
        popItems.forEach(drawPopItem);

        // Khối năng lượng toán học (mỗi khối một ký hiệu)
        mysteryBoxes.forEach((box, i) => {
          const by = box.y - (box.bump > 0 ? Math.sin((box.bump / 8) * Math.PI) * 10 : 0);
          if (IMG.box.ok && box.active) {
            ctx.drawImage(IMG.box, box.x, by, BOX_SIZE, BOX_SIZE);
          } else {
            const glow = box.active ? 0.5 + 0.5 * Math.sin(performance.now() / 250 + i) : 0;
            if (box.active) { ctx.shadowColor = "#22d3ee"; ctx.shadowBlur = 8 + glow * 10; }
            const g = ctx.createLinearGradient(box.x, by, box.x + BOX_SIZE, by + BOX_SIZE);
            if (box.active) { g.addColorStop(0, "#6366f1"); g.addColorStop(1, "#06b6d4"); }
            else { g.addColorStop(0, "#334155"); g.addColorStop(1, "#1e293b"); }
            ctx.fillStyle = g;
            ctx.fillRect(box.x, by, BOX_SIZE, BOX_SIZE);
            ctx.shadowBlur = 0;
            ctx.strokeStyle = box.active ? "#a5f3fc" : "#475569"; ctx.lineWidth = 3;
            ctx.strokeRect(box.x, by, BOX_SIZE, BOX_SIZE);
            // mặt trên khối lập phương (giả 3D)
            ctx.fillStyle = box.active ? "rgba(255,255,255,0.28)" : "rgba(255,255,255,0.06)";
            ctx.beginPath(); ctx.moveTo(box.x, by); ctx.lineTo(box.x + 8, by - 8); ctx.lineTo(box.x + BOX_SIZE + 8, by - 8); ctx.lineTo(box.x + BOX_SIZE, by); ctx.fill();
            ctx.fillStyle = box.active ? "#fff" : "#4ade80";
            ctx.font = "bold 22px 'Plus Jakarta Sans', sans-serif";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(box.active ? CUBE_SYMBOLS[i % CUBE_SYMBOLS.length] : "✓", box.x + BOX_SIZE / 2, by + BOX_SIZE / 2 + 1);
            ctx.textAlign = "left"; ctx.textBaseline = "alphabetic";
          }
        });

        // Chữ thông báo (+1 MẠNG / -1 MẠNG) vẽ trên cùng
        popItems.forEach(drawPopLabel);

        floatingCoins.forEach(fc => {       // tinh thể năng lượng bay lên
          const cx = fc.x + 12;
          ctx.fillStyle = "#e879f9";
          ctx.beginPath(); ctx.moveTo(cx, fc.y - 13); ctx.lineTo(cx + 10, fc.y); ctx.lineTo(cx, fc.y + 13); ctx.lineTo(cx - 10, fc.y); ctx.closePath();
          ctx.fill();
          ctx.strokeStyle = "#701a75"; ctx.lineWidth = 2; ctx.stroke();
          ctx.fillStyle = "rgba(255,255,255,0.6)"; ctx.fillRect(cx - 3, fc.y - 6, 3, 6);
        });
      }

      drawGround();
      drawHero();

      if (gameState.inBossFight && !gameState.defeatedBoss) drawBoss();

      if (laser.active) {
        ctx.fillStyle = "rgba(34,211,238,0.45)";
        ctx.fillRect(laser.x - 40, laser.y - 7, 50, 14);
        ctx.fillStyle = "#a5f3fc";
        ctx.fillRect(laser.x - 30, laser.y - 3, 40, 6);
        ctx.fillStyle = "#fff";
        ctx.beginPath(); ctx.arc(laser.x + 10, laser.y, 6, 0, Math.PI * 2); ctx.fill();
      }

      ctx.restore();
    }

    // Vòng lặp bước cố định 60 lần/giây -> tốc độ như nhau trên màn 60Hz hay 144Hz
    const STEP_MS = 1000 / 60;
    let lastTime = performance.now();
    let accumulator = 0;
    function gameLoop(now) {
      accumulator += Math.min(250, now - lastTime);
      lastTime = now;
      while (accumulator >= STEP_MS) { step(); accumulator -= STEP_MS; }
      drawWorld();
      requestAnimationFrame(gameLoop);
    }
    requestAnimationFrame(gameLoop);

    // ===== BẮT ĐẦU =====
    function startGame() {
      const name = document.getElementById("input-name").value.trim();
      const sClass = document.getElementById("input-class").value.trim();
      if (!name || !sClass) { alert("Em vui lòng nhập đầy đủ Họ tên và Lớp nhé!"); return; }

      gameState.studentName = name;
      gameState.studentClass = sClass;
      gameState.examData = buildExam();
      initLevelBoxes();
      resetHero(100);
      cameraX = 0;

      document.getElementById("login-modal").classList.add("hidden");
      document.getElementById("hud-world").textContent = "P-1";
      document.getElementById("hud-quest").textContent = "0/5";
      updateHud();
      if (document.activeElement) document.activeElement.blur();
      gameState.started = true;
      gameState.isPaused = false;
      if (audioCtx.state === 'suspended') audioCtx.resume();
      startBgm();
    }
    document.getElementById("btn-start-game").onclick = startGame;
    ["input-name", "input-class"].forEach(id => {
      document.getElementById(id).addEventListener("keydown", (e) => { if (e.key === "Enter") startGame(); });
    });

    // ===== CÂU HỎI =====
    const quizModal = document.getElementById("quiz-modal");
    const badgeEl = document.getElementById("quiz-level-badge");
    const timerTextEl = document.getElementById("quiz-timer-text");
    const timerBarEl = document.getElementById("timer-bar");
    const questionTextEl = document.getElementById("quiz-question-text");
    const optionsBox = document.getElementById("quiz-options-container");
    const shortBox = document.getElementById("quiz-short-container");
    const shortInput = document.getElementById("quiz-short-input");
    const shortSubmit = document.getElementById("quiz-short-submit");
    const feedbackEl = document.getElementById("quiz-feedback");

    let currentQ = null;

    function closeQuizModal() {
      quizModal.classList.add("hidden");
      if (document.activeElement) document.activeElement.blur();
    }

    function openNextQuestion() {
      if (gameState.isGameOver) return;
      gameState.isPaused = true;
      keys.left = keys.right = false;
      feedbackEl.innerHTML = "";

      if (!gameState.inBossFight) {
        const curStage = gameState.examData.stages[gameState.currentStageIdx];
        currentQ = curStage.questions[gameState.currentQuestionIdx];
        badgeEl.textContent = `Màn ${gameState.currentStageIdx + 1} • Câu ${gameState.currentQuestionIdx + 1}/5 • ${currentQ.level}`;
      } else {
        const list = gameState.examData.bossQuestions;
        currentQ = list[gameState.bossQIdx % list.length];
        gameState.bossQIdx++;
        sndRoar();
        badgeEl.textContent = `⚔️ ĐẠI CHIẾN QUÁI THÚ TỨ GIÁC (HP: ${gameState.bossHp}/${gameState.bossMaxHp})`;
      }

      questionTextEl.textContent = currentQ.q;
      quizModal.classList.remove("hidden");
      gameState.answerLocked = false;

      gameState.timerSec = currentQ.time;
      gameState.timerMax = currentQ.time;
      timerTextEl.textContent = gameState.timerSec + "s";
      timerBarEl.style.width = "100%";

      if (gameState.timerInterval) clearInterval(gameState.timerInterval);
      gameState.timerInterval = setInterval(() => {
        gameState.timerSec--;
        timerTextEl.textContent = Math.max(0, gameState.timerSec) + "s";
        timerBarEl.style.width = Math.max(0, (gameState.timerSec / gameState.timerMax) * 100) + "%";
        if (gameState.timerSec <= 0) handleAnswer(false, "Đã hết thời gian!");
      }, 1000);

      if (currentQ.type === "mcq") {
        optionsBox.classList.remove("hidden");
        shortBox.classList.add("hidden");
        optionsBox.innerHTML = "";
        currentQ.answers.forEach((ans, idx) => {
          const btn = document.createElement("button");
          btn.className = "w-full text-left bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl p-3 text-xs font-semibold disabled:opacity-60";
          const num = document.createElement("span");
          num.className = "text-amber-400 font-bold";
          num.textContent = (idx + 1) + ". ";
          btn.appendChild(num);
          btn.appendChild(document.createTextNode(ans));
          btn.onclick = () => handleAnswer(idx === currentQ.correct, null, idx);
          optionsBox.appendChild(btn);
        });
      } else {
        optionsBox.classList.add("hidden");
        shortBox.classList.remove("hidden");
        shortInput.value = "";
        shortInput.disabled = false;
        shortSubmit.disabled = false;
        setTimeout(() => shortInput.focus(), 150);
      }
    }

    function submitShortAnswer() {
      const val = normalizeAnswer(shortInput.value);
      if (!val) return;
      const isOk = currentQ.correctAnswers.some(ans => normalizeAnswer(ans) === val);
      handleAnswer(isOk);
    }
    shortSubmit.onclick = submitShortAnswer;
    shortInput.addEventListener("keydown", (e) => { if (e.key === "Enter") submitShortAnswer(); });

    function handleAnswer(isCorrect, customReason = null, pickedIdx = null) {
      if (gameState.answerLocked) return;          // chống bấm 2 lần / trùng với hết giờ
      gameState.answerLocked = true;
      clearInterval(gameState.timerInterval);

      // Khóa giao diện, tô màu đáp án
      shortInput.disabled = true;
      shortSubmit.disabled = true;
      [...optionsBox.children].forEach((btn, i) => {
        btn.disabled = true;
        if (currentQ.type === "mcq" && i === currentQ.correct) btn.classList.add("border-emerald-400", "bg-emerald-900/40");
        else if (i === pickedIdx) btn.classList.add("border-rose-400", "bg-rose-900/40");
      });

      if (isCorrect) {
        sndCoin();
        gameState.score += gameState.inBossFight ? 300 : 100;
        updateHud();
        feedbackEl.innerHTML = '<span class="text-emerald-400 font-bold">🎉 CHÍNH XÁC!</span>';

        if (gameState.inBossFight) {
          gameState.bossHp--;
          laser.active = true;
          laser.x = hero.x + 30;
          laser.y = hero.y + hero.h * 0.4;
          laser.vx = 9;
        } else if (!hero.isJumping && !hero.falling) {
          hero.isJumping = true;
          hero.vy = -10;
        }

        setTimeout(() => { closeQuizModal(); advanceProgress(); }, 1100);
      } else {
        sndWrong();
        gameState.lives = Math.max(0, gameState.lives - 1);
        updateHud();
        const correctText = currentQ.type === "mcq" ? currentQ.answers[currentQ.correct] : currentQ.correctAnswers[0];
        feedbackEl.innerHTML = "";
        const line1 = document.createElement("div");
        line1.className = "text-rose-400 font-bold";
        line1.textContent = "❌ " + (customReason || "Chưa chính xác!") + " Đáp án: " + correctText;
        const line2 = document.createElement("div");
        line2.className = "text-[11px] text-slate-300 mt-1";
        line2.textContent = "Ghi nhớ: " + currentQ.explain;
        feedbackEl.append(line1, line2);

        setTimeout(() => {
          closeQuizModal();
          if (gameState.lives <= 0) finishGameSession(false);
          else advanceProgress();
        }, 3000);
      }
    }

    const stageClearModal = document.getElementById("stage-clear-modal");
    const teacherNotes = [
      "Cô Mai Phương rất vui khi em nắm vững tính chất góc tứ giác lồi! Sang Ải 2 nhé!",
      "Làm tốt lắm! Em đã thuộc lòng tính chất hai đường chéo của hình thang cân. Sang Ải 3 nào!",
      "Xuất sắc! Tính chất hai đường chéo cắt nhau tại trung điểm là chìa khóa vàng. Tiến lên Ải 4!",
      "Tuyệt vời! Em đã vận dụng thành thạo tính chất hình chữ nhật. Ải 5 đang chờ đón!",
      "Hoàn thành 5 Ải! Hãy tập trung cao độ đánh bại Quái Thú Tứ Giác để nhận +5 Điểm cộng nhé!"
    ];

    function advanceProgress() {
      if (gameState.isGameOver) return;

      if (gameState.inBossFight) {
        if (gameState.bossHp <= 0) {
          gameState.defeatedBoss = true;
          setTimeout(() => finishGameSession(true), 500);
        } else {
          setTimeout(() => openNextQuestion(), 700);
        }
        return;
      }

      gameState.currentQuestionIdx++;
      document.getElementById("hud-quest").textContent = `${gameState.currentQuestionIdx}/5`;

      if (gameState.currentQuestionIdx >= 5) {
        const curStage = gameState.examData.stages[gameState.currentStageIdx];
        document.getElementById("stage-clear-title").textContent = "HOÀN THÀNH " + curStage.name.toUpperCase() + "!";
        document.getElementById("stage-clear-msg").textContent = teacherNotes[gameState.currentStageIdx];
        stageClearModal.classList.remove("hidden");
      } else {
        gameState.isPaused = false;
      }
    }

    document.getElementById("btn-continue-next-stage").onclick = (e) => {
      e.currentTarget.blur();
      stageClearModal.classList.add("hidden");
      gameState.currentStageIdx++;
      gameState.currentQuestionIdx = 0;
      resetHero(100);
      cameraX = 0;
      document.getElementById("hud-quest").textContent = "0/5";

      if (gameState.currentStageIdx >= gameState.examData.stages.length) {
        // Đấu trùm: không có hố, không có khối năng lượng
        gameState.inBossFight = true;
        groundPits = [];
        mysteryBoxes = [];
        floatingCoins = [];
        resetHero(1000);
        cameraX = 900;
        document.getElementById("hud-world").textContent = "BOSS";
        document.getElementById("hud-quest").textContent = "BOSS";
        sndRoar();
        setTimeout(() => openNextQuestion(), 800);
      } else {
        document.getElementById("hud-world").textContent = `P-${gameState.currentStageIdx + 1}`;
        initLevelBoxes();
        gameState.isPaused = false;
      }
    };

    // ===== KẾT THÚC & GỬI KẾT QUẢ =====
    function finishGameSession(isVictory) {
      if (gameState.isGameOver) return;           // chỉ chạy 1 lần
      gameState.isGameOver = true;
      gameState.isPaused = true;
      clearInterval(gameState.timerInterval);
      stopBgm();
      quizModal.classList.add("hidden");
      stageClearModal.classList.add("hidden");

      document.getElementById("sum-name").textContent = gameState.studentName;
      document.getElementById("sum-class").textContent = gameState.studentClass;
      document.getElementById("sum-examcode").textContent = gameState.examData.code;
      document.getElementById("sum-score").textContent = gameState.score;

      const subtitle = document.getElementById("summary-subtitle");
      if (isVictory) {
        document.getElementById("summary-badge-icon").textContent = "👑";
        document.getElementById("summary-title").textContent = "CHIẾN THẮNG TUYỆT ĐỐI!";
        subtitle.textContent = "Đã xuất sắc vượt qua 5 Ải & Hạ gục Quái Thú Tứ Giác";
        subtitle.className = "text-[11px] text-emerald-400 font-semibold";
        document.getElementById("sum-bonus").textContent = "+5 ĐIỂM CỘNG";
        document.getElementById("summary-teacher-note").innerHTML = '🎉 <b>Lời khen từ Cô Mai Phương:</b> Em đã xuất sắc hạ gục Quái Thú Tứ Giác! Cô cộng <b>+5 điểm thực tế</b> vào sổ điểm cho em!';
      } else {
        const reached = gameState.inBossFight ? "trận đấu Quái Thú Tứ Giác" : "Màn " + (gameState.currentStageIdx + 1);
        document.getElementById("summary-badge-icon").textContent = "🛡️";
        document.getElementById("summary-title").textContent = "DỪNG BƯỚC THỬ THÁCH";
        subtitle.textContent = "Em đã dừng lại ở " + reached;
        subtitle.className = "text-[11px] text-rose-400 font-semibold";
        document.getElementById("sum-bonus").textContent = "0 ĐIỂM CỘNG";
        document.getElementById("summary-teacher-note").innerHTML = '💡 <b>Lời dặn từ Cô Mai Phương:</b> Em đã nỗ lực đạt <b>' + gameState.score + ' điểm</b>. Hãy xem lại bài và bấm Chơi lại để phục thù nhé!';
      }

      document.getElementById("summary-modal").classList.remove("hidden");

      const payload = {
        time: new Date().toLocaleString("vi-VN"),
        examCode: gameState.examData.code,
        name: gameState.studentName,
        student_class: gameState.studentClass,
        score: gameState.score,
        topic: "Minigame Tứ Giác (Vượt Ải Không Gian)",
        feedback: isVictory ? "Hạ gục Quái Thú Tứ Giác (+5đ)" : ("Chưa hạ Quái Thú - dừng ở " + (gameState.inBossFight ? "BOSS" : "Màn " + (gameState.currentStageIdx + 1)))
      };

      gameState.lastPayload = payload;
      syncToGoogleSheets(payload);
    }

    async function syncToGoogleSheets(payload) {
      const syncStatusText = document.getElementById("sync-status-text");
      const retryBtn = document.getElementById("btn-retry-sync");

      if (!GOOGLE_SCRIPT_WEBAPP_URL || GOOGLE_SCRIPT_WEBAPP_URL.includes("EXAMPLE_REPLACE")) {
        syncStatusText.innerHTML = "⚠️ Cô chưa cấu hình link Google Sheets. Em hãy chụp màn hình kết quả gửi cô nhé!";
        syncStatusText.className = "text-xs text-amber-300 font-bold";
        retryBtn.classList.add("hidden");
        return;
      }

      syncStatusText.innerHTML = "⏳ Đang kết nối gửi kết quả về Google Sheets của cô...";
      syncStatusText.className = "text-xs text-yellow-400 font-medium";
      retryBtn.classList.add("hidden");

      try {
        // no-cors chỉ cho phép Content-Type "text/plain"; Apps Script đọc bằng e.postData.contents
        await fetch(GOOGLE_SCRIPT_WEBAPP_URL, {
          method: "POST",
          mode: "no-cors",
          headers: { "Content-Type": "text/plain;charset=utf-8" },
          body: JSON.stringify(payload)
        });
        syncStatusText.innerHTML = "✅ Đã gửi kết quả về Google Sheets của Cô Mai Phương!";
        syncStatusText.className = "text-xs text-emerald-400 font-bold";
      } catch (err) {
        syncStatusText.innerHTML = '<div class="text-rose-400 font-bold">⚠️ Chưa có mạng! Kết quả chưa gửi được.</div><div class="text-[10px] text-slate-300 mt-1">Em hãy chụp màn hình gửi cô hoặc bấm nút thử lại:</div>';
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


with tab3:
    st.subheader("🚀 Phi Hành Gia Toán Học: Vượt Ải Không Gian")
    st.caption("Cùng cô Mai Phương chinh phục Quái Thú Tứ Giác! Cẩn thận với khối năng lượng bí ẩn và hố đen vũ trụ nha!")

    sheet_webhook = get_secret("GOOGLE_SHEET_WEBHOOK_URL", DEFAULT_WEBHOOK) or DEFAULT_WEBHOOK
    game_html = SPACE_GAME_HTML.replace('"WEBHOOK_URL_PLACEHOLDER"', json.dumps(sheet_webhook))
    components.html(game_html, height=780, scrolling=True)

# ================= TAB 4: BẢNG ĐIỂM LỚP =================
with tab4:
    st.markdown("### 🔒 Trạm Bảo Mật Sổ Điểm Giáo Viên")
    st.caption("Dữ liệu hạm đội học sinh được mã hóa bảo mật.")

    teacher_password = st.text_input("🔑 Nhập mật khẩu hạm đội để mở sổ điểm:", type="password", key="teacher_pass_tab4")
    # Nên đặt TEACHER_PASSWORD trong Secrets: mã nguồn để công khai trên GitHub thì học sinh đọc được mật khẩu mặc định.
    ADMIN_PASS = get_secret("TEACHER_PASSWORD", "Maiphuong2026")

    if teacher_password:
        if hmac.compare_digest(teacher_password.encode(), str(ADMIN_PASS).encode()):
            st.success("🔓 Xác thực trạm thành công! Chào cô Mai Phương.")
            st.caption("Bảng dưới gồm bài nộp ở Tab 2 kể từ lần khởi động app gần nhất. Điểm game Vượt Ải Không Gian và bản lưu lâu dài nằm trong Google Sheets.")

            if len(submission_history) == 0:
                st.info("Chưa có phi hành gia nào truyền bài nộp kể từ khi app khởi động.")
            else:
                df = pd.DataFrame(list(submission_history))
                st.dataframe(df, use_container_width=True)

                csv_data = df.to_csv(index=False).encode("utf-8-sig")

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
