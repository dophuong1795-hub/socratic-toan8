import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

st.set_page_config(page_title="Học toán cùng cô Phương - Hình học 8", page_icon="📐", layout="centered")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Chưa cấu hình API Key trong mục Secrets của Streamlit!")
    st.stop()

genai.configure(api_key=api_key)
MODEL_NAME = "gemini-3.8-flash"

# Prompt buộc AI trả về cấu trúc JSON phục vụ thiết kế giao diện Game
GAME_SYSTEM_PROMPT = """
Bạn là Trợ lý Game Hóa Hình học 8 theo phương pháp Socratic.
Nhiệm vụ: Dựa vào đề bài/hình vẽ hoặc câu trả lời trước đó, hãy tạo ra 01 THỬ THÁCH TIẾP THEO cho học sinh.

BẠN BẮT BUỘC PHẢI TRẢ VỀ DUY NHẤT MỘT ĐOẠN ĐỊNH DẠNG JSON HỢP LỆ (Không kèm bất kỳ lời giải thích nào bên ngoài mã JSON):
{
  "feedback": "Nhận xét ngắn 1 câu về bước làm trước (nếu là câu đầu tiên thì ghi lời chào ngắn)",
  "question": "Nội dung câu hỏi thử thách tiếp theo (ngắn gọn, tập trung vào 1 suy luận cụ thể)",
  "question_type": "multiple_choice" (hoặc "true_false" hoặc "completed"),
  "options": [
    "Phương án 1",
    "Phương án 2",
    "Phương án 3",
    "Phương án 4"
  ],
  "correct_index": 0,
  "explanation": "Giải thích ngắn vì sao đáp án này đúng và hướng tư duy tiếp theo",
  "is_finished": false (Đặt true nếu học sinh đã hoàn thành toàn bộ sơ đồ chứng minh bài toán)
}
"""

st.title("📐 Đấu trường Hình học 8: Cô Phương")

tab1, tab2 = st.tabs(["🎮 Vượt chướng ngại vật (Gợi mở)", "📝 Nộp bài tập & Chấm tự động"])

