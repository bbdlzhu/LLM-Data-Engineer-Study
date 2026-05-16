# Phase 2 Milestone — Multimodal Data Computing Engine

**Timeframe**: Month 3-4
**Status**: ⚪ Not Started

---

## Milestone Project

**Task**: Download a subset of Common Crawl or Wudao dataset and build a complete pretraining data cleaning pipeline using Ray.

### Pipeline Stages

```
Raw Data → Text Extraction → Language Detection → PCL Filtering → MinHash Dedup → Quality Scoring → JSONL Output
```

### Requirements Checklist

#### 1. Data Acquisition
- [ ] Select data source (Common Crawl WET files / Wudao subset)
- [ ] Download manageable subset (~10-50GB raw)
- [ ] Store in appropriate format (Parquet / JSONL)

#### 2. Text Extraction
- [ ] HTML to plain text extraction (trafilatura / boilerpipe3 / readability)
- [ ] Metadata preservation (URL, timestamp, source)
- [ ] Encoding normalization (UTF-8)

#### 3. Language Detection
- [ ] Language detection operator (fasttext / lingua-py)
- [ ] Configurable language filter (keep: zh, en, or target languages)
- [ ] Confidence threshold tuning

#### 4. PCL Filtering
- [ ] Toxicity scoring (perspective API or open-source model)
- [ ] Personal identifiable information (PII) detection and masking
- [ ] Configurable threshold-based filtering

#### 5. MinHash LSH Deduplication
- [ ] Document-level MinHash computation
- [ ] LSH-based near-duplicate detection
- [ ] Configurable similarity threshold (e.g., Jaccard ≥ 0.8)
- [ ] Dedup statistics reporting

#### 6. Quality Scoring
- [ ] Perplexity-based quality scoring
- [ ] Text length filtering
- [ ] Repetition / gibberish detection
- [ ] Composite quality score + threshold filtering

#### 7. Output
- [ ] JSONL format with consistent schema
- [ ] Statistics file (doc counts per stage, dedup ratio, language distribution)
- [ ] Pipeline configuration file for reproducibility

#### 8. Performance
- [ ] Ray Data pipeline orchestration
- [ ] Shuffle monitoring and optimization
- [ ] Throughput logging (docs/sec per stage)
- [ ] Ray Dashboard screenshots / metrics

### Completion Criteria

- Pipeline runs end-to-end on the selected data subset
- Each stage produces verifiable intermediate outputs
- Performance metrics recorded
- Output passes manual quality spot-check

---

## Learning Resources

- **Docs**: [Ray Core](https://docs.ray.io/en/latest/ray-core/walkthrough.html), [Ray Data](https://docs.ray.io/en/latest/data/data.html)
- **Libraries**: [datasketch](https://github.com/ekzhu/datasketch), [text-dedup](https://github.com/ChenghaoMou/text-dedup), [fasttext](https://fasttext.cc/), [trafilatura](https://trafilatura.readthedocs.io/)
- **Reference**: [CCNet](https://github.com/facebookresearch/cc_net), [BigScience ROOTS](https://github.com/bigscience-workshop/data-preparation)

---

*Created: 2026-05-16*
