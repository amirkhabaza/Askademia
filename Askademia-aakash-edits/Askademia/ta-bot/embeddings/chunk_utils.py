"""
Robust token-window splitter.
Works even when the PDF is one long paragraph or OCR’d text.
"""

import tiktoken

# GPT-4o / GPT-4 / GPT-3.5 all share cl100k_base
try:
    ENC = tiktoken.encoding_for_model("gpt-4o")
except KeyError:
    ENC = tiktoken.get_encoding("cl100k_base")

def sliding_chunks(text: str,
                   max_tokens: int = 800,
                   overlap: int = 80):
    """
    Yield chunks of ≤ *max_tokens* tokens with *overlap* tokens of context.
    """
    toks = ENC.encode(text, disallowed_special=())
    step = max_tokens - overlap
    for i in range(0, len(toks), step):
        yield ENC.decode(toks[i:i + max_tokens])

