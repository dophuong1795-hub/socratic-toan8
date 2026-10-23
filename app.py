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
    # Bộ lưu trữ danh sách sản phẩm triển lãm dùng chung cho toàn bộ học sinh
@st.cache_resource
def get_shared_gallery():
    return []

gallery_items = get_shared_gallery()


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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🪐 Thử Thách Tương Tác",
    "📝 Nộp Bài Tập",
    "👾 Vượt Ải Không Gian",
    "🎨 Triển Lãm Sản Phẩm",
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
  <title>Vượt Ải Không Gian - Lớp Toán Cô Mai Phương</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800;900&family=Chakra+Petch:wght@600;700;800&display=swap');
    .font-hud { font-family: 'Chakra Petch', sans-serif; letter-spacing: 0.05em; }
    .font-body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .shake { animation: shake-anim 0.35s cubic-bezier(.36,.07,.19,.97) both; }
    html, body { touch-action: manipulation; -webkit-touch-callout: none; -webkit-tap-highlight-color: transparent; }
    .pad-btn { touch-action: none; -webkit-user-select: none; user-select: none; }
    .pad-btn.pressed { transform: scale(0.92); filter: brightness(1.3); }
    @keyframes shake-anim {
      10%, 90% { transform: translate3d(-3px, 0, 0); }
      20%, 80% { transform: translate3d(5px, 0, 0); }
      30%, 50%, 70% { transform: translate3d(-6px, 0, 0); }
      40%, 60% { transform: translate3d(6px, 0, 0); }
    }
  </style>
