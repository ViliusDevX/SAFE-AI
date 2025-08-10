# Model Interpret Explorer

Peek inside small language models **as they generate**, one token at a time.

This tool logs and visualizes:
- **Top-k next-token probabilities** at each step (what the model *considered*)
- **Attention heatmaps** (what the model *looked at* inside the prompt / running context).

It’s meant for students/engineers who want a hands-on, code-level feel for interpretability without a giant research stack.

---

## Features

- **Incremental generation** with fast cache (`past_key_values`)
- **Nucleus (top-p) sampling** + temperature
- **Safety against junk outputs**: repetition penalty, no-repeat n-grams, early blocking of EOS/whitespace
- **Attention snapshots** every _N_ steps (final layer, heads averaged)
- **Artifacts you can share**: `trace.json`, attention PNGs, token-prob PNGs, and `output.txt`

---

## Install

```bash
# from repo root
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt

```

## Quick start

Generate and save plots with a small GPT-2 model:

    python tools/model-interpret-explorer/explorer.py \
      --prompt "What are the benefits and risks of AI transparency? Answer in 5 sentences." \
      --model gpt2 \
      --max_new_tokens 120 --min_new_tokens 60 \
      --temperature 0.8 --top_p 0.9 \
      --repetition_penalty 1.15 --no_repeat_ngram_size 3 \
      --block_eos_steps 10 --block_ws_steps 14 \
      --attn_every 20 --seed 42

Prefer a chat-tuned open model for nicer prose (slower on CPU):

    python tools/model-interpret-explorer/explorer.py \
      --prompt "USER: Why does AI transparency matter to ordinary people? Please answer in 5 sentences.\nASSISTANT:" \
      --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
      --max_new_tokens 180 --min_new_tokens 80 \
      --temperature 0.7 --top_p 0.9 \
      --repetition_penalty 1.15 --no_repeat_ngram_size 3 \
      --block_eos_steps 12 --block_ws_steps 16 \
      --attn_every 30 --seed 42

Artifacts will be written to model-interpret-explorer/examples/:

    trace.json – full step-by-step log (tokens, probs, optional attentions)

    final_step_token_probs.png – last-step top-k bar chart

    prompt_attention_heatmap.png – prompt attention (final layer, heads avg)

    attn_step_*.png – attention snapshots (if --attn_every > 0)

    output.txt – final generated text

## How it works (short version)

    Tokenize the prompt -> ids.

    Run a first forward pass to get next-token logits + prompt attentions.

    For each step:

        Adjust logits (repetition penalty, no-repeat n-grams, early EOS/whitespace block).

        Sample the next token (top-p + temperature).

        Append token and run a fast incremental forward pass (with cache).

        Log top-k next-token candidates; optionally recompute a full attention snapshot.

        Stop after --min_new_tokens and a clean stop (or --stop_on).

## Tips

    If outputs look like blank lines or lists, raise --block_ws_steps and lower --temperature.

    For nicer writing, use a chat-tuned open model (e.g., TinyLlama 1.1B Chat).

    Attention snapshots are expensive; start with --attn_every 20 and adjust.

## Limitations

    Attention ≠ explanation: it’s a useful signal, not a proof of causality.

    Small models (GPT-2 class) can be repetitive and need stronger constraints.

    GPU optional: CPU works but will be slower on 1B-class models.

## Contributing

Free for contribution! Good first issues:

    Compare-two-models mode with side-by-side plots

    Head-specific attention viewers

    More readable token labels for BPE
