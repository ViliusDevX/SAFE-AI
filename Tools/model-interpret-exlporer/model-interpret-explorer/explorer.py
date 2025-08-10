import argparse, json
from pathlib import Path
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils.visualize import save_json_trace, plot_token_probs, matplotlib_attention_quick
import random

def set_seed(s=42):
    random.seed(s); np.random.seed(s); torch.manual_seed(s);
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(s)

def softmax(x):
    x = x - np.max(x)
    e = np.exp(x)
    return e / e.sum()

def sample_top_p(logits_np, top_p=0.9, temperature=0.8, block_id=None):
    """
    Robust nucleus (top-p) sampling:
    - applies temperature
    - turns logits -> probs in a numerically stable way
    - optionally blocks a token (e.g., EOS early)
    - chooses the smallest prefix whose cumulative prob >= top_p
    """
    # temperature
    if temperature and temperature != 1.0:
        logits_np = logits_np / float(temperature)

    # stable softmax
    m = np.max(logits_np)
    exp = np.exp(logits_np - m)
    probs = exp / exp.sum()

    # block a token (e.g., EOS)
    if block_id is not None and 0 <= block_id < probs.size:
        probs[block_id] = 0.0
        s = probs.sum()
        if s > 0:
            probs /= s
        else:
            # fall back to uniform over all but blocked token
            probs[:] = 1.0 / (probs.size - 1)
            probs[block_id] = 0.0

    # sort by prob desc
    sorted_idx = np.argsort(-probs)
    sorted_probs = probs[sorted_idx]

    # cumulative sum and choose cutoff length k
    cumsum = np.cumsum(sorted_probs)
    # index where cumulative prob first exceeds top_p
    k = int(np.searchsorted(cumsum, top_p, side="left")) + 1
    if k < 1:
        k = 1
    if k > sorted_probs.size:
        k = sorted_probs.size

    keep = sorted_idx[:k]
    keep_probs = probs[keep]
    keep_probs = keep_probs / keep_probs.sum()  # renormalize

    choice = int(np.random.choice(keep, p=keep_probs))
    return choice, probs

def build_blocklist(tokenizer, vocab_size: int, step: int, eos_id: int,
                    block_eos_steps: int, block_ws_steps: int):
    """
    Returns a boolean mask of length vocab_size indicating which tokens to block at this step.
    We only block EOS early and tokens that decode to pure whitespace (e.g., '\n', '   ').
    """
    mask = np.zeros(vocab_size, dtype=bool)
    if eos_id is not None and step <= block_eos_steps:
        mask[eos_id] = True

    if step <= block_ws_steps:
        # Cheap way: block a few common whitespace tokens explicitly
        common_ws = []
        try:
            common_ws += tokenizer.encode("\n")          # GPT-2: [198]
            common_ws += tokenizer.encode("\n\n")        # often two newlines
            common_ws += tokenizer.encode(" ")           # space-only token(s)
            common_ws += tokenizer.encode("\t")
        except Exception:
            pass
        for tid in common_ws:
            if 0 <= tid < vocab_size:
                mask[tid] = True
    return mask

def apply_repetition_penalty(logits, generated_ids, penalty=1.1):
    # decrease logits of tokens we've already used
    if penalty <= 1.0 or generated_ids is None or generated_ids.numel() == 0:
        return logits
    unique_ids = torch.unique(generated_ids)
    logits[unique_ids] /= penalty
    return logits

def banned_ngrams(generated_ids: torch.Tensor, n: int):
    """
    Build a dict mapping (n-1)-gram tuples -> set of next-token ids that would repeat an n-gram.
    generated_ids: [seq_len] tensor of ints
    """
    if n <= 1 or generated_ids.numel() < n:
        return {}
    seq = generated_ids.tolist()
    bans = {}
    for i in range(len(seq) - n + 1):
        prefix = tuple(seq[i:i + n - 1])
        nxt = seq[i + n - 1]
        s = bans.get(prefix)
        if s is None:
            bans[prefix] = {nxt}
        else:
            s.add(nxt)
    return bans

def apply_no_repeat_ngram(logits_np: np.ndarray, generated_ids: torch.Tensor, n: int):
    """Zero out logits that would complete a seen n-gram."""
    if n <= 1 or generated_ids.numel() < n - 1:
        return logits_np
    bans = banned_ngrams(generated_ids, n)
    if not bans:
        return logits_np
    prefix = tuple(generated_ids[-(n-1):].tolist())
    if prefix in bans:
        logits_np = logits_np.copy()
        for tid in bans[prefix]:
            if 0 <= tid < logits_np.shape[0]:
                logits_np[tid] = -1e9
    return logits_np

