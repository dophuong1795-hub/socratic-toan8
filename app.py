def execute_openrouter_request(inputs, system_prompt=None, is_json=False):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Socratic Geometry Game"
    }

    content_parts = []
    for item in inputs:
        if isinstance(item, str):
            content_parts.append({"type": "text", "text": item})
        elif isinstance(item, Image.Image):
            buffered = io.BytesIO()
            img_format = "JPEG" if item.format == "JPEG" else "PNG"
            item.convert("RGB").save(buffered, format=img_format)
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{img_format.lower()};base64,{img_b64}"
                }
            })

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": content_parts})

    payload = {
        "model": MODEL_NAME,
        "messages": messages
    }
    # Chỉ bật json_object khi mô hình hỗ trợ
    if is_json and "free" not in MODEL_NAME:
        payload["response_format"] = {"type": "json_object"}

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise Exception(f"Lỗi OpenRouter ({resp.status_code}): {resp.text}")

    res_data = resp.json()
    if not res_data.get("choices") or not res_data["choices"][0].get("message"):
        raise Exception("Mô hình không trả về nội dung, vui lòng thử lại!")

    text_out = res_data["choices"][0]["message"].get("content", "")

    if is_json:
        # Bóc tách khối JSON nằm giữa cặp ngoặc nhọn { ... }
        match = re.search(r"\{[\s\S]*\}", text_out)
        if match:
            clean = match.group(0)
            return json.loads(clean)
        else:
            clean = re.sub(r"^```json\s*|^```\s*|```$", "", text_out.strip(), flags=re.MULTILINE)
            return json.loads(clean)
            
    return text_out
