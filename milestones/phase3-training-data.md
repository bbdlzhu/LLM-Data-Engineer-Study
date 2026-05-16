# Phase 3 Milestone — LLM Training Data Construction

**Timeframe**: Month 5-6
**Status**: ⚪ Not Started

---

## Milestone Project

**Task**: For a specific domain (medical consultation or code generation), synthesize 2,000 high-quality SFT (Supervised Fine-Tuning) samples using LLM APIs. Output must strictly conform to Llama 3 or Qwen 2 training template.

### Requirements Checklist

#### 1. Domain & Task Design
- [ ] Select target domain (medical QA / code generation / other)
- [ ] Define task taxonomy within the domain (sub-categories of questions)
- [ ] Design difficulty gradient (easy → medium → hard)
- [ ] Create seed prompts for data generation (~50-100 seeds)

#### 2. SFT Data Synthesis
- [ ] Implement Self-Instruct pipeline:
  - Instruction generation from seeds
  - Response generation (Claude / GPT-4 API)
  - Quality filtering (length, relevance, format checks)
- [ ] Implement Evol-Instruct pipeline (optional enhancement):
  - Instruction evolution (deepen, broaden, add constraints)
  - Response regeneration for evolved instructions
- [ ] Rate limiting, retry logic, error handling for API calls
- [ ] Cost tracking per API call

#### 3. Quality Control
- [ ] Automated validation checks:
  - Response length thresholds
  - Format compliance
  - Keyword / entity presence
  - No model refusal or hallucination markers
- [ ] Manual spot-check of 100 samples (~5%)
- [ ] Deduplication of instruction pairs (semantic similarity check)
- [ ] Balance check across sub-categories

#### 4. Output Format
- [ ] Llama 3 chat template format:
  ```
  <|begin_of_text|><|start_header_id|>user<|end_header_id|>
  {instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
  {response}<|eot_id|>
  ```
- [ ] Or Qwen 2 chat template format:
  ```
  <|im_start|>system
  {system_message}<|im_end|>
  <|im_start|>user
  {instruction}<|im_end|>
  <|im_start|>assistant
  {response}<|im_end|>
  ```
- [ ] JSONL file with consistent schema
- [ ] Metadata: generation model, prompt template used, quality score

#### 5. Documentation
- [ ] Data card (following HuggingFace / Google data card template)
- [ ] Prompt templates documented
- [ ] Known limitations and biases noted
- [ ] Intended use and out-of-scope use cases

### Completion Criteria

- 2,000 valid SFT samples generated and validated
- Training template format verified (tokenizer round-trip test)
- Data card complete
- Manual spot-check pass rate ≥ 90%

---

## Learning Resources

- **Papers**: [Self-Instruct](https://arxiv.org/abs/2212.10560), [Evol-Instruct](https://arxiv.org/abs/2304.12244), [LIMA](https://arxiv.org/abs/2305.11206)
- **Reference**: [HuggingFace Data Card Guide](https://huggingface.co/docs/hub/datasets-cards), [Llama 3 Prompt Format](https://llama.meta.com/docs/model-cards-and-prompt-formats/meta-llama-3/)
- **Tools**: Claude API, OpenAI API, [guidance](https://github.com/guidance-ai/guidance)

---

*Created: 2026-05-16*
