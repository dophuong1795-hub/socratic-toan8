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

# Chỉ định trực tiếp mô hình chuẩn mới nhất của Google
MODEL_NAME = "gemini-3.8-flash"

# Lời nhắc sư phạm Socratic cho Tab 1
SYSTEM_SOCRATIC = """
Bạn là Giáo viên Toán THCS tại Việt Nam chuyên bồi dưỡng tư duy Hình học 8 theo phương pháp Socratic.
Quy tắc:
1. TUYỆT ĐỐI KHÔNG giải hộ bài toán, không viết sẵn bài chứng minh dài dòng.
2. Sử dụng tiếng Việt chuẩn mực sư phạm, giữ đúng ký hiệu đỉnh, đoạn thẳng, góc, song song, vuông góc (A, B, C, D, M, N...).
3. Mỗi phản hồi chỉ gồm 1-2 câu: Nhận xét hình vẽ/câu trả lời của học sinh và đặt 01 câu hỏi tư duy suy luận ngược hoặc gợi ý vẽ thêm điểm đối xứng, đường trung bình.
"""

st.title("📐 Học toán cùng cô Phương: Hình học 8")

# Chia 2 tab: Gia sư gợi mở & Nộp bài tự động chấm
tab1, tab2 = st.tabs(["💬 Gia sư Socratic (Hỏi đáp gợi mở)", "📝 Nộp bài tập & Chấm tự động"])

# ================= TAB 1: GIA SƯ SOCRATIC =================
with tab1:
    st.caption("AI đóng vai trò trợ lý gợi mở, không giải hộ, hướng dẫn suy luận ngược theo SGK.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Chào em! Em đang gặp khó khăn ở bài toán chứng minh hay hình vẽ nào? Hãy chụp ảnh đề bài hoặc gửi giả thiết để cô trò mình cùng tháo gỡ nhé!"
        }]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "img" in msg and msg["img"] is not None:
                st.image(msg["img"], width=300)
                
    up_chat_img = st.file_uploader("📸 Tải ảnh đề bài/hình vẽ tay lên đây:", type=["jpg", "png", "jpeg"], key="chat_up")
    
    if user_prompt := st.chat_input("Nhập câu hỏi hoặc câu trả lời của em..."):
        chat_img = Image.open(up_chat_img) if up_chat_img else None
        st.session_state.messages.append({"role": "user", "content": user_prompt, "img": chat_img})
        
        with st.chat_message("user"):
            st.markdown(user_prompt)
            if chat_img:
                st.image(chat_img, width=300)
                
        with st.chat_message("assistant"):
            with st.spinner("Cô đang quan sát hình vẽ và gợi ý..."):
                try:
                    model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=SYSTEM_SOCRATIC)
                    input_payload = []
                    if chat_img:
                        input_payload.append(chat_img)
                    input_payload.append(user_prompt)
                    
                    response = model.generate_content(input_payload)
                    reply_text = response.text
                except Exception as e:
                    reply_text = f"Lỗi phản hồi: {str(e)}"
                    
                st.markdown(reply_text)
                st.session_state.messages.append({"role": "assistant", "content": reply_text})

# ================= TAB 2: NỘP BÀI & CHẤM ĐIỂM =================
with tab2:
    st.caption("Chấm tự luận tự động bằng AI theo Rubric sư phạm chuẩn.")
    
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
