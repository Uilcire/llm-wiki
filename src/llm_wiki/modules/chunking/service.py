def chunk_text(text: str, max_tokens: int = 500, overlap: int = 100) -> list[dict]:
    """把文本按段落切块，每块大约 max_tokens 个词。"""
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""
    current_start = 0
    char_pos = 0

    for para in paragraphs:
        # 粗略估算：1 token ≈ 4 个字符（英文），中文大约 1-2 字符一个 token
        estimated_tokens = len(current_chunk) // 4

        if estimated_tokens > max_tokens and current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "start_offset": current_start,
                "end_offset": char_pos,
            })
            # overlap: 保留当前块的最后一部分作为下一块的开头
            overlap_text = current_chunk[-(overlap * 4):]
            current_start = char_pos - len(overlap_text)
            current_chunk = overlap_text

        current_chunk += para + "\n\n"
        char_pos += len(para) + 2  # +2 for "\n\n"

    # 最后一块
    if current_chunk.strip():
        chunks.append({
            "content": current_chunk.strip(),
            "start_offset": current_start,
            "end_offset": char_pos,
        })

    return chunks