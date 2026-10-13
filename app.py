import streamlit as st
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

# ================= CSS TÙY CHỈNH GIAO DIỆN =================
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
    }
    .reward-box {
        background: #F0FDF4;
        border: 2px solid #86EFAC;
        border-radius: 16px;
        padding: 20px;
        margin-top: 15px;
    }
    .svg-container {
        display: flex;
        justify-content: center;
        align-items: center;
        background: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
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
MODEL_NAME = "gemini-2.5-flash"

# ================= BỘ LỌC CHUẨN HÓA KÝ HIỆU TOÁN HỌC (ĐẠI SỐ & HÌNH HỌC) =================
def format_math(text: str) -> str:
    """
    Chuẩn hóa biểu thức cả Toán Số (Đại số) và Toán Hình về Unicode sạch,
    chống lỗi gãy cú pháp, chữ đỏ và hiển thị thân thiện trên web.
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Khử log suy nghĩ nội bộ AI
    text = re.sub(r"^(?:User Safety|Thinking Process|Thought):[^\n]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)

    # 2. Xóa bỏ dấu $ đơn thuần để hiển thị Unicode mượt mà
    text = text.replace("$", "")

    # --- [A. NHÓM TOÁN HÌNH] ---
    # Chuẩn hóa góc: \widehat{AEM}, \hat{A} -> ∠AEM, ∠A
    text = re.sub(r"\\(?:widehat|hat)\s*[\{\[]\s*([A-Za-z0-9]{1,3})\s*[\}\]]", r"∠\1", text)
    text = re.sub(r"\\(?:angle)\s+([A-Za-z0-9]{1,3})\b", r"∠\1", text)

    # Chuẩn hóa tam giác: \Delta ABC, \triangle ABC -> Δ ABC
    text = re.sub(r"\\(?:Delta|triangle)\s*([A-Za-z]{3})", r"Δ \1", text)
    text = re.sub(r"Δ([A-Za-z]{3})", r"Δ \1", text)

    # Quan hệ hình học: vuông góc, song song, thuộc
    text = re.sub(r"\\perp|£", " ⊥ ", text)
    text = re.sub(r"\\parallel", " // ", text)
    text = re.sub(r"\\in", " ∈ ", text)

    # Số đo độ: 90^\circ, 90 ^\circ -> 90°
    text = re.sub(r"\^?\\circ", "°", text)
    text = text.replace("°°", "°")

    # --- [B. NHÓM TOÁN SỐ (ĐẠI SỐ / SỐ HỌC)] ---
    # Phép toán so sánh & suy luận đại số
    text = re.sub(r"\\(?:Leftrightarrow|iff)|<=>", " ⇔ ", text)
    text = re.sub(r"\\(?:Rightarrow|implies)|=>", " ⇒ ", text)
    text = re.sub(r"\\le(?:q)?|<=|≤", " ≤ ", text)
    text = re.sub(r"\\ge(?:q)?|>=|≥", " ≥ ", text)
    text = re.sub(r"\\ne(?:q)?|!=|≠", " ≠ ", text)
    text = re.sub(r"\\pm|±", " ± ", text)
    text = re.sub(r"\\times|\\cdot|\*", " · ", text)

    # Căn thức: \sqrt{x+1} -> √(x+1), \sqrt[3]{x} -> ∛(x)
    text = re.sub(r"\\sqrt\[3\]\{([^{}]+)\}", r"∛(\1)", text)
    text = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", text)
    text = re.sub(r"\\sqrt\s*([0-9a-zA-Z]+)", r"√\1", text)

    # Lũy thừa thông dụng (Unicode superscript)
    superscripts = {
        "^0": "⁰", "^1": "¹", "^2": "²", "^3": "³", "^4": "⁴",
        "^5": "⁵", "^6": "⁶", "^7": "⁷", "^8": "⁸", "^9": "⁹",
        "^{2}": "²", "^{3}": "³", "^{n}": "ⁿ"
    }
    for k, v in superscripts.items():
        text = text.replace(k, v)

    # Chuẩn hóa phân số: \frac{a}{b} -> (a / b)
    text = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1 / \2)", text)

    # --- [C. CHUẨN HÓA THUẬT NGỮ SGK TOÁN 8] ---
    text = re.sub(r"\bhypotenuse\b", "cạnh huyền", text, flags=re.IGNORECASE)
    text = re.sub(r"\bpolynomial\b", "đa thức", text, flags=re.IGNORECASE)
    text = re.sub(r"\bfactorization\b", "phân tích đa thức thành nhân tử", text, flags=re.IGNORECASE)
    text = re.sub(r"\\because|\bbecause\b", "vì", text, flags=re.IGNORECASE)
    text = re.sub(r"\\therefore|\btherefore\b", "do đó", text, flags=re.IGNORECASE)

    # Dọn dẹp khoảng trắng
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

# ================= HÀM ĐỊNH DẠNG BÀI GIẢI AN TOÀN =================
def format_solution_step_by_step(raw_text: str) -> str:
    """Tách dòng bài giải chuẩn, hỗ trợ cả công thức Đại số KaTeX và lập luận Hình học"""
    if not raw_text:
        return ""
    
    text = raw_text.replace("Lời giải chi tiết:", "").replace("Bài giải chi tiết:", "").strip()
    
    # 1. Heading cho các ý a), b), c) hoặc câu 1, 2
    text = re.sub(r"(?m)^\s*([a-d]\))\s*", r"\n\n### **\1** ", text)
    text = re.sub(r"(?m)^\s*(Câu\s+\d+[\:\.]?)\s*", r"\n\n### **\1** ", text)

    # 2. Xử lý biểu thức Đại số sang KaTeX để hiển thị gạch ngang phân số đẹp mắt
    # Chuyển đổi (a)/(b) hoặc phân thức đại số
    text = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"$\\dfrac{\1}{\2}$", text)
    text = re.sub(r"\(([a-zA-Z0-9\+\-\*\s]+)\)\s*/\s*([a-zA-Z0-9\+\-\*\s]+)", r"$\\dfrac{\1}{\2}$", text)
    
    # 3. Chuyển đổi tam giác: ΔABC -> $\Delta ABC$
    text = re.sub(r"Δ\s*([A-Za-z]{3})", r"$\\Delta \1$", text)
    
    # 4. Định dạng gạch đầu dòng và mũi tên suy luận
    text = re.sub(r"(?<=\.)\s*-\s*", r"\n- ", text)
    text = re.sub(r"\s*(?:=>|⇒|\\Rightarrow)\s*", r"\n  - $\\Rightarrow$ ", text)
    text = re.sub(r"\s*(?:<=>|⇔|\\Leftrightarrow)\s*", r"\n  - $\\Leftrightarrow$ ", text)
    
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if l:
            l = re.sub(r"\${2,}", "$", l)
            l = re.sub(r"\$\s*\$", "", l)
            cleaned_lines.append(l)
            
    return "\n\n".join(cleaned_lines)

GAME_PROMPT = """
Bạn là Trợ lý Sư phạm Toán 8 (Cả Đại số và Hình học) của Cô Mai Phương (Chương trình GDPT 2018 - Kết nối tri thức).
Đối tượng học sinh: Lớp 8 (13-14 tuổi).

QUY TẮC SƯ PHẠM:
1. Nhận diện dạng bài từ hình ảnh/đề bài:
   - NẾU LÀ TOÁN SỐ (Đại số / Số học / Thống kê): Đơn thức, Đa thức, Hằng đẳng thức đáng nhớ, Phân thức đại số, Phương trình bậc nhất, Hàm số bậc nhất.
   - NẾU LÀ TOÁN HÌNH: Tứ giác, Định lý Thalès, Tam giác đồng dạng, Hình khối không gian.
2. Lời văn gần gũi, chuẩn ngôn ngữ SGK Toán 8 Việt Nam. KHÔNG dùng tiếng Anh thuật ngữ.
3. Câu hỏi tối đa 2 câu, hỏi trực diện. 4 lựa chọn ngắn gọn (1-2 dòng), KHÔNG ghi tiền tố 'A.', 'B.'.
4. KÝ HIỆU TOÁN BẮT BUỘC DÙNG UNICODE THUẦN (KHÔNG dùng LaTeX gạch chéo ngược):
   - Đại số: ⇔, ⇒, ≤, ≥, ≠, √, ², ³, ±, x = 2.
   - Hình học: ∠ABC = 90°, ΔABC, AB // CD, ME ⊥ AB, M ∈ BC.

CẤU TRÚC 3 BƯỚC THỬ THÁCH (Socratic Gamification):
- Bước 1: Khai thác giả thiết cốt lõi (điều kiện xác định, hằng đẳng thức liên quan, yếu tố hình học ban đầu).
- Bước 2: Bước biến đổi trung gian (phân tích nhân tử, quy đồng, chứng minh hình bình hành / tam giác đồng dạng).
- Bước 3: Đưa ra đáp số cuối cùng hoặc kết luận điều phải chứng minh.

KHI is_finished = true:
- full_solution: Bài giải chi tiết hoàn chỉnh mẫu mực, từng bước rõ ràng để chép vở.
- svg_code: 
   + NẾU LÀ BÀI TOÁN HÌNH: BẮT BUỘC sinh mã SVG khung <svg viewBox='0 0 500 400'> với các đoạn thẳng rõ nét, các đỉnh có nhãn riêng biệt bằng thẻ <text>, cạnh khuất nét đứt (stroke-dasharray='4,4').
   + NẾU LÀ BÀI TOÁN SỐ: Trả về chuỗi rỗng "" (không cần hình vẽ).

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
  "explanation": "Giải thích ngắn vì sao đúng theo định lý/hằng đẳng thức nào",
  "is_finished": false,
  "full_solution": "",
  "svg_code": ""
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
            return json.loads(target_str, strict=False)
        except Exception:
            fixed_str = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', target_str)
            return json.loads(fixed_str, strict=False)

    return text_out

if "submission_history" not in st.session_state:
    st.session_state.submission_history = []

# ================= BANNER TIÊU ĐỀ =================
st.markdown("""
<div class="hero-banner">
    <h1>📐 ĐẤU TRƯỜNG TOÁN HỌC 8</h1>
    <p>Chinh phục Đại số & Hình học cùng cô Mai Phương • Học tập gợi mở theo từng bước</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎮 Thử Thách Tương Tác", "📝 Nộp Bài Tập", "📊 Bảng Điểm Lớp"])

# ================= TAB 1: GAME TƯƠNG TÁC (ĐẠI SỐ & HÌNH HỌC) =================
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
    if "reward_svg" not in st.session_state:
        st.session_state.reward_svg = None

    with st.expander("📸 Đề bài / Ảnh chụp bài toán (Số học, Đại số hoặc Hình học)", expanded=(st.session_state.card is None)):
        up_game_img = st.file_uploader("Tải/chụp ảnh bài toán (hỗ trợ cả Đại số và Hình học):", type=["jpg", "png", "jpeg"], key="up_game_img")
        math_mode = st.radio("Phân loại môn:", ["Tự động nhận diện", "Toán Số (Đại số)", "Toán Hình (Hình học)"], horizontal=True)
        
        if up_game_img:
            st.session_state.img_data = Image.open(up_game_img)
            st.image(st.session_state.img_data, caption="Ảnh đề bài đang xử lý", use_container_width=True)

        if st.session_state.img_data and st.session_state.card is None:
            if st.button("🚀 Bắt đầu nhận Thử thách Bước 1!", type="primary", use_container_width=True):
                with st.spinner("Đợi cô phân tích đề bài một chút nhé..."):
                    try:
                        p_start = f"Tạo câu hỏi thử thách Bước 1 ngắn gọn. Phân loại yêu cầu: {math_mode}."
                        c_data = execute_gemini_request([st.session_state.img_data, p_start], GAME_PROMPT, is_json=True)
                        st.session_state.card = c_data
                        st.session_state.total_steps = c_data.get("total_steps", 3)
                        st.session_state.step = 1
                        st.session_state.answered = False
                        st.session_state.reward = None
                        st.session_state.reward_svg = None
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
        st.markdown(f'<span class="step-badge">[{badge_type}] CỬA ẢI: BƯỚC {curr} / {total}</span>', unsafe_allow_html=True)
        
        fb = format_math(card.get("feedback", ""))
        if fb:
            st.info(f"💡 {fb}")

        st.markdown(f"#### 🎯 {format_math(card.get('question', ''))}")
        st.write("")

        opts = card.get("options", [])
        correct = card.get("correct_index", 0)

        if not st.session_state.answered:
            st.markdown("**👉 Em hãy bấm chọn một đáp án đúng nhất:**")
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
                st.success("🎉 **Chính xác!** Em đã lựa chọn tư duy chuẩn xác.")
            else:
                st.error("❌ **Chưa chính xác.**")
                st.markdown(f"Đáp án đúng là: **{chr(65+correct)}. {correct_text}**")

            st.markdown(f"**💡 Hướng suy luận:** {format_math(card.get('explanation', ''))}")

            is_finish = card.get("is_finished") or (curr >= total)

            if is_finish:
                st.balloons()
                st.success("🏆 **XUẤT SẮC! Em đã hoàn thành trọn vẹn bài toán!**")

                if not st.session_state.reward:
                    sol = card.get("full_solution", "")
                    svg = card.get("svg_code", "")
                    if not sol and st.session_state.img_data:
                        with st.spinner("Đang mở khóa bài giải hoàn chỉnh..."):
                            p_sol = """Hãy viết bài giải mẫu mực hoàn chỉnh. 
                            Nếu là Toán Hình: Sinh kèm mã SVG chuẩn.
                            Nếu là Toán Số: Trình bày các bước biến đổi đại số rõ ràng.
                            YÊU CẦU KÝ HIỆU: Dùng ký hiệu Unicode thuần (⇔, ⇒, ≤, ≥, √, ², ∠, ⊥, //, Δ, °).
                            Trả về JSON: {"full_solution": "...", "svg_code": "..."}"""
                            try:
                                res_final = execute_gemini_request([st.session_state.img_data, p_sol], is_json=True)
                                sol = res_final.get("full_solution", "")
                                svg = res_final.get("svg_code", "")
                            except Exception as e:
                                sol = "Đã xảy ra lỗi khi tạo lời giải chi tiết."
                    st.session_state.reward = sol
                    st.session_state.reward_svg = svg

                st.markdown("""
                <div class="reward-box">
                    <h3 style="color: #15803D; margin-top:0;">🎁 PHẦN THƯỞNG: BÀI GIẢI MẪU HOÀN CHỈNH</h3>
                    <p style="color: #166534; font-size: 14px;">Em hãy đối chiếu các bước lập luận và ghi chép cẩn thận vào vở nhé!</p>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.reward_svg and "<svg" in st.session_state.reward_svg:
                    st.markdown("#### 📐 Hình vẽ minh họa chuẩn xác:")
                    clean_svg_match = re.search(r"<svg[\s\S]*?</svg>", st.session_state.reward_svg)
                    if clean_svg_match:
                        st.markdown(f'<div class="svg-container">{clean_svg_match.group(0)}</div>', unsafe_allow_html=True)

                st.markdown("#### 📝 Lời giải chi tiết:")
                formatted_solution = format_solution_step_by_step(st.session_state.reward or "")
                st.markdown(formatted_solution)

                st.write("")
                st.success("📝 **Bước tiếp theo:** Hãy chuyển sang tab **'Nộp Bài Tập'** để nộp bài làm của em cho cô chấm nhé!")
            else:
                st.write("")
                if st.button("➡️ Sang thử thách tiếp theo", type="primary", use_container_width=True):
                    with st.spinner("Đang chuẩn bị cửa ải tiếp theo..."):
                        p_next = f"""Học sinh vừa vượt qua bước {curr} với đáp án đúng: {correct_text}. Tạo thử thách trắc nghiệm bước {curr + 1} / {total}. 
                        Giữ câu hỏi và 4 phương án ngắn gọn, dễ hiểu cho học sinh lớp 8. Dùng ký hiệu Unicode thuần: ⇔, ⇒, ≤, ≥, √, ², ∠, ⊥, //, Δ, °.
                        Nếu đây là bước cuối, hãy đặt is_finished = true, viết bài giải chi tiết vào full_solution (và svg_code nếu là hình học)."""
                        try:
                            st.session_state.card = execute_gemini_request([st.session_state.img_data, p_next], GAME_PROMPT, is_json=True)
                            st.session_state.step += 1
                            st.session_state.answered = False
                            st.session_state.selected_idx = None
                            st.rerun()
                        except Exception as err:
                            st.error(f"Lỗi tải màn: {err}")

        st.write("")
        if st.button("🔄 Giải bài tập khác", use_container_width=True):
            st.session_state.step = 1
            st.session_state.card = None
            st.session_state.answered = False
            st.session_state.selected_idx = None
            st.session_state.img_data = None
            st.session_state.reward = None
            st.session_state.reward_svg = None
            st.rerun()

# ================= TAB 2: NỘP BÀI & CHẤM ĐIỂM (CẢ ĐẠI SỐ & HÌNH HỌC) =================
with tab2:
    st.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 14px; margin-bottom: 20px;">
        <span style="font-weight: 700; color: #334155;">📋 Chấm tự luận bằng AI theo Rubric chuẩn môn Toán THCS (Đại số & Hình học)</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        s_name = st.text_input("Họ và tên học sinh:")
    with c2:
        s_class = st.selectbox("Lớp:", ["8A13", "8A18"])

    # Danh mục phong phú cả Đại số và Hình học 8
    topic = st.selectbox("Chọn chuyên đề bài tập nộp:", [
        # --- Đại số 8 ---
        "Đại số 8: Đơn thức và Đa thức nhiều biến",
        "Đại số 8: Các hằng đẳng thức đáng nhớ",
        "Đại số 8: Phân tích đa thức thành nhân tử",
        "Đại số 8: Phân thức đại số và rút gọn phân thức",
        "Đại số 8: Phương trình bậc nhất một ẩn",
        "Đại số 8: Giải bài toán bằng cách lập phương trình",
        "Đại số 8: Hàm số bậc nhất và đồ thị",
        # --- Hình học 8 ---
        "Hình học 8: Tứ giác và Hình thang cân",
        "Hình học 8: Hình bình hành và Hình chữ nhật",
        "Hình học 8: Hình thoi và Hình vuông",
        "Hình học 8: Định lý Thalès trong tam giác",
        "Hình học 8: Tam giác đồng dạng và định lý liên quan",
        "Hình học 8: Hình chóp tam giác đều & tứ giác đều",
        "Bài kiểm tra tổng hợp (Số và Hình)"
    ])

    up_hw = st.file_uploader("📸 Chụp ảnh bài giải viết tay trong vở:", type=["jpg", "png", "jpeg"], key="hw_submit_img")

    if st.button("🚀 Nộp bài và nhận kết quả", type="primary", use_container_width=True):
        if not s_name:
            st.warning("Em hãy điền Họ và tên trước khi nộp nhé!")
        elif not up_hw:
            st.warning("Em chưa tải ảnh bài làm lên!")
        else:
            with st.spinner("Cô đang chấm bài chi tiết theo Rubric môn Toán..."):
                try:
                    hw_img = Image.open(up_hw)
                    RUBRIC = f"""
Bạn là Giám khảo chấm thi môn Toán THCS tại Việt Nam.
Chuyên đề nộp: "{topic}".
Đọc ảnh bài làm viết tay của học sinh và đánh giá theo Rubric thang điểm 10.

HƯỚNG DẪN ĐẶC THÙ THEO DẠNG TOÁN:
1. NẾU LÀ TOÁN ĐẠI SỐ (Số học):
   - Đánh giá: Tìm ĐKXĐ, biến đổi đại số đúng công thức/hằng đẳng thức, thứ tự thực hiện phép tính, kết luận tập nghiệm/giá trị.
2. NẾU LÀ TOÁN HÌNH HỌC:
   - Đánh giá: Vẽ hình đúng quy ước (ký hiệu góc, cạnh bằng nhau), lập luận logic chặt chẽ, dẫn chứng định lý rõ ràng.

QUY TẮC BẮT BUỘC KÝ HIỆU (UNICODE THUẦN):
- TUYỆT ĐỐI KHÔNG dùng mã LaTeX có dấu gạch chéo ngược (\\frac, \\perp, \\Rightarrow, \\sqrt, $).
- DÙNG KÝ HIỆU UNICODE:
  + Đại số: ⇔, ⇒, ≤, ≥, ≠, √, ², ³, ±.
  + Hình học: ∠ABC = 90°, dấu ⊥, dấu //, dấu ∈, dấu Δ, số đo °.

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

Gợi ý cách trình bày chuẩn để đạt điểm tối đa:
(Trình bày từng dòng ngắn gọn, rõ ràng theo đúng ký hiệu trên).
"""
                    # Gọi AI chấm bài
                    score_res = execute_gemini_request([hw_img, RUBRIC])
                    score_res_clean = format_math(score_res)

                    # Trích xuất điểm số
                    score_match = re.search(r"(\d+(?:[.,]\d+)?)\s*/\s*10", score_res_clean)
                    extracted_score = score_match.group(1).replace(",", ".") if score_match else "Chưa xác định"

                    # 1. Lưu phiên hiện tại
                    sub_record = {
                        "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Họ và tên": s_name,
                        "Lớp": s_class,
                        "Bài tập": topic,
                        "Điểm số": extracted_score,
                        "Nhận xét của AI": score_res_clean.replace("\n", " ")
                    }
                    st.session_state.submission_history.append(sub_record)

                    # 2. TỰ ĐỘNG GỬI SANG GOOGLE SHEETS
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

                    st.success("🎉 Đã hoàn tất chấm bài và tự động cập nhật vào sổ điểm của cô!")
                    st.markdown(f"### Kết quả của: **{s_name}** - Lớp **{s_class}**")
                    st.markdown(score_res_clean)
                except Exception as err:
                    st.error(f"Lỗi trong quá trình chấm bài: {err}")
                    st.info("💡 Cô kiểm tra lại ảnh bài làm hoặc kết nối API nhé.")

# ================= TAB 3: BẢNG ĐIỂM (BẢO MẬT & XUẤT GOOGLE SHEETS) =================
with tab3:
    st.markdown("### 🔒 Khu Vực Quản Lý Điểm Của Giáo Viên")
    st.caption("Dữ liệu điểm số được bảo mật để đảm bảo tính riêng tư của học sinh.")

    teacher_password = st.text_input("🔑 Nhập mật khẩu giáo viên để xem sổ điểm:", type="password")
    ADMIN_PASS = "Maiphuong2026"

    if teacher_password:
        if teacher_password == ADMIN_PASS:
            st.success("🔓 Xác thực thành công! Chào cô Mai Phương.")
            
            if len(st.session_state.submission_history) == 0:
                st.info("Chưa có học sinh nào nộp bài trong phiên làm việc này.")
            else:
                df = pd.DataFrame(st.session_state.submission_history)
                st.dataframe(df, use_container_width=True)

                csv_data = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

                st.write("---")
                st.markdown("**📥 Tải file để mở thẳng trên Google Sheets hoặc Excel:**")
                st.download_button(
                    label="📗 Tải file bảng điểm (.CSV cho Google Sheets)",
                    data=csv_data,
                    file_name=f"Bang_Diem_Toan8_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )

                st.info("💡 **Cách mở trên Google Sheets:** Mở `sheets.google.com` ➔ Chọn **Tệp (File)** ➔ **Mở (Open)** ➔ Chọn **Tải lên (Upload)** file vừa tải về.")
        else:
            st.error("⛔ Mật khẩu không chính xác! Học sinh vui lòng không truy cập khu vực này.")
    else:
        st.info("👉 Vui lòng nhập mật khẩu để mở khóa sổ theo dõi điểm.")
