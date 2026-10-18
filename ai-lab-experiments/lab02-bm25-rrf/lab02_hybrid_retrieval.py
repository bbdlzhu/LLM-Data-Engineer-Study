#!/usr/bin/env python3
"""实验2：混合检索——亲手实现 BM25 + RRF 融合（对齐 10-17《RAG 检索增强生成》课）"""

import math
from collections import Counter


def tok_bigram(text):
    t = "".join(text.split())
    return [t[i : i + 2] for i in range(len(t) - 1)]


def tok_unigram(text):
    return list("".join(text.split()))


# ---- 小数据集：8 篇 AI 知识短文 ----
corpus = {
    "d1": "BPE 分词通过合并高频字符对构建词表。词表大小是关键超参数：太小导致 fertility 过高、序列变长；太大则稀疏。训练与推理必须使用同一份 tokenizer，否则 token 边界错位会直接影响模型行为。",
    "d2": "预训练数据的混合配比被称为配方学。常见做法是按来源设定权重并用温度采样平滑分布，DoReMi 则通过代理模型自动优化配比。数据重复次数也需控制，Muennighoff 2023 指出同一数据超过 4 个 epoch 收益递减。",
    "d3": "MinHash 通过 shingling 把文档变成集合，再用最小哈希签名估计 Jaccard 相似度，配合 LSH 分桶实现近似去重。band 参数决定阈值 s_star 约等于 (1/b) 的 1/r 次方，工程上先精确去重再模糊去重是标准顺序。",
    "d4": "数据污染指评测题混入预训练语料。GPT-3 用 13-gram 重叠检测：评测题的 n-gram 若有 80% 以上出现在某文档中即判污染。释义改写属于更隐蔽的污染层级，n-gram 方法抓不住它。",
    "d5": "模型崩塌指用模型生成数据反复训练下一代模型后分布退化，表现为均值回归和尾部丢失。防崩塌的三件套是保留真实数据锚点、对合成数据做质量加权、持续监控尾部指标。",
    "d6": "Chinchilla scaling law 用 IsoFLOP 方法证明：固定算力下模型参数与数据量应按 N_opt 与 C 的 0.46 次方、D_opt 与 C 的 0.54 次方配比，经验法则是数据量约为参数量的 20 倍。70B 参数配 1.4T token 的 Chinchilla 击败了 280B 参数的 Gopher。",
    "d7": "DPO 把 RLHF 的奖励建模与策略优化合二为一，损失函数为负期望 log sigmoid(beta 乘 margin)，其中 margin 是偏好对在当前策略与参考策略下的对数概率差。超参数 beta 控制偏离参考模型的 KL 约束强度，典型取值 0.01 到 0.5。",
    "d8": "混合检索把 BM25 的关键词匹配与稠密检索的语义匹配用 RRF 融合，再经 cross-encoder 重排形成漏斗。生成端要注意 Lost in the Middle：关键证据放在上下文中间容易被模型忽略，应把最相关的片段放在首尾。",
}

queries = {
    "q1": "去重时如何估计两个文档的相似度",
    "q2": "评测题泄露进训练数据怎么发现",
    "q3": "模型参数量和训练数据量如何配比",
}
EXPECTED = {"q1": "d3", "q2": "d4", "q3": "d6"}

# ---- BM25：课程公式原样实现 ----
K1, B = 1.2, 0.75


class BM25:
    def __init__(self, tokenizer):
        self.tok = tokenizer
        self.terms = {did: tokenizer(t) for did, t in corpus.items()}
        self.dl = {did: len(ts) for did, ts in self.terms.items()}
        self.N = len(self.terms)
        self.avgdl = sum(self.dl.values()) / self.N
        self.df = Counter()
        for ts in self.terms.values():
            self.df.update(set(ts))

    def idf(self, term):
        return math.log(1 + (self.N - self.df.get(term, 0) + 0.5) / (self.df.get(term, 0) + 0.5))

    def score(self, query):
        qterms = self.tok(query)
        out = {}
        for did, ts in self.terms.items():
            tf = Counter(ts)
            s = 0.0
            for t in set(qterms):
                f = tf.get(t, 0)
                if f == 0:
                    continue
                s += self.idf(t) * f * (K1 + 1) / (f + K1 * (1 - B + B * self.dl[did] / self.avgdl))
            out[did] = s
        return out


retriever_a = BM25(tok_bigram)   # A 路：细粒度（字符 bigram）
retriever_b = BM25(tok_unigram)  # B 路：粗粒度（单字）

# ---- RRF 融合：score = Σ 1/(k + rank) ----
RRF_K = 60


def rrf(ranked_lists):
    fused = Counter()
    for ranked in ranked_lists:
        for rank, did in enumerate(ranked, start=1):
            fused[did] += 1.0 / (RRF_K + rank)
    return fused


def topn(scores, n=3):
    return sorted(scores, key=scores.get, reverse=True)[:n]


print("=" * 64)
all_ok = True
for qid, qtext in queries.items():
    sa, sb = retriever_a.score(qtext), retriever_b.score(qtext)
    ra, rb = topn(sa), topn(sb)
    rf = topn(rrf([ra, rb]))
    ok = rf[0] == EXPECTED[qid]
    all_ok &= ok
    print(f"{qid}「{qtext}」")
    print(f"  A路 bigram top3: {' '.join(ra)}")
    print(f"  B路 单字   top3: {' '.join(rb)}")
    print(f"  RRF 融合 top3: {' '.join(rf)}   {'✅' if ok else '❌'} 期望 {EXPECTED[qid]}")
print("=" * 64)
print("融合 top1 全部符合预期 ✅" if all_ok else "有查询未命中预期，请检查语料 ❌")
