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
   - QUAN TRỌNG NHẤT VỀ TÊN ĐIỂM: Thẻ <text> của TỪNG ĐIỂM phải có tọa độ x, y cụ thể đặt ngay cạnh điểm đó (cách điểm khoảng 8-12px) để chữ nằm sát đỉnh. Ví dụ: điểm tại cx="40" cy="40" thì <text x="25" y="35" font-weight="bold" font-size="14">A</text>. KHÔNG gom dồn chữ sang một góc!

Trả về duy nhất định dạng JSON:
{
  "total_steps": 3,
  "feedback": "Khen ngợi ngắn 1 câu",
  "question": "Câu hỏi ngắn gọn",
  "options": [
    "Phương án 1",
    "Phương án 2",
    "Phương án 3",
    "Phương án 4"
  ],
  "correct_index": 0,
  "explanation": "Giải thích ngắn 2 câu theo SGK Toán 8",
  "is_finished": false,
  "full_solution": "",
  "svg_code": ""
}
"""

def execute_openrouter_request(inputs, system_prompt=None, is_json=False):
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
            img_to_send.convert("RGB").save(buffered, format="JPEG", quality=75)
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"
                }
            })

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": content_parts})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.2
    }

    resp = None
    for attempt in range(2):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=25)
            if resp.status_code == 200:
                break
            elif resp.status_code == 429:
                time.sleep(1.5)
                continue
        except Exception:
            time.sleep(1)
            continue
            
    if not resp or resp.status_code != 200:
        payload["model"] = "openrouter/free"
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code != 200:
            raise Exception("Hệ thống AI phản hồi chậm, em hãy bấm lại nút một lần nữa nhé!")

    res_data = resp.json()
    choices = res_data.get("choices", [])
    if not choices or not choices[0].get("message"):
        raise Exception("Mô hình bận, em hãy bấm thử lại một lần nữa nhé!")

    msg = choices[0]["message"]
    text_out = msg.get("content") or msg.get("reasoning") or ""
    if not text_out.strip():
        raise Exception("Nội dung rỗng, vui lòng bấm nhận lại thử thách!")

    if is_json:
        clean_text = re.sub(r"^```json\s*|^```\s*|```$", "", text_out.strip(), flags=re.MULTILINE)
        match = re.search(r"\{[\s\S]*\}", clean_text)
        target_str = match.group(0) if match else clean_text
        sanitized_str = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', target_str)
        
        try:
            return json.loads(sanitized_str, strict=False)
        except Exception:
            q_match = re.search(r'"question"\s*:\s*"([^"]+)"', target_str)
            opts_match = re.findall(r'"([^"]+)"', target_str)
            if q_match:
                return {
                    "total_steps": 3,
                    "feedback": "Rất tốt! Chúng ta tiếp tục nhé.",
                    "question": q_match.group(1),
                    "options": [opts_match[i] for i in range(len(opts_match)) if len(opts_match[i]) > 8][:4] or ["A", "B", "C", "D"],
                    "correct_index": 0,
                    "explanation": "Đúng theo định lý trong SGK Toán 8.",
                    "is_finished": False,
                    "full_solution": "",
                    "svg_code": ""
                }
            raise Exception("AI chưa hoàn thành cấu trúc câu hỏi, em bấm nút thêm 1 lần nhé!")
            
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
    if "reward_svg" not in st.session_state:
        st.session_state.reward_svg = None

    with st.expander("📸 Đề bài / Hình vẽ bài toán", expanded=(st.session_state.card is None)):
        up_img = st.file_uploader("Tải/chụp ảnh bài tập cần gợi ý lên đây:", type=["jpg", "png", "jpeg"], key="up_game_img")
        if up_img:
            st.session_state.img_data = Image.open(up_img)
            st.image(st.session_state.img_data, caption="Hình vẽ / Đề bài đang giải", use_column_width=True)

        if st.session_state.img_data and st.session_state.card is None:
            if st.button("🚀 Bắt đầu nhận Thử thách Bước 1!", type="primary", use_container_width=True):
                with st.spinner("Cô Mai Phương đang chuẩn bị câu hỏi gợi ý..."):
                    try:
                        p_start = "Tạo câu hỏi thử thách Bước 1 ngắn gọn, tập trung khai thác giả thiết khởi đầu của bài toán."
                        c_data = execute_openrouter_request([st.session_state.img_data, p_start], GAME_PROMPT, is_json=True)
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
        fb = clean_math_text(card.get("feedback", ""))
        if fb:
            st.info(f"💡 {fb}")

        st.markdown(f"#### 🎯 {clean_math_text(card.get('question', ''))}")
        st.write("")

        opts = card.get("options", [])
        correct = card.get("correct_index", 0)

        if not st.session_state.answered:
            st.markdown("**👉 Em hãy bấm chọn một đáp án đúng nhất:**")
            for idx, opt in enumerate(opts):
                clean_opt = clean_math_text(opt)
                clean_opt = re.sub(r"^[A-D]\s*[\.\:\)]\s*", "", clean_opt)
                label = f"{chr(65+idx)}. {clean_opt}"
                if st.button(label, key=f"btn_choice_{idx}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.selected_idx = idx
                    st.rerun()
        else:
            sel = st.session_state.selected_idx
            sel_text = clean_math_text(opts[sel]) if (sel is not None and sel < len(opts)) else ""
            sel_text = re.sub(r"^[A-D]\s*[\.\:\)]\s*", "", sel_text)

            correct_text = clean_math_text(opts[correct]) if correct < len(opts) else ""
            correct_text = re.sub(r"^[A-D]\s*[\.\:\)]\s*", "", correct_text)

            if sel == correct:
                st.success("🎉 **Chính xác!** Em đã lựa chọn hướng tư duy rất chuẩn.")
            else:
                st.error("❌ **Chưa chính xác.**")
                st.markdown(f"Đáp án đúng là: **{chr(65+correct)}. {correct_text}**")

            st.markdown(f"**💡 Hướng suy luận:** {clean_math_text(card.get('explanation', ''))}")

            is_finish = card.get("is_finished") or (curr >= total)

            if is_finish:
                st.balloons()
                st.success("🏆 **XUẤT SẮC! Em đã hoàn thành toàn bộ sơ đồ chứng minh!**")

                if not st.session_state.reward:
                    sol = card.get("full_solution", "")
                    svg = card.get("svg_code", "")
                    if not sol:
                        with st.spinner("Đang mở khóa bài giải và hình vẽ chuẩn..."):
                            p_sol = """Hãy viết bài giải mẫu mực hoàn chỉnh và kèm theo mã SVG chuẩn vẽ lại hình bài toán này.
                            YÊU CẦU:
                            1. Bài giải xuống dòng riêng cho từng bước, mở ngoặc nêu lý do định lý.
                            2. Mã SVG nhỏ gọn (viewBox="0 0 300 240"), thẻ <text> tên điểm phải có tọa độ x, y nằm sát từng điểm.
                            Trả về JSON: {"full_solution": "...", "svg_code": "<svg ...>...</svg>"}"""
                            res_final = execute_openrouter_request([st.session_state.img_data, p_sol], is_json=True)
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

                # Hiển thị hình vẽ SVG nhỏ gọn, đúng vị trí điểm
                if st.session_state.reward_svg and "<svg" in st.session_state.reward_svg:
                    st.markdown("#### 📐 Hình vẽ minh họa chuẩn xác:")
                    clean_svg_match = re.search(r"<svg[\s\S]*?</svg>", st.session_state.reward_svg)
                    if clean_svg_match:
                        svg_html = clean_svg_match.group(0)
                        svg_html = re.sub(r'width="[^"]+"', 'width="280"', svg_html)
                        svg_html = re.sub(r'height="[^"]+"', 'height="220"', svg_html)
                        st.markdown(f'<div class="svg-container">{svg_html}</div>', unsafe_allow_html=True)

                # Hiển thị bài giải trong khung chuyên dụng cách dòng thoáng đãng
                st.markdown("#### 📝 Bài giải chi tiết chuẩn mực:")
                sol_html = format_solution_to_html(st.session_state.reward)
                st.markdown(f'<div class="solution-box">{sol_html}</div>', unsafe_allow_html=True)
                
                st.write("")
                st.success("📝 **Bước tiếp theo:** Hãy chuyển sang tab **'Nộp Bài Tập'** ở trên để chụp ảnh bài vở nộp cô chấm nhé!")
            else:
                st.write("")
                if st.button("➡️ Sang thử thách tiếp theo", type="primary", use_container_width=True):
                    with st.spinner("Đang chuẩn bị cửa ải tiếp theo..."):
                        p_next = f"""Học sinh vừa vượt qua bước {curr} với đáp án đúng: {correct_text}. Tạo thử thách trắc nghiệm bước {curr + 1} / {total}. 
                        Nhớ giữ câu hỏi và 4 phương án ngắn gọn (1 dòng), dễ hiểu cho học sinh lớp 8.
                        Nếu đây là bước cuối, hãy đặt is_finished = true, viết bài giải vào full_solution (xuống dòng rõ ràng) và sinh mã vẽ hình vào svg_code (chữ tên điểm nằm sát điểm)."""
                        try:
                            st.session_state.card = execute_openrouter_request([st.session_state.img_data, p_next], GAME_PROMPT, is_json=True)
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
                2. Lập luận chứng minh (6.0 điểm): Căn cứ định lý, tính chất, dấu hiệu nhận biết, logic chặt chẽ.
                3. Trình bày & Kết luận (2.0 điểm): Rõ ràng, đúng chuẩn sư phạm.

                ĐỊNH DẠNG BẮT BUỘC TRẢ VỀ:
                - Tổng điểm: [Ghi điểm số]/10
                - Nhận xét chi tiết: (Chỉ ra rõ chỗ làm tốt và lỗi sai nếu có)
                """
                score_res = execute_openrouter_request([RUBRIC, hw_img])
                score_res_clean = format_solution_to_html(score_res)

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
