def chunk_text(text, max_len=500):
    """Split long text into clean chunks."""
    words = text.split()
    chunks, curr = [], []

    for w in words:
        curr.append(w)
        if len(curr) >= max_len:
            chunks.append(" ".join(curr))
            curr = []

    if curr:
        chunks.append(" ".join(curr))

    return chunks