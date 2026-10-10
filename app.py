import streamlit as st
import requests
from PIL import Image, ImageOps
import re
import base64
import io
import json
import pandas as pd
from datetime import datetime

# ================= CẤU HÌNH GIAO DIỆN STREAMLIT =================
st.set_page_config(
    page_title="Đấu Trường Hình Học 8 - Cô Mai Phương",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CSS TỐI ƯU GIAO DIỆN HIỆN ĐẠI =================
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
        padding: 14px 18px !important;
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        text-align: left !important;
        justify-content: flex-start !important;
        line-height: 1.6 !important;
        margin-bottom: 8px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
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
    .solution-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #4F46E5;
        padding: 18px 20px;
        border-radius: 10px;
        line-height: 2;
        font-size: 16px;
        color: #1E293B;
        margin-top: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ================= KIỂM TRA API KEY =================
API_KEY = st.secrets.get("OPENROUTER_API_KEY")
if not API_KEY:
    st.error("Chưa cấu hình OPENROUTER_API_KEY trong Secrets của Streamlit Cloud!")
    st.stop()

MODELS_PRIORITY = [
    "google/gemini-2.0-flash-lite-001",
    "google/gemini-2.0-flash-001",
    "google/gemini-flash-1.5",
    "google/gemini-2.0-flash-lite-preview:free"
]

# ================= BỘ LỌC CHUẨN HÓA TOÁN HỌC 8 =================
def clean_math_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""

    # 1. Cắt bỏ hoàn toàn mọi tàn dư Thinking Process và User Safety
    text = re.sub(r"^(?:User Safety|Safety|Thinking Process|Thought|Reasoning):[^\n]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    text = text.replace("undefined", "")

    # 2. Khử triệt để các từ ngoại lai
    text = re.sub(r"\\implies|\bimplies\b", " suy ra ", text, flags=re.IGNORECASE)
    text = re.sub(r"\\because|\bbecause\b", " vì ", text, flags=re.IGNORECASE)
    text = re.sub(r"\\therefore|\btherefore\b", " do đó ", text, flags=re.IGNORECASE)
    text = re.sub(r"\bhypotenuse\b", "cạnh huyền", text, flags=re.IGNORECASE)
    text = re.sub(r"\btriangle\b", "tam giác", text, flags=re.IGNORECASE)

    # 3. CHUẨN HÓA PHÂN SỐ CÓ NÉT GẠCH NGANG: \dfrac{a}{b}
    text = re.sub(r"(?<![a-zA-Z0-9_\$])([A-Z]{1,2}|\d+)\s*/\s*([A-Z]{1,2}|\d+)(?![a-zA-Z0-9_\$])", r"$\\dfrac{\1}{\2}$", text)
    text = re.sub(r"\$?\\frac\{([^}]+)\}\{([^}]+)\}\$?", r"$\\dfrac{\1}{\2}$", text)

    # 4. CHUẨN HÓA GÓC: Chuyển ∠ABC, \widehat{ABC}, góc ABC về $\widehat{ABC}$
    def replace_angle(match):
        pts = match.group(1).strip()
        return f"$\\widehat{{{pts}}}$"

    text = re.sub(r"(?:[∠∡∢]|\\angle\s*|\\widehat\{|\\hat\{|\bgóc\s+)([A-Z]{1,3})\b\}?", replace_angle, text)

    # 5. Xóa lỗi lặp từ
    text = re.sub(r"góc\s+góc\s+", "góc ", text, flags=re.IGNORECASE)
    text = re.sub(r"tam giác\s+tam giác\s+", "tam giác ", text, flags=re.IGNORECASE)
    text = re.sub(r"\btư giác\b", "tứ giác", text, flags=re.IGNORECASE)

    # 6. Ký hiệu hình học: song song //, vuông góc ⊥, thuộc
    text = re.sub(r"\b([A-Z]{2})\s*(?://|riangle|°)\s*([A-Z]{2})\b", r"\1 // \2", text)
    text = re.sub(r"\\?parallel", " // ", text)
    text = re.sub(r"\\perp|£", " ⊥ ", text)
    text = re.sub(r"\b([A-Z])\s*(?://|riangle|°)\s*([A-Z]{2})\b", r"\1 thuộc \2", text)
    text = text.replace(r"\in", " thuộc ")

    # 7. Chuẩn hóa số đo độ
    text = re.sub(r"\b(1[0-8]0|[3469]0)\s*(?:\^?\s*(?:circ|°)|(?=\s*[\.,\)\s]|$))(?!\s*(?:bước|cạnh|đoạn|tam giác))", r"\1°", text)
    text = text.replace("°°", "°")

    text = re.sub(r"\s+", " ", text)
    return text.strip()

def format_solution_to_clean_html(raw_solution: str) -> str:
    cleaned = clean_math_text(raw_solution)
    raw_lines = re.split(r'[\r\n]+', cleaned)
    valid_lines = []

    for l in raw_lines:
        s = l.strip()
        if not s or s in ["*", "•", "-", ".", "**", "***"]:
            continue
        s = re.sub(r"^[\*\•\-\s]+", "", s).strip()
        if not s:
            continue
        valid_lines.append(s)

    html_items = []
    for item in valid_lines:
        if re.match(r"^(\*\*?[a-z]\)|[a-z]\))\s*", item, flags=re.IGNORECASE):
            html_items.append(f"<br><strong style='color:#4F46E5; font-size:16px;'>{item}</strong>")
        elif "BÀI GIẢI" in item.upper():
            html_items.append(f"<strong style='color:#1E293B; font-size:16px;'>{item}</strong>")
        else:
            html_items.append(f"<div style='margin-left: 14px; margin-bottom: 8px;'>• {item}</div>")

    return "".join(html_items)

# ================= HÀM BÓC TÁCH JSON TOÀN DIỆN =================
def safe_parse_json(text: str):
    text = re.sub(r"^(?:User Safety|Safety|Thinking Process):[^\n]*\n?", "", text, flags=re.IGNORECASE)
    
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        json_str = match.group(0)
        json_str = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', json_str)         try:             data = json.loads(json_str, strict=False)             q = data.get("question", "")             opts = data.get("options", [])             if q and len(opts) >= 4:                 return {                     "question": clean_math_text(q),                     "options": [clean_math_text(o) for o in opts[:4]],                     "correct_index": int(data.get("correct_index", 0)) \% 4,                     "explanation": clean_math_text(data.get("explanation", "")),                     "full_solution": clean_math_text(data.get("full_solution", ""))                 }         except Exception:             pass      # Bộ trích xuất fallback khi JSON bị lỗi định dạng     lines = [l.strip() for l in text.split("\n") if l.strip()]     question = "Dựa vào hình vẽ và giả thiết bài toán, khẳng định nào sau đây là đúng?"     options = []     for l in lines:         if re.match(r"^[A-D][\.\:\)]\s*", l):
            options.append(re.sub(r"^[A-D][\.\:\)]\s*", "", l))
    
    while len(options) < 4:
        options.append(f"Khẳng định {len(options)+1}")

    return {
        "question": clean_math_text(question),
        "options": [clean_math_text(o) for o in options[:4]],
        "correct_index": 0,
        "explanation": "Căn cứ theo định lý và tính chất trong SGK Toán 8.",
        "full_solution": ""
    }

# ================= PROMPT CHUẨN CHO GEMINI VISION =================
GAME_PROMPT = """
Bạn là Trợ lý Sư phạm Hình học 8 của Cô Mai Phương (Chương trình GDPT 2018 - bộ sách Kết nối tri thức).
Nhiệm vụ: Đọc kỹ hình ảnh bài toán và tạo câu hỏi gợi mở trắc nghiệm Socratic từng bước.

QUY TẮC SƯ PHẠM:
- Bước 1: Khai thác mắt xích giả thiết ban đầu (ví dụ: tam giác vuông con AHB có đường trung tuyến HI ứng với cạnh huyền AB nên HI = \\dfrac{AB}{2}, hoặc tam giác AHI cân...). TUYỆT ĐỐI KHÔNG hỏi ngay điều kết luận của đề bài.
- Bước 2: Dẫn dắt chứng minh quan hệ trung gian (cộng góc, hai tam giác bằng nhau, hình bình hành...).
- Bước 3: Đạt đến kết luận cuối cùng của đề bài.
- KÝ HIỆU PHÂN SỐ: Viết dạng phân số có gạch ngang: \\dfrac{AB}{2}, \\dfrac{BC}{2}.
- KÝ HIỆU GÓC: Viết 'góc ABC' hoặc '\\widehat{ABC}'. Không dùng ký tự lạ ∠. Không dùng tiếng Anh.

BẮT BUỘC TRẢ VỀ DUY NHẤT 1 KHỐI JSON HỢP LỆ VỚI CẤU TRÚC SAU:
{
  "question": "Nội dung câu hỏi ngắn gọn",
  "options": [
    "Phương án A cụ thể",
    "Phương án B cụ thể",
    "Phương án C cụ thể",
    "Phương án D cụ thể"
  ],
  "correct_index": 0,
  "explanation": "Giải thích ngắn 2 câu theo SGK Toán 8",
  "full_solution": ""
}
"""

def execute_openrouter_request(inputs, system_prompt=GAME_PROMPT):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Socratic Geometry Game - Co Mai Phuong"
    }

    content_parts = []
    for item in inputs:
        if isinstance(item, str):
            content_parts.append({"type": "text", "text": item})
        elif isinstance(item, Image.Image):
            img_to_send = ImageOps.exif_transpose(item)
            if max(img_to_send.size) > 800:
                img_to_send.thumbnail((800, 800))

            buffered = io.BytesIO()
            img_to_send.convert("RGB").save(buffered, format="JPEG", quality=80)
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"
                }
            })

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content_parts}
    ]

    payload = {
        "model": MODELS_PRIORITY[0],
        "models": MODELS_PRIORITY,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1200
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
    except Exception:
        raise Exception("Thời gian phản hồi quá lâu, em bấm thử lại nhé!")

    if resp.status_code != 200:
        raise Exception(f"Máy chủ AI bận ({resp.status_code}), em bấm lại nhé!")

    res_data = resp.json()
    choices = res_data.get("choices", [])
    if not choices or not choices[0].get("message"):
        raise Exception("Mô hình bận, em bấm thử lại nhé!")

    msg = choices[0]["message"]
    text_out = (msg.get("content") or "").strip()
    if not text_out:
        text_out = (msg.get("reasoning") or "").strip()

    if not text_out:
        raise Exception("Nội dung phản hồi rỗng, vui lòng bấm lại!")

    return text_out

if "submission_history" not in st.session_state:
    st.session_state.submission_history = []

# ================= BANNER TIÊU ĐỀ =================
st.markdown("""
<div class="hero-banner">
    <h1>📐 ĐẤU TRƯỜNG HÌNH HỌC 8</h1>
    <p>Học toán gợi mở cùng Cô Mai Phương • Chinh phục thử thách từng bước</p>
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

    with st.expander("📸 Đề bài / Hình vẽ bài toán", expanded=(st.session_state.card is None)):
        up_img = st.file_uploader("Tải/chụp ảnh bài tập cần gợi ý lên đây:", type=["jpg", "png", "jpeg"], key="up_game_img")
        if up_img:
            st.session_state.img_data = Image.open(up_img)
            st.image(st.session_state.img_data, caption="Hình vẽ / Đề bài đang giải", use_column_width=True)

        if st.session_state.img_data and st.session_state.card is None:
            if st.button("🚀 Bắt đầu nhận Thử thách Bước 1!", type="primary", use_container_width=True):
                with st.spinner("Cô Mai Phương đang chuẩn bị câu hỏi gợi ý..."):
                    try:
                        p_start = """Đọc đề bài trong ảnh. Tạo thử thách Bước 1: 
                        Khai thác tính chất khởi đầu quan trọng nhất (như tính chất trung tuyến trong tam giác vuông con bằng nửa cạnh huyền: \\dfrac{AB}{2}, tam giác cân...). Tuyệt đối không hỏi điều kết luận của đề bài.
                        Bắt buộc trả về đúng định dạng JSON có question, options (4 lựa chọn cụ thể), correct_index, explanation."""
                        raw_resp = execute_openrouter_request([st.session_state.img_data, p_start])
                        st.session_state.card = safe_parse_json(raw_resp)
                        st.session_state.total_steps = 3
                        st.session_state.step = 1
                        st.session_state.answered = False
                        st.session_state.reward = None
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
        st.markdown(f"#### 🎯 {card.get('question', '')}")
        st.write("")

        opts = card.get("options", [])
        correct = card.get("correct_index", 0)

        if not st.session_state.answered:
            st.markdown("**👉 Em hãy bấm chọn một đáp án đúng nhất:**")
            for idx, opt in enumerate(opts):
                button_text = f"{chr(65+idx)}. {opt}"
                if st.button(button_text, key=f"btn_opt_{idx}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.selected_idx = idx
                    st.rerun()
        else:
            sel = st.session_state.selected_idx
            sel_text = opts[sel] if (sel is not None and sel < len(opts)) else ""
            correct_text = opts[correct] if correct < len(opts) else ""

            if sel == correct:
                st.success("🎉 **Chính xác!** Em đã lựa chọn hướng tư duy rất chuẩn.")
            else:
                st.error("❌ **Chưa chính xác.**")
                st.markdown(f"Đáp án đúng là: **{chr(65+correct)}. {correct_text}**")

            st.markdown(f"**💡 Hướng suy luận:** {card.get('explanation', '')}")

            is_finish = (curr >= total)

            if is_finish:
                st.balloons()
                st.success("🏆 **XUẤT SẮC! Em đã hoàn thành toàn bộ sơ đồ chứng minh!**")

                if not st.session_state.reward:
                    sol = card.get("full_solution", "")
                    if not sol:
                        with st.spinner("Đang mở khóa bài giải chuẩn mực..."):
                            p_sol = """Hãy viết bài giải mẫu mực hoàn chỉnh cho đề bài trong ảnh.
                            YÊU CẦU: Trình bày từng bước có căn cứ định lý, mở ngoặc rõ ràng, xuống dòng sạch sẽ. Phân số viết dạng gạch ngang \\dfrac{a}{b}.
                            Trả về JSON: {"full_solution": "..."}"""
                            raw_sol = execute_openrouter_request([st.session_state.img_data, p_sol])
                            sol_parsed = safe_parse_json(raw_sol)
                            sol = sol_parsed.get("full_solution") or raw_sol
                    st.session_state.reward = sol

                st.markdown("""
                <div class="reward-box">
                    <h3 style="color: #15803D; margin-top:0;">🎁 PHẦN THƯỞNG: BÀI GIẢI MẪU HOÀN CHỈNH</h3>
                    <p style="color: #166534; font-size: 14px;">Em hãy đối chiếu các bước lập luận và trình bày thật đẹp vào vở nhé!</p>
                </div>
                """, unsafe_allow_html=True)

                clean_solution_html = format_solution_to_clean_html(st.session_state.reward)
                st.markdown(f'<div class="solution-box">{clean_solution_html}</div>', unsafe_allow_html=True)

                st.write("")
                st.success("📝 **Bước tiếp theo:** Hãy chuyển sang tab **'Nộp Bài Tập'** ở trên để chụp ảnh bài vở nộp cô chấm nhé!")
            else:
                st.write("")
                if st.button("➡️ Sang thử thách tiếp theo", type="primary", use_container_width=True):
                    with st.spinner("Đang chuẩn bị cửa ải tiếp theo..."):
                        p_next = f"""Học sinh vừa vượt qua bước {curr} với đáp án đúng là: '{correct_text}'. 
                        Tạo câu hỏi thử thách Bước {curr + 1} / {total} (dẫn dắt bước suy luận tiếp theo). Phân số viết dạng \\dfrac{{a}}{{b}}. 
                        Bắt buộc trả về JSON có question, options (4 lựa chọn cụ thể), correct_index, explanation."""
                        try:
                            raw_next = execute_openrouter_request([st.session_state.img_data, p_next])
                            st.session_state.card = safe_parse_json(raw_next)
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
            st.rerun()

# ================= TAB 2: NỘP BÀI & CHẤM ĐIỂM =================
with tab2:
    st.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 14px; margin-bottom: 18px;">
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
            with st.spinner("Hệ thống đang chấm bài theo Rubric chuẩn..."):
                hw_img = Image.open(up_hw)
                RUBRIC = f"""
                Bạn là Giám khảo chấm thi Toán THCS tại Việt Nam.
                Đề bài: "{topic}".
                Hãy đọc ảnh chụp bài làm tự luận viết tay và chấm điểm theo Rubric (Thang 10):
                1. Hình vẽ (2.0 điểm): Đúng hình, ký hiệu góc, trung điểm.
                2. Lập luận chứng minh (6.0 điểm): Căn cứ định lý, tính chất, logic.
                3. Trình bày & Kết luận (2.0 điểm): Rõ ràng, đúng chuẩn.

                ĐỊNH DẠNG BẮT BUỘC TRẢ VỀ:
                - Tổng điểm: [Ghi điểm số]/10
                - Nhận xét chi tiết: (Chỉ ra rõ chỗ làm tốt và lỗi sai nếu có)
                """
                score_res = execute_openrouter_request([RUBRIC, hw_img])
                score_res_clean = format_solution_to_clean_html(score_res)

                score_match = re.search(r"(\d+(\.\d+)?)/10", score_res)
                extracted_score = score_match.group(1) if score_match else "Chưa xác định"

                sub_record = {
                    "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Họ và tên": s_name,
                    "Lớp": s_class,
                    "Bài tập": topic,
                    "Điểm số": extracted_score,
                    "Nhận xét của AI": clean_math_text(score_res).replace("\n", " ")
                }
                st.session_state.submission_history.append(sub_record)

                st.success("Đã hoàn tất chấm bài và lưu kết quả vào sổ điểm!")
                st.markdown(f"### Kết quả của: **{s_name}** - Lớp **{s_class}**")
                st.markdown(f'<div class="solution-box">{score_res_clean}</div>', unsafe_allow_html=True)

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
            label="📗 Tải file bảng điểm (.CSV cho Google Sheets / Excel)",
            data=csv_data,
            file_name=f"Bang_Diem_HinhHoc8_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

        st.info("💡 **Cách mở trên Google Sheets:** Mở `sheets.google.com` ➔ Chọn **Tệp (File)** ➔ **Mở (Open)** ➔ Chọn **Tải lên (Upload)** file vừa tải về là toàn bộ bảng điểm sẽ hiển thị đầy đủ, không bị lỗi font chữ tiếng Việt.")