def main():
    p = argparse.ArgumentParser(description="Model Interpret Explorer")
    p.add_argument("--model", default="distilgpt2", help="HF model id (CPU friendly default)")
    p.add_argument("--prompt", required=True, help="Input prompt")
    p.add_argument("--max_new_tokens", type=int, default=30)
    p.add_argument("--topk", type=int, default=20)
    p.add_argument("--no_repeat_ngram_size", type=int, default=3)
    p.add_argument("--min_new_tokens", type=int, default=40)
    p.add_argument("--repetition_penalty", type=float, default=1.1)
    p.add_argument("--block_eos_steps", type=int, default=5, help="Block EOS for first N steps")
    p.add_argument("--block_ws_steps", type=int, default=8, help="Block pure-whitespace/newline tokens for first N steps")
    p.add_argument("--outdir", default="tools/model-interpret-explorer/examples")
    p.add_argument("--attn_every", type=int, default=0, help="Recompute & save full attention every N steps (0=off)")
    p.add_argument("--top_p", type=float, default=0.9)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    set_seed(args.seed)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, output_attentions=True)
    model.to(device).eval()

    enc = tokenizer(args.prompt, return_tensors="pt")
    input_ids = enc["input_ids"].to(device)

    trace = {"model": args.model, "prompt": args.prompt, "steps": []}

    with torch.no_grad():
        # Initial forward pass on the prompt
        out = model(input_ids=input_ids, use_cache=True, output_attentions=True)
        try:
            from transformers import DynamicCache
            HAS_DYNCACHE = True
        except Exception:
            HAS_DYNCACHE = False

        cache = (DynamicCache.from_legacy_cache(out.past_key_values) if HAS_DYNCACHE and hasattr(DynamicCache, "from_legacy_cache")
                 else out.past_key_values)
        logits = out.logits[:, -1, :].squeeze(0).detach().cpu().numpy()

        probs = softmax(logits)
        topk_idx = probs.argsort()[::-1][:args.topk]
        topk_tokens = [tokenizer.decode([i]) for i in topk_idx]
        topk_probs = probs[topk_idx].tolist()

        # attention over prompt (avg heads, last layer)
        attn_layers = out.attentions
        final_layer_attn = attn_layers[-1][0].mean(dim=0).detach().cpu().numpy()
        tokens_prompt = tokenizer.convert_ids_to_tokens(input_ids[0])
        step0 = {
            "step": 0,
            "generated_token": None,
            "topk_tokens": topk_tokens,
            "topk_probs": topk_probs,
            "attention_avg_final_layer": final_layer_attn.tolist(),
            "tokens": tokens_prompt
        }
        trace["steps"].append(step0)

        generated = input_ids.clone()

        decoded = tokenizer.decode(generated[0], skip_special_tokens=True)

        for step in range(1, args.max_new_tokens + 1):
            # 1) repetition penalty → logits_np
            logits_t = torch.from_numpy(logits).to(device)
            logits_t = apply_repetition_penalty(logits_t, generated[0], penalty=args.repetition_penalty)
            logits_np = logits_t.detach().cpu().numpy()

            # 2) no-repeat n-gram
            logits_np = apply_no_repeat_ngram(logits_np, generated[0], n=args.no_repeat_ngram_size)

            # 3) block EOS/whitespace early
            eos_id = tokenizer.eos_token_id
            block_mask = build_blocklist(tokenizer, logits_np.shape[-1], step, eos_id,
                                         args.block_eos_steps, args.block_ws_steps)
            logits_blocked = logits_np.copy()
            logits_blocked[block_mask] = -1e9

            # 3) sample next token
            next_id, probs = sample_top_p(
                logits_blocked, top_p=args.top_p, temperature=args.temperature, block_id=None
            )

            next_token = torch.tensor([[next_id]], device=device)
            generated = torch.cat([generated, next_token], dim=1)

            out = model(input_ids=next_token, use_cache=True, past_key_values=cache, output_attentions=bool(args.attn_every))
            cache = out.past_key_values  # DynamicCache or tuple depending on version
            logits = out.logits[:, -1, :].squeeze(0).detach().cpu().numpy()

            # log this step
            topk_idx = probs.argsort()[::-1][:args.topk]
            step_entry = {
                "step": step,
                "generated_token": tokenizer.decode([next_id]),
                "topk_tokens": [tokenizer.decode([i]) for i in topk_idx],
                "topk_probs": probs[topk_idx].tolist()
            }

            if step % 10 == 0:
                plot_token_probs(step_entry["topk_tokens"], step_entry["topk_probs"],
                                 str(outdir / f"probs_step_{step}.png"), topk=args.topk)

            # Optional full attention snapshot
            if args.attn_every and step % args.attn_every == 0:
                out_full = model(input_ids=generated, output_attentions=True, use_cache=False)
                attn_layers = out_full.attentions
                final_attn = attn_layers[-1][0].mean(dim=0).detach().cpu().numpy()
                step_entry["attention_avg_final_layer"] = final_attn.tolist()
                labels = tokenizer.convert_ids_to_tokens(generated[0])
                labels = [tokenizer.convert_tokens_to_string([t]).replace("\n", "\\n") for t in labels]
                labels = [l if len(l) <= 12 else l[:11] + "…" for l in labels]
                matplotlib_attention_quick(final_attn, labels, labels, str(outdir / f"attn_step_{step}.png"))

            trace["steps"].append(step_entry)

            decoded = tokenizer.decode(generated[0], skip_special_tokens=True)
            # stop when we hit a period followed by space (and min tokens satisfied)
            if step >= args.min_new_tokens and decoded.strip().endswith("."):
                break

    save_json_trace(str(outdir / "trace.json"), trace)

    final = trace["steps"][-1]
    plot_token_probs(final["topk_tokens"], final["topk_probs"], str(outdir / "final_step_token_probs.png"), topk=args.topk)

    # initial prompt attention heatmap
    attn0 = np.array(trace["steps"][0]["attention_avg_final_layer"])
    tokens = [t if len(t) <= 10 else t[:9] + "…" for t in trace["steps"][0]["tokens"]]
    matplotlib_attention_quick(attn0, tokens, tokens, str(outdir / "prompt_attention_heatmap.png"))

    text = tokenizer.decode(generated[0], skip_special_tokens=True)
    print("\n=== Generated Text ===\n")
    print(text)
    print("\nSaved:")
    print(f"- JSON trace: {outdir / 'trace.json'}")
    print(f"- Final step token probs: {outdir / 'final_step_token_probs.png'}")
    print(f"- Prompt attention heatmap: {outdir / 'prompt_attention_heatmap.png'}")

    with open(outdir / "output.txt", "w", encoding="utf-8") as f:
        f.write(text)

    if args.attn_every:
        print(f"- Attention snapshots every {args.attn_every} steps (attn_step_*.png)")

if __name__ == "__main__":
    main()
