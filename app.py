import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Học toán cùng cô Phương - Hình học 8", page_icon="📐", layout="centered")

# Lấy khóa API bảo mật từ Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Chưa cấu hình API Key trong mục Secrets của Streamlit!")
    st.stop()

genai.configure(api_key=api_key)

MODEL_NAME = "gemini-3.8-flash"

# Prompt sư phạm Socratic đa tương tác (Trắc nghiệm + Đúng/Sai + Câu hỏi ngắn)
SYSTEM_SOCRATIC = """
Bạn là Giáo viên Toán THCS tại Việt Nam chuyên hướng dẫn học sinh giải Hình học 8 theo phương pháp giàn giáo Socratic tương tác đa dạng.

QUY TẮC PHẢN HỒI:
1. TUYỆT ĐỐI KHÔNG giải hộ hay viết sẵn bài chứng minh hoàn chỉnh.
2. Với mỗi bước suy luận, bạn hãy:
   - Nhận xét ngắn gọn câu trả lời hoặc hình vẽ của học sinh (1 câu).
   - Đưa ra 01 câu hỏi tương tác tiếp theo thuộc một trong các dạng sau để học sinh dễ chọn và suy nghĩ:
     + Dạng 1 (Trắc nghiệm 4 lựa chọn): Gợi ý bước suy luận tiếp theo với 4 phương án A, B, C, D rõ ràng.
     + Dạng 2 (Đúng / Sai): Đưa ra một nhận định về cặp cạnh/góc hoặc dấu hiệu nhận biết để học sinh kiểm tra đúng hay sai.
     + Dạng 3 (Trả lời ngắn): Yêu cầu điền tên định lý, dấu hiệu hoặc đoạn thẳng còn thiếu.
3. KHI HỌC SINH ĐÃ SUY LUẬN ĐỦ CÁC BƯỚC HOÀN THÀNH BÀI:
   - Hãy chúc mừng học sinh và dặn: "Em đã nắm trọn vẹn sơ đồ chứng minh! Hãy ghi hoàn chỉnh bài giải vào vở và chuyển sang tab 'Nộp bài tập & Chấm tự động' bên cạnh để cô chấm điểm nhé!"
4. Giữ nguyên ký hiệu toán học đỉnh, đoạn thẳng (A, B, C, D, E, F...).
"""

st.title("📐 Học toán cùng cô Phương: Hình học 8")

# Khởi tạo trạng thái tab nếu chưa có
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "tab1"

tab1, tab2 = st.tabs(["💬 Hướng dẫn tương tác Socratic", "📝 Nộp bài tập & Chấm tự động"])

# ================= TAB 1: TƯƠNG TÁC TỪNG BƯỚC =================
with tab1:
    st.caption("AI đồng hành gợi mở từng bước qua trắc nghiệm, đúng/sai và câu hỏi ngắn.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Chào em! Em đang gặp khó khăn ở bài toán chứng minh hay hình vẽ nào? Hãy tải ảnh đề bài/hình vẽ lên hoặc gửi câu hỏi để cô trò mình cùng tháo gỡ từng bước nhé!"
        }]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "img" in msg and msg["img"] is not None:
                st.image(msg["img"], width=300)
                
    up_chat_img = st.file_uploader("📸 Tải ảnh đề bài/hình vẽ tay lên đây:", type=["jpg", "png", "jpeg"], key="chat_up")
    
    # Khu vực gửi câu trả lời tương tác nhanh
    st.write("---")
    st.markdown("**✍️ Nhập phản hồi của em (hoặc chọn nhanh A / B / C / D / Đúng / Sai):**")
    
    col_a, col_b, col_c, col_d, col_tf1, col_tf2 = st.columns(6)
    quick_choice = None
    if col_a.button("Đáp án A"):
        quick_choice = "Em chọn đáp án A"
    if col_b.button("Đáp án B"):
        quick_choice = "Em chọn đáp án B"
    if col_c.button("Đáp án C"):
        quick_choice = "Em chọn đáp án C"
    if col_d.button("Đáp án D"):
        quick_choice = "Em chọn đáp án D"
    if col_tf1.button("ĐÚNG"):
        quick_choice = "Em chọn: ĐÚNG"
    if col_tf2.button("SAI"):
        quick_choice = "Em chọn: SAI"

    chat_text_input = st.chat_input("Nhập câu trả lời ngắn hoặc thắc mắc của em tại đây...")
    
    final_prompt = quick_choice if quick_choice else chat_text_input

    if final_prompt:
        chat_img = Image.open(up_chat_img) if up_chat_img else None
        st.session_state.messages.append({"role": "user", "content": final_prompt, "img": chat_img})
        
        with st.chat_message("user"):
            st.markdown(final_prompt)
            if chat_img:
                st.image(chat_img, width=300)
                
        with st.chat_message("assistant"):
            with st.spinner("Cô đang phân tích câu trả lời của em..."):
                try:
                    model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=SYSTEM_SOCRATIC)
                    input_payload = []
                    if chat_img:
                        input_payload.append(chat_img)
                    input_payload.append(final_prompt)
                    
                    response = model.generate_content(input_payload)
                    reply_text = response.text
                except Exception as e:
                    reply_text = f"Lỗi phản hồi: {str(e)}"
                    
                st.markdown(reply_text)
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
                st.rerun()

    # Nút xác nhận khi học sinh đã nắm được bài
    st.write("---")
    st.info("💡 **Khi em đã hiểu cách chứng minh và hoàn thành vào vở:** Hãy bấm nút bên dưới để chuyển sang nộp bài!")
    if st.button("✅ Em đã làm xong bài vào vở! Chuyển sang Nộp bài ➔"):
        st.success("Tuyệt vời! Em hãy chuyển sang tab **'📝 Nộp bài tập & Chấm tự động'** ở phía trên màn hình để chụp ảnh vở nộp bài nhé.")

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
                1. Hình vẽ (2.0 điểm): Vẽ đúng tam giác/tứ giác, ký hiệu góc, trung điểm, tính trực quan.
                2. Lập luận chứng minh (6.0 điểm): Căn cứ định lý, tính chất, dấu hiệu nhận biết, tính logic chặt chẽ.
                3. Trình bày & Kết luận (2.0 điểm): Trình bày mạch lạc, danh pháp chuẩn xác, kết luận đúng yêu cầu.
                
                ĐỊNH DẠNG TRẢ VỀ:
                - Tổng điểm: .../10 điểm
                - Chi tiết: Hình vẽ (.../2.0), Lập luận (.../6.0), Trình bày (.../2.0)
                - Lỗi sai cụ thể cần sửa: (nêu rõ bước nào, dòng nào)
                - Nhận xét khích lệ sư phạm:
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
