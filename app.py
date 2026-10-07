import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

st.set_page_config(page_title="Học toán cùng cô Phương - Hình học 8", page_icon="📐", layout="centered")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Chưa cấu hình API Key trong mục Secrets của Streamlit!")
    st.stop()

genai.configure(api_key=api_key)
MODEL_NAME = "gemini-3.8-flash"

# Prompt Socratic: Tự động phân chia bước theo bài và xuất kèm bài giải mẫu hoàn chỉnh khi kết thúc
GAME_SYSTEM_PROMPT = """
Bạn là Trợ lý Sư phạm Game Hóa Hình học 8 theo phương pháp Socratic.
Nhiệm vụ: Phân tích bài toán trong ảnh, chia sơ đồ chứng minh thành các bước tư duy nhỏ (2 đến 4 bước tùy độ khó).
Tạo thử thách trắc nghiệm 4 lựa chọn cho bước hiện tại.
ĐẶC BIỆT: Nếu là bước cuối cùng (hoặc is_finished = true), hãy viết kèm một bài giải hoàn chỉnh, mẫu mực sư phạm từng bước làm phần thưởng.

BẮT BUỘC TRẢ VỀ DUY NHẤT 01 MÃ JSON HỢP LỆ (Không có bất kỳ ký tự nào khác ngoài JSON):
{
  "total_steps": 2, // Tổng số bước cần thiết của bài (2, 3 hoặc 4 bước)
  "feedback": "Nhận xét ngắn 1 câu về bước làm trước của học sinh",
  "question": "Nội dung câu hỏi thử thách cho bước này",
  "options": [
    "Phương án 1",
    "Phương án 2",
    "Phương án 3",
    "Phương án 4"
  ],
  "correct_index": 0,
  "explanation": "Giải thích ngắn vì sao đúng và liên kết sang bước tiếp theo",
  "is_finished": false, // Đặt true nếu bước này là bước kết thúc chứng minh
  "full_solution": "" // ĐỂ TRỐNG nếu chưa xong. Khi is_finished = true, hãy viết bài giải hoàn chỉnh chuẩn mực sư phạm từng bước có ký hiệu toán học đầy đủ vào đây!
}
"""

def extract_json(text):
    clean_text = text.strip()
    match = re.search(r'\{.*\}', clean_text, re.DOTALL)
    if match:
        clean_text = match.group(0)
    return json.loads(clean_text)

st.title("📐 Đấu trường Hình học 8: Cô Phương")

tab1, tab2 = st.tabs(["🎮 Vượt chướng ngại vật (Gợi mở)", "📝 Nộp bài tập & Chấm tự động"])

