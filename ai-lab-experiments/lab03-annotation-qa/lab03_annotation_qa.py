#!/usr/bin/env python3
"""实验3：标注质量门——Cohen's kappa + 金标准埋点 + 双人仲裁
对齐 10-18《人工标注流水线》课。仅标准库，Mac 直接跑：python3 lab03_annotation_qa.py
"""

# ---- 小数据集：20 条商品评论，两位标注员做二分类情感标注（1=正面，0=负面）----
# idx 4 / 13 / 14 是"难例"：评论本身褒贬混杂，两位标注员给了不同标签
items = [
    ("快递隔天就到了，包装严实无破损。", 1, 1),
    ("客服回复很快，问题一次就解决了。", 1, 1),
    ("这个价位能买到这种质量，值了。", 1, 1),
    ("用了两天就开裂，质量太差了。", 0, 0),
    ("外观还行，但续航比宣传的短不少。", 1, 0),
    ("退货流程折腾了一周，体验糟糕。", 0, 0),
    ("操作简单，老人也能轻松上手。", 1, 1),
    ("噪音大得离谱，晚上根本没法用。", 0, 0),
    ("客服态度敷衍，问三句回一句。", 0, 0),
    ("比实体店便宜两百，功能一模一样。", 1, 1),
    ("充电速度确实快，半小时满血。", 1, 1),
    ("屏幕有坏点，换货还要自己掏运费。", 0, 0),
    ("宣传图和实物差距太大，失望。", 0, 0),
    ("便宜是真便宜，但做工确实粗糙。", 1, 0),
    ("物流慢了三天，不过东西本身不错。", 0, 1),
    ("安装师傅很专业，十分钟搞定。", 1, 1),
    ("用了一个月就充不进电了，垃圾。", 0, 0),
    ("颜值在线，放在桌上很好看。", 1, 1),
    ("差评，根本不是正品。", 0, 0),
    ("味道刺鼻，散了三天还有味。", 0, 0),
]

# ---- 金标准埋点：5 条"卧底题"，标注员不知道哪几条是金标准，混在任务里一起标 ----
GOLD = {1: 1, 6: 1, 13: 0, 14: 1, 18: 0}

# ---- 仲裁：分歧项交给资深标注员（senior）裁定 ----
SENIOR = {4: 0, 13: 0, 14: 1}


def confusion(labels_a, labels_b):
    m = {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 0}
    for a, b in zip(labels_a, labels_b):
        m[(a, b)] += 1
    return m


def kappa(labels_a, labels_b):
    """Cohen's kappa = (p_o - p_e) / (1 - p_e)。"""
    n = len(labels_a)
    m = confusion(labels_a, labels_b)
    p_o = (m[(0, 0)] + m[(1, 1)]) / n                      # 观察一致率
    p_e = sum(                                             # 偶然一致率（边际分布乘积）
        (sum(1 for a in labels_a if a == c) / n)
        * (sum(1 for b in labels_b if b == c) / n)
        for c in (0, 1)
    )
    return (p_o - p_e) / (1 - p_e), p_o, p_e


def kappa_level(k):
    if k < 0.0:
        return "差（不如瞎猜）"
    if k < 0.2:
        return "轻微"
    if k < 0.4:
        return "一般"
    if k < 0.6:
        return "中等"
    if k < 0.8:
        return "高度一致"
    return "几乎完全一致"


la = [a for _, a, _ in items]
lb = [b for _, _, b in items]
m = confusion(la, lb)
k, p_o, p_e = kappa(la, lb)
disagree_idx = [i for i, (_, a, b) in enumerate(items) if a != b]

print("=" * 58)
print("【1】一致率与 Cohen's kappa")
print("      B=0   B=1")
print("  A=0  %-4d  %-4d" % (m[(0, 0)], m[(0, 1)]))
print("  A=1  %-4d  %-4d" % (m[(1, 0)], m[(1, 1)]))
print("观察一致率 p_o = %.0f%%，偶然一致率 p_e = %.0f%%" % (p_o * 100, p_e * 100))
print("kappa = (p_o - p_e)/(1 - p_e) = %.2f（%s）" % (k, kappa_level(k)))

print("=" * 58)
print("【2】金标准埋点：谁在系统性犯错？")
for name, lab in (("标注员A", la), ("标注员B", lb)):
    hit = sum(1 for i, g in GOLD.items() if lab[i] == g)
    print("%s：金标准 %d/%d = %.0f%%" % (name, hit, len(GOLD), hit / len(GOLD) * 100))
    bad = [i for i, g in GOLD.items() if lab[i] != g]
    if bad:
        print("  错的全在分歧项里：%s（'难例'判断有系统性偏差）" % bad)

print("=" * 58)
print("【3】双人仲裁：分歧项交资深标注员裁定")
print("分歧 %d/%d = %.0f%%（< 20%%，仲裁适用；> 20%% 应回炉改指南）"
      % (len(disagree_idx), len(items), len(disagree_idx) / len(items) * 100))
final = []
for i, (_, a, b) in enumerate(items):
    if i in SENIOR:
        final.append(SENIOR[i])
        print("  idx%-2d「%s…」A=%d B=%d → senior=%d" % (i, items[i][0][:14], a, b, SENIOR[i]))
    else:
        final.append(a)  # 一致项直接采用
hit = sum(1 for i, g in GOLD.items() if final[i] == g)
print("仲裁后终版标签的金标准准确率：%d/%d = %.0f%%" % (hit, len(GOLD), hit / len(GOLD) * 100))
print("=" * 58)
