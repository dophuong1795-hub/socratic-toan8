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
    .geogebra-container {
        display: flex;
        justify-content: center;
        align-items: center;
        background: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-radius: 14px;
        padding: 12px;
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

# ================= BANNER TIÊU ĐỀ =================
st.markdown("""
<div class="hero-banner">
    <h1>📐 ĐẤU TRƯỜNG TOÁN HỌC 8</h1>
    <p>Chinh phục Đại số & Hình học cùng cô Mai Phương • Học tập gợi mở theo từng bước</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🎮 Thử Thách Tương Tác", 
    "📝 Nộp Bài Tập", 
    "🍄 Đại Chiến Bowser",
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

    with st.expander("📸 Đề bài / Ảnh chụp bài toán (Số học, Đại số hoặc Hình học)", expanded=(st.session_state.card is None)):
        up_game_img = st.file_uploader("Tải/chụp ảnh bài toán:", type=["jpg", "png", "jpeg"], key="up_game_img")
        math_mode = st.radio("Phân loại môn:", ["Tự động nhận diện", "Toán Số (Đại số)", "Toán Hình (Hình học)"], horizontal=True)
        
        if up_game_img:
            st.session_state.img_data = Image.open(up_game_img)
            st.image(st.session_state.img_data, caption="Ảnh đề bài đang xử lý", use_container_width=True)

        if st.session_state.img_data and st.session_state.card is None:
            if st.button("🚀 Bắt đầu nhận Thử thách Bước 1!", type="primary", use_container_width=True):
                with st.spinner("Đợi cô phân tích đề bài theo chuẩn chương trình SGK Toán 8..."):
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
                    ggb_cmds = card.get("ggb_commands", [])
                    if (not sol or not ggb_cmds) and st.session_state.img_data:
                        with st.spinner("Đang mở khóa bài giải hoàn chỉnh và lệnh dựng hình GeoGebra chính xác theo đề bài..."):
                            p_sol = """Hãy viết bài giải mẫu mực hoàn chỉnh đúng chuẩn kiến thức SGK Toán 8 (Kết nối tri thức). 
                            TUYỆT ĐỐI KHÔNG dùng kiến thức đường tròn.
                            Nếu là Toán Hình: BẮT BUỘC sinh mảng ggb_commands chứa các lệnh GeoGebra tiếng Anh để dựng đúng hình của đề bài (ví dụ tọa độ điểm, tam giác, đường cao).
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
                    <h3 style="color: #15803D; margin-top:0;">🎁 PHẦN THƯỞNG: BÀI GIẢI MẪU HOÀN CHỈNH</h3>
                    <p style="color: #166534; font-size: 14px;">Em hãy đối chiếu các bước lập luận và ghi chép cẩn thận vào vở nhé!</p>
                </div>
                """, unsafe_allow_html=True)

                if card.get("subject_type") == "geometry":
                    st.markdown("#### 📐 Bảng vẽ Hình học động GeoGebra (Dựng hình chuẩn theo đề bài):")
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
                st.success("📝 **Bước tiếp theo:** Hãy chuyển sang tab **'Nộp Bài Tập'** để nộp bài làm của em cho cô chấm nhé!")
            else:
                st.write("")
                if st.button("➡️ Sang thử thách tiếp theo", type="primary", use_container_width=True):
                    with st.spinner("Đang chuẩn bị cửa ải tiếp theo..."):
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
        if st.button("🔄 Giải bài tập khác", use_container_width=True):
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
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 14px; margin-bottom: 20px;">
        <span style="font-weight: 700; color: #334155;">📋 Chấm tự luận bằng AI theo Rubric chuẩn môn Toán THCS (Đại số & Hình học)</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        s_name = st.text_input("Họ và tên học sinh:")
    with c2:
        s_class = st.selectbox("Lớp:", ["8A13", "8A18"])

    topic = st.selectbox("Chọn chuyên đề bài tập nộp:", [
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

                    st.success("🎉 Đã hoàn tất chấm bài và tự động cập nhật vào sổ điểm của cô!")
                    st.markdown(f"### Kết quả của: **{s_name}** - Lớp **{s_class}**")
                    st.markdown(score_res_clean)
                except Exception as err:
                    st.error(f"Lỗi trong quá trình chấm bài: {err}")

# ================= TAB 3: MINIGAME ĐẠI CHIẾN BOWSER (TỨ GIÁC) =================
with tab3:
    st.subheader("🍄 Vượt Ải Tứ Giác - Đại Chiến Bowser")
    st.caption("Auto-runner vượt 5 ải Hình học 8 (KNTT) & Hạ gục Bowser nhận +5 điểm cộng thực tế từ Cô Mai Phương!")

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
    <body class="bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-slate-100 font-body min-h-screen flex flex-col items-center justify-start p-2 select-none">

      <div id="login-modal" class="fixed inset-0 z-50 bg-slate-950/95 backdrop-blur-md flex items-center justify-center p-4">
        <div class="bg-slate-900 border-2 border-pink-400/80 rounded-2xl max-w-md w-full p-6 shadow-2xl text-center relative overflow-hidden">
          <div class="absolute -top-10 -left-10 w-32 h-32 bg-pink-500/10 rounded-full blur-2xl"></div>
          <div class="absolute -bottom-10 -right-10 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl"></div>

          <div class="inline-block p-3.5 bg-gradient-to-tr from-pink-600 to-amber-500 rounded-2xl shadow-lg mb-3">
            <span class="font-pixel text-2xl text-white">M</span>
          </div>
          <h1 class="text-xl font-extrabold text-pink-400 mb-1">LỚP TOÁN CÔ MAI PHƯƠNG</h1>
          <p class="text-xs text-slate-300 mb-5">Đại chiến Bowser - Vượt ải Tứ Giác Toán 8</p>
          
          <div class="space-y-3.5 text-left mb-6">
            <div>
              <label class="block text-xs font-bold text-pink-300 uppercase mb-1">Họ và tên học sinh:</label>
              <input type="text" id="input-name" placeholder="Ví dụ: Nguyễn Văn An" class="w-full bg-slate-800/90 border border-pink-500/40 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-pink-400">
            </div>
            <div>
              <label class="block text-xs font-bold text-pink-300 uppercase mb-1">Lớp:</label>
              <input type="text" id="input-class" placeholder="Ví dụ: 8A13" class="w-full bg-slate-800/90 border border-pink-500/40 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-pink-400">
            </div>
          </div>

          <div class="bg-slate-800/80 border border-pink-500/30 rounded-xl p-3 text-xs text-slate-200 text-left mb-5 space-y-1.5 shadow-inner">
            <p>• 🌸 <b>5 Mạng sống (❤️❤️❤️❤️❤️)</b>. Mario tự động chạy!</p>
            <p>• ⏱️ Thời gian: <b>15s</b> - <b>30s</b> tùy cấp độ tư duy.</p>
            <p>• 🎁 Hạ gục Bowser nhận ngay <b>+5 Điểm cộng thực tế</b> từ Cô Mai Phương!</p>
          </div>

          <button id="btn-start-game" class="w-full py-3.5 bg-gradient-to-r from-pink-600 via-purple-600 to-amber-500 hover:opacity-90 text-white font-extrabold text-sm rounded-xl shadow-lg transition transform active:scale-95">
            BẮT ĐẦU VƯỢT ẢI NGAY 🚀
          </button>
        </div>
      </div>

      <header class="w-full max-w-2xl flex items-center justify-between bg-slate-900/90 border border-slate-800 px-3 py-2 rounded-2xl mb-2 shadow-lg">
        <div class="flex items-center space-x-2">
          <div class="w-7 h-7 rounded-lg bg-pink-600 flex items-center justify-center font-pixel text-white text-[10px]">M</div>
          <div>
            <h2 class="text-xs font-extrabold text-pink-400 leading-tight">LỚP TOÁN CÔ MAI PHƯƠNG</h2>
            <p id="hud-student" class="text-[10px] text-slate-300">Học sinh: Đang kết nối...</p>
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

      <main id="game-arena" class="relative w-full max-w-2xl aspect-[16/9] bg-sky-400 rounded-2xl border-2 border-pink-400/80 shadow-2xl overflow-hidden">
        <canvas id="gameCanvas" width="860" height="484" class="w-full h-full block"></canvas>
      </main>

      <div id="quiz-modal" class="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-sm flex items-center justify-center p-3 hidden">
        <div class="bg-slate-900 border-2 border-pink-500/80 rounded-2xl max-w-xl w-full p-4 shadow-2xl flex flex-col max-h-[92vh] overflow-y-auto">
          
          <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
            <span id="quiz-level-badge" class="px-2.5 py-1 bg-pink-500/20 text-pink-300 border border-pink-500/40 rounded-lg text-xs font-bold uppercase">
              NHẬN BIẾT (15s)
            </span>
            <div class="flex items-center space-x-1.5 font-pixel text-xs text-amber-400">
              <span>⏳</span>
              <span id="quiz-timer-text">15s</span>
            </div>
          </div>

          <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-3">
            <div id="quiz-timer-bar" class="h-full bg-pink-500 transition-all duration-100 ease-linear" style="width: 100%;"></div>
          </div>

          <div id="quiz-question-text" class="text-sm font-bold text-pink-200 mb-3 leading-relaxed">
            Đề bài...
          </div>

          <div id="quiz-options-container" class="space-y-2 mb-2"></div>

          <div id="quiz-short-container" class="space-y-2 mb-2 hidden">
            <input type="text" id="quiz-short-input" placeholder="Nhập đáp số hoặc tên hình..." autocomplete="off" class="w-full bg-slate-800 border-2 border-pink-500/60 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-pink-400">
            <button id="quiz-short-submit" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-md transition">
              XÁC NHẬN ĐÁP ÁN (ENTER)
            </button>
          </div>

          <div id="quiz-feedback" class="mt-2 text-xs font-semibold min-h-[20px]"></div>
        </div>
      </div>

      <div id="stage-clear-modal" class="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-sm flex items-center justify-center p-4 hidden">
        <div class="bg-slate-900 border-2 border-emerald-400 rounded-2xl max-w-md w-full p-6 text-center shadow-2xl">
          <div class="text-3xl mb-2">🌟</div>
          <h3 id="stage-clear-title" class="text-base font-extrabold text-emerald-400 mb-1">HOÀN THÀNH ẢI!</h3>
          <p class="text-xs text-pink-400 font-bold mb-3">LỜI DẶN DÒ TỪ CÔ MAI PHƯƠNG</p>
          
          <div id="stage-clear-msg" class="bg-slate-800/80 border border-slate-700 rounded-xl p-3.5 text-xs text-slate-200 text-left mb-5 leading-relaxed"></div>

          <button id="btn-continue-next-stage" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl transition shadow-lg">
            TIẾP TỤC TIẾN LÊN ẢI TIẾP THEO ⏩
          </button>
        </div>
      </div>

      <div id="summary-modal" class="fixed inset-0 z-50 bg-slate-950/95 backdrop-blur-md flex items-center justify-center p-3 hidden">
        <div class="bg-slate-900 border-2 border-pink-500 rounded-2xl max-w-md w-full p-5 shadow-2xl flex flex-col max-h-[92vh] overflow-y-auto">
          
          <div class="text-center mb-3">
            <span id="summary-badge-icon" class="text-3xl">🏆</span>
            <h2 id="summary-title" class="text-lg font-extrabold text-pink-400 mt-1">VINH DANH CHIẾN THẮNG!</h2>
            <p id="summary-subtitle" class="text-[11px] text-emerald-400 font-semibold">Đã xuất sắc vượt qua 5 Ải & Hạ gục Bowser</p>
          </div>

          <div class="bg-slate-800/80 border border-slate-700 rounded-xl p-3 mb-3 grid grid-cols-2 gap-2 text-xs">
            <div><span class="text-slate-400">Học sinh:</span> <b id="sum-name" class="text-white">...</b></div>
            <div><span class="text-slate-400">Lớp:</span> <b id="sum-class" class="text-white">...</b></div>
            <div><span class="text-slate-400">Mã đề:</span> <b id="sum-examcode" class="text-pink-300">...</b></div>
            <div><span class="text-slate-400">Tổng điểm:</span> <b id="sum-score" class="text-pink-400 font-pixel">0</b></div>
            <div class="col-span-2 bg-emerald-950/60 border border-emerald-500/40 p-2 rounded-lg text-emerald-300 text-center font-bold">
              🎁 Phần thưởng: <span id="sum-bonus" class="text-pink-300 font-extrabold">+5 ĐIỂM CỘNG</span> từ Cô Mai Phương!
            </div>
          </div>

          <div id="summary-teacher-note" class="bg-pink-950/30 border border-pink-500/30 rounded-xl p-3 text-xs text-pink-200 mb-3 leading-relaxed"></div>

          <div id="sync-status-box" class="border border-slate-700 bg-slate-950/60 rounded-xl p-2.5 text-center mb-3">
            <div id="sync-status-text" class="text-xs text-yellow-400 font-medium">
              ⏳ Đang kết nối gửi kết quả về Google Sheets...
            </div>
            <button id="btn-retry-sync" class="mt-2 hidden px-3 py-1 bg-pink-500 hover:bg-pink-400 text-slate-950 font-bold text-xs rounded-lg transition">
              🔄 Thử gửi lại dữ liệu
            </button>
          </div>

          <button onclick="location.reload()" class="w-full py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white font-bold text-xs rounded-xl transition">
            CHƠI LẠI VỚI BỘ ĐỀ MỚI 🔁
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

        function sndJump() { playTone(180, 'square', 0.15, 0.12); setTimeout(() => playTone(450, 'square', 0.15, 0.12), 60); }
        function sndCoin() { playTone(988, 'square', 0.08, 0.15); setTimeout(() => playTone(1318, 'square', 0.22, 0.15), 70); }
        function sndFireball() { playTone(320, 'triangle', 0.12, 0.25); setTimeout(() => playTone(140, 'sawtooth', 0.3, 0.25), 80); }
        function sndWrong() { playTone(200, 'sawtooth', 0.2, 0.2); setTimeout(() => playTone(120, 'sawtooth', 0.3, 0.2), 150); }
        function sndRoar() { playTone(85, 'sawtooth', 0.45, 0.3); setTimeout(() => playTone(60, 'sawtooth', 0.5, 0.3), 180); }

        let bgmInterval = null;
        const bgmNotes = [261.6, 261.6, 0, 261.6, 0, 207.6, 233.1, 261.6];
        let noteIdx = 0;
        function startBgm() {
          if (bgmInterval || isSoundMuted) return;
          bgmInterval = setInterval(() => {
            if (!gameState.isPaused && !gameState.isGameOver && bgmNotes[noteIdx] > 0) {
              playTone(bgmNotes[noteIdx], 'square', 0.1, 0.03);
            }
            noteIdx = (noteIdx + 1) % bgmNotes.length;
          }, 220);
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
            code: "CMP-8A-" + Math.floor(1000 + Math.random() * 9000),
            stages: [
              { name: "Màn 1: Tứ giác lồi", questions: shuffle(rawQuestionPool.stage1).slice(0, 3) },
              { name: "Màn 2: Hình thang cân", questions: shuffle(rawQuestionPool.stage2).slice(0, 4) },
              { name: "Màn 3: Hình bình hành", questions: shuffle(rawQuestionPool.stage3).slice(0, 5) },
              { name: "Màn 4: Hình chữ nhật", questions: shuffle(rawQuestionPool.stage4).slice(0, 5) },
              { name: "Màn 5: Hình thoi & Hình vuông", questions: shuffle(rawQuestionPool.stage5).slice(0, 5) },
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

        const mario = { x: 100, y: 340, w: 32, h: 42, vy: 0, isJumping: false, legAnim: 0 };
        const clouds = [
          { x: 120, y: 60, w: 70, h: 30, speed: 0.6 },
          { x: 450, y: 90, w: 90, h: 35, speed: 0.4 },
          { x: 720, y: 50, w: 60, h: 25, speed: 0.7 }
        ];

        function triggerShake() {
          arenaEl.classList.add("shake");
          setTimeout(() => arenaEl.classList.remove("shake"), 380);
        }

        function updateWorld() {
          if (gameState.isPaused || gameState.isGameOver) return;
          mario.legAnim += 0.2;

          clouds.forEach(c => {
            c.x -= c.speed;
            if (c.x < -100) c.x = 900;
          });

          if (mario.isJumping) {
            mario.y += mario.vy;
            mario.vy += 0.8;
            if (mario.y >= 340) { mario.y = 340; mario.isJumping = false; }
          }

          if (fireball.active) {
            fireball.x += fireball.vx;
            if (fireball.x >= 680) {
              fireball.active = false;
              triggerShake();
              sndFireball();
            }
          }

          if (!gameState.inBossFight) {
            mysteryBox.x -= 3.2;
            if (mysteryBox.x <= 220 && mysteryBox.active) {
              mysteryBox.active = false;
              openNextQuestion();
            }
          }
        }

        function drawWorld() {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          
          const skyGrad = ctx.createLinearGradient(0, 0, 0, 400);
          skyGrad.addColorStop(0, '#38bdf8');
          skyGrad.addColorStop(1, '#bae6fd');
          ctx.fillStyle = skyGrad;
          ctx.fillRect(0, 0, canvas.width, canvas.height);

          ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
          clouds.forEach(c => {
            ctx.beginPath();
            ctx.arc(c.x, c.y + 10, 16, 0, Math.PI * 2);
            ctx.arc(c.x + 18, c.y, 22, 0, Math.PI * 2);
            ctx.arc(c.x + 38, c.y + 10, 16, 0, Math.PI * 2);
            ctx.fill();
          });

          ctx.fillStyle = "rgba(251, 146, 60, 0.2)";
          ctx.beginPath();
          ctx.arc(750, 150, 45, 0, Math.PI * 2);
          ctx.arc(800, 130, 35, 0, Math.PI * 2);
          ctx.fill();

          ctx.fillStyle = "#16a34a";
          ctx.fillRect(0, 382, canvas.width, 18);
          ctx.fillStyle = "#78350f";
          ctx.fillRect(0, 400, canvas.width, 84);

          if (!gameState.inBossFight && mysteryBox.x > -60) {
            ctx.fillStyle = "#f59e0b";
            ctx.fillRect(mysteryBox.x, mysteryBox.y, 48, 48);
            ctx.strokeStyle = "#b45309";
            ctx.lineWidth = 4;
            ctx.strokeRect(mysteryBox.x, mysteryBox.y, 48, 48);
            
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 26px 'Press Start 2P', monospace";
            ctx.fillText("?", mysteryBox.x + 13, mysteryBox.y + 34);
          }

          const mx = mario.x;
          const my = mario.y;
          ctx.fillStyle = "#dc2626";
          ctx.fillRect(mx + 4, my, 24, 12);
          ctx.fillRect(mx + 2, my + 6, 28, 6);
          ctx.fillStyle = "#fed7aa";
          ctx.fillRect(mx + 6, my + 12, 20, 12);
          ctx.fillStyle = "#ef4444";
          ctx.fillRect(mx + 2, my + 24, 28, 12);
          ctx.fillStyle = "#1d4ed8";
          ctx.fillRect(mx + 6, my + 34, 20, 10);
          
          const legOffset = Math.sin(mario.legAnim) * 5;
          ctx.fillStyle = "#78350f";
          ctx.fillRect(mx + 4, my + 42, 8, 6 + legOffset);
          ctx.fillRect(mx + 20, my + 42, 8, 6 - legOffset);

          if (fireball.active) {
            ctx.fillStyle = "#f97316";
            ctx.beginPath();
            ctx.arc(fireball.x, fireball.y, 14, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#fef08a";
            ctx.beginPath();
            ctx.arc(fireball.x - 3, fireball.y - 3, 5, 0, Math.PI * 2);
            ctx.fill();
          }

          if (gameState.inBossFight && !gameState.defeatedBoss) {
            const bx = 670, by = 285;
            ctx.fillStyle = "#064e3b";
            ctx.beginPath();
            ctx.arc(bx + 40, by + 45, 46, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = "#d97706";
            ctx.fillRect(bx - 10, by + 25, 42, 54);
            ctx.fillStyle = "#dc2626";
            ctx.fillRect(bx - 4, by + 4, 30, 22);

            ctx.fillStyle = "#000000";
            ctx.fillRect(bx - 25, by - 38, 130, 18);
            ctx.fillStyle = "#ef4444";
            const hpW = (gameState.bossHp / gameState.bossMaxHp) * 122;
            ctx.fillRect(bx - 21, by - 35, Math.max(0, hpW), 12);
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 9px monospace";
            ctx.fillText("BOWSER HP: " + gameState.bossHp + "/" + gameState.bossMaxHp, bx - 16, by - 24);
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
          if (!name || !sClass) { alert("Em vui lòng nhập đầy đủ Họ tên và Lớp nhé!"); return; }
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
            badgeEl.textContent = "⚔️ BOWSER HP: " + gameState.bossHp + "/" + gameState.bossMaxHp + " - VẬN DỤNG CAO";
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
              handleAnswer(false, "Đã hết thời gian!");
            }
          }, 1000);

          if (currentQ.type === "mcq") {
            optionsBox.classList.remove("hidden");
            shortBox.classList.add("hidden");
            optionsBox.innerHTML = "";

            currentQ.answers.forEach((ans, idx) => {
              const btn = document.createElement("button");
              btn.className = "w-full text-left bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl p-3 text-xs font-semibold";
              btn.innerHTML = '<span class="text-pink-400 font-bold">' + (idx + 1) + '.</span> ' + ans;
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
            feedbackEl.innerHTML = '<span class="text-emerald-400 font-bold">🎉 CHÍNH XÁC! +' + (gameState.inBossFight ? 300 : 100) + ' Điểm</span>';

            mario.isJumping = true;
            mario.vy = -12;

            if (gameState.inBossFight) {
              fireball.active = true;
              fireball.x = mario.x + 30;
              fireball.y = mario.y + 16;
              fireball.vx = 14;
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
            feedbackEl.innerHTML = '<span class="text-rose-400 font-bold">❌ ' + (customReason || "Chưa chính xác!") + '</span><br><span class="text-[11px] text-slate-300">Ghi nhớ: ' + currentQ.explain + '</span>';

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
          "Cô Mai Phương rất vui khi em nắm vững tính chất góc tứ giác lồi! Sang Ải 2 nhé!",
          "Làm tốt lắm! Em đã thuộc lòng tính chất hai đường chéo của hình thang cân. Sang Ải 3 nào!",
          "Xuất sắc! Tính chất hai đường chéo cắt nhau tại trung điểm là chìa khóa vàng. Tiến lên Ải 4!",
          "Tuyệt vời! Em đã vận dụng thành thạo tính chất hình chữ nhật. Ải 5 đang chờ đón!",
          "Hoàn thành 5 Ải! Hãy tập trung cao độ đánh bại Bowser để nhận +5 Điểm cộng nhé!"
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
            mysteryBox.x = 760;
            mysteryBox.active = true;
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
            mysteryBox.x = 760;
            mysteryBox.active = true;
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
            document.getElementById("summary-title").textContent = "CHIẾN THẮNG TUYỆT ĐỐI!";
            document.getElementById("sum-bonus").textContent = "+5 ĐIỂM CỘNG";
            document.getElementById("summary-teacher-note").innerHTML = '🎉 <b>Lời khen từ Cô Mai Phương:</b> Em đã xuất sắc hạ gục Bowser! Cô cộng <b>+5 điểm thực tế</b> vào sổ điểm cho em!';
          } else {
            document.getElementById("summary-badge-icon").textContent = "🛡️";
            document.getElementById("summary-title").textContent = "DỪNG BƯỚC THỬ THÁCH";
            document.getElementById("sum-bonus").textContent = "0 ĐIỂM";
            document.getElementById("summary-teacher-note").innerHTML = '💡 <b>Lời dặn từ Cô Mai Phương:</b> Em đã nỗ lực đạt <b>' + gameState.score + ' điểm</b>. Hãy xem lại bài và bấm Chơi lại để phục thù nhé!';
          }

          document.getElementById("summary-modal").classList.remove("hidden");

          const payload = {
            time: new Date().toLocaleString("vi-VN"),
            examCode: gameState.examData.code,
            name: gameState.studentName,
            student_class: gameState.studentClass,
            score: gameState.score,
            topic: "Minigame Tứ Giác (Bowser)",
            feedback: isVictory ? "Hạ gục Bowser (+5đ)" : "Chưa diệt Bowser"
          };

          gameState.lastPayload = payload;
          syncToGoogleSheets(payload);
        }

        async function syncToGoogleSheets(payload) {
          const syncStatusText = document.getElementById("sync-status-text");
          const retryBtn = document.getElementById("btn-retry-sync");

          syncStatusText.innerHTML = "⏳ Đang kết nối gửi kết quả về Google Sheets của cô...";
          syncStatusText.className = "text-xs text-yellow-400 font-medium";
          retryBtn.classList.add("hidden");

          try {
            await fetch(GOOGLE_SCRIPT_WEBAPP_URL, {
              method: "POST",
              mode: "no-cors",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });

            syncStatusText.innerHTML = "✅ Đã lưu kết quả thành công vào Google Sheets của Cô Mai Phương!";
            syncStatusText.className = "text-xs text-emerald-400 font-bold";
          } catch (err) {
            syncStatusText.innerHTML = '<div class="text-rose-400 font-bold">⚠️ Chưa có mạng! Kết quả chưa gửi được.</div><div class="text-[10px] text-slate-300 mt-1">Em hãy chụp màn hình gửi cô hoặc bấm nút thử lại:</div>';
            retryBtn.classList.add("hidden");
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
    st.markdown("### 🔒 Khu Vực Quản Lý Điểm Của Giáo Viên")
    st.caption("Dữ liệu điểm số được bảo mật để đảm bảo tính riêng tư của học sinh.")

    teacher_password = st.text_input("🔑 Nhập mật khẩu giáo viên để xem sổ điểm:", type="password", key="teacher_pass_tab4")
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
                st.download_button(
                    label="📗 Tải file bảng điểm (.CSV cho Google Sheets)",
                    data=csv_data,
                    file_name=f"Bang_Diem_Toan8_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
        else:
            st.error("⛔ Mật khẩu không chính xác! Học sinh vui lòng không truy cập khu vực này.")
    else:
        st.info("👉 Vui lòng nhập mật khẩu để mở khóa sổ theo dõi điểm.")