# ================= TAB 1: GAME TƯƠNG TÁC CÓ PHẦN THƯỞNG =================
with tab1:
    if "game_step" not in st.session_state:
        st.session_state.game_step = 1
    if "total_steps" not in st.session_state:
        st.session_state.total_steps = 3
    if "current_card" not in st.session_state:
        st.session_state.current_card = None
    if "answered" not in st.session_state:
        st.session_state.answered = False
    if "user_selected_idx" not in st.session_state:
        st.session_state.user_selected_idx = None
    if "problem_image" not in st.session_state:
        st.session_state.problem_image = None
    if "reward_solution" not in st.session_state:
        st.session_state.reward_solution = None

    with st.expander("📸 Đề bài / Hình vẽ bài toán", expanded=(st.session_state.current_card is None)):
        up_img = st.file_uploader("Tải ảnh bài tập cần gợi ý lên đây:", type=["jpg", "png", "jpeg"], key="game_img")
        if up_img:
            st.session_state.problem_image = Image.open(up_img)
            st.image(st.session_state.problem_image, caption="Hình vẽ bài tập đang giải", width=350)
        
        if st.session_state.problem_image and st.session_state.current_card is None:
            if st.button("🚀 Bắt đầu giải bài cùng cô!", type="primary"):
                with st.spinner("Cô đang phân tích hình vẽ và tạo thử thách bước 1..."):
                    try:
                        model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=GAME_SYSTEM_PROMPT)
                        prompt_start = "Hãy tạo câu hỏi thử thách Bước 1 cho bài toán trong ảnh."
                        res = model.generate_content([st.session_state.problem_image, prompt_start])
                        card_data = extract_json(res.text)
                        st.session_state.current_card = card_data
                        st.session_state.total_steps = card_data.get("total_steps", 3)
                        st.session_state.game_step = 1
                        st.session_state.answered = False
                        st.session_state.reward_solution = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khởi tạo: {str(e)}")

    card = st.session_state.current_card
    if card:
        st.write("---")
        total = st.session_state.total_steps
        current = st.session_state.game_step
        progress_val = min(int((current / total) * 100), 100)
        st.progress(progress_val)
        st.caption(f"🎯 **Thử thách: Bước {current} / {total}**")

        if card.get("feedback"):
            st.info(f"💡 {card['feedback']}")

        st.markdown(f"### {card.get('question', '')}")

        opts = card.get("options", [])
        correct = card.get("correct_index", 0)

        if not st.session_state.answered:
            st.write("👉 **Em hãy chọn phương án đúng nhất:**")
            for idx, opt in enumerate(opts):
                label = f"{chr(65+idx)}. {opt}"
                if st.button(label, key=f"btn_opt_{idx}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.user_selected_idx = idx
                    st.rerun()
        else:
            chosen = st.session_state.user_selected_idx
            chosen_text = opts[chosen] if (chosen is not None and chosen < len(opts)) else ""
            correct_text = opts[correct] if correct < len(opts) else ""

            if chosen == correct:
                st.success(f"🎉 **Chính xác!** Em đã chọn: **{chosen_text}**")
            else:
                st.error(f"❌ **Chưa chính xác.** Em đã chọn: **{chosen_text}**")
                st.info(f"Đáp án đúng là: **{chr(65+correct)}. {correct_text}**")

            st.markdown(f"**Giải thích hướng đi:** {card.get('explanation', '')}")

            # ĐIỀU KIỆN HOÀN THÀNH TOÀN BỘ BÀI TOÁN
            is_done = card.get("is_finished") or (current >= total)
            
            if is_done:
                st.balloons()
                st.success("🏆 **XUẤT SẮC! Em đã vượt qua toàn bộ thử thách tư duy!**")
                
                # Tạo phần thưởng bài giải mẫu nếu chưa có
                if not st.session_state.reward_solution:
                    sol = card.get("full_solution", "")
                    if not sol:
                        with st.spinner("Đang mở khóa phần thưởng bài giải chi tiết..."):
                            try:
                                model = genai.GenerativeModel(model_name=MODEL_NAME)
                                p_sol = "Hãy trình bày bài giải mẫu hoàn chỉnh, chuẩn mực sư phạm môn Toán 8 từng bước rõ ràng cho bài toán này để học sinh đối chiếu ghi vào vở."
                                inputs_sol = [p_sol]
                                if st.session_state.problem_image:
                                    inputs_sol.insert(0, st.session_state.problem_image)
                                res_sol = model.generate_content(inputs_sol)
                                sol = res_sol.text
                            except Exception:
                                sol = "Chúc mừng em đã hoàn thành bài giải xuất sắc!"
                    st.session_state.reward_solution = sol

                # HIỂN THỊ PHẦN THƯỞNG BÀI GIẢI MẪU
                st.markdown("---")
                st.markdown("### 🎁 **PHẦN THƯỞNG DÀNH CHO EM: BÀI GIẢI MẪU HOÀN CHỈNH**")
                st.markdown("*(Em hãy đọc kỹ, đối chiếu với các bước vừa suy luận và trình bày thật đẹp vào vở nhé!)*")
                st.info(st.session_state.reward_solution)
                
                st.success("📝 **Bước tiếp theo:** Sau khi ghi bài vào vở xong, em hãy bấm chuyển sang tab **'Nộp bài tập & Chấm tự động'** ở phía trên để chụp ảnh vở nộp cho cô nhé!")
            else:
                if st.button("➡️ Sang thử thách tiếp theo", type="primary"):
                    with st.spinner("Đang chuẩn bị bước suy luận tiếp theo..."):
                        try:
                            model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=GAME_SYSTEM_PROMPT)
                            prompt_next = f"Học sinh vừa chọn đúng bước {current}: {correct_text}. Tạo thử thách trắc nghiệm cho bước {current + 1} / {total}. Nếu đây là bước cuối cùng, hãy set is_finished = true và viết bài giải hoàn chỉnh vào full_solution."
                            
                            inputs = [prompt_next]
                            if st.session_state.problem_image:
                                inputs.insert(0, st.session_state.problem_image)
                                
                            res = model.generate_content(inputs)
                            st.session_state.current_card = extract_json(res.text)
                            st.session_state.game_step += 1
                            st.session_state.answered = False
                            st.session_state.user_selected_idx = None
                            st.rerun()
