import tiktoken
ENC = tiktoken.encoding_for_model("gpt-4o")   # any BPE works

def chunk(text: str, max_tokens: int = 800):
    """Yield ≤ max_tokens-token slices, preferring paragraph boundaries."""
    buf, ntok = [], 0
    for para in text.split("\n\n"):
        t = len(ENC.encode(para))
        if ntok + t > max_tokens and buf:
            yield "\n\n".join(buf)
            buf, ntok = [], 0
        buf.append(para); ntok += t
    if buf:
        yield "\n\n".join(buf)
