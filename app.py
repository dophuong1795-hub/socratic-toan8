import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import re
import pandas as pd
from datetime import datetime

# ================= CẤU HÌNH GIAO DIỆN STREAMLIT =================
st.set_page_config(
    page_title="Đấu Trường Hình Học 8 - Cô Mai Phương",
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

# Khởi tạo Gemini Client với model chuẩn theo thông báo API
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-3.8-flash"

# ================= BỘ LỌC CHUẨN HÓA KÝ HIỆU TOÁN HỌC 8 =================
def format_math(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""

    # 1. Khử bỏ rác hệ thống & từ ngoại lai
    text = re.sub(r"^(?:User Safety|Thinking Process|Thought):[^\n]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\\implies|\bimplies\b", " suy ra ", text, flags=re.IGNORECASE)
    text = re.sub(r"\\because|\bbecause\b", " vì ", text, flags=re.IGNORECASE)
    text = re.sub(r"\\therefore|\btherefore\b", " do đó ", text, flags=re.IGNORECASE)
    text = re.sub(r"\bhypotenuse\b", "cạnh huyền", text, flags=re.IGNORECASE)

    # 2. Chuẩn hóa phân số nét gạch ngang: AC/2, AB/2 -> $\dfrac{AC}{2}$
    text = re.sub(r"(?<![a-zA-Z0-9_\$])([A-Z]{1,2}|\d+)\s*/\s*([A-Z]{1,2}|\d+)(?![a-zA-Z0-9_\$])", r"$\\dfrac{\1}{\2}$", text)
    text = re.sub(r"\$?\\frac\{([^}]+)\}\{([^}]+)\}\$?", r"$\\dfrac{\1}{\2}$", text)

    # 3. Chuẩn hóa góc thành dấu mũ: Góc IHA, góc A -> $\widehat{IHA}$, $\widehat{A}$
    def to_latex_angle(m):
        name = m.group(1).strip()
        return f"$\\widehat{{{name}}}$"

    text = re.sub(r"(?:[∠∡∢]|\\angle\s*|\\widehat\{|\\hat\{|[Gg]óc\s+)([A-Z]{1,3})\b\}?", to_latex_angle, text)

    # 4. Ký hiệu hình học khác: song song //, vuông góc ⊥, thuộc
    text = re.sub(r"\b([A-Z]{2})\s*(?://|riangle|°)\s*([A-Z]{2})\b", r"\1 // \2", text)
    text = re.sub(r"\\?parallel", " // ", text)
    text = re.sub(r"\\perp|£", " ⊥ ", text)
    text = re.sub(r"\b([A-Z])\s*(?://|riangle|°)\s*([A-Z]{2})\b", r"\1 thuộc \2", text)
    text = text.replace(r"\in", " thuộc ")

    # 5. Chuẩn hóa độ
    text = re.sub(r"\b(1[0-8]0|[3469]0)\s*(?:\^?\s*(?:circ|°)|(?=\s*[\.,\)\s]|$))(?!\s*(?:bước|cạnh|đoạn|tam giác))", r"\1°", text)
    text = text.replace("°°", "°")

    return text.strip()

clean_math_text = format_math
clean_math = format_math

# ================= HÀM ĐỊNH DẠNG BÀI GIẢI AN TOÀN =================
def format_solution_step_by_step(raw_text: str) -> str:
    """Tách dòng bài giải rõ ràng mà KHÔNG làm vỡ công thức cộng chu vi"""
    if not raw_text:
        return ""
    
    text = raw_text.replace("Lời giải chi tiết:", "").replace("Bài giải chi tiết:", "").strip()
    
    # Đưa các tiêu đề câu a), b), c) thành tiêu đề rõ ràng
    text = re.sub(r"(?:\n|^|\s+)([a-c]\))\s*", r"\n\n### **\1** ", text)
    
    # Chỉ ngắt dòng khi dấu gạch ngang '-' hoặc '=>' đứng sau dấu chấm hoặc xuống dòng,
    # TUYỆT ĐỐI KHÔNG ngắt dấu '+' để tránh làm nát phép cộng chu vi
    text = re.sub(r"(?<=\.)\s*-\s*", r"\n- ", text)
    text = re.sub(r"\s*=>\s*", r"\n  - $\\Rightarrow$ ", text)
    
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if l:
            cleaned_lines.append(format_math(line))
            
    return "\n\n".join(cleaned_lines)

GAME_PROMPT = """
Bạn là Trợ lý Sư phạm Hình học 8 của Cô Mai Phương (Chương trình GDPT 2018 - bộ sách Kết nối tri thức).
Học sinh lớp 8 (13-14 tuổi).

YÊU CẦU NGÔN NGỮ & SƯ PHẠM:
1. Lời văn gần gũi, ngắn gọn, dễ hiểu như lời cô giảng trên lớp.
2. TUYỆT ĐỐI KHÔNG chêm tiếng Anh ('hypotenuse', 'triangle'). Dùng đúng từ SGK: 'cạnh huyền', 'đường trung tuyến', 'cạnh góc vuông'.
3. NẾU CÓ TAM GIÁC CON: Phải nói rõ tên tam giác để học sinh không nhầm lẫn (ví dụ: 'Xét tam giác con AHB vuông tại H có cạnh huyền AB...').
4. ĐỘ DÀI:
   - Câu hỏi: Tối đa 2 câu, hỏi thẳng vào trọng tâm.
   - Mỗi lựa chọn (options): Ngắn gọn 1 đến 2 dòng. KHÔNG ghi tiền tố 'A. ', 'B. ' ở đầu câu.
5. KÝ HIỆU TOÁN: Phân số viết dạng \\dfrac{a}{b}, góc viết dạng \\widehat{ABC}.

CẤU TRÚC 3 BƯỚC THỬ THÁCH:
- Bước 1: Khai thác yếu tố quan trọng từ hình vẽ hoặc giả thiết ban đầu (chưa hỏi ngay kết luận đề bài).
- Bước 2: Dẫn dắt chứng minh quan hệ trung gian (cộng góc, hai tam giác bằng nhau, hình bình hành, đường trung bình).
- Bước 3: Đạt được điều cần chứng minh của đề bài.

KHI is_finished = true:
- Viết bài giải mẫu (full_solution) từng bước mẫu mực có xuống dòng từng ý rõ ràng bằng \\n để học sinh ghi vào vở. Giữ nguyên vẹn dòng tính toán chu vi, không ngắt vụn công thức cộng.
- BẮT BUỘC TẠO MÃ SVG (svg_code): Vẽ lại hình bài toán với khung viewBox='0 0 400 300', gồm đường thẳng nét xanh/đen rõ nét, điểm chấm tròn đen, chữ cái in hoa (A, B, C, P, Q, M, H, I, K...) to rõ nét và ký hiệu góc vuông.

BẮT BUỘC TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON SAU:
{
  "total_steps": 3,
  "feedback": "Khen ngợi/động viên ngắn 1 câu",
  "question": "Câu hỏi ngắn gọn, gợi ý trực diện vào mắt xích cần tìm",
  "options": [
    "Phương án ngắn 1",
    "Phương án ngắn 2",
    "Phương án ngắn 3",
    "Phương án ngắn 4"
  ],
  "correct_index": 0,
  "explanation": "Giải thích ngắn 2-3 câu vì sao đúng theo định lý nào trong SGK Toán 8",
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
            if max(img.size) > 1000:
                img.thumbnail((1000, 1000))
            prepared_contents.append(img)
        else:
            prepared_contents.append(item)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prepared_contents,
        config=config
    )

    text_out = response.text or ""
    if not text_out.strip():
        raise Exception("Nội dung phản hồi bị rỗng, vui lòng thử lại!")

    if is_json:
        clean_text = re.sub(r"^```json\s*|^```\s*|```$", "", text_out.strip(), flags=re.MULTILINE)
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
    <h1>📐 ĐẤU TRƯỜNG HÌNH HỌC 8</h1>
    <p>Học toán gợi mở cùng cô Mai Phương • Chinh phục thử thách từng bước</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎮 Thử thách hình học", "📝 Nộp Bài Tập", "📊 Bảng Điểm"])

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
    if "reward_svg" not in st.session_state:
        st.session_state.reward_svg = None

    with st.expander("📸 Đề bài / Hình vẽ bài toán", expanded=(st.session_state.card is None)):
        up_img = st.file_uploader("Tải/chụp ảnh bài tập cần chú ý lên đây:", type=["jpg", "png", "jpeg"], key="up_game_img")
        if up_img:
            st.session_state.img_data = Image.open(up_img)
            st.image(st.session_state.img_data, caption="Hình vẽ bài toán đang giải", use_container_width=True)

        if st.session_state.img_data and st.session_state.card is None:
            if st.button("🚀 Bắt đầu nhận Thử thách Bước 1!", type="primary", use_container_width=True):
                with st.spinner("Đợi cô một chút..."):
                    try:
                        p_start = "Tạo câu hỏi thử thách Bước 1 ngắn gọn, tập trung khai thác giả thiết khởi đầu."
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
        progress_val = min(int((curr / total) * 100), 100)
        st.progress(progress_val)

        st.markdown(f'<span class="step-badge">CỬA ẢI: BƯỚC {curr} / {total}</span>', unsafe_allow_html=True)
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
                    if not sol:
                        with st.spinner("Đang mở khóa bài giải và hình vẽ chuẩn..."):
                            p_sol = """Hãy viết bài giải mẫu mực hoàn chỉnh và kèm theo mã SVG vẽ lại hình bài toán này.
                            YÊU CẦU: Trình bày bài giải rõ ràng, các biểu thức tính chu vi/đoạn thẳng giữ nguyên vẹn trên cùng một dòng.
                            Trả về JSON: {"full_solution": "...", "svg_code": "<svg viewBox='0 0 400 300' ...>...</svg>"}"""
                            res_final = execute_gemini_request([st.session_state.img_data, p_sol], is_json=True)
                            sol = res_final.get("full_solution", "")
                            svg = res_final.get("svg_code", "")
                    st.session_state.reward = sol
                    st.session_state.reward_svg = svg

                st.markdown("""
                <div class="reward-box">
                    <h3 style="color: #15803D; margin-top:0;">🎁 PHẦN THƯỞNG: HÌNH VẼ & BÀI GIẢI MẪU HOÀN CHỈNH</h3>
                    <p style="color: #166534; font-size: 14px;">Em hãy quan sát hình vẽ chuẩn, đối chiếu lập luận và trình bày thật đẹp vào vở nhé!</p>
                </div>
                """, unsafe_allow_html=True)

                # HIỂN THỊ HÌNH VẼ MINH HỌA SVG
                if st.session_state.reward_svg and "<svg" in st.session_state.reward_svg:
                    st.markdown("#### 📐 Hình vẽ minh họa chuẩn xác:")
                    clean_svg_match = re.search(r"<svg[\s\S]*?</svg>", st.session_state.reward_svg)
                    if clean_svg_match:
                        st.markdown(f'<div class="svg-container">{clean_svg_match.group(0)}</div>', unsafe_allow_html=True)

                # HIỂN THỊ BÀI GIẢI LIỀN MẠCH, RÕ RÀNG
                st.markdown("#### 📝 Lời giải chi tiết:")
                formatted_solution = format_solution_step_by_step(st.session_state.reward)
                st.markdown(formatted_solution)

                st.write("")
                st.success("📝 **Bước tiếp theo:** Hãy chuyển sang tab **'Nộp Bài Tập'** ở trên để chụp ảnh bài vở nộp cô chấm nhé!")
            else:
                st.write("")
                if st.button("➡️ Sang thử thách tiếp theo", type="primary", use_container_width=True):
                    with st.spinner("Đang chuẩn bị cửa ải tiếp theo..."):
                        p_next = f"""Học sinh vừa vượt qua bước {curr} với đáp án đúng: {correct_text}. Tạo thử thách trắc nghiệm bước {curr + 1} / {total}. 
                        Nhớ giữ câu hỏi và 4 phương án ngắn gọn, dễ hiểu cho học sinh lớp 8. Phân số viết dạng \\dfrac{{a}}{{b}}, góc viết \\widehat{{ABC}}.
                        Nếu đây là bước cuối, hãy đặt is_finished = true, viết bài giải chi tiết từng ý vào full_solution và sinh mã vẽ hình chuẩn vào svg_code."""
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

# ================= TAB 2: NỘP BÀI & CHẤM ĐIỂM =================
with tab2:
    st.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 14px; margin-bottom: 20px;">
        <span style="font-weight: 700; color: #334155;">📋 Chấm tự luận bằng AI theo Rubric chuẩn môn Toán THCS</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        s_name = st.text_input("Họ và tên học sinh:")
    with c2:
        s_class = st.selectbox("Lớp:", ["8A13", "8A18"])

    topic = st.selectbox("Chọn dạng bài tập nộp:", [
        "Bài 1: Hình thang cân (Chụp kèm đề bài)",
        "Bài 2: Hình bình hành (Chụp kèm đề bài)",
        "Bài 3: Hình chữ nhật (Chụp kèm đề bài)",
        "Bài 4: Hình thoi (Chụp kèm đề bài)",
        "Bài 5: Hình vuông (Chụp kèm đề bài)",
        "Bài 6: Định lý Thalès và Tam giác đồng dạng",
        "Bài 7: Bài tập tổng hợp (Chụp kèm đề bài)"
    ])

    up_hw = st.file_uploader("📸 Chụp ảnh bài giải viết tay trong vở:", type=["jpg", "png", "jpeg"], key="hw_submit_img")

    if st.button("🚀 Nộp bài & Nhận kết quả chấm", type="primary", use_container_width=True):
        if not s_name:
            st.warning("Em hãy điền Họ và tên trước khi nộp nhé!")
        elif not up_hw:
            st.warning("Em chưa tải ảnh bài làm lên!")
        else:
            with st.spinner("Hệ thống đang chấm bài theo Rubric..."):
                hw_img = Image.open(up_hw)
                RUBRIC = f"""
                Bạn là Giám khảo chấm thi Toán THCS tại Việt Nam.
                Đề bài: "{topic}".
                Hãy đọc ảnh chụp bài làm tự luận viết tay và chấm điểm theo Rubric (Thang 10):
                1. Hình vẽ (2.0 điểm): Đúng hình, ký hiệu góc, trung điểm.
                2. Lập luận chứng minh (6.0 điểm): Căn cứ định lý, tính chất, dấu hiệu nhận biết, logic.
                3. Trình bày & Kết luận (2.0 điểm): Rõ ràng, kết luận chuẩn.

                ĐỊNH DẠNG BẮT BUỘC TRẢ VỀ:
                - Tổng điểm: [Ghi điểm số]/10
                - Nhận xét chi tiết:
                """
                score_res = execute_gemini_request([RUBRIC, hw_img])
                score_res_clean = format_math(score_res)

                score_match = re.search(r"(\d+([.,]\d+)?)\s*/\s*10", score_res_clean)
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

                st.success("Đã hoàn tất chấm bài và lưu kết quả vào sổ điểm!")
                st.markdown(f"### Kết quả của: **{s_name}** - Lớp **{s_class}**")
                st.markdown(score_res_clean)

# ================= TAB 3: BẢNG ĐIỂM & XUẤT GOOGLE SHEETS =================
with tab3:
    st.markdown("### 📊 Sổ Theo Dõi Điểm & Xuất Google Sheets")
    st.caption("Danh sách học sinh đã nộp bài tập và điểm số được chấm tự động.")

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
            file_name=f"Bang_Diem_HinhHoc8_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

        st.info("💡 **Cách mở trên Google Sheets:** Mở `sheets.google.com` ➔ Chọn **Tệp (File)** ➔ **Mở (Open)** ➔ Chọn **Tải lên (Upload)** file vừa tải về là toàn bộ bảng điểm sẽ hiển thị đầy đủ, chuẩn font tiếng Việt.")
