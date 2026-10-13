#!/usr/bin/env python3
"""实验1：用 n-gram 重叠检测预训练语料中的测试集污染"""


def char_ngrams(text, n=13):
    text = "".join(text.split())  # 去掉空白，字符级切分
    if len(text) < n:
        return set()
    return {text[i:i + n] for i in range(len(text) - n + 1)}


# ---- 小数据集：6 篇"预训练文档"（模拟爬来的网页文本）----
corpus = {
    "doc1": "中国的首都是北京。北京是中国的政治中心，拥有天安门、故宫等著名景点，每年吸引大量游客。",
    "doc2": "光合作用是植物将光能转化为化学能的过程。叶绿体是光合作用的主要场所，反应式为6CO2+6H2O→C6H12O6+6O2。",
    "doc3": "牛顿第二定律指出，物体的加速度与作用在它上面的合外力成正比，与物体的质量成反比，公式为F=ma。",
    "doc4": "下列关于光合作用的说法正确的是？A.只在白天进行 B.叶绿体是光合作用的主要场所 C.不需要光 D.只在根部进行。本题考查光合作用的场所，正确答案是B。解析：叶绿体含有叶绿素，是光合作用的主要场所。",
    "doc5": "植物通过一系列复杂的生化反应把太阳光转化为自身养分，这一过程主要发生在一种名为叶绿体的细胞器中。",
    "doc6": "量子计算利用量子比特进行运算。与经典比特只能取0或1不同，量子比特可以处于叠加态，这使得量子计算机在特定问题上具有指数级加速潜力。",
}

# ---- 评测集：3 道题（模拟要保密的 benchmark）----
benchmark = {
    "q1": "下列关于光合作用的说法正确的是？A.只在白天进行 B.叶绿体是光合作用的主要场所 C.不需要光 D.只在根部进行。",
    "q2": "牛顿第二定律的数学表达式是什么？",
    "q3": "量子比特与经典比特的根本区别是什么？",
}


def contamination_ratio(bench_text, doc_text, n=13):
    """评测题的 n-gram 有多大比例出现在某篇文档里。"""
    b, d = char_ngrams(bench_text, n), char_ngrams(doc_text, n)
    if not b:
        return 0.0
    return len(b & d) / len(b)


THRESHOLD = 0.8  # GPT-3 论文式阈值：重叠超 80% 判为污染
print(f"{'评测题':<6}{'最可疑文档':<10}{'重叠率':<8}结论")
print("-" * 42)
contaminated = 0
for qid, qtext in benchmark.items():
    best_doc, best_r = max(
        ((did, contamination_ratio(qtext, dtext)) for did, dtext in corpus.items()),
        key=lambda x: x[1],
    )
    hit = best_r >= THRESHOLD
    contaminated += hit
    print(f"{qid:<8}{best_doc:<10}{best_r:<8.0%}{'⚠️ 污染' if hit else '干净'}")
print("-" * 42)
print(f"污染率：{contaminated}/{len(benchmark)}")