# ================= TAB 1: GAME TƯƠNG TÁC =================
with tab1:
    # Khởi tạo trạng thái game
    if "game_step" not in st.session_state:
        st.session_state.game_step = 1
    if "current_card" not in st.session_state:
        st.session_state.current_card = None
    if "answered" not in st.session_state:
        st.session_state.answered = False
    if "user_selected_idx" not in st.session_state:
        st.session_state.user_selected_idx = None
    if "problem_image" not in st.session_state:
        st.session_state.problem_image = None

    # Khung tải đề bài / hình vẽ ban đầu
    with st.expander("📸 Đề bài / Hình vẽ bài toán", expanded=(st.session_state.current_card is None)):
        up_img = st.file_uploader("Tải ảnh bài tập cần gợi ý lên đây:", type=["jpg", "png", "jpeg"], key="game_img")
        if up_img:
            st.session_state.problem_image = Image.open(up_img)
            st.image(st.session_state.problem_image, caption="Hình vẽ bài tập đang giải", width=350)
        
        if st.session_state.problem_image and st.session_state.current_card is None:
            if st.button("🚀 Bắt đầu giải bài cùng cô!", type="primary"):
                with st.spinner("Cô đang phân tích hình vẽ để tạo thử thách..."):
                    try:
                        model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=GAME_SYSTEM_PROMPT)
                        prompt_start = "Hãy tạo câu hỏi thử thách bước 1 dạng trắc nghiệm 4 lựa chọn cho bài toán trong ảnh."
                        res = model.generate_content([st.session_state.problem_image, prompt_start])
                        # Lọc chuỗi json
                        raw_text = res.text.strip().replace("```json", "").replace("```", "")
                        st.session_state.current_card = json.loads(raw_text)
                        st.session_state.answered = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khởi tạo: {str(e)}")

    # GIAO DIỆN CHƠI TƯƠNG TÁC (CHỈ HIỂN THỊ 1 THẺ DUY NHẤT)
    card = st.session_state.current_card
    if card:
        st.write("---")
        # Thanh tiến trình bước làm
        st.progress(min(st.session_state.game_step * 25, 100))
        st.caption(f"🎯 **Thử thách bước {st.session_state.game_step}**")

        if card.get("feedback"):
            st.info(f"💡 {card['feedback']}")

        # Hộp câu hỏi
        st.markdown(f"### {card['question']}")

        # Nếu chưa bấm chọn đáp án: hiển thị danh sách nút lựa chọn
        if not st.session_state.answered:
            st.write("👉 **Em hãy chọn phương án đúng nhất:**")
            for idx, opt in enumerate(card.get("options", [])):
                if st.button(f"{chr(65+idx)}. {opt}", key=f"btn_opt_{idx}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.user_selected_idx = idx
                    st.rerun()
        else:
            # Khi đã chọn: hiển thị kết quả Đúng/Sai và giải thích
            chosen = st.session_state.user_selected_idx
            correct = card.get("correct_index", 0)

            if chosen == correct:
                st.success(f"🎉 **Chính xác! Em đã chọn: [chosen]}**")
            else:
                st.error(f"❌ **Chưa chính xác. Em đã chọn: [chosen]}**")
                st.info(f"Đáp án đúng là: **{chr(65+correct)}. {card['options'][correct]}**")

            st.markdown(f"**Giải thích hướng đi:** {card.get('explanation', '')}")

            # Kiểm tra xem bài đã xong chưa
            if card.get("is_finished") or st.session_state.game_step >= 4:
                st.balloons()
                st.success("🏆 **Tuyệt vời! Em đã hoàn thành đủ sơ đồ chứng minh!** Hãy trình bày hoàn chỉnh vào vở và nộp bài ở tab bên cạnh nhé.")
            else:
                if st.button("➡️ Sang thử thách tiếp theo", type="primary"):
                    with st.spinner("Đang chuẩn bị bước suy luận tiếp theo..."):
                        try:
                            model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=GAME_SYSTEM_PROMPT)
                            prompt_next = f"Học sinh vừa vượt qua bước {st.session_state.game_step} với đáp án: {card['options'][correct]}. Hãy tạo câu hỏi trắc nghiệm hoặc đúng/sai cho bước {st.session_state.game_step + 1} tiếp theo."
                            
                            inputs = [prompt_next]
                            if st.session_state.problem_image:
                                inputs.insert(0, st.session_state.problem_image)
                                
                            res = model.generate_content(inputs)
                            raw_text = res.text.strip().replace("```json", "").replace("```", "")
                            st.session_state.current_card = json.loads(raw_text)
                            st.session_state.game_step += 1
                            st.session_state.answered = False
                            st.session_state.user_selected_idx = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi tạo bước tiếp: {str(e)}")

        # Nút làm lại bài toán từ đầu
        if st.button("🔄 Làm lại bài từ đầu"):
            st.session_state.game_step = 1
            st.session_state.current_card = None
            st.session_state.answered = False
            st.rerun()

# ================= TAB 2: NỘP BÀI & CHẤM ĐIỂM =================
with tab2:
    st.caption("Chấm tự luận tự động bằng AI theo Rubric sư phạm chuẩn môn Toán THCS.")
    
    c1, c2 = st.columns(2)
    with c1:
        s_name = st.text_input("Họ và tên học sinh:")
    with c2:
        s_class = st.selectbox("Lớp:", ["8A1", "8A2", "8A9", "8A13"])
        
    topic = st.selectbox("Chọn dạng bài tập nộp:", [
        "Bài 1: Hình thang cân (Học sinh chụp kèm cả đề bài)",
        "Bài 2: Hình bình hành (Học sinh chụp kèm cả đề bài)",
        "Bài 3: Hình chữ nhật (Học sinh chụp kèm cả đề bài)",
        "Bài 4: Hình thoi (Học sinh chụp kèm cả đề bài)",
        "Bài 5: Hình vuông (Học sinh chụp kèm cả đề bài)",
        "Bài 6: Bài tập tổng hợp (Học sinh chụp kèm cả đề bài)"
    ])
    
    up_hw = st.file_uploader("📸 Chụp ảnh bài giải viết tay trong vở:", type=["jpg", "png", "jpeg"], key="hw_up")
    
    if st.button("🚀 Nộp bài & Nhận kết quả chấm"):
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
                try:
                    model = genai.GenerativeModel(model_name=MODEL_NAME)
                    response = model.generate_content([RUBRIC, hw_img])
                    res_text = response.text
                except Exception as e:
                    res_text = f"Lỗi chấm bài: {str(e)}"
                    
                st.success("Đã hoàn tất chấm bài!")
                st.markdown(f"### Kết quả của: **{s_name}** - Lớp **{s_class}**")
                st.markdown(res_text)
