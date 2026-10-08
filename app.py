import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

st.set_page_config(page_title="Đấu trường Toán 8 - Cô Phương", page_icon="📐", layout="centered")

# Lấy khóa API từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Chưa cấu hình API Key trong mục Secrets của Streamlit!")
    st.stop()

genai.configure(api_key=api_key)
MODEL_NAME = "gemini-3.8-flash"

# Prompt Game Hóa: Buộc AI chia nấc thang tư duy và trả về dữ liệu nút bấm
GAME_PROMPT = """
Bạn là Trợ lý Game Hóa Hình học 8 (Cô Phương).
Nhiệm vụ: Phân tích ảnh đề bài/hình vẽ, chia bài toán thành 2 đến 4 bước thử thách tư duy nhỏ.
Tạo câu hỏi trắc nghiệm 4 lựa chọn cho bước hiện tại.
ĐẶC BIỆT: Nếu là bước cuối cùng (hoặc is_finished = true), hãy viết kèm một bài giải hoàn chỉnh, mẫu mực sư phạm từng bước làm phần thưởng.

BẮT BUỘC TRẢ VỀ DUY NHẤT 01 MÃ JSON HỢP LỆ (Không có bất kỳ ký tự nào ngoài JSON):
{
  "total_steps": 3,
  "feedback": "Nhận xét ngắn 1 câu về câu trả lời trước đó của học sinh",
  "question": "Nội dung câu hỏi thử thách cho bước này",
  "options": [
    "Phương án A",
    "Phương án B",
    "Phương án C",
    "Phương án D"
  ],
  "correct_index": 0,
  "explanation": "Giải thích ngắn vì sao đúng và gợi ý bước tiếp theo",
  "is_finished": false,
  "full_solution": ""
}
"""

def call_ai(inputs, system_prompt=None):
    try:
        if system_prompt:
            model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=system_prompt)
        else:
            model = genai.GenerativeModel(model_name=MODEL_NAME)
        res = model.generate_content(inputs)
        return res.text
    except Exception as e:
        return f"Lỗi: {str(e)}"

def parse_card_json(raw_text):
    match = re.search(r'\{.*\}', raw_text.strip(), re.DOTALL)
    clean = match.group(0) if match else raw_text
    return json.loads(clean)

st.title("📐 Đấu trường Hình học 8: Cô Phương")

tab1, tab2 = st.tabs(["🎮 Vượt chướng ngại vật (Thử thách)", "📝 Nộp bài tập & Chấm tự động"])

