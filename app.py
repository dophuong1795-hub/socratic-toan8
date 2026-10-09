import streamlit as st
import requests
from PIL import Image, ImageOps
import json
import re
import base64
import io
import time
import pandas as pd
from datetime import datetime

# ================= CẤU HÌNH GIAO DIỆN STREAMLIT =================
st.set_page_config(
    page_title="Đấu Trường Hình Học 8 - Cô Mai Phương",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CSS TỐI ƯU MOBILE & MÁY TÍNH =================
st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 780px !important;
    }
    .hero-banner {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        border-radius: 18px;
        padding: 20px 16px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.25);
        margin-bottom: 18px;
    }
    .hero-banner h1 {
        font-size: 24px !important;
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
        padding: 5px 15px;
        border-radius: 999px;
        margin-bottom: 12px;
        border: 1px solid #C7D2FE;
    }
    div[data-testid="stButton"] button {
        border-radius: 14px !important;
        border: 2px solid #E2E8F0 !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        text-align: left !important;
        justify-content: flex-start !important;
        line-height: 1.4 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #EEF2FF !important;
        border-color: #6366F1 !important;
        color: #4F46E5 !important;
        transform: translateY(-2px) !important;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5, #6366F1) !important;
        color: white !important;
        border: none !important;
        text-align: center !important;
        justify-content: center !important;
    }
    .reward-box {
        background: #F0FDF4;
        border: 2px solid #86EFAC;
        border-radius: 16px;
        padding: 18px;
        margin-top: 15px;
    }
    .svg-container {
        display: flex;
        justify-content: center;
        align-items: center;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 14px;
        margin: 15px auto;
        max-width: 320px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    .svg-container svg {
        max-width: 100%;
        height: auto;
        display: block;
    }
    .solution-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #4F46E5;
        padding: 18px 20px;
        border-radius: 10px;
        line-height: 1.85;
        font-size: 15px;
        color: #1E293B;
        margin-top: 14px;
    }
    .solution-box p {
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ================= KIỂM TRA API KEY =================
API_KEY = st.secrets.get("OPENROUTER_API_KEY")
if not API_KEY:
    st.error("Chưa cấu hình OPENROUTER_API_KEY trong Secrets của Streamlit Cloud!")
    st.stop()

MODEL_NAME = "google/gemma-4-26b-a4b-it:free"

# ================= BỘ LỌC CHUẨN HÓA TOÁN HỌC & TRÌNH BÀY =================
def clean_math_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    
    # 1. Loại bỏ các lệnh LaTeX logic gây lỗi hiển thị
    text = re.sub(r"\\implies|implies", " suy ra ", text, flags=re.IGNORECASE)
    text = re.sub(r"\\because|because", " vì ", text, flags=re.IGNORECASE)
    text = re.sub(r"\\therefore|therefore", " do đó ", text, flags=re.IGNORECASE)
    text = re.sub(r"\bhypotenuse\b", "cạnh huyền", text, flags=re.IGNORECASE)

    # 2. Sửa lỗi chính tả tiếng Việt
    text = re.sub(r"\btư giác\b", "tứ giác", text, flags=re.IGNORECASE)
    text = re.sub(r"\bTư giác\b", "Tứ giác", text)

    # 3. Ký hiệu góc và độ
    text = re.sub(r"góc\s*(?:tam giác|riangle|//|/|°)\s*", "góc ", text, flags=re.IGNORECASE)
    text = re.sub(r"góc\s+góc\s+", "góc ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b([A-Z])\s*(?://|riangle|°)\s*([A-Z]{2})\b", r"\1 thuộc \2", text)
    text = text.replace(r"\in", " thuộc ")
    text = re.sub(r"\b([A-Z]{2})\s*(?:riangle|°)\s*([A-Z]{2})\b", r"\1 // \2", text)
    text = re.sub(r"\\?parallel", " // ", text)

    text = re.sub(r"bước\s*(\d+)°?", r"bước \1", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(1[0-8]0|[3469]0)\s*(?:\^?\s*(?:circ|riangle|°)|(?=\s*[\.,\)\s]|$))(?!\s*(?:bước|cạnh|đoạn|tam giác))", r"\1°", text)
    text = text.replace("°°", "°")
    text = text.replace(r"^\circ", "°")
    text = text.replace("^circ", "°")

    # 4. Ký hiệu tam giác, vuông góc
    text = re.sub(r"\\?t?riangle\s*", "tam giác ", text, flags=re.IGNORECASE)
    text = re.sub(r"tam giác\s+tam giác\s+", "tam giác ", text, flags=re.IGNORECASE)
    text = re.sub(r"\\?angle\s*", "góc ", text, flags=re.IGNORECASE)
    text = text.replace("riangle", " // ")
    text = text.replace("Île", "góc ")
    text = text.replace("£", " ⊥ ")
    text = text.replace(r"\perp", " ⊥ ")
    text = text.replace("$", "")

    # 5. Mũ góc
    text = re.sub(r"\\hat\{([A-Za-z0-9]+)\}", r"góc \1", text)
    text = re.sub(r"\\widehat\{([A-Za-z0-9]+)\}", r"góc \1", text)
    
    return text.strip()

def format_solution_to_html(raw_solution: str) -> str:
    """Tự động phân đoạn, thụt dòng và làm đẹp bài giải"""
    text = clean_math_text(raw_solution)
    # Tách các ý chính a), b)
    text = re.sub(r"(\*\*[a-z]\)|\b[a-z]\))\s*", r"\n\n<b>\1 </b>", text)
    # Tách các gạch đầu dòng dấu sao hoặc dấu chấm
    text = re.sub(r"\s*(\*|\•)\s*", r"<br>• ", text)
    # Tách đoạn suy luận nếu viết dính
    text = re.sub(r"(?<=[.!?])\s+(?=(?:Xét|Do đó|Suy ra|Ta có|Mà)\b)", r"<br>• ", text)
    # Thay ngắt dòng thành HTML <br>
    formatted = text.replace("\n\n", "<br><br>").replace("\n", "<br>")
    return formatted

GAME_PROMPT = """
Bạn là Trợ lý Sư phạm Hình học 8 của Cô Mai Phương. 
Học sinh lớp 8 (13-14 tuổi), học bộ sách Kết nối tri thức.

QUY TẮC CÂU HỎI:
1. Thân thiện, ngắn gọn, dễ hiểu.
2. Dùng đúng thuật ngữ SGK: 'cạnh huyền', 'đường trung tuyến', 'cạnh góc vuông'.
3. Câu hỏi tối đa 2 câu. Mỗi lựa chọn tối đa 1 dòng. KHÔNG ghi A., B. ở đầu options.

QUY TẮC TRÌNH BÀY BÀI GIẢI (KHI is_finished = true):
1. full_solution:
   - Trình bày dạng từng dòng gạch đầu dòng rõ ràng.
   - Xuống dòng riêng biệt cho mỗi bước suy luận, mở ngoặc ghi rõ lý do định lý.
   - Tuyệt đối không dùng ký hiệu LaTeX phức tạp như \\implies, \\because.
2. svg_code: Sinh mã SVG gọn gàng (viewBox="0 0 300 240", width="300", height="240"):
   - Vẽ các đoạn thẳng nét đen (stroke="#1E293B" stroke-width="2.5").
   - Các điểm đỉnh có chấm tròn đỏ (r="4" fill="#EF4444").
   - QUAN TRỌNG NHẤT VỀ TÊN ĐIỂM: Thẻ <text> của TỪNG ĐIỂM phải có tọa độ x, y cụ thể đặt ngay cạnh điểm đó (cách điểm khoảng 8-12px) để chữ nằm sát đỉnh. Ví dụ: điểm tại cx="40" cy="40" thì <text x="25" y="35" font-weight="bold
