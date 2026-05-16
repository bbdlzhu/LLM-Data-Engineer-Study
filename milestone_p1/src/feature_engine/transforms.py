"""特征计算模块。

这是流水线的核心——将原始事件和用户画像转换为一维特征向量。
对应 Spark 中的 groupBy、agg、窗口函数（window function）和 StringIndexer。

本模块展示的生产级 Python 实践：
  - 生成器函数（generator）用于内存高效的数据流式处理
  - assert isinstance 作为 mypy 类型守卫（type guard）
  - 在数据边界进行显式错误处理
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Iterator

from feature_engine.types import (
    FeatureVector,
    RawEvent,
    UserProfile,
    WindowedFeature,
)


def compute_windowed_features(
    events: list[RawEvent],
    user_ids: list[str],
    reference_date: str,
    *,
    short_window_days: int = 7,
    long_window_days: int = 30,
) -> dict[str, WindowedFeature]:
    """为每个用户计算滚动时间窗口的聚合特征。

    这是替代 Spark 中以下写法的纯 Python 实现：
      df.groupBy("user_id")
        .agg(
            sum(when(col("event_type")=="click", 1)
                .when(col("timestamp")>=window_start, 1)
                .otherwise(0)).alias("click_count_7d"),
            ...
        )

    关键区别：
      Spark 版本是声明式的——你描述"要什么结果"。
      纯 Python 版本是命令式的——你描述"怎么做"。
      但因为有 TypedDict + mypy strict，编译器在开发期就能捕获 schema
      不匹配的错误，而不像 Spark 要等到运行时。

    Args:
        events: 窗口期内的所有原始事件。
        user_ids: 需要计算特征的用户列表。
        reference_date: 参考日期（ISO 8601 格式），窗口以此为基准向前推算。
        short_window_days: 短窗口天数，默认 7 天。
        long_window_days: 长窗口天数，默认 30 天。

    Returns:
        user_id -> WindowedFeature 的映射字典。
    """
    ref_date = datetime.fromisoformat(reference_date)
    short_start = ref_date - timedelta(days=short_window_days)
    long_start = ref_date - timedelta(days=long_window_days)

    # 为每个用户初始化累加器
    # 使用 dict 而非 defaultdict，是因为我们需要显式声明初始值类型。
    # 这对应 Spark groupBy + agg 的初始化阶段。
    # 注意：distinct_items 用 set 来去重，最后再转成 count。
    accumulators: dict[str, dict[str, float | int | set[str]]] = {
        uid: {
            "click_count_7d": 0,
            "click_count_30d": 0,
            "purchase_count_7d": 0,
            "purchase_count_30d": 0,
            "total_spend_7d": 0.0,
            "total_spend_30d": 0.0,
            "distinct_items_7d": set(),
            "distinct_items_30d": set(),
        }
        for uid in user_ids
    }

    user_id_set = frozenset(user_ids)

    for event in events:
        uid = event["user_id"]
        if uid not in user_id_set:
            continue

        ts = datetime.fromisoformat(event["timestamp"])
        acc = accumulators[uid]

        in_short = ts >= short_start
        in_long = ts >= long_start

        if event["event_type"] == "click":
            if in_short:
                # 类型守卫：mypy 需要通过 assert isinstance 来窄化 union 类型
                c7 = acc["click_count_7d"]
                assert isinstance(c7, int)
                acc["click_count_7d"] = c7 + 1
            if in_long:
                c30 = acc["click_count_30d"]
                assert isinstance(c30, int)
                acc["click_count_30d"] = c30 + 1

        elif event["event_type"] == "purchase":
            if in_short:
                p7 = acc["purchase_count_7d"]
                s7 = acc["total_spend_7d"]
                assert isinstance(p7, int)
                assert isinstance(s7, float)
                acc["purchase_count_7d"] = p7 + 1
                acc["total_spend_7d"] = s7 + event["value"]
            if in_long:
                p30 = acc["purchase_count_30d"]
                s30 = acc["total_spend_30d"]
                assert isinstance(p30, int)
                assert isinstance(s30, float)
                acc["purchase_count_30d"] = p30 + 1
                acc["total_spend_30d"] = s30 + event["value"]

            # 追踪去重商品：用 set 记录，最后转换成数量
            if in_short:
                di7 = acc["distinct_items_7d"]
                assert isinstance(di7, set)
                di7.add(event["item_id"])
            if in_long:
                di30 = acc["distinct_items_30d"]
                assert isinstance(di30, set)
                di30.add(event["item_id"])

    # 组装输出：将 set 转为长度计数
    result: dict[str, WindowedFeature] = {}
    for uid, acc in accumulators.items():
        # 先提取到带类型守卫的局部变量，mypy 才能正确窄化类型
        c7 = acc["click_count_7d"]
        c30 = acc["click_count_30d"]
        p7 = acc["purchase_count_7d"]
        p30 = acc["purchase_count_30d"]
        s7 = acc["total_spend_7d"]
        s30 = acc["total_spend_30d"]
        di7 = acc["distinct_items_7d"]
        di30 = acc["distinct_items_30d"]
        assert isinstance(c7, int)
        assert isinstance(c30, int)
        assert isinstance(p7, int)
        assert isinstance(p30, int)
        assert isinstance(s7, float)
        assert isinstance(s30, float)
        assert isinstance(di7, set)
        assert isinstance(di30, set)

        result[uid] = WindowedFeature(
            user_id=uid,
            reference_date=reference_date,
            click_count_7d=c7,
            click_count_30d=c30,
            purchase_count_7d=p7,
            purchase_count_30d=p30,
            total_spend_7d=s7,
            total_spend_30d=s30,
            distinct_items_7d=len(di7),
            distinct_items_30d=len(di30),
        )

    return result


def stream_events_in_batches(
    events: list[RawEvent],
    batch_size: int = 10000,
) -> Iterator[list[RawEvent]]:
    """将事件列表按固定批次大小流式输出。

    生成器函数（generator）——每次 yield 后控制权交还给调用方。
    在 Spark 中这由执行引擎自动处理；在纯 Python 中需要显式管理内存。

    使用场景：当事件量超出内存时，从磁盘/S3 分批读取并处理。
    这个生成器模式是 Python 中实现背压感知（backpressure-aware）
    流水线的惯用方式。

    类比：就像 Spark 中每个 partition 逐个处理，但由你手动控制粒度。

    Args:
        events: 全量事件列表。
        batch_size: 每批的大小，默认 10000。

    Yields:
        大小为 batch_size 的事件批次（最后一批可能不足）。
    """
    for i in range(0, len(events), batch_size):
        yield events[i : i + batch_size]


def encode_categorical(
    value: str,
    mapping: dict[str, int],
    *,
    default: int = -1,
) -> int:
    """将类别字符串编码为整数。

    等价于 Spark 的 StringIndexer + 后续 one-hot 编码的准备工作。
    未见过（unknown）的类别返回 default（默认 -1）——
    在生产环境中，此时应该记录一条 warning 日志，
    并可能将数据路由到死信队列（dead-letter queue）做人工审查。

    Args:
        value: 原始类别字符串。
        mapping: 类别字符串到整数的映射表。
        default: 未匹配时的默认值。

    Returns:
        编码后的整数值。

    Raises:
        ValueError: 当 mapping 为空字典时抛出。
    """
    if not mapping:
        raise ValueError("编码映射表不能为空")
    return mapping.get(value, default)


# 预定义的编码映射 —— 生产环境中这些值应从配置文件
# 或训练好的 encoder artifact 中加载，而非硬编码。
AGE_GROUP_ENCODING: dict[str, int] = {
    "18-24": 0,
    "25-34": 1,
    "35-44": 2,
    "45+": 3,
}

CITY_TIER_ENCODING: dict[str, int] = {
    "T1": 0,
    "T2": 1,
    "T3": 2,
}


def build_feature_vector(
    windowed: WindowedFeature,
    profile: UserProfile,
    *,
    label_lookahead_events: list[RawEvent] | None = None,
) -> FeatureVector:
    """组装最终特征向量：窗口聚合 + 用户画像 → 一条 FeatureVector。

    组装过程包含：
      1. 原始窗口聚合特征（来自 compute_windowed_features）
      2. 衍生特征：7天/30天增长率
      3. 编码后的类别特征（年龄组、城市等级）
      4. 标签：未来7天是否有购买（来自 lookahead 窗口）

    Args:
        windowed: 已计算好的窗口聚合特征。
        profile: 用户画像数据。
        label_lookahead_events: 参考日期后 7 天内的未来事件，
            用于计算监督学习标签。None 表示无标签（如预测阶段）。

    Returns:
        完整的 FeatureVector，可直接供模型消费。
    """
    # 衍生特征：增长率。分母为 0 时返回 0.0，避免 inf。
    click_growth = _safe_ratio(windowed["click_count_7d"], windowed["click_count_30d"])
    spend_growth = _safe_ratio(windowed["total_spend_7d"], windowed["total_spend_30d"])

    # 标签：lookahead 窗口内是否存在购买事件？
    label = 0
    if label_lookahead_events:
        label = 1 if any(e["event_type"] == "purchase" for e in label_lookahead_events) else 0

    return FeatureVector(
        user_id=windowed["user_id"],
        reference_date=windowed["reference_date"],
        click_count_7d=windowed["click_count_7d"],
        click_count_30d=windowed["click_count_30d"],
        purchase_count_7d=windowed["purchase_count_7d"],
        purchase_count_30d=windowed["purchase_count_30d"],
        total_spend_7d=windowed["total_spend_7d"],
        total_spend_30d=windowed["total_spend_30d"],
        distinct_items_7d=windowed["distinct_items_7d"],
        distinct_items_30d=windowed["distinct_items_30d"],
        click_growth_7d_to_30d=click_growth,
        spend_growth_7d_to_30d=spend_growth,
        age_group_encoded=encode_categorical(profile["age_group"], AGE_GROUP_ENCODING),
        city_tier_encoded=encode_categorical(profile["city_tier"], CITY_TIER_ENCODING),
        label=label,
    )


def _safe_ratio(numerator: int | float, denominator: int | float) -> float:
    """安全除法：分子/分母，分母为 0 时返回 0.0 而非抛出异常。"""
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)
