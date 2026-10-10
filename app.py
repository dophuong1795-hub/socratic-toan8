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
    page_title="Đấu Trường Hình Học 8",
    page_icon="📐",
    layout="centered"
)

st.title("📐 ĐẤU TRƯỜNG HÌNH HỌC 8")
st.caption("Trợ lý Sư phạm Hình học 8 - Học toán gợi mở cùng Cô Mai Phương")

# ================= KIỂM TRA API KEY =================
API_KEY = st.secrets.get("OPENROUTER_API_KEY")
if not API_KEY:
    st.error("Chưa cấu hình OPENROUTER_API_KEY trong Secrets của Streamlit Cloud!")
    st.stop()

MODELS_PRIORITY = [
    "google/gemini-2.0-flash-lite-001",
    "google/gemini-2.0-flash-001",
    "google/gemini-flash-1.5"
]

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

    # 2. CHUẨN HÓA PHÂN SỐ CÓ NÉT GẠCH NGANG: AC/2, AB/2 -> $\dfrac{AC}{2}$
    text = re.sub(r"(?<![a-zA-Z0-9_\$])([A-Z]{1,2}|\d+)\s*/\s*([A-Z]{1,2}|\d+)(?![a-zA-Z0-9_\$])", r"$\\dfrac{\1}{\2}$", text)
    text = re.sub(r"\$?\\frac\{([^}]+)\}\{([^}]+)\}\$?", r"$\\dfrac{\1}{\2}$", text)

    # 3. CHUẨN HÓA GÓC THÀNH DẤU MŨ: Góc IHA, góc A -> $\widehat{IHA}$, $\widehat{A}$
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

# ================= PROMPT CHUẨN SƯ PHẠM =================
ORIGINAL_PROMPT = """
Bạn là Trợ lý Sư phạm Hình học 8 của Cô Mai Phương. 
Học sinh lớp 8, bộ sách Kết nối tri thức.

QUY TẮC CÂU HỎI VÀ ĐÁP ÁN:
1. Thân thiện, ngắn gọn, khai thác từng bước gợi mở Socratic.
2. Bước 1: Khai thác giả thiết khởi đầu (trung tuyến ứng với cạnh huyền, tam giác cân...). Tuyệt đối không hỏi ngay kết luận của bài toán.
3. Phân số viết dạng: \\dfrac{AB}{2}. Góc viết dạng: \\widehat{ABC}.
4. MẢNG options: Gồm 4 phương án ngắn gọn. KHÔNG ghi A., B., C., D. ở đầu các phương án.
5. Tuyệt đối KHÔNG xuất hiện suy nghĩ nội bộ (Thinking Process) hay thông báo an toàn hệ thống.

BẮT BUỘC TRẢ VỀ DUY NHẤT 1 KHỐI JSON:
{
  "total_steps": 3,
  "feedback": "Khen ngợi ngắn 1 câu",
  "question": "Nội dung câu hỏi ngắn gọn",
  "options": [
    "Phương án 1",
    "Phương án 2",
    "Phương án 3",
    "Phương án 4"
  ],
  "correct_index": 0,
  "explanation": "Giải thích ngắn 2 câu theo SGK Toán 8",
  "is_finished": false,
  "full_solution": ""
}
"""

# ================= GỌI API OPENROUTER =================
def call_ai(inputs, prompt_system=ORIGINAL_PROMPT):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    content_parts = []
    for item in inputs:
        if isinstance(item, str):
            content_parts.append({"type": "text", "text": item})
        elif isinstance(item, Image.Image):
            img = ImageOps.exif_transpose(item)
            if max(img.size) > 800:
                img.thumbnail((800, 800))
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="JPEG", quality=80)
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            })

    payload = {
        "model": MODELS_PRIORITY[0],
        "models": MODELS_PRIORITY,
        "messages": [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": content_parts}
        ],
        "temperature": 0.2,
        "max_tokens": 1200
    }

    res = requests.post(url, headers=headers, json=payload, timeout=25)
    if res.status_code != 200:
        raise Exception(f"Máy chủ AI bận ({res.status_code})")

    data = res.json()
    msg = data["choices"][0]["message"]
    text = msg.get("content") or msg.get("reasoning") or ""
    return text.strip()

