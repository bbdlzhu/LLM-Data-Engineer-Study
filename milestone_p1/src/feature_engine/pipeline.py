"""流水线编排模块。

协调各阶段：拉取事件 → 计算窗口特征 → 关联画像 → 输出特征向量。

在 Spark 中，这是你的 driver 程序，负责把多个 DataFrame 转换串起来。
在生产级 Python 中，我们用显式的构造函数依赖注入来实现可测试性。

架构决策记录（ADR-001）：
  通过构造函数注入 EventSource 和 ProfileSource，而非在模块内直接
  import 具体实现。这让流水线可以不依赖真实数据库进行测试——
  只需传入符合 Protocol 的 mock 对象即可。

对比：如果你在 Spark 中测试特征工程，通常需要启动一个
local SparkSession 或测试集群。而 Protocol 注入让我们的
流水线测试在毫秒级完成，零外部依赖。
"""

from datetime import datetime, timedelta

from feature_engine.types import (
    EventSource,
    FeatureVector,
    ProfileSource,
)
from feature_engine.transforms import build_feature_vector, compute_windowed_features


class FeaturePipeline:
    """特征工程流水线编排器。

    通过构造函数注入数据源，遵循依赖倒置原则（Dependency Inversion Principle）：
    高层策略（流水线的处理逻辑）不依赖于低层细节（数据库连接、文件格式）。

    用法：
        pipeline = FeaturePipeline(event_source, profile_source)
        features = pipeline.run(reference_date="2024-01-15")
    """

    def __init__(self, event_source: EventSource, profile_source: ProfileSource) -> None:
        self._events = event_source
        self._profiles = profile_source

    def run(self, reference_date: str) -> list[FeatureVector]:
        """执行完整的特征工程流水线。

        流水线各阶段：
          1. 拉取 30 天回看窗口 + 7 天前瞻窗口内的所有事件
          2. 确定活跃用户集合（回看窗口内有事件的用户）
          3. 计算窗口聚合特征（7天、30天）
          4. 批量拉取用户画像
          5. 画像与窗口特征关联（类似 SQL JOIN）
          6. 组装最终特征向量（含标签）

        Args:
            reference_date: 参考日期（ISO 8601 格式）。所有特征以该日期为基准，
                使用历史窗口计算特征，使用未来窗口计算标签。

        Returns:
            每个活跃用户一条 FeatureVector，按 user_id 排序。
        """
        ref_dt = datetime.fromisoformat(reference_date)

        # 回看窗口：参考日期前 30 天
        lookback_start = (ref_dt - timedelta(days=30)).isoformat()
        # 前瞻窗口：参考日期后 7 天（仅用于计算标签）
        lookahead_end = (ref_dt + timedelta(days=7)).isoformat()

        # 第 1 步：拉取原始事件（回看 + 前瞻）
        all_events = self._events.fetch_events(lookback_start, lookahead_end)

        # 第 2 步：确定活跃用户集合
        active_user_ids = self._events.fetch_distinct_user_ids(
            lookback_start, reference_date
        )

        if not active_user_ids:
            return []

        # 第 3 步：划分回看事件（特征）和前瞻事件（标签）
        lookback_events = [
            e for e in all_events if e["timestamp"] < reference_date
        ]
        lookahead_events = [
            e for e in all_events if e["timestamp"] >= reference_date
        ]

        # 计算窗口聚合
        windowed = compute_windowed_features(
            lookback_events, active_user_ids, reference_date
        )

        # 第 4 步：批量拉取用户画像
        profiles = self._profiles.fetch_profiles(active_user_ids)
        # 构建 user_id -> profile 的索引，类似 Spark 的 broadcast hash join
        profile_map = {p["user_id"]: p for p in profiles}

        # 第 5、6 步：关联画像 + 组装特征向量
        result: list[FeatureVector] = []
        for uid in sorted(active_user_ids):
            wf = windowed.get(uid)
            pf = profile_map.get(uid)

            if wf is None:
                # 理论不应发生：活跃用户在窗口聚合中应有结果
                continue
            if pf is None:
                # 数据质量问题：有事件但缺画像，应记录日志
                continue

            # 只取该用户的前瞻事件，用于计算标签
            user_lookahead = [e for e in lookahead_events if e["user_id"] == uid]
            fv = build_feature_vector(wf, pf, label_lookahead_events=user_lookahead)
            result.append(fv)

        return result
