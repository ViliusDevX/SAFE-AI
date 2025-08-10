# tools/model-interpret-explorer/utils/visualize.py
from typing import List, Dict
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import json
from pathlib import Path

def save_json_trace(path: str, trace: Dict):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace, f, ensure_ascii=False, indent=2)

def plot_token_probs(tokens: List[str], probs: List[float], out_path: str, topk: int = 20):
    # filter blanks/specials
    filtered = [(t, p) for t, p in zip(tokens, probs) if t.strip() and "endoftext" not in t]
    filtered = filtered[:topk] if len(filtered) >= topk else filtered
    if not filtered:
        filtered = [("…", 1.0)]
    toks, pr = zip(*filtered)
    fig = go.Figure(go.Bar(x=pr, y=toks, orientation="h"))
    fig.update_layout(title="Top-k token probabilities (next token)", xaxis_title="Probability", yaxis_title="Token")
    fig.write_image(out_path)

def plot_attention_heatmap(attn: np.ndarray, tokens_src: List[str], tokens_tgt: List[str], out_path: str):
    fig = go.Figure(data=go.Heatmap(z=attn, x=tokens_src, y=tokens_tgt))
    fig.update_layout(title="Attention heatmap (avg over heads)", xaxis_title="Source tokens", yaxis_title="Target tokens")
    fig.write_image(out_path)

def matplotlib_attention_quick(attn: np.ndarray, tokens_src: List[str], tokens_tgt: List[str], out_path: str):
    plt.figure()
    plt.imshow(attn, aspect='auto')
    plt.colorbar()
    plt.xticks(range(len(tokens_src)), tokens_src, rotation=90)
    plt.yticks(range(len(tokens_tgt)), tokens_tgt)
    plt.title("Attention heatmap (avg over heads)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()