</head>
<body class="bg-[#030712] text-slate-100 font-body min-h-screen flex flex-col items-center justify-start p-2 select-none">

  <!-- TAB TIÊU ĐỀ -->
  <div class="w-full max-w-3xl flex items-center justify-between mb-2 px-1">
    <div class="flex items-center gap-2 bg-indigo-950/90 border border-cyan-400/50 rounded-xl px-3.5 py-1.5 shadow-lg shadow-cyan-950/40">
      <span class="text-xl">🌌</span>
      <span class="text-xs sm:text-sm font-extrabold text-cyan-300 tracking-wider uppercase font-hud">TAB: VƯỢT ẢI KHÔNG GIAN</span>
    </div>
    <div class="text-[11px] text-slate-400 font-medium hidden sm:block">Hình học 8 - Khám Phá Thế Giới Tứ Giác</div>
  </div>

  <!-- MODAL ĐĂNG NHẬP -->
  <div id="login-modal" class="fixed inset-0 z-50 bg-[#030712]/95 backdrop-blur-md flex items-start sm:items-center justify-center p-3 sm:p-4 overflow-y-auto">
    <div class="bg-slate-900 border-2 border-cyan-400/80 rounded-2xl max-w-md w-full p-6 shadow-2xl text-center">
      <div class="inline-block p-3.5 bg-gradient-to-tr from-cyan-600 to-indigo-600 rounded-2xl shadow-lg mb-3">
        <span class="text-3xl">👨‍🚀</span>
      </div>
      <h1 class="text-lg sm:text-xl font-extrabold text-amber-400 mb-1">LỚP TOÁN CÔ MAI PHƯƠNG</h1>
      <p class="text-xs text-cyan-300 font-semibold mb-4">Vượt Ải Không Gian: Giải Mã Hạm Đội UFO & Tiêu Diệt Quái Thú Tứ Giác</p>

      <div class="space-y-3 text-left mb-5">
        <div>
          <label class="block text-[11px] font-bold text-slate-300 uppercase mb-1">Họ và tên học sinh:</label>
          <input type="text" id="input-name" placeholder="Ví dụ: Nguyễn Mai An" class="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-400">
        </div>
        <div>
          <label class="block text-[11px] font-bold text-slate-300 uppercase mb-1">Lớp:</label>
          <input type="text" id="input-class" placeholder="Ví dụ: 8A13" class="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-400">
        </div>
      </div>

      <div class="bg-slate-800/80 border border-slate-700 rounded-xl p-3 text-xs text-slate-300 text-left mb-5 space-y-1.5">
        <p>🎮 <b>Máy tính:</b> <b>← / →</b> để chạy, <b>Space / ↑</b> kích hoạt Jetpack nhảy.</p>
        <p>📱 <b>Điện thoại:</b> giữ <b>◀</b> lùi, <b>▶</b> tiến; bấm <b>JETPACK</b> để bay lên.</p>
        <p>🛸 <b>Hạm đội UFO lơ lửng:</b> Nhảy húc đầu để mở 5 Câu hỏi, 🧪 Bình oxy, 💎 Tinh thể, ☄️ Thiên thạch.</p>
        <p>⚠️ <b>Hố sâu:</b> Có cột Laser cảnh báo tím chiếu rọi từ xa.</p>
        <p>🇻🇳 Thắng ải 5 để cắm cờ Việt Nam trên Mặt Trăng và lái phi thuyền về Trái Đất!</p>
      </div>

      <button id="btn-start-game" class="w-full py-3.5 bg-gradient-to-r from-cyan-600 via-indigo-600 to-fuchsia-600 hover:from-cyan-500 hover:to-fuchsia-500 text-white font-extrabold text-sm rounded-xl shadow-lg transition transform active:scale-95">
        BẮT ĐẦU VƯỢT ẢI NGAY 🚀
      </button>
    </div>
  </div>

  <!-- HUD THÔNG TIN -->
  <header class="w-full max-w-3xl flex flex-wrap items-center justify-between gap-x-2 gap-y-1 bg-black/90 backdrop-blur border-2 border-cyan-900 px-3 py-2 mb-2 font-hud text-xs sm:text-sm text-white rounded-xl shadow-lg">
    <div class="text-center">
      <div class="text-cyan-400 mb-0.5 text-[9px]">SCORE</div>
      <div id="hud-score" class="text-white font-bold">000000</div>
    </div>
    <div class="text-center">
      <div class="text-cyan-400 mb-0.5 text-[9px]">CRYSTALS</div>
      <div id="hud-coins" class="text-cyan-300 font-bold">💎 x0</div>
    </div>
    <div class="text-center">
      <div class="text-cyan-400 mb-0.5 text-[9px]">SECTOR</div>
      <div id="hud-world" class="text-amber-300 font-bold">P-1</div>
    </div>
    <div class="text-center">
      <div class="text-cyan-400 mb-0.5 text-[9px]">ENERGY</div>
      <div id="hud-quest" class="text-emerald-400 font-bold">0/5</div>
    </div>
    <div class="text-center">
      <div class="text-cyan-400 mb-0.5 text-[9px]">OXYGEN</div>
      <div id="hud-lives" class="text-rose-500 font-bold text-sm">❤️❤️❤️❤️❤️</div>
    </div>
    <button id="btn-toggle-sound" class="p-1.5 bg-slate-800 hover:bg-slate-700 rounded border border-slate-700 text-xs font-body">🔊</button>
  </header>

  <!-- MÀN HÌNH GAME CANVAS -->
  <main id="game-arena" class="relative w-full max-w-3xl aspect-[16/9] bg-[#030712] rounded-2xl border-4 border-slate-800 shadow-2xl overflow-hidden">
    <canvas id="gameCanvas" width="900" height="506" class="w-full h-full block"></canvas>
  </main>

  <!-- NÚT ĐIỀU KHIỂN CẢM ỨNG DI ĐỘNG -->
  <div id="touch-pad" class="w-full max-w-3xl flex items-center justify-between mt-3 px-1">
    <div class="flex items-center gap-3">
      <button id="pad-left" class="pad-btn w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-slate-800/90 border-4 border-cyan-400 text-4xl text-white shadow-lg transition-transform">◀</button>
      <button id="pad-jump" class="pad-btn w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-gradient-to-br from-cyan-600 to-indigo-600 border-4 border-cyan-300 font-extrabold text-base sm:text-lg leading-tight text-white shadow-lg transition-transform">JETPACK<br>⤴</button>
    </div>
    <button id="pad-right" class="pad-btn w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-slate-800/90 border-4 border-cyan-400 text-4xl text-white shadow-lg transition-transform">▶</button>
  </div>

  <!-- MODAL CÂU HỎI -->
  <div id="quiz-modal" class="fixed inset-0 z-50 bg-[#030712]/90 backdrop-blur-sm flex items-center justify-center p-3 hidden">
    <div class="bg-slate-900 border-2 border-cyan-400/90 rounded-2xl max-w-xl w-full p-4 shadow-2xl flex flex-col max-h-[92vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
        <span id="quiz-level-badge" class="px-2.5 py-1 bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 rounded-lg text-xs font-bold uppercase">🛸 HẠM ĐỘI UFO (15s)</span>
        <div class="flex items-center space-x-1.5 font-hud text-xs text-amber-400">
          <span>⏳</span><span id="quiz-timer-text">15s</span>
        </div>
      </div>

      <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-3">
        <div id="timer-bar" class="h-full bg-cyan-400 transition-all duration-100 ease-linear" style="width: 100%;"></div>
      </div>

      <div id="quiz-question-text" class="text-sm font-bold text-amber-200 mb-3 leading-relaxed">Đề bài...</div>
      <div id="quiz-options-container" class="space-y-2 mb-2"></div>

      <div id="quiz-short-container" class="space-y-2 mb-2 hidden">
        <input type="text" id="quiz-short-input" placeholder="Nhập đáp số hoặc kết quả tính toán..." autocomplete="off" class="w-full bg-slate-800 border-2 border-cyan-500/60 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-400">
        <button id="quiz-short-submit" class="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-xs rounded-xl shadow-md transition">BẮN TIA NĂNG LƯỢNG (ENTER)</button>
      </div>

      <div id="quiz-feedback" class="mt-2 text-xs font-semibold min-h-[20px]"></div>
    </div>
  </div>

  <!-- MODAL HOÀN THÀNH ẢI -->
  <div id="stage-clear-modal" class="fixed inset-0 z-50 bg-[#030712]/90 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto hidden">
    <div class="bg-slate-900 border-2 border-emerald-400 rounded-2xl max-w-md w-full p-6 text-center shadow-2xl">
      <div class="text-4xl mb-2">🌌✨</div>
      <h3 id="stage-clear-title" class="text-base font-extrabold text-emerald-400 mb-1">VƯỢT ẢI THÀNH CÔNG!</h3>
      <p class="text-xs text-amber-400 font-bold mb-3">LỜI DẶN DÒ TỪ CÔ MAI PHƯƠNG</p>
      <div id="stage-clear-msg" class="bg-slate-800/80 border border-slate-700 rounded-xl p-3.5 text-xs text-slate-200 text-left mb-5 leading-relaxed"></div>
      <button id="btn-continue-next-stage" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl transition shadow-lg">TIẾP TỤC TIẾN LÊN ẢI TIẾP THEO ⏩</button>
    </div>
  </div>

  <!-- MODAL TỔNG KẾT CHIẾN THẮNG -->
  <div id="summary-modal" class="fixed inset-0 z-50 bg-[#030712]/95 backdrop-blur-md flex items-center justify-center p-3 hidden">
    <div class="bg-slate-900 border-2 border-amber-400 rounded-2xl max-w-md w-full p-5 shadow-2xl flex flex-col max-h-[92vh] overflow-y-auto">
      <div class="text-center mb-3">
        <span class="text-4xl">🇻🇳👑</span>
        <h2 id="summary-title" class="text-lg font-extrabold text-amber-400 mt-1">VINH DANH CHIẾN THẮNG!</h2>
        <p id="summary-subtitle" class="text-[11px] text-cyan-400 font-semibold">Đã cắm cờ Việt Nam lên Mặt Trăng & Trở về Trái Đất an toàn!</p>
      </div>

      <div class="bg-slate-800/80 border border-slate-700 rounded-xl p-3 mb-3 grid grid-cols-2 gap-2 text-xs">
        <div><span class="text-slate-400">Học sinh:</span> <b id="sum-name" class="text-white">...</b></div>
        <div><span class="text-slate-400">Lớp:</span> <b id="sum-class" class="text-white">...</b></div>
        <div><span class="text-slate-400">Mã đề:</span> <b id="sum-examcode" class="text-amber-300">...</b></div>
        <div><span class="text-slate-400">Tổng điểm:</span> <b id="sum-score" class="text-amber-400 font-hud">0</b></div>
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

    // ===== HỆ THỐNG ÂM THANH KHÔNG GIAN =====
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

    function sndJump() {
      if (isSoundMuted) return;
      if (audioCtx.state === 'suspended') audioCtx.resume();
      try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(160, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(580, audioCtx.currentTime + 0.18);
        gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.18);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.18);
      } catch(e) {}
    }

    function sndCrystal() {
      playTone(1046.5, 'sine', 0.08, 0.15);
      setTimeout(() => playTone(1318.5, 'sine', 0.1, 0.14), 60);
      setTimeout(() => playTone(2093.0, 'sine', 0.22, 0.16), 120);
    }

    function sndOxygen() {
      playTone(440, 'triangle', 0.12, 0.15);
      setTimeout(() => playTone(659.25, 'triangle', 0.12, 0.15), 80);
      setTimeout(() => playTone(880, 'sine', 0.22, 0.16), 160);
    }

    function sndMeteorImpact() {
      playTone(180, 'sawtooth', 0.2, 0.25);
      setTimeout(() => playTone(85, 'square', 0.35, 0.25), 80);
    }

    function sndWrong() {
      playTone(220, 'sawtooth', 0.2, 0.2);
      setTimeout(() => playTone(140, 'sawtooth', 0.3, 0.2), 120);
    }

    function sndBossRoar() {
      playTone(95, 'sawtooth', 0.5, 0.3);
      setTimeout(() => playTone(65, 'sawtooth', 0.6, 0.3), 150);
    }

    function sndBump() { playTone(130, 'square', 0.08, 0.12); }
    function sndVictoryFanfare() {
      const notes = [523.25, 659.25, 783.99, 1046.5];
      notes.forEach((f, i) => setTimeout(() => playTone(f, 'triangle', 0.35, 0.2), i * 150));
    }

    let bgmInterval = null;
    const ufoNotes = [330, 392, 493.88, 587.33, 523.25, 392, 440, 293.66];
    let noteIdx = 0;
    function startBgm() {
      if (bgmInterval || isSoundMuted) return;
      bgmInterval = setInterval(() => {
        if (gameState.started && !gameState.isPaused && !gameState.isGameOver && !endingCutscene.active) {
          playTone(ufoNotes[noteIdx], 'sine', 0.28, 0.035);
        }
        noteIdx = (noteIdx + 1) % ufoNotes.length;
      }, 300);
    }
    function stopBgm() { if (bgmInterval) { clearInterval(bgmInterval); bgmInterval = null; } }

    document.getElementById("btn-toggle-sound").onclick = (e) => {
      isSoundMuted = !isSoundMuted;
      e.currentTarget.textContent = isSoundMuted ? "🔇" : "🔊";
      e.currentTarget.blur();
      if (isSoundMuted) stopBgm(); else startBgm();
    };

    // ===== NGÂN HÀNG CÂU HỎI TỨ GIÁC =====
    const rawQuestionPool = {
      stage1: [
        { level: "Nhận biết", time: 15, type: "short", q: "Tổng các góc trong một tứ giác lồi luôn bằng bao nhiêu độ? (Chỉ nhập số)", correctAnswers: ["360"], explain: "Định lý: Tổng các góc của một tứ giác luôn bằng 360 độ." },
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác luôn nằm trong một nửa mặt phẳng có bờ là đường thẳng chứa bất kì cạnh nào gọi là tứ giác gì?", correctAnswers: ["lồi", "tứ giác lồi"], explain: "Định nghĩa: Đó là tứ giác lồi." },
        { level: "Nhận biết", time: 15, type: "short", q: "Một tứ giác lồi có tổng cộng bao nhiêu đường chéo? (Chỉ nhập số)", correctAnswers: ["2"], explain: "Mỗi tứ giác lồi có đúng 2 đường chéo nối các đỉnh đối nhau." },
        { level: "Thông hiểu", time: 20, type: "short", q: "Tứ giác có bốn góc bằng nhau thì mỗi góc bằng bao nhiêu độ? (Nhập số)", correctAnswers: ["90"], explain: "Mỗi góc = 360° : 4 = 90°." },
        { level: "Vận dụng", time: 30, type: "short", q: "Tứ giác ABCD có góc A = 70°, B = 90°, C = 80°. Tính số đo góc D bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["120"], explain: "Góc D = 360° - (70° + 90° + 80°) = 120°." }
      ],
      stage2: [
        { level: "Nhận biết", time: 15, type: "short", q: "Hình thang có hai góc kề một đáy bằng nhau là hình thang gì?", correctAnswers: ["cân", "hình thang cân"], explain: "Định nghĩa: Hình thang có 2 góc kề một đáy bằng nhau là hình thang cân." },
        { level: "Nhận biết", time: 15, type: "mcq", q: "Trong hình thang cân, hai đường chéo có mối quan hệ gì với nhau?", answers: ["Bằng nhau", "Vuông góc với nhau", "Cắt nhau tại trung điểm mỗi đường"], correct: 0, explain: "Tính chất: Trong hình thang cân, hai đường chéo bằng nhau." },
        { level: "Thông hiểu", time: 20, type: "short", q: "Hình thang có hai đường chéo bằng nhau là hình thang gì?", correctAnswers: ["cân", "hình thang cân"], explain: "Dấu hiệu nhận biết: Hình thang có 2 đường chéo bằng nhau là hình thang cân." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình thang cân ABCD (AB // CD) có góc D = 70°. Tính số đo góc A kề cạnh bên AD: (Nhập số)", correctAnswers: ["110"], explain: "Góc A = 180° - 70° = 110°." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình thang có một góc vuông được gọi là hình gì?", answers: ["Hình thang vuông", "Hình thang cân", "Hình chữ nhật"], correct: 0, explain: "Định nghĩa: Hình thang có một góc vuông là hình thang vuông." }
      ],
      stage3: [
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có các cạnh đối song song được gọi là hình gì?", correctAnswers: ["hình bình hành", "bình hành"], explain: "Định nghĩa: Hình bình hành là tứ giác có các cạnh đối song song." },
        { level: "Nhận biết", time: 15, type: "mcq", q: "Trong hình bình hành, hai đường chéo có tính chất gì?", answers: ["Cắt nhau tại trung điểm của mỗi đường", "Vuông góc với nhau", "Bằng nhau"], correct: 0, explain: "Tính chất: Hai đường chéo cắt nhau tại trung điểm của mỗi đường." },
        { level: "Thông hiểu", time: 20, type: "short", q: "Tứ giác có hai đường chéo cắt nhau tại trung điểm mỗi đường là hình gì?", correctAnswers: ["hình bình hành", "bình hành"], explain: "Dấu hiệu nhận biết hình bình hành." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình bình hành ABCD có góc A = 115°. Tính số đo góc đối C bằng bao nhiêu độ? (Nhập số):", correctAnswers: ["115"], explain: "Hai góc đối hình bình hành bằng nhau: C = A = 115°." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình thang có hai cạnh bên song song là hình gì?", answers: ["Hình bình hành", "Hình thang cân", "Hình chữ nhật"], correct: 0, explain: "Hình thang có 2 cạnh bên song song là hình bình hành." }
      ],
      stage4: [
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có bốn góc vuông được gọi là hình gì?", correctAnswers: ["hình chữ nhật", "chữ nhật"], explain: "Định nghĩa: Hình chữ nhật là tứ giác có bốn góc vuông." },
        { level: "Thông hiểu", time: 20, type: "short", q: "Hình bình hành có hai đường chéo bằng nhau là hình gì?", correctAnswers: ["hình chữ nhật", "chữ nhật"], explain: "Dấu hiệu nhận biết hình chữ nhật." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình chữ nhật có hai cạnh dài 6 cm và 8 cm. Đường chéo dài bao nhiêu cm? (Nhập số):", correctAnswers: ["10"], explain: "Pythagore: d² = 6² + 8² = 100 => d = 10 cm." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình bình hành có một góc vuông là hình gì?", answers: ["Hình chữ nhật", "Hình thoi", "Hình thang cân"], correct: 0, explain: "Dấu hiệu nhận biết: Hình bình hành có 1 góc vuông là hình chữ nhật." },
        { level: "Nhận biết", time: 15, type: "short", q: "Hình chữ nhật có tất cả bao nhiêu trục đối xứng? (Nhập số)", correctAnswers: ["2"], explain: "Hình chữ nhật có 2 trục đối xứng." }
      ],
      stage5: [
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác có bốn cạnh bằng nhau được gọi là hình gì?", correctAnswers: ["hình thoi", "thoi"], explain: "Định nghĩa: Hình thoi là tứ giác có bốn cạnh bằng nhau." },
        { level: "Nhận biết", time: 15, type: "short", q: "Tứ giác vừa là hình chữ nhật vừa là hình thoi là hình gì?", correctAnswers: ["hình vuông", "vuông"], explain: "Định nghĩa: Hình vuông là hình chữ nhật đồng thời là hình thoi." },
        { level: "Thông hiểu", time: 20, type: "mcq", q: "Hình thoi có một góc vuông là hình gì?", answers: ["Hình vuông", "Hình chữ nhật không vuông", "Hình thang cân"], correct: 0, explain: "Dấu hiệu: Hình thoi có một góc vuông là hình vuông." },
        { level: "Vận dụng", time: 30, type: "short", q: "Một hình thoi có chu vi bằng 52 cm. Độ dài một cạnh bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["13"], explain: "Cạnh = 52 / 4 = 13 cm." },
        { level: "Vận dụng", time: 30, type: "short", q: "Hình vuông có cạnh 5 cm. Chu vi hình vuông bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["20"], explain: "Chu vi = 4 · 5 = 20 cm." }
      ],
      boss: [
        { level: "Vận dụng cao", time: 30, type: "mcq", q: "[QUÁI THÚ TỨ GIÁC] Nối trung điểm 4 cạnh của một hình chữ nhật ta luôn nhận được hình gì?", answers: ["Hình thoi", "Hình bình hành thông thường", "Hình vuông"], correct: 0, explain: "Bốn cạnh bằng nhau vì bằng nửa đường chéo hình chữ nhật => Hình thoi." },
        { level: "Vận dụng cao", time: 30, type: "mcq", q: "[QUÁI THÚ TỨ GIÁC] Nối trung điểm 4 cạnh của một hình thoi ta luôn nhận được hình gì?", answers: ["Hình chữ nhật", "Hình vuông", "Hình bình hành có góc 60°"], correct: 0, explain: "Hai đường chéo hình thoi vuông góc nên các cạnh vuông góc với nhau => Hình chữ nhật." },
        { level: "Vận dụng cao", time: 30, type: "short", q: "[QUÁI THÚ TỨ GIÁC] Hình thoi ABCD có cạnh 10 cm và góc A = 60°. Độ dài đường chéo BD bằng bao nhiêu cm? (Nhập số):", correctAnswers: ["10"], explain: "Tam giác ABD cân có góc 60° nên là tam giác đều => BD = 10 cm." },
        { level: "Vận dụng cao", time: 30, type: "short", q: "[QUÁI THÚ TỨ GIÁC] Hình vuông có đường chéo dài 8 cm. Diện tích hình vuông bằng bao nhiêu cm²? (Nhập số):", correctAnswers: ["32"], explain: "Diện tích = (8 · 8) : 2 = 32 cm²." }
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

    function prepareQuestion(q) {
      if (q.type !== "mcq") return { ...q };
      const order = shuffle(q.answers.map((_, i) => i));
      return { ...q, answers: order.map(i => q.answers[i]), correct: order.indexOf(q.correct) };
    }

    function pickStageQuestions(pool) {
      return shuffle(pool).slice(0, 5).map(prepareQuestion);
    }

    function buildExam() {
      return {
        code: "CMP-8A-" + Math.floor(1000 + Math.random() * 9000),
        stages: [
          { name: "Ải 1: Tinh Vân Tứ Giác Lồi", questions: pickStageQuestions(rawQuestionPool.stage1), bg: "#04081c", ground: "#1e293b", groundLine: "#38bdf8", moonColor: "#e2e8f0" },
          { name: "Ải 2: Vành Đai Hình Thang Cân", questions: pickStageQuestions(rawQuestionPool.stage2), bg: "#1e0b2e", ground: "#3b1754", groundLine: "#c084fc", moonColor: "#f3e8ff" },
          { name: "Ải 3: Quỹ Đạo Hình Bình Hành", questions: pickStageQuestions(rawQuestionPool.stage3), bg: "#022226", ground: "#0f4249", groundLine: "#2dd4bf", moonColor: "#ccfbf1" },
          { name: "Ải 4: Hành Tinh Hình Chữ Nhật", questions: pickStageQuestions(rawQuestionPool.stage4), bg: "#0a1945", ground: "#1b2c6b", groundLine: "#60a5fa", moonColor: "#dbeafe" },
          { name: "Ải 5: Đại Chiến Quái Thú Tứ Giác", questions: pickStageQuestions(rawQuestionPool.stage5), bg: "#2d0614", ground: "#540d27", groundLine: "#f43f5e", moonColor: "#ffe4e6" }
        ],
        bossQuestions: shuffle(rawQuestionPool.boss).map(prepareQuestion)
      };
    }

    function normalizeAnswer(s) {
      return String(s).normalize("NFC").toLowerCase().replace(/°|độ|cm²|cm2|cm/g, "").replace(/\\s+/g, " ").trim();
    }

    // ===== TRẠNG THÁI GAME =====
    const gameState = {
      started: false, studentName: "", studentClass: "", examData: null,
      currentStageIdx: 0, currentQuestionIdx: 0, inBossFight: false,
      bossHp: 3, bossMaxHp: 3, bossQIdx: 0, score: 0, coins: 0, lives: 5,
      isPaused: true, isGameOver: false, defeatedBoss: false, answerLocked: true,
      timerSec: 15, timerMax: 15, timerInterval: null
    };

    const endingCutscene = {
      active: false,
      step: 0,
      timer: 0,
      shipX: 520,
      shipY: 340,
      shipVy: 0,
      flagPlanted: false,
      earthX: 720,
      earthY: 100
    };

    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const arenaEl = document.getElementById("game-arena");

    const WORLD_W = 3000;
    const GROUND_TOP = 406;
    const ASTRONAUT_W = 44, ASTRONAUT_H = 60;
    const GROUND_Y = GROUND_TOP - ASTRONAUT_H;
    const UFO_W = 72, UFO_H = 46;
    const UFO_Y = 220;
    const MAX_LIVES = 9;
    const BOSS_X = 1200, BOSS_Y = 220;
    const STAGE_PITS = [ { start: 1140, width: 85 }, { start: 2200, width: 95 } ];

    const astronaut = {
      x: 100, y: GROUND_Y, w: ASTRONAUT_W, h: ASTRONAUT_H,
      vx: 0, vy: 0, isJumping: false, falling: false, fallPit: null,
      facing: 1, runFrame: 0, speed: 4.8
    };

    let cameraX = 0;
    let animTick = 0;
    const keys = { left: false, right: false };

    let ufoFleet = [];
    let groundPits = [];
    let popItems = [];
    const laserShot = { active: false, x: 0, y: 0, vx: 0 };
    let bossFlash = 0;

    function initLevelBoxes() {
      const symbols = ["Δ", "π", "√x", "Δ", "π", "√x", "Δ", "π", "√x", "Δ", "π", "√x", "Δ", "π"];
      const blockConfigs = [
        { x: 300,  type: 'quiz' },
        { x: 470,  type: 'oxygen' },
        { x: 640,  type: 'crystal' },
        { x: 810,  type: 'quiz' },
        { x: 980,  type: 'oxygen' },
        { x: 1350, type: 'quiz' },
        { x: 1520, type: 'meteor' },
        { x: 1690, type: 'oxygen' },
        { x: 1870, type: 'quiz' },
        { x: 2040, type: 'crystal' },
        { x: 2420, type: 'oxygen' },
        { x: 2580, type: 'meteor' },
        { x: 2740, type: 'quiz' },
        { x: 2890, type: 'oxygen' }
      ];

      ufoFleet = blockConfigs.map((b, idx) => ({
        ...b,
        baseY: UFO_Y,
        y: UFO_Y,
        w: UFO_W,
        h: UFO_H,
        symbol: symbols[idx % symbols.length],
        active: true,
        bump: 0,
        floatSeed: idx * 1.5
      }));

      groundPits = STAGE_PITS.map(p => ({ ...p }));
      popItems = [];
    }

    function resetAstronaut(x) {
      astronaut.x = x; astronaut.y = GROUND_Y; astronaut.vy = 0;
      astronaut.isJumping = false; astronaut.falling = false; astronaut.fallPit = null; astronaut.facing = 1;
      keys.left = keys.right = false;
    }

    function updateHud() {
      document.getElementById("hud-score").textContent = String(gameState.score).padStart(6, '0');
      document.getElementById("hud-coins").textContent = "💎 x" + gameState.coins;
      document.getElementById("hud-lives").textContent = gameState.lives > 0 ? "❤️x" + gameState.lives : "💀";
    }

    function isTyping(e) {
      const t = e.target;
      return t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
    }

    window.addEventListener('keydown', (e) => {
      if (isTyping(e) || endingCutscene.active) return;
      if (e.code === 'ArrowLeft' || e.code === 'KeyA') keys.left = true;
      if (e.code === 'ArrowRight' || e.code === 'KeyD') keys.right = true;
      if (e.code === 'Space' || e.code === 'ArrowUp') {
        e.preventDefault();
        doJump();
      }
    });

    function doJump() {
      if (!astronaut.isJumping && !astronaut.falling && !gameState.isPaused && !gameState.isGameOver && !endingCutscene.active) {
        astronaut.isJumping = true;
        astronaut.vy = -14;
        sndJump();
      }
    }

    window.addEventListener('keyup', (e) => {
      if (e.code === 'ArrowLeft' || e.code === 'KeyA') keys.left = false;
      if (e.code === 'ArrowRight' || e.code === 'KeyD') keys.right = false;
    });

    function bindHoldButton(id, key) {
      const btn = document.getElementById(id);
      if (!btn) return;
      const press = (e) => {
        e.preventDefault();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        if (endingCutscene.active) return;
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

    function findPitUnderAstronaut() {
      const cx = astronaut.x + astronaut.w / 2;
      return groundPits.find(p => cx > p.start + 6 && cx < p.start + p.width - 6) || null;
    }

    function spawnPopItem(ufo, kind, label, color) {
      popItems.push({ kind, label, color, x: ufo.x + ufo.w / 2, baseY: ufo.y, rise: 0, life: 90 });
    }

    // XỬ LÝ HÚC TRÚNG UFO: ĐÃ SỬA TRIỆT ĐỂ LỖI KẸT ĐỨNG HÌNH
    function hitUFO(ufo) {
      ufo.active = false;
      ufo.bump = 10;
      // Đẩy phi hành gia bắt đầu rơi xuống đất ngay lập tức, không cho kẹt lơ lửng
      astronaut.vy = 3.5;

      if (ufo.type === 'crystal') {
        sndCrystal();
        gameState.coins += 2;
        gameState.score += 200;
        spawnPopItem(ufo, 'crystal', "+200", "#38bdf8");
        updateHud();
      } else if (ufo.type === 'oxygen') {
        sndOxygen();
        gameState.lives = Math.min(MAX_LIVES, gameState.lives + 1);
        spawnPopItem(ufo, 'oxygen', "+1 MẠNG", "#4ade80");
        updateHud();
      } else if (ufo.type === 'meteor') {
        sndMeteorImpact();
        triggerShake();
        gameState.score = Math.max(0, gameState.score - 200);
        spawnPopItem(ufo, 'meteor', "-1 MẠNG", "#f87171");
        loseLife();
      } else {
        openNextQuestion();
      }
    }

    // VA CHẠM VỚI UFO: CHỈ BẮT KHI UFO ĐANG ACTIVE
    function checkUFOBump() {
      for (const ufo of ufoFleet) {
        if (!ufo.active) continue; // Bỏ qua nếu UFO này đã mở rồi -> Tránh đứng hình!

        const overlapX = astronaut.x + astronaut.w - 6 > ufo.x && astronaut.x + 6 < ufo.x + ufo.w;
        const headHit = astronaut.y <= ufo.y + ufo.h && astronaut.y > ufo.y + ufo.h - 22;
        
        if (overlapX && headHit && astronaut.vy < 0) {
          astronaut.y = ufo.y + ufo.h;
          hitUFO(ufo);
          return;
        }
      }
    }

    function step() {
      if (!gameState.started || gameState.isGameOver) return;
      animTick++;

      if (endingCutscene.active) {
        endingCutscene.timer++;
        if (endingCutscene.step === 0) {
          if (astronaut.x < 360) {
            astronaut.x += 2;
            astronaut.runFrame += 0.25;
          } else {
            endingCutscene.flagPlanted = true;
            sndVictoryFanfare();
            endingCutscene.step = 1;
            endingCutscene.timer = 0;
          }
        } else if (endingCutscene.step === 1) {
          if (endingCutscene.timer > 80) {
            endingCutscene.step = 2;
          }
        } else if (endingCutscene.step === 2) {
          if (astronaut.x < endingCutscene.shipX + 10) {
            astronaut.x += 2.5;
            astronaut.runFrame += 0.25;
          } else {
            endingCutscene.step = 3;
            endingCutscene.timer = 0;
          }
        } else if (endingCutscene.step === 3) {
          endingCutscene.shipVy -= 0.15;
          endingCutscene.shipY += endingCutscene.shipVy;
          endingCutscene.shipX += 1.6;
          if (endingCutscene.shipY < -100) {
            endingCutscene.active = false;
            finishGameSession(true);
          }
        }
        return;
      }

      const active = !gameState.isPaused;

      if (active && !astronaut.falling) {
        if (keys.left)  { astronaut.x = Math.max(30, astronaut.x - astronaut.speed); astronaut.facing = -1; astronaut.runFrame += 0.25; }
        if (keys.right) { astronaut.x = Math.min(WORLD_W - 60, astronaut.x + astronaut.speed); astronaut.facing = 1; astronaut.runFrame += 0.25; }
        cameraX = Math.max(0, Math.min(WORLD_W - canvas.width, astronaut.x - 300));
      }

      if (astronaut.falling) {
        astronaut.y += 7;
        if (astronaut.y > canvas.height + 20) {
          sndMeteorImpact();
          triggerShake();
          const pit = astronaut.fallPit;
          loseLife();
          if (!gameState.isGameOver) resetAstronaut(Math.max(60, pit.start - 90));
        }
      } else if (astronaut.isJumping) {
        astronaut.y += astronaut.vy;
        astronaut.vy += 0.8;
        if (active && astronaut.vy < 0 && !gameState.inBossFight) checkUFOBump();
        if (astronaut.y >= GROUND_Y) { astronaut.y = GROUND_Y; astronaut.vy = 0; astronaut.isJumping = false; }
      }

      if (active && !astronaut.isJumping && !astronaut.falling) {
        const pit = findPitUnderAstronaut();
        if (pit) { astronaut.falling = true; astronaut.fallPit = pit; }
      }

      ufoFleet.forEach(ufo => {
        ufo.y = ufo.baseY + Math.sin(animTick * 0.05 + ufo.floatSeed) * 7;
        if (ufo.bump > 0) ufo.bump--;
      });

      popItems.forEach(p => { if (p.rise < 46) p.rise += 2.5; p.life--; });
      popItems = popItems.filter(p => p.life > 0);

      if (laserShot.active) {
        laserShot.x += laserShot.vx;
        if (laserShot.x >= BOSS_X + 40) {
          laserShot.active = false;
          bossFlash = 18;
          sndMeteorImpact();
          triggerShake();
        }
      }
      if (bossFlash > 0) bossFlash--;
    }

    // ===== HỆ THỐNG VẼ ĐỒ HỌA =====
    function drawPixelAstronaut() {
      ctx.save();
      ctx.translate(astronaut.x, astronaut.y);
      if (astronaut.facing < 0) { ctx.translate(astronaut.w, 0); ctx.scale(-1, 1); }

      ctx.save();
      ctx.translate(astronaut.w / 2, astronaut.h / 2);

      // Ba lô phản lực Jetpack
      ctx.fillStyle = "#475569";
      ctx.fillRect(-22, -18, 9, 32);
      ctx.fillStyle = "#06b6d4";
      ctx.fillRect(-21, -12, 7, 8);

      // Ngọn lửa Jetpack
      if (astronaut.isJumping || endingCutscene.step === 3) {
        const flameH = 14 + (animTick % 3) * 4;
        ctx.fillStyle = "#f97316";
        ctx.beginPath();
        ctx.moveTo(-21, 14); ctx.lineTo(-13, 14); ctx.lineTo(-17, 14 + flameH);
        ctx.closePath(); ctx.fill();

        ctx.fillStyle = "#fef08a";
        ctx.beginPath();
        ctx.moveTo(-19, 14); ctx.lineTo(-15, 14); ctx.lineTo(-17, 14 + flameH * 0.6);
        ctx.closePath(); ctx.fill();
      }

      // Tay sau
      const armSwing = (!astronaut.isJumping && (keys.left || keys.right)) ? Math.sin(astronaut.runFrame) * 8 : 0;
      ctx.fillStyle = "#cbd5e1";
      ctx.beginPath();
      ctx.roundRect(-8 - armSwing, -6, 7, 18, 3);
      ctx.fill();
      ctx.fillStyle = "#06b6d4";
      ctx.fillRect(-8 - armSwing, 8, 7, 5);

      // Hai chân
      const legRun = (!astronaut.isJumping && (keys.left || keys.right)) ? Math.sin(astronaut.runFrame) * 6 : 0;
      ctx.fillStyle = "#e2e8f0";
      ctx.fillRect(-8 - legRun, 12, 7, 12);
      ctx.fillStyle = "#0284c7";
      ctx.fillRect(-8 - legRun, 22, 10, 5);

      ctx.fillStyle = "#f8fafc";
      ctx.fillRect(2 + legRun, 12, 7, 12);
      ctx.fillStyle = "#0ea5e9";
      ctx.fillRect(2 + legRun, 22, 10, 5);

      // Thân áo
      ctx.fillStyle = "#f1f5f9";
      ctx.beginPath();
      ctx.roundRect(-14, -12, 26, 26, 6);
      ctx.fill();
      ctx.strokeStyle = "#cbd5e1";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Bảng vi mạch
      ctx.fillStyle = "#0f172a";
      ctx.fillRect(-5, -6, 12, 9);
      ctx.fillStyle = (animTick % 30 < 15) ? "#22c55e" : "#10b981";
      ctx.fillRect(-3, -4, 3, 3);
      ctx.fillStyle = "#ef4444";
      ctx.fillRect(2, -4, 3, 3);

      // Tay trước
      if (endingCutscene.step === 1) {
        ctx.fillStyle = "#f8fafc";
        ctx.beginPath(); ctx.roundRect(4, -18, 7, 18, 3); ctx.fill();
        ctx.fillStyle = "#06b6d4"; ctx.fillRect(4, -22, 7, 5);
      } else {
        ctx.fillStyle = "#f8fafc";
        ctx.beginPath();
        ctx.roundRect(2 + armSwing, -6, 7, 18, 3);
        ctx.fill();
        ctx.fillStyle = "#06b6d4";
        ctx.fillRect(2 + armSwing, 8, 7, 5);
      }

      // Mũ bảo hộ
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.arc(0, -18, 14, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "#cbd5e1";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Kính Visor
      const visorGrad = ctx.createLinearGradient(0, -25, 10, -11);
      visorGrad.addColorStop(0, "#fde047");
      visorGrad.addColorStop(0.5, "#eab308");
      visorGrad.addColorStop(1, "#ca8a04");
      ctx.fillStyle = visorGrad;
      ctx.beginPath();
      ctx.roundRect(0, -24, 11, 12, 4);
      ctx.fill();

      ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
      ctx.fillRect(3, -22, 3, 3);

      ctx.restore();
      ctx.restore();
    }

    function drawUFOBlock(ufo) {
      const by = ufo.y - (ufo.bump > 0 ? Math.sin((ufo.bump / 10) * Math.PI) * 12 : 0);
      ctx.save();
      ctx.translate(ufo.x + ufo.w / 2, by + ufo.h / 2);

      if (ufo.active) {
        const beamGrad = ctx.createLinearGradient(0, 0, 0, 80);
        beamGrad.addColorStop(0, "rgba(56, 189, 248, 0.4)");
        beamGrad.addColorStop(1, "rgba(56, 189, 248, 0.0)");
        ctx.fillStyle = beamGrad;
        ctx.beginPath();
        ctx.moveTo(-16, 8); ctx.lineTo(16, 8); ctx.lineTo(34, 80); ctx.lineTo(-34, 80);
        ctx.closePath(); ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(0, -6, 20, Math.PI, 0);
      if (ufo.active) {
        const domeGrad = ctx.createRadialGradient(0, -10, 2, 0, -6, 20);
        domeGrad.addColorStop(0, "#ffffff");
        domeGrad.addColorStop(0.5, "#38bdf8");
        domeGrad.addColorStop(1, "#0369a1");
        ctx.fillStyle = domeGrad;
      } else {
        ctx.fillStyle = "rgba(71, 85, 105, 0.8)";
      }
      ctx.fill();
      ctx.strokeStyle = ufo.active ? "#a5f3fc" : "#475569";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = ufo.active ? "#ffffff" : "#94a3b8";
      ctx.font = "800 16px 'Plus Jakarta Sans'";
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillText(ufo.symbol, 0, -8);

      ctx.beginPath();
      ctx.ellipse(0, 4, 34, 11, 0, 0, Math.PI * 2);
      if (ufo.active) {
        const saucerGrad = ctx.createLinearGradient(0, -6, 0, 14);
        saucerGrad.addColorStop(0, "#f8fafc");
        saucerGrad.addColorStop(0.5, "#94a3b8");
        saucerGrad.addColorStop(1, "#475569");
        ctx.fillStyle = saucerGrad;
      } else {
        ctx.fillStyle = "#334155";
      }
      ctx.fill();
      ctx.strokeStyle = ufo.active ? "#38bdf8" : "#1e293b";
      ctx.lineWidth = 2;
      ctx.stroke();

      const lightXs = [-24, -12, 0, 12, 24];
      lightXs.forEach((lx, idx) => {
        ctx.beginPath();
        ctx.arc(lx, 4.5, 2.5, 0, Math.PI * 2);
        if (ufo.active) {
          const activeIdx = Math.floor((animTick / 8) % lightXs.length);
          ctx.fillStyle = (idx === activeIdx) ? "#facc15" : (idx % 2 === 0 ? "#4ade80" : "#f43f5e");
        } else {
          ctx.fillStyle = "#0f172a";
        }
        ctx.fill();
      });

      ctx.restore();
    }

    function drawDetailedMoon(x, y, r, moonColor) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      const moonGrad = ctx.createRadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r);
      moonGrad.addColorStop(0, moonColor || "#f8fafc");
      moonGrad.addColorStop(0.8, "#cbd5e1");
      moonGrad.addColorStop(1, "#94a3b8");
      ctx.fillStyle = moonGrad;
      ctx.fill();
      ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
      ctx.lineWidth = 3;
      ctx.stroke();

      const craters = [
        { dx: -25, dy: -20, cr: 14 },
        { dx: 18, dy: -15, cr: 10 },
        { dx: -10, dy: 24, cr: 16 },
        { dx: 28, dy: 18, cr: 12 },
        { dx: -35, dy: 10, cr: 8 },
        { dx: 5, dy: -32, cr: 7 }
      ];

      craters.forEach(c => {
        ctx.beginPath();
        ctx.arc(x + c.dx, y + c.dy, c.cr, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(100, 116, 139, 0.35)";
        ctx.fill();
        ctx.strokeStyle = "rgba(71, 85, 105, 0.4)";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      });

      ctx.restore();
    }

    function drawVietnamFlag(x, y) {
      ctx.save();
      ctx.fillStyle = "#e2e8f0";
      ctx.fillRect(x, y - 70, 4, 70);
      ctx.fillStyle = "#cbd5e1";
      ctx.fillRect(x - 2, y - 2, 8, 4);

      const wave = Math.sin(animTick * 0.1) * 3;
      ctx.fillStyle = "#da251d";
      ctx.beginPath();
      ctx.moveTo(x + 4, y - 70);
      ctx.lineTo(x + 48, y - 70 + wave);
      ctx.lineTo(x + 48, y - 40 + wave);
      ctx.lineTo(x + 4, y - 40);
      ctx.closePath();
      ctx.fill();

      const starX = x + 26, starY = y - 55 + wave * 0.7;
      ctx.fillStyle = "#ffff00";
      ctx.beginPath();
      for (let i = 0; i < 5; i++) {
        const outerAngle = (i * 72 - 18) * Math.PI / 180;
        const innerAngle = (i * 72 + 18) * Math.PI / 180;
        const ox = starX + Math.cos(outerAngle) * 8;
        const oy = starY + Math.sin(outerAngle) * 8;
        const ix = starX + Math.cos(innerAngle) * 3.5;
        const iy = starY + Math.sin(innerAngle) * 3.5;
        if (i === 0) ctx.moveTo(ox, oy); else ctx.lineTo(ox, oy);
        ctx.lineTo(ix, iy);
      }
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    function drawSpaceship(x, y, vy) {
      ctx.save();
      ctx.translate(x, y);

      if (endingCutscene.step === 3) {
        const flameL = 25 + Math.random() * 15;
        ctx.fillStyle = "#f97316";
        ctx.beginPath();
        ctx.moveTo(-10, 25); ctx.lineTo(10, 25); ctx.lineTo(0, 25 + flameL);
        ctx.closePath(); ctx.fill();
        ctx.fillStyle = "#fef08a";
        ctx.beginPath();
        ctx.moveTo(-6, 25); ctx.lineTo(6, 25); ctx.lineTo(0, 25 + flameL * 0.6);
        ctx.closePath(); ctx.fill();
      }

      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.moveTo(0, -35);
      ctx.lineTo(16, 25);
      ctx.lineTo(-16, 25);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = "#cbd5e1";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = "#ef4444";
      ctx.beginPath();
      ctx.moveTo(-16, 10); ctx.lineTo(-28, 25); ctx.lineTo(-16, 25); ctx.closePath(); ctx.fill();
      ctx.beginPath();
      ctx.moveTo(16, 10); ctx.lineTo(28, 25); ctx.lineTo(16, 25); ctx.closePath(); ctx.fill();

      ctx.fillStyle = "#0284c7";
      ctx.beginPath();
      ctx.arc(0, -6, 6, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();
    }

    function drawEarth(x, y, r) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      const earthGrad = ctx.createRadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r);
      earthGrad.addColorStop(0, "#38bdf8");
      earthGrad.addColorStop(0.7, "#0284c7");
      earthGrad.addColorStop(1, "#0f172a");
      ctx.fillStyle = earthGrad;
      ctx.fill();

      ctx.fillStyle = "#22c55e";
      ctx.beginPath(); ctx.arc(x - 10, y - 8, 14, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(x + 12, y + 10, 16, 0, Math.PI * 2); ctx.fill();

      ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
      ctx.lineWidth = 4;
      ctx.stroke();
      ctx.restore();
    }

    function drawOxygenBottle(cx, bottom) {
      ctx.fillStyle = "#0284c7";
      ctx.fillRect(cx - 9, bottom - 26, 18, 24);
      ctx.strokeStyle = "#38bdf8"; ctx.lineWidth = 2; ctx.strokeRect(cx - 9, bottom - 26, 18, 24);
      ctx.fillStyle = "#38bdf8"; ctx.fillRect(cx - 5, bottom - 32, 10, 6);
      ctx.fillStyle = "#ffffff"; ctx.font = "bold 10px 'Plus Jakarta Sans'"; ctx.textAlign = "center";
      ctx.fillText("O2", cx, bottom - 10);
    }

    function drawMeteorItem(cx, bottom) {
      const cy = bottom - 16;
      ctx.fillStyle = "#78350f"; ctx.beginPath(); ctx.arc(cx, cy, 15, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#ea580c"; ctx.lineWidth = 2; ctx.stroke();
      ctx.fillStyle = (animTick % 6 < 3) ? "#facc15" : "#f97316"; ctx.beginPath(); ctx.arc(cx + 4, cy - 4, 5, 0, Math.PI * 2); ctx.fill();
    }

    function drawCrystalItem(cx, bottom) {
      const cy = bottom - 16;
      ctx.fillStyle = "#38bdf8"; ctx.beginPath();
      ctx.moveTo(cx, cy - 14); ctx.lineTo(cx + 10, cy); ctx.lineTo(cx, cy + 14); ctx.lineTo(cx - 10, cy); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = "#e0f2fe"; ctx.lineWidth = 1.5; ctx.stroke();
    }

    function drawPopItem(p) {
      const bottom = p.baseY - p.rise + 15;
      ctx.save();
      ctx.globalAlpha = Math.min(1, p.life / 20);
      if (p.kind === 'oxygen') drawOxygenBottle(p.x, bottom);
      else if (p.kind === 'meteor') drawMeteorItem(p.x, bottom);
      else if (p.kind === 'crystal') drawCrystalItem(p.x, bottom);
      ctx.restore();
    }

    function drawPopLabel(p) {
      const y = p.baseY - p.rise - 30;
      ctx.save();
      ctx.globalAlpha = Math.min(1, p.life / 20);
      ctx.font = "800 18px 'Plus Jakarta Sans', sans-serif";
      ctx.textAlign = "center"; ctx.lineWidth = 4; ctx.strokeStyle = "#000";
      ctx.strokeText(p.label, p.x, y); ctx.fillStyle = p.color; ctx.fillText(p.label, p.x, y);
      ctx.restore();
    }

    function drawGroundAndPits(stage) {
      ctx.fillStyle = stage ? stage.ground : "#1e293b";
      ctx.strokeStyle = "#000"; ctx.lineWidth = 3;
      const segments = [];
      let lastX = 0;
      groundPits.forEach(pit => { segments.push([lastX, pit.start]); lastX = pit.start + pit.width; });
      segments.push([lastX, WORLD_W]);

      segments.forEach(([a, b]) => {
        ctx.fillRect(a, GROUND_TOP, b - a, canvas.height - GROUND_TOP);
        ctx.fillStyle = stage ? stage.groundLine : "#38bdf8";
        ctx.fillRect(a, GROUND_TOP, b - a, 5);
        ctx.fillStyle = stage ? stage.ground : "#1e293b";
      });

      groundPits.forEach(pit => {
        ctx.fillStyle = "#000000";
        ctx.fillRect(pit.start, GROUND_TOP, pit.width, canvas.height - GROUND_TOP);

        const pulse = 0.35 + Math.sin(animTick * 0.1) * 0.25;
        const beamGrad = ctx.createLinearGradient(0, GROUND_TOP - 150, 0, GROUND_TOP);
        beamGrad.addColorStop(0, "rgba(168, 85, 247, 0.0)");
        beamGrad.addColorStop(1, `rgba(192, 132, 252, ${pulse + 0.35})`);

        ctx.fillStyle = beamGrad;
        ctx.fillRect(pit.start, GROUND_TOP - 150, pit.width, 150);

        ctx.strokeStyle = "#c084fc"; ctx.lineWidth = 3;
        ctx.strokeRect(pit.start, GROUND_TOP, pit.width, 5);

        ctx.fillStyle = "#facc15"; ctx.font = "bold 12px 'Plus Jakarta Sans'"; ctx.textAlign = "center";
        ctx.fillText("⚠️ HỐ SÂU", pit.start + pit.width / 2, GROUND_TOP - 16);
      });
    }

    function drawBossQuadrilateral() {
      const bx = BOSS_X, by = BOSS_Y;
      const shakeX = bossFlash > 0 ? (bossFlash % 4 < 2 ? -5 : 5) : 0;
      const floatY = Math.sin(animTick * 0.06) * 8;

      ctx.save();
      ctx.translate(bx + shakeX, by + floatY);

      ctx.beginPath();
      ctx.moveTo(35, 10); ctx.lineTo(170, 30); ctx.lineTo(150, 160); ctx.lineTo(15, 140);
      ctx.closePath();

      if (bossFlash > 0 && bossFlash % 4 < 2) {
        ctx.fillStyle = "#ffffff";
      } else {
        const monsterGrad = ctx.createLinearGradient(15, 10, 170, 160);
        monsterGrad.addColorStop(0, "#881337"); monsterGrad.addColorStop(0.5, "#be123c"); monsterGrad.addColorStop(1, "#4c0519");
        ctx.fillStyle = monsterGrad;
      }
      ctx.fill();
      ctx.strokeStyle = "#fda4af"; ctx.lineWidth = 4; ctx.stroke();

      ctx.fillStyle = "#fef08a"; ctx.font = "bold 13px 'Chakra Petch'";
      ctx.fillText("A", 28, 5); ctx.fillText("B", 175, 28); ctx.fillText("C", 155, 175); ctx.fillText("D", 0, 155);

      const eyeX = 90, eyeY = 85;
      ctx.fillStyle = "#ffffff"; ctx.beginPath(); ctx.arc(eyeX, eyeY, 26, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#e11d48"; ctx.lineWidth = 3; ctx.stroke();

      const eyeAngle = Math.atan2((astronaut.y + astronaut.h / 2) - (by + eyeY), (astronaut.x + astronaut.w / 2) - (bx + eyeX));
      const pupilX = eyeX + Math.cos(eyeAngle) * 9;
      const pupilY = eyeY + Math.sin(eyeAngle) * 9;
      ctx.fillStyle = "#e11d48"; ctx.beginPath(); ctx.arc(pupilX, pupilY, 11, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#000000"; ctx.beginPath(); ctx.arc(pupilX, pupilY, 5, 0, Math.PI * 2); ctx.fill();

      ctx.fillStyle = "#0f172a"; ctx.fillRect(10, -25, 160, 12);
      ctx.fillStyle = "#ef4444";
      const hpW = (gameState.bossHp / gameState.bossMaxHp) * 156;
      ctx.fillRect(12, -23, Math.max(0, hpW), 8);
      ctx.strokeStyle = "#fecdd3"; ctx.lineWidth = 1.5; ctx.strokeRect(10, -25, 160, 12);

      ctx.fillStyle = "#ffffff"; ctx.font = "9px 'Chakra Petch'"; ctx.fillText("QUÁI THÚ ABCD", 22, -32);
      ctx.restore();
    }

    function drawWorld() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const curStage = !gameState.examData ? null : gameState.examData.stages[Math.min(gameState.currentStageIdx, 4)];
      ctx.fillStyle = gameState.inBossFight ? "#2d0614" : (curStage ? curStage.bg : "#04081c");
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = "rgba(255, 255, 255, 0.75)";
      for (let i = 0; i < 45; i++) {
        const sx = (i * 97) % canvas.width;
        const sy = (i * 61) % 360;
        const s = (i % 3 === 0) ? 2.2 : 1.2;
        ctx.fillRect(sx, sy, s, s);
      }

      drawDetailedMoon(760, 120, 68, curStage ? curStage.moonColor : "#e2e8f0");

      if (endingCutscene.active) {
        drawEarth(endingCutscene.earthX, endingCutscene.earthY, 48);
      }

      ctx.save();
      ctx.translate(-Math.round(cameraX), 0);

      if (!gameState.inBossFight && !endingCutscene.active) {
        popItems.forEach(drawPopItem);
        ufoFleet.forEach(ufo => drawUFOBlock(ufo));
        popItems.forEach(drawPopLabel);
      }

      drawGroundAndPits(curStage);

      if (endingCutscene.active) {
        if (endingCutscene.flagPlanted) {
          drawVietnamFlag(360, GROUND_TOP);
        }
        drawSpaceship(endingCutscene.shipX, endingCutscene.shipY, endingCutscene.shipVy);
      }

      drawPixelAstronaut();

      if (gameState.inBossFight && !gameState.defeatedBoss && !endingCutscene.active) {
        drawBossQuadrilateral();
      }

      if (laserShot.active) {
        ctx.fillStyle = "#38bdf8";
        ctx.beginPath(); ctx.arc(laserShot.x, laserShot.y, 10, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#ffffff";
        ctx.beginPath(); ctx.arc(laserShot.x, laserShot.y, 5, 0, Math.PI * 2); ctx.fill();
      }

      ctx.restore();
    }

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

    // ===== BẮT ĐẦU GAME =====
    function startGame() {
      const name = document.getElementById("input-name").value.trim();
      const sClass = document.getElementById("input-class").value.trim();
      if (!name || !sClass) { alert("Em vui lòng nhập đầy đủ Họ tên và Lớp nhé!"); return; }

      gameState.studentName = name;
      gameState.studentClass = sClass;
      gameState.examData = buildExam();
      initLevelBoxes();
      resetAstronaut(100);
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

    // ===== MODAL CÂU HỎI =====
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
      if (gameState.isGameOver || endingCutscene.active) return;
      gameState.isPaused = true;
      keys.left = keys.right = false;
      feedbackEl.innerHTML = "";

      if (!gameState.inBossFight) {
        const curStage = gameState.examData.stages[gameState.currentStageIdx];
        const qIndex = gameState.currentQuestionIdx % curStage.questions.length;
        currentQ = curStage.questions[qIndex];
        badgeEl.textContent = `ẢI ${gameState.currentStageIdx + 1} • CÂU ${gameState.currentQuestionIdx + 1}/5 • ${currentQ.level}`;
      } else {
        const list = gameState.examData.bossQuestions;
        currentQ = list[gameState.bossQIdx % list.length];
        gameState.bossQIdx++;
        sndBossRoar();
        badgeEl.textContent = `⚔️ QUÁI THÚ TỨ GIÁC ABCD (HP: ${gameState.bossHp}/${gameState.bossMaxHp})`;
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
        if (gameState.timerSec <= 0) handleAnswer(false, "Đã hết thời gian phản xạ!");
      }, 1000);

      if (currentQ.type === "mcq") {
        optionsBox.classList.remove("hidden");
        shortBox.classList.add("hidden");
        optionsBox.innerHTML = "";
        currentQ.answers.forEach((ans, idx) => {
          const btn = document.createElement("button");
          btn.className = "w-full text-left bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl p-3 text-xs font-semibold disabled:opacity-60";
          const num = document.createElement("span");
          num.className = "text-cyan-400 font-bold";
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
      if (gameState.answerLocked) return;
      gameState.answerLocked = true;
      clearInterval(gameState.timerInterval);

      shortInput.disabled = true;
      shortSubmit.disabled = true;
      [...optionsBox.children].forEach((btn, i) => {
        btn.disabled = true;
        if (currentQ.type === "mcq" && i === currentQ.correct) btn.classList.add("border-emerald-400", "bg-emerald-900/40");
        else if (i === pickedIdx) btn.classList.add("border-rose-400", "bg-rose-900/40");
      });

      if (isCorrect) {
        sndCrystal();
        gameState.score += gameState.inBossFight ? 300 : 100;
        updateHud();
        feedbackEl.innerHTML = '<span class="text-emerald-400 font-bold">🎉 CHÍNH XÁC TUYỆT ĐỐI!</span>';

        if (gameState.inBossFight) {
          gameState.bossHp--;
          laserShot.active = true;
          laserShot.x = astronaut.x + 30;
          laserShot.y = astronaut.y + astronaut.h * 0.4;
          laserShot.vx = 9;
        } else if (!astronaut.isJumping && !astronaut.falling) {
          astronaut.isJumping = true;
          astronaut.vy = -10;
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
        line1.textContent = "❌ " + (customReason || "Chưa chính xác!") + " Đáp án đúng: " + correctText;
        const line2 = document.createElement("div");
        line2.className = "text-[11px] text-slate-300 mt-1";
        line2.textContent = "Ghi nhớ: " + currentQ.explain;
        feedbackEl.append(line1, line2);

        setTimeout(() => {
          closeQuizModal();
          if (gameState.lives <= 0) finishGameSession(false);
          else advanceProgress();
        }, 2800);
      }
    }

    const stageClearModal = document.getElementById("stage-clear-modal");
    const teacherNotes = [
      "Cô Mai Phương rất vui khi em nắm vững định lý góc tứ giác lồi! Tiến vào Ải 2 nhé!",
      "Làm tốt lắm! Em đã thuộc lòng tính chất hai đường chéo bằng nhau của hình thang cân.",
      "Xuất sắc! Tính chất hai đường chéo cắt nhau tại trung điểm là chìa khóa vàng của hình bình hành.",
      "Tuyệt vời! Em đã vận dụng thành thạo định lý và tính chất hình chữ nhật. Ải 5 đang chờ đón!",
      "Hoàn thành xuất sắc 5 Ải! Hãy tập trung phản xạ để bắn hạ Quái Thú Tứ Giác ABCD nhé!"
    ];

    function advanceProgress() {
      if (gameState.isGameOver) return;

      if (gameState.inBossFight) {
        if (gameState.bossHp <= 0) {
          gameState.defeatedBoss = true;
          setTimeout(() => {
            endingCutscene.active = true;
            endingCutscene.step = 0;
            endingCutscene.timer = 0;
            resetAstronaut(120);
            cameraX = 0;
          }, 600);
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
      resetAstronaut(100);
      cameraX = 0;
      document.getElementById("hud-quest").textContent = "0/5";

      if (gameState.currentStageIdx >= gameState.examData.stages.length) {
        gameState.inBossFight = true;
        groundPits = [];
        ufoFleet = [];
        resetAstronaut(1000);
        cameraX = 900;
        document.getElementById("hud-world").textContent = "BOSS";
        document.getElementById("hud-quest").textContent = "BOSS";
        sndBossRoar();
        setTimeout(() => openNextQuestion(), 800);
      } else {
        document.getElementById("hud-world").textContent = `P-${gameState.currentStageIdx + 1}`;
        initLevelBoxes();
        gameState.isPaused = false;
      }
    };

    function finishGameSession(isWin) {
      if (gameState.isGameOver) return;           // chỉ chạy 1 lần
      gameState.isGameOver = true;
      gameState.isPaused = true;
      clearInterval(gameState.timerInterval);
      stopBgm();
      const modal = document.getElementById("summary-modal");
      document.getElementById("sum-name").textContent = gameState.studentName;
      document.getElementById("sum-class").textContent = gameState.studentClass;
      document.getElementById("sum-examcode").textContent = gameState.examData.code;
      document.getElementById("sum-score").textContent = gameState.score;

      const noteEl = document.getElementById("summary-teacher-note");
      if (isWin) {
        noteEl.textContent = `Lời khen từ Cô Mai Phương: Xuất sắc lắm phi hành gia ${gameState.studentName}! Em đã hoàn thành sứ mệnh lịch sử: cắm cờ Việt Nam lên Mặt Trăng và trở về Trái Đất an toàn!`;
      } else {
        document.getElementById("summary-title").textContent = "HẢI TRÌNH TẠM DỪNG";
        document.getElementById("summary-subtitle").textContent = "Oxy đã cạn kiệt trước khi đánh bại Quái Thú!";
        document.getElementById("sum-bonus").textContent = "CỐ GẮNG LẦN SAU";
        noteEl.textContent = "Đừng nản lòng nhé! Em hãy ôn lại các định lý và dấu hiệu nhận biết tứ giác rồi thử sức lại!";
      }

      modal.classList.remove("hidden");

      const payload = {
        time: new Date().toLocaleString("vi-VN"),
        examCode: gameState.examData.code,
        name: gameState.studentName,
        student_class: gameState.studentClass,
        score: gameState.score,
        topic: "Minigame Tứ Giác (Vượt Ải Không Gian)",
        feedback: isWin ? "Hạ gục Quái Thú Tứ Giác, cắm cờ trên Mặt Trăng (+5đ)" : ("Chưa hạ Quái Thú - dừng ở " + (gameState.inBossFight ? "BOSS" : "Ải " + (gameState.currentStageIdx + 1)))
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
    st.caption("Cùng cô Mai Phương giải mã hạm đội UFO, hạ Quái Thú Tứ Giác và cắm cờ Việt Nam lên Mặt Trăng! Cẩn thận các hố sâu có cột laser cảnh báo nha!")

    sheet_webhook = get_secret("GOOGLE_SHEET_WEBHOOK_URL", DEFAULT_WEBHOOK) or DEFAULT_WEBHOOK
    game_html = SPACE_GAME_HTML.replace('"WEBHOOK_URL_PLACEHOLDER"', json.dumps(sheet_webhook))
    components.html(game_html, height=820, scrolling=True)

# ================= TAB 4: TRIỂN LÃM SẢN PHẨM & BÌNH CHỌN (CHỈ GV QUẢN TRỊ) =================
with tab4:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.75); border: 1px solid rgba(56, 189, 248, 0.5); padding: 18px; border-radius: 18px; margin-bottom: 20px;">
        <h3 style="color: #38bdf8; margin: 0 0 6px 0;">🖼️ Trạm Trưng Bày Sản Phẩm Học Tập</h3>
        <p style="color: #cbd5e1; font-size: 13px; margin: 0;">Không gian triển lãm các tác phẩm xuất sắc do Cô Mai Phương chọn lọc. Các phi hành gia hãy chiêm ngưỡng và thả tim ủng hộ tác phẩm mình yêu thích nhé!</p>
    </div>
    """, unsafe_allow_html=True)

    ADMIN_PASS = get_secret("TEACHER_PASSWORD", "Maiphuong2026")
    TOPIC_LIST = [
        "Chương III: Tứ giác (Hình bình hành, chữ nhật, thoi, vuông)"
        # Thêm các chủ đề sau này tại đây
    ]

    # 1. KHU VỰC QUẢN TRỊ VIÊN DÀNH RIÊNG CHO GIÁO VIÊN (ĐĂNG BÀI MỚI)
    with st.expander("🔐 Trạm Quản Trị Viên (Dành cho Giáo viên đăng bài & duyệt sản phẩm)"):
        admin_input = st.text_input("🔑 Nhập mật khẩu quản trị để mở trạm đăng bài:", type="password", key="teacher_gal_admin_pass")
        is_teacher = bool(admin_input) and hmac.compare_digest(admin_input.encode(), str(ADMIN_PASS).encode())

        if is_teacher:
            st.success("🔓 Xác thực Giáo viên thành công! Cô có thể đăng tải sản phẩm của học sinh lên sảnh triển lãm.")
            
            c_up1, c_up2 = st.columns(2)
            with c_up1:
                author_name = st.text_input("Tác giả (Học sinh / Nhóm làm):", key="admin_gal_author", placeholder="Ví dụ: Nguyễn Văn A hoặc Tổ 1")
                author_class = st.selectbox("Lớp:", ["8A13", "8A18", "Khác"], key="admin_gal_class")
            with c_up2:
                prod_title = st.text_input("Tên tác phẩm / mô hình:", key="admin_gal_title", placeholder="Ví dụ: Mô hình tứ giác lồi tự chế")
                prod_topic = st.selectbox("Chủ đề bài học:", TOPIC_LIST, key="admin_gal_topic")

            prod_file = st.file_uploader("Tải ảnh sản phẩm học sinh:", type=["jpg", "png", "jpeg"], key="admin_gal_file")
            prod_caption = st.text_area("Lời nhận xét / Thuyết minh của cô:", key="admin_gal_desc", placeholder="Nhận xét ngắn về ý tưởng, sự sáng tạo...")

            if st.button("🚀 Đăng tác phẩm lên Sảnh Trưng Bày", type="primary", use_container_width=True):
                if not author_name.strip() or not prod_title.strip() or not prod_file:
                    st.warning("Cô vui lòng nhập tên tác giả, tên tác phẩm và đính kèm ảnh nhé!")
                else:
                    try:
                        img_uploaded = Image.open(prod_file)
                        img_uploaded.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                        
                        new_item = {
                            "id": f"item_{len(gallery_items) + 1}_{datetime.now().strftime('%M%S')}",
                            "title": prod_title.strip(),
                            "author": author_name.strip(),
                            "class": author_class,
                            "topic": prod_topic,
                            "desc": prod_caption.strip() if prod_caption.strip() else "Tác phẩm xuất sắc được trưng bày.",
                            "img": img_uploaded,
                            "time": datetime.now().strftime("%d/%m %H:%M"),
                            "likes": 0
                        }
                        gallery_items.insert(0, new_item)
                        st.success("🎉 Đã đăng tải tác phẩm lên sảnh triển lãm thành công!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi tải ảnh: {e}")
        elif admin_input:
            st.error("⛔ Mật khẩu không chính xác! Khu vực chỉ dành cho Giáo viên quản trị.")

    # 2. KHU VỰC HIỂN THỊ TRIỂN LÃM & BÌNH CHỌN CHO HỌC SINH
    st.markdown("---")
    st.markdown(f"#### 🏆 Danh sách tác phẩm triển lãm ({len(gallery_items)} tác phẩm)")

    if len(gallery_items) == 0:
        st.info("Hiện tại chưa có tác phẩm nào được đăng tải. Cô Mai Phương sẽ cập nhật các sản phẩm tiêu biểu sớm nhất!")
    else:
        # Bộ lọc chủ đề
        selected_topic = st.selectbox(
            "Lọc tác phẩm theo chuyên đề:",
            ["Tất cả chủ đề"] + list(set([item["topic"] for item in gallery_items]))
        )

        display_list = gallery_items if selected_topic == "Tất cả chủ đề" else [it for it in gallery_items if it["topic"] == selected_topic]

        # Hiển thị lưới sản phẩm 2 cột
        cols = st.columns(2)
        for idx, item in enumerate(display_list):
            col = cols[idx % 2]
            with col:
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 16px; padding: 12px; margin-bottom: 8px;">
                    <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.4);">{item['topic']}</span>
                    <h4 style="color: #fef08a; margin: 8px 0 2px 0;">{item['title']}</h4>
                    <p style="color: #94a3b8; font-size: 12px; margin: 0;">Tác giả: <b style="color: #ffffff;">{item['author']}</b> ({item['class']}) • <span style="font-size: 11px;">{item['time']}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Ảnh sản phẩm
                st.image(item["img"], use_container_width=True)
                st.caption(f"💡 {item['desc']}")

                # Các nút thao tác (Thả tim & Xem lớn; có thêm Sửa/Xóa nếu cô đang đăng nhập)
                if is_teacher:
                    btn_c1, btn_c2, btn_c3 = st.columns([1.2, 1, 1])
                else:
                    btn_c1, btn_c2 = st.columns([1.2, 1])

                with btn_c1:
                    # Học sinh bấm thả tim
                    if st.button(f"💖 Thả tim ({item['likes']})", key=f"like_btn_{item['id']}", use_container_width=True):
                        item["likes"] += 1
                        st.toast(f"Đã tặng 1 ❤️ cho tác phẩm của {item['author']}!")
                        st.rerun()

                with btn_c2:
                    with st.popover("🔍 Xem lớn"):
                        st.markdown(f"### {item['title']}")
                        st.write(f"**Tác giả:** {item['author']} - Lớp {item['class']}")
                        st.write(f"**Thuyết minh / Lời phê:** {item['desc']}")
                        st.image(item["img"], use_container_width=True)

                # Nút quản lý Sửa / Xóa chỉ hiện khi Cô Mai Phương đã đăng nhập mật khẩu ở trên
                if is_teacher:
                    with btn_c3:
                        with st.popover("⚙️ Quản lý"):
                            st.markdown(f"**Quản lý bài: {item['title']}**")
                            tab_edit, tab_del = st.tabs(["✏️ Sửa", "🗑️ Xóa"])
                            
                            with tab_edit:
                                edit_title = st.text_input("Tên tác phẩm:", value=item["title"], key=f"ed_t_{item['id']}")
                                edit_author = st.text_input("Tác giả:", value=item["author"], key=f"ed_a_{item['id']}")
                                edit_desc = st.text_area("Thuyết minh / Nhận xét:", value=item["desc"], key=f"ed_d_{item['id']}")
                                edit_img = st.file_uploader("Đổi ảnh khác:", type=["jpg", "png", "jpeg"], key=f"ed_f_{item['id']}")
                                
                                if st.button("💾 Lưu chỉnh sửa", key=f"btn_save_{item['id']}", use_container_width=True):
                                    item["title"] = edit_title.strip()
                                    item["author"] = edit_author.strip()
                                    item["desc"] = edit_desc.strip()
                                    if edit_img:
                                        new_pic = Image.open(edit_img)
                                        new_pic.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                                        item["img"] = new_pic
                                    st.success("Đã lưu thay đổi!")
                                    st.rerun()

                            with tab_del:
                                st.warning("Xác nhận gỡ tác phẩm này khỏi sảnh triển lãm?")
                                if st.button("❌ Gỡ tác phẩm", key=f"btn_del_{item['id']}", type="primary", use_container_width=True):
                                    gallery_items.remove(item)
                                    st.success("Đã xóa tác phẩm!")
                                    st.rerun()

                st.write("")
# ================= TAB 5: BẢNG ĐIỂM LỚP (ĐỔI SANG with tab5) =================
with tab5:
    st.markdown("### 🔒 Trạm Bảo Mật Sổ Điểm Giáo Viên")
    st.caption("Dữ liệu hạm đội học sinh được mã hóa bảo mật.")

    teacher_password = st.text_input("🔑 Nhập mật khẩu hạm đội để mở sổ điểm:", type="password", key="teacher_pass_tab5")
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
