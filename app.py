import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import random
import pandas as pd
from datetime import datetime

# Cấu hình hiển thị trang
st.set_page_config(
    page_title="Đấu Trường Hình Học 8 - Cô Phương",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CSS TÙY CHỈNH GIAO DIỆN HIỆN ĐẠI =================
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
</style>
""", unsafe_allow_html=True)

# Lấy danh sách khóa từ Secrets (hỗ trợ cả danh sách GEMINI_KEYS lẫn key đơn GEMINI_API_KEY)
raw_keys = st.secrets.get("GEMINI_KEYS") or [st.secrets.get("GEMINI_API_KEY")]
if not raw_keys or not raw_keys[0]:
    st.error("Chưa cấu hình API Key trong Secrets của Streamlit!")
    st.stop()

AVAILABLE_KEYS = [k for k in raw_keys if k]
MODEL_NAME = "gemini-2.5-flash"

GAME_PROMPT = """
Bạn là Trợ lý Sư phạm Game Hóa Hình học 8 (Cô Phương).
Nhiệm vụ: Phân tích ảnh đề bài/hình vẽ, chia bài toán thành 2 đến 4 bước thử thách tư duy nhỏ.
Tạo câu hỏi trắc nghiệm 4 lựa chọn cho bước hiện tại.
ĐẶC BIỆT: Nếu là bước cuối cùng (hoặc is_finished = true), hãy viết kèm một bài giải hoàn chỉnh, mẫu mực sư phạm từng bước làm phần thưởng.

QUY TẮC KÝ HIỆU TOÁN HỌC:
- Các tên đỉnh, đoạn thẳng, tam giác viết in hoa bình thường (AB, CD, tam giác ABC), không kẹp dấu $ vào từng chữ cái.
- Chỉ dùng ký hiệu thông thường hoặc LaTeX đơn giản nếu thật sự cần thiết.

BẮT BUỘC TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON SAU ĐÂY:
{
  "total_steps": 2,
  "feedback": "Nhận xét ngắn 1 câu về câu trả lời trước đó",
  "question": "Nội dung câu hỏi thử thách",
  "options": ["Phương án A", "Phương án B", "Phương án C", "Phương án D"],
  "correct_index": 0,
  "explanation": "Giải thích ngắn vì sao đúng",
  "is_finished": false,
  "full_solution": ""
}
"""

# HÀM TỰ ĐỘNG XOAY VÒNG KHÓA VÀ DỰ PHÒNG KHI BỊ NGHẼN HOẶC 429
def execute_gemini_request(inputs, system_prompt=None, is_json=False):
    shuffled_keys = AVAILABLE_KEYS.copy()
    random.shuffle(shuffled_keys)
    last_err = None

    for key in shuffled_keys:
        try:
            genai.configure(api_key=key)
            config = {"response_mime_type": "application/json"} if is_json else None
            
            if system_prompt:
                model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=system_prompt, generation_config=config)
            else:
                model = genai.GenerativeModel(model_name=MODEL_NAME, generation_config=config)
                
            res = model.generate_content(inputs)
            
            if is_json:
                clean = re.sub(r"^```json\s*|^```\s*|```$", "", res.text.strip(), flags=re.MULTILINE)
                match = re.search(r"\{.*\}", clean, re.DOTALL)
                return json.loads(match.group(0) if match else clean)
            return res.text
        except Exception as e:
            last_err = e
            continue

    if is_json:
        raise last_err
    return f"Lỗi: {str(last_err)}"

if "submission_history" not in st.session_state:
    st.session_state.submission_history = []

# ================= BANNER TIÊU ĐỀ =================
st.markdown("""
<div class="hero-banner">
    <h1>📐 ĐẤU TRƯỜNG HÌNH HỌC 8</h1>
    <p>Học toán gợi mở cùng cô Phương • Chinh phục thử thách từng bước</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎮 Vượt Chướng Ngại Vật", "📝 Nộp Bài Tập & Chấm Điểm", "📊 Bảng Điểm & Xuất Google Sheets"])

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
            st.image(st.session_state.img_data, caption="Hình vẽ bài toán đang giải", use_column_width=True)

        if st.session_state.img_data and st.session_state.card is None:
            if st.button("🚀 Bắt đầu nhận Thử thách Bước 1!", type="primary", use_container_width=True):
                with st.spinner("Cô đang quan sát hình vẽ để tạo thử thách..."):
                    try:
                        c_data = execute_gemini_request([st.session_state.img_data, "Tạo câu hỏi thử thách Bước 1 cho bài toán trong ảnh."], GAME_PROMPT, is_json=True)
                        st.session_state.card = c_data
                        st.session_state.total_steps = c_data.get("total_steps", 3)
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
        fb = card.get("feedback", "")
        if fb:
            st.info(f"💡 {fb}")
            
        st.markdown(f"#### 🎯 {card.get('question', '')}")
        st.write("")

        opts = card.get("options", [])
        correct = card.get("correct_index", 0)

        if not st.session_state.answered:
            st.markdown("**👉 Em hãy bấm chọn một đáp án đúng nhất:**")
            for idx, opt in enumerate(opts):
                clean_opt = opt.replace("$", "")
                label = f"{chr(65+idx)}. {clean_opt}"
                if st.button(label, key=f"btn_choice_{idx}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.selected_idx = idx
                    st.rerun()
        else:
            sel = st.session_state.selected_idx
            sel_text = opts[sel] if (sel is not None and sel < len(opts)) else ""
            correct_text = opts[correct] if correct < len(opts) else ""

            if sel == correct:
                st.success("🎉 **Chính xác!** Em đã chọn đáp án đúng.")
            else:
                st.error("❌ **Chưa chính xác.**")
                st.markdown(f"Đáp án đúng là: **{chr(65+correct)}. {correct_text}**")

            st.markdown(f"**💡 Hướng suy luận:** {card.get('explanation', '')}")

            is_finish = card.get("is_finished") or (curr >= total)

            if is_finish:
                st.balloons()
                st.success("🏆 **XUẤT SẮC! Em đã hoàn thành toàn bộ sơ đồ chứng minh!**")

                if not st.session_state.reward:
                    sol = card.get("full_solution", "")
                    if not sol:
                        with st.spinner("Đang mở khóa bài giải mẫu phần thưởng..."):
                            p_sol = "Hãy viết bài giải hoàn chỉnh, mẫu mực sư phạm môn Toán 8 từng bước rõ ràng cho bài toán này để học sinh đối chiếu ghi vào vở."
                            sol = execute_gemini_request([st.session_state.img_data, p_sol])
                    st.session_state.reward = sol

                st.markdown("""
                <div class="reward-box">
                    <h3 style="color: #15803D; margin-top:0;">🎁 PHẦN THƯỞNG: BÀI GIẢI MẪU HOÀN CHỈNH</h3>
                    <p style="color: #166534; font-size: 14px;">Em hãy đối chiếu các bước suy luận và trình bày thật đẹp vào vở nhé!</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(st.session_state.reward)
                st.success("📝 **Bước tiếp theo:** Hãy chuyển sang tab **'Nộp Bài Tập & Chấm Điểm'** ở trên để chụp ảnh bài vở nộp cô chấm nhé!")
            else:
                st.write("")
                if st.button("➡️ Sang thử thách tiếp theo", type="primary", use_container_width=True):
                    with st.spinner("Đang chuẩn bị cửa ải tiếp theo..."):
                        p_next = f"Học sinh vừa vượt qua bước {curr} với đáp án đúng: {correct_text}. Tạo thử thách trắc nghiệm bước {curr + 1} / {total}. Nếu đây là bước kết luận bài toán, hãy đặt is_finished = true và viết bài giải mẫu vào full_solution."
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
        s_class = st.selectbox("Lớp:", ["8A1", "8A2", "8A9", "8A13"])

    topic = st.selectbox("Chọn dạng bài tập nộp:", [
        "Bài 1: Hình thang cân (Chụp kèm đề bài)",
        "Bài 2: Hình bình hành (Chụp kèm đề bài)",
        "Bài 3: Hình chữ nhật (Chụp kèm đề bài)",
        "Bài 4: Hình thoi (Chụp kèm đề bài)",
        "Bài 5: Hình vuông (Chụp kèm đề bài)",
        "Bài 6: Bài tập tổng hợp (Chụp kèm đề bài)"
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
                
                score_match = re.search(r"(\d+(\.\d+)?)/10", score_res)
                extracted_score = score_match.group(1) if score_match else "Chưa xác định"

                sub_record = {
                    "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Họ và tên": s_name,
                    "Lớp": s_class,
                    "Bài tập": topic,
                    "Điểm số": extracted_score,
                    "Nhận xét của AI": score_res.replace("\n", " ")
                }
                st.session_state.submission_history.append(sub_record)

                st.success("Đã hoàn tất chấm bài và lưu kết quả vào sổ điểm!")
                st.markdown(f"### Kết quả của: **{s_name}** - Lớp **{s_class}**")
                st.markdown(score_res)

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

        st.info("💡 **Cách mở trên Google Sheets:** Mở `sheets.google.com` ➔ Chọn **Tệp (File)** ➔ **Mở (Open)** ➔ Chọn **Tải lên (Upload)** file vừa tải về là toàn bộ bảng điểm sẽ hiển thị đầy đủ, không bị lỗi font chữ tiếng Việt.")
