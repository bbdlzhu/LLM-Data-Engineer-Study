# Phase 4 Milestone — Evaluation-Driven Development & Data Flywheel

**Timeframe**: Month 7-8
**Status**: ⚪ Not Started

---

## Milestone Project

**Task**: Fine-tune Qwen2-7B using Phase 3 SFT data (via LLaMA-Factory), run benchmark comparison pre/post fine-tuning, and produce a quantitative analysis report on how data quality impacts model metrics.

### Requirements Checklist

#### 1. Benchmark Setup
- [ ] Set up evaluation harness for at least 2 benchmarks:
  - Knowledge: MMLU (subset — relevant categories)
  - Code: HumanEval (if code domain) OR Math: GSM8K (if QA domain)
- [ ] Run baseline evaluation on Qwen2-7B base model
- [ ] Record and store baseline scores

#### 2. Fine-tuning
- [ ] Set up LLaMA-Factory environment
- [ ] Configure LoRA fine-tuning:
  - Rank, alpha, dropout
  - Learning rate schedule
  - Batch size and gradient accumulation
- [ ] Train on Phase 3 SFT data
- [ ] Monitor training loss and log to W&B or TensorBoard
- [ ] Save checkpoint(s)

#### 3. Post-Fine-tuning Evaluation
- [ ] Run same benchmarks on fine-tuned model
- [ ] Compare scores: per-category breakdown
- [ ] Statistical significance check (if applicable)
- [ ] Qualitative analysis: spot-check model outputs

#### 4. LLM-as-a-Judge Evaluation
- [ ] Design evaluation prompts for GPT-4 as judge:
  - Pairwise comparison (baseline vs fine-tuned)
  - Rubric-based scoring (accuracy, helpfulness, safety)
- [ ] Sample 200 test prompts
- [ ] Run LLM-as-a-Judge evaluation
- [ ] Analyze judge scores and agreement

#### 5. Quantitative Impact Report
- [ ] Executive summary
- [ ] Benchmark score comparison (before/after)
- [ ] Win-rate from LLM-as-a-Judge
- [ ] Data quality → metric correlation analysis
- [ ] Ablation analysis (if applicable):
  - Effect of data size (500 vs 1000 vs 2000)
  - Effect of quality filtering
- [ ] Recommendations for next data iteration
- [ ] Limitations and caveats

### Completion Criteria

- Baseline and fine-tuned benchmark scores documented
- LLM-as-a-Judge evaluation complete
- Quantitative impact report written (min 5 pages)
- Clear, actionable recommendations for the next data flywheel iteration

---

## Learning Resources

- **Benchmarks**: [MMLU](https://github.com/hendrycks/test), [GSM8K](https://github.com/openai/grade-school-math), [HumanEval](https://github.com/openai/human-eval)
- **Evaluation**: [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness), [AlpacaEval](https://github.com/tatsu-lab/alpaca_eval)
- **Fine-tuning**: [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory), [LoRA paper](https://arxiv.org/abs/2106.09685)
- **LLM-as-Judge**: [Judging LLM-as-a-Judge (paper)](https://arxiv.org/abs/2306.05685), [MT-Bench](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge)

---

*Created: 2026-05-16*