# ================= TAB 1: GIAO DIỆN GAME TƯƠNG TÁC =================
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

    # Vùng tải đề bài (tự thu gọn khi đã bắt đầu chơi)
    with st.expander("📸 Đề bài / Hình vẽ bài toán", expanded=(st.session_state.card is None)):
        up_img = st.file_uploader("Chụp/tải ảnh đề bài lên đây:", type=["jpg", "png", "jpeg"], key="up_game_img")
        if up_img:
            st.session_state.img_data = Image.open(up_img)
            st.image(st.session_state.img_data, caption="Hình vẽ bài toán", width=380)

        if st.session_state.img_data and st.session_state.card is None:
            if st.button("🚀 Bắt đầu nhận thử thách Bước 1!", type="primary", use_container_width=True):
                with st.spinner("Cô đang quan sát hình vẽ để tạo thử thách..."):
                    raw = call_ai([st.session_state.img_data, "Tạo câu hỏi thử thách Bước 1 cho bài toán trong ảnh."], GAME_PROMPT)
                    try:
                        c_data = parse_card_json(raw)
                        st.session_state.card = c_data
                        st.session_state.total_steps = c_data.get("total_steps", 3)
                        st.session_state.step = 1
                        st.session_state.answered = False
                        st.session_state.reward = None
                        st.rerun()
                    except Exception as err:
                        st.error(f"Lỗi nạp thử thách: {err}")

    # GIAO DIỆN THẺ BÀI TRÒ CHƠI
    card = st.session_state.card
    if card:
        st.write("---")
        total = st.session_state.total_steps
        curr = st.session_state.step
        progress_val = min(int((curr / total) * 100), 100)
        st.progress(progress_val)
        st.caption(f"🎯 **Cửa ải hiện tại: Bước {curr} / {total}**")

        if card.get("feedback"):
            st.info(f"💡 {card['feedback']}")

        st.markdown(f"### {card.get('question', '')}")

        opts = card.get("options", [])
        correct = card.get("correct_index", 0)

        # Trạng thái 1: Chưa chọn -> hiển thị 4 nút bấm
        if not st.session_state.answered:
            st.write("👉 **Em hãy bấm chọn một đáp án đúng nhất:**")
            for idx, opt in enumerate(opts):
                label = f"{chr(65+idx)}. {opt}"
                if st.button(label, key=f"btn_choice_{idx}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.selected_idx = idx
                    st.rerun()
        else:
            # Trạng thái 2: Đã chọn -> báo kết quả
            sel = st.session_state.selected_idx
            sel_text = opts[sel] if (sel is not None and sel < len(opts)) else ""
            correct_text = opts[correct] if correct < len(opts) else ""

            if sel == correct:
                st.success(f"🎉 **Chính xác!** Em đã chọn: **{sel_text}**")
            else:
                st.error(f"❌ **Chưa chính xác.** Em đã chọn: **{sel_text}**")
                st.info(f"Đáp án đúng là: **{chr(65+correct)}. {correct_text}**")

            st.markdown(f"**Giải thích:** {card.get('explanation', '')}")

            # Kiểm tra nếu hoàn thành toàn bộ cửa ải
            is_finish = card.get("is_finished") or (curr >= total)

            if is_finish:
                st.balloons()
                st.success("🏆 **XUẤT SẮC! Em đã hoàn thành toàn bộ sơ đồ chứng minh!**")

                if not st.session_state.reward:
                    sol = card.get("full_solution", "")
                    if not sol:
                        with st.spinner("Đang mở khóa bài giải mẫu phần thưởng..."):
                            p_sol = "Hãy viết bài giải hoàn chỉnh, mẫu mực sư phạm môn Toán 8 từng bước rõ ràng cho bài toán này để học sinh đối chiếu ghi vào vở."
                            sol = call_ai([st.session_state.img_data, p_sol])
                    st.session_state.reward = sol

                st.markdown("---")
                st.markdown("### 🎁 **PHẦN THƯỞNG DÀNH CHO EM: BÀI GIẢI MẪU HOÀN CHỈNH**")
                st.markdown("*(Em hãy đối chiếu các bước lập luận và ghi cẩn thận vào vở nhé!)*")
                st.info(st.session_state.reward)
                st.success("📝 **Sau khi ghi vào vở xong:** Hãy chuyển sang tab **'Nộp bài tập & Chấm tự động'** ở trên để chụp ảnh nộp cô chấm điểm nhé!")
            else:
                if st.button("➡️ Sang thử thách tiếp theo", type="primary", use_container_width=True):
                    with st.spinner("Đang mở ải tiếp theo..."):
                        p_next = f"Học sinh vừa vượt qua bước {curr} với đáp án đúng: {correct_text}. Tạo thử thách trắc nghiệm bước {curr + 1} / {total}. Nếu đây là bước kết luận bài toán, hãy đặt is_finished = true và viết bài giải mẫu vào full_solution."
                        raw_next = call_ai([st.session_state.img_data, p_next], GAME_PROMPT)
                        try:
                            st.session_state.card = parse_card_json(raw_next)
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
    st.caption("Chấm tự luận tự động bằng AI theo Rubric chuẩn môn Toán THCS.")

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

                ĐỊNH DẠNG TRẢ VỀ:
                - Tổng điểm: .../10 điểm
                - Chi tiết: Hình vẽ (.../2.0), Lập luận (.../6.0), Trình bày (.../2.0)
                - Lỗi sai cụ thể cần sửa:
                - Lời khen/động viên sư phạm:
                """
                score_res = call_ai([RUBRIC, hw_img])
                st.success("Đã hoàn tất chấm bài!")
                st.markdown(f"### Kết quả của: **{s_name}** - Lớp **{s_class}**")
                st.markdown(score_res)