# ================= BÓC TÁCH KẾT QUẢ JSON =================
def parse_result(text: str):
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            d = json.loads(m.group(0))
            if "question" in d and "options" in d and len(d["options"]) >= 4:
                return {
                    "total_steps": d.get("total_steps", 3),
                    "feedback": format_math(d.get("feedback", "")),
                    "question": format_math(d.get("question", "")),
                    "options": [format_math(o) for o in d.get("options", [])[:4]],
                    "correct_index": int(d.get("correct_index", 0)) % 4,
                    "explanation": format_math(d.get("explanation", "")),
                    "is_finished": d.get("is_finished", False),
                    "full_solution": format_math(d.get("full_solution", ""))
                }
        except Exception:
            pass

    return {
        "total_steps": 3,
        "feedback": "Cùng phân tích tiếp nhé!",
        "question": "Dựa vào các dữ kiện hình học, khẳng định nào sau đây là đúng?",
        "options": ["Khẳng định 1", "Khẳng định 2", "Khẳng định 3", "Khẳng định 4"],
        "correct_index": 0,
        "explanation": "Căn cứ theo định lý trong SGK Toán 8.",
        "is_finished": False,
        "full_solution": ""
    }

# Khởi tạo Session State
if "submission_history" not in st.session_state:
    st.session_state.submission_history = []
if "step" not in st.session_state:
    st.session_state.step = 1
if "card" not in st.session_state:
    st.session_state.card = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = None
if "img_data" not in st.session_state:
    st.session_state.img_data = None

# Giao diện Tabs
tab1, tab2, tab3 = st.tabs(["🎮 Thử thách", "📝 Nộp Bài Tập", "📊 Bảng Điểm"])

