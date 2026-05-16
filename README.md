# LLM Data Engineer Study

🚀 **从大数据工程师到LLM数据工程师的系统进阶之路**

这是我从大数据工程师（Spark/Hadoop/Java/Scala）转行到大模型数据工程师（LLM Data Engineer）的学习仓库。借助 Claude Code 作为 AI 导师，基于 Guided Learning 方法进行系统化学习。

**参考灵感**: 感谢 [@chenran818/CFP-Study](https://github.com/chenran818/CFP-Study) 提供的 AI 驱动学习范式。

**关于我**: 大数据背景，正在系统学习 LLM 数据工程。欢迎交流:
- GitHub: [@bbdlzhu](https://github.com/bbdlzhu)

---

## 学习路线图 (8个月，4个阶段)

| 阶段 | 时间 | 主题 | 核心目标 |
|------|------|------|----------|
| **Phase 1** | 第1-2月 | Python 工程化改造 | 从"写脚本"升级到"写系统" |
| **Phase 2** | 第3-4月 | 全模态数据计算引擎 | Spark → Ray 分布式 AI 计算 |
| **Phase 3** | 第5-6月 | 大模型训练数据构建 | SFT/RLHF 数据构造逻辑 |
| **Phase 4** | 第7-8月 | 评测驱动开发 (EDD) | 数据→评测→模型提升 闭环 |

### Phase 1: Python 生产级改造
- 高级 Python: Decorators, Generators, Type Hints
- 工具链: ruff, pre-commit, pytest (coverage ≥ 80%)
- Docker 封装运行环境
- **里程碑**: 用纯 Python 重写一个 Spark 数据处理任务

### Phase 2: 多模态数据计算引擎
- Ray 生态: Ray Core, Ray Data
- 文本算子: 语种检测, PCL 过滤, MinHash LSH 去重
- 跨模态: CLIP Score 图文相似度
- **里程碑**: 用 Ray 编写完整预训练数据清洗 Pipeline

### Phase 3: 大模型训练数据构建
- 预训练数据配比策略
- SFT 数据合成: Self-Instruct, Evol-Instruct
- DPO/RLHF 偏好数据构建
- **里程碑**: 合成 2000 条高质量 SFT 数据

### Phase 4: 评测驱动开发
- Benchmark 体系: MMLU, GSM8K, HumanEval
- LLM-as-a-Judge 评测
- Qwen2-7B 微调 + 跑分对比
- **里程碑**: 数据质量对模型指标的量化分析报告

---

## 如何使用

### 每日学习

1. 在本仓库中打开 Claude Code：
   ```bash
   claude-code
   ```
2. 像和导师对话一样提问
3. Claude 会使用苏格拉底式教学法进行引导
4. 每次学习后，Claude 会自动记录学习笔记和进度

### 复习与回顾

当你需要复习时，直接问 Claude：
- "帮我回顾一下最近薄弱的知识点"
- "今天我应该学什么？"
- "考考我 Phase 2 的内容"
- "看看我的整体进度"

Claude 会读取你的学习历史，制定个性化的复习计划。

### 追踪进度

查看 `/progress/learning-tracker.md` 了解：
- 整体学习进度
- 各阶段完成情况
- 已掌握的技能
- 待攻克的知识盲区

---

## 仓库结构

```
/sessions/                    # 每日学习记录
  /YYYY-MM-DD/
    session-notes.md          # 详细学习笔记
  SESSION-TEMPLATE.md         # 笔记模板

/progress/
  learning-tracker.md         # 全局学习追踪（唯一真相来源）

/milestones/                   # 阶段性里程碑
  phase1-python-engineering.md
  phase2-multimodal-engine.md
  phase3-training-data.md
  phase4-evaluation-driven.md

CLAUDE.md                      # AI 导师系统提示词
README.md                      # 本文件
```

---

## 如何使用本仓库开始你的学习

想用这套 AI 驱动的学习系统来规划你自己的转行之路？

1. **Clone 本仓库**:
   ```bash
   git clone https://github.com/bbdlzhu/LLM-Data-Engineer-Study.git
   cd LLM-Data-Engineer-Study
   ```

2. **清除我的学习记录** (从零开始):
   ```bash
   rm -rf progress/learning-tracker.md sessions/20*/
   ```

3. **修改 CLAUDE.md** 中的背景信息为你自己的背景

4. **启动 Claude Code**:
   ```bash
   claude-code
   ```

5. **开始学习！** 提出你的第一个问题，Claude 会：
   - 用苏格拉底式教学法引导你
   - 自动创建 `progress/` 和 `sessions/` 目录
   - 追踪你的学习历程

`CLAUDE.md` 文件包含了所有 AI 导师的行为指令，**直接生效**。

---

## 学习哲学

**Guided Learning 方法:**
- 对话式、无评判的学习氛围
- 从你已有的大数据知识出发，建立知识桥梁
- 每个概念都配合可运行的代码
- 先动手，再理解理论
- 聚焦实际工程需求，不学无用的屠龙术


