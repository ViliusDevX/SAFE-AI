# AI Safety Landscape & Research Vectors

## Purpose of This Folder
This folder is dedicated to mapping the **landscape of AI safety research** — inspired by resources such as the [Future of Life Institute’s AI Safety Research Landscape](https://futureoflife.org/landscape/), and expanding it with **original analysis** on promising and high-impact research vectors.

It’s meant to:
- Clarify the **different domains** of AI safety work.
- Identify **which directions** are most valuable for new researchers.
- Connect landscape concepts to **practical Safe-AI projects**.

---

## What is the AI Safety Landscape?
In simple terms, the AI safety landscape is a **map of all the research areas** aimed at making advanced AI systems **safe, interpretable, and aligned** with human values.

Broad categories include:
- **Robustness & Reliability** – ensuring AI systems behave as expected even in adversarial or rare conditions.
- **Alignment & Value Learning** – making sure AI goals match human intent and moral frameworks.
- **Interpretability & Transparency** – making AI’s internal decision-making understandable.
- **Societal Impacts & Governance** – legal, ethical, and political mechanisms for safe deployment.
- **Control & Corrigibility** – the ability to update, correct, or shut down AI without resistance.

---

## My Current Research Analysis

### **Top Priority Vectors to Learn in 2025**
These are **technically deep** areas that:
1. Have high potential impact on preventing catastrophic AI failure.
2. Are still young enough that a single dedicated person can contribute meaningfully.

#### 1. **Interpretability of Large Models**
- **Why**: Without understanding *how* a model makes decisions, you can’t ensure safety. Interpretability is the bedrock for debugging alignment failures.
- **Skills to learn**:
  - Transformer architecture internals.
  - Mechanistic interpretability (e.g., Anthropic’s work, TransformerLens library).
  - Visualization and attribution methods.
- **Practical next step**: Start with *transformer circuit analysis* using Python + PyTorch.

#### 2. **Robustness Against Adversarial Attacks**
- **Why**: Models in the wild will face malicious inputs. Adversarial robustness overlaps with your cybersecurity background.
- **Skills to learn**:
  - Adversarial example generation (FGSM, PGD).
  - Robust training methods.
  - Distributional shift detection.
- **Practical next step**: Build an adversarial defense benchmark for small models.

#### 3. **Scalable Oversight**
- **Why**: As models grow beyond human review capacity, we need systems that can supervise AI effectively at scale.
- **Skills to learn**:
  - Debate/iterated amplification.
  - AI-assisted auditing.
  - Reward modeling.
- **Practical next step**: Implement a small-scale AI debate system between GPT-like models.

#### 4. **Model Provenance & Data Lineage**
- **Why**: Understanding where model training data came from is key for both bias reduction and misinformation control.
- **Skills to learn**:
  - Data tracking pipelines.
  - Cryptographic signatures for datasets.
  - Dataset filtering techniques.
- **Practical next step**: Experiment with embedding-based deduplication and source tagging.

#### 5. **AI Honeypots & Intrusion Detection**
- **Why**: Borrowing from cybersecurity, these systems bait and detect misuse attempts, helping identify dangerous behaviors early.
- **Skills to learn**:
  - Security deception design.
  - Behavioral anomaly detection.
  - Event-triggered automated responses.
- **Practical next step**: Expanding `GUARDIAN` tool to detect unexpected prompt patterns.

---

## Why These Vectors Matter for Safe-AI
Safe-AI’s mission is to **operationalize** AI safety — turning research theory into working, testable code.  
The above vectors are chosen to:
- Align with the **current bottlenecks** in AI safety research.
- Leverage your existing strengths in Python, cybersecurity, and automation.
- Lead toward **unique tools** that other researchers and policymakers can actually use.

---

## Next Steps
1. Read and annotate the official [FLI Landscape](https://futureoflife.org/landscape/).
2. Pick **one vector** above and go deep — publish small, iterative tools here.
3. Document findings in this folder so others can follow and build on them.

---

*Vilius — Cybersecurity & AI Safety Enthusiast*