# ================= TAB 1: THỬ THÁCH =================
with tab1:
    with st.expander("📸 Tải ảnh đề bài / hình vẽ", expanded=(st.session_state.card is None)):
        up = st.file_uploader("Chọn ảnh đề bài:", type=["jpg", "png", "jpeg"])
        if up:
            st.session_state.img_data = Image.open(up)
            st.image(st.session_state.img_data, caption="Đề bài đang giải", use_column_width=True)

        if st.session_state.img_data and st.session_state.card is None:
            if st.button("🚀 Bắt đầu nhận Thử thách Bước 1!", type="primary", use_container_width=True):
                with st.spinner("Cô Mai Phương đang chuẩn bị câu hỏi gợi ý..."):
                    try:
                        out = call_ai([st.session_state.img_data, "Tạo câu hỏi trắc nghiệm Bước 1 khai thác giả thiết khởi đầu."])
                        st.session_state.card = parse_result(out)
                        st.session_state.step = 1
                        st.session_state.answered = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

    card = st.session_state.card
    if card:
        total = card.get("total_steps", 3)
        curr = st.session_state.step
        st.info(f"**CỬA ẢI: BƯỚC {curr} / {total}**")

        if card.get("feedback"):
            st.caption(f"💡 {card['feedback']}")

        # Hiển thị câu hỏi với đầy đủ phân số gạch ngang và dấu mũ góc LaTeX
        st.markdown(f"### 🎯 {card['question']}")
        st.write("")

        opts = card.get("options", [])
        correct = card.get("correct_index", 0)

        if not st.session_state.answered:
            st.write("**👉 Em hãy chọn một đáp án đúng nhất:**")
            
            # Hiển thị từng phương án dạng Markdown chuẩn LaTeX kèm nút bấm chọn
            for idx, opt in enumerate(opts):
                st.markdown(f"**{chr(65+idx)}.** {opt}")
                if st.button(f"Chọn đáp án {chr(65+idx)}", key=f"btn_choice_{idx}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.selected_idx = idx
                    st.rerun()
                st.write("")
        else:
            sel = st.session_state.selected_idx
            if sel == correct:
                st.success("🎉 **Chính xác!** Em đã lựa chọn hướng tư duy rất chuẩn.")
            else:
                st.error("❌ **Chưa chính xác.**")
                st.markdown(f"Đáp án đúng là: **{chr(65+correct)}. {opts[correct]}**")

            st.info(f"**💡 Hướng suy luận:** {card.get('explanation', '')}")

            is_done = card.get("is_finished") or (curr >= total)
            if is_done:
                st.balloons()
                st.success("🏆 **XUẤT SẮC! Em đã hoàn thành toàn bộ bài toán!**")
                if card.get("full_solution"):
                    st.markdown("#### 🎁 BÀI GIẢI MẪU HOÀN CHỈNH:")
                    st.markdown(card["full_solution"])
            else:
                if st.button("➡️ Sang thử thách tiếp theo", type="primary", use_container_width=True):
                    with st.spinner("Đang chuẩn bị câu hỏi tiếp theo..."):
                        try:
                            prompt_next = f"Học sinh đã chọn đúng phương án {chr(65+correct)}. Tạo câu hỏi Bước {curr + 1} / {total}. Dùng phân số gạch ngang \\dfrac{{a}}{{b}} và góc \\widehat{{ABC}}. Nếu là bước cuối, hãy đặt is_finished = true và viết bài giải vào full_solution."
                            out = call_ai([st.session_state.img_data, prompt_next])
                            st.session_state.card = parse_result(out)
                            st.session_state.step += 1
                            st.session_state.answered = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

        st.write("---")
        if st.button("🔄 Giải bài tập khác", use_container_width=True):
            st.session_state.step = 1
            st.session_state.card = None
            st.session_state.answered = False
            st.session_state.img_data = None
            st.rerun()

# ================= TAB 2: NỘP BÀI =================
with tab2:
    st.subheader("📋 Nộp bài tập tự luận chấm bằng AI")
    s_name = st.text_input("Họ và tên học sinh:")
    s_class = st.selectbox("Lớp:", ["8A13", "8A18"])
    topic = st.selectbox("Dạng bài:", ["Hình thang cân", "Hình bình hành", "Hình chữ nhật", "Hình thoi", "Hình vuông", "Định lý Thalès", "Bài tập tổng hợp"])
    hw_file = st.file_uploader("Chụp ảnh bài giải trong vở:", type=["jpg", "png", "jpeg"], key="hw_file")

    if st.button("🚀 Nộp bài & Chấm điểm", type="primary", use_container_width=True):
        if not s_name:
            st.warning("Vui lòng điền Họ và tên!")
        elif not hw_file:
            st.warning("Vui lòng tải ảnh bài làm!")
        else:
            with st.spinner("Đang chấm bài..."):
                hw_img = Image.open(hw_file)
                rubric = f"Chấm bài tự luận Toán 8 dạng '{topic}' theo thang điểm 10. Trả về: Điểm số/10 và Nhận xét chi tiết."
                res_score = call_ai([rubric, hw_img], prompt_system="Bạn là giáo viên chấm bài thi Toán THCS chuẩn mực.")
                st.session_state.submission_history.append({
                    "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Họ và tên": s_name,
                    "Lớp": s_class,
                    "Bài tập": topic,
                    "Kết quả": res_score.replace("\n", " ")
                })
                st.success("Đã hoàn tất chấm bài!")
                st.markdown(format_math(res_score))

# ================= TAB 3: BẢNG ĐIỂM =================
with tab3:
    st.subheader("📊 Sổ Điểm Lớp Học")
    if len(st.session_state.submission_history) == 0:
        st.info("Chưa có bài nộp nào.")
    else:
        df = pd.DataFrame(st.session_state.submission_history)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="📗 Tải bảng điểm CSV (cho Google Sheets / Excel)",
            data=csv,
            file_name=f"Bang_Diem_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
