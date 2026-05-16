"""特征工程流水线的类型定义。

在 Spark 中，你用 StructType/StructField 定义 schema。
在生产级 Python 中，我们用 TypedDict 定义行级数据契约，
用 Protocol 定义抽象接口（类似 Java 的 interface）。
"""

from typing import Protocol, TypedDict


class RawEvent(TypedDict):
    """单条用户行为事件。

    对应 Spark DataFrame 的一行，schema 等价于：
      user_id: StringType, event_type: StringType,
      item_id: StringType, timestamp: TimestampType, value: DoubleType
    """

    user_id: str
    event_type: str  # "click", "view", "purchase", "add_to_cart"
    item_id: str
    timestamp: str  # ISO 8601 格式
    value: float  # 购买金额，非购买事件为 0.0


class UserProfile(TypedDict):
    """用户画像/人口统计信息。

    对应星型模型中的维度表（dimension table）。
    """

    user_id: str
    age_group: str  # "18-24", "25-34", "35-44", "45+"
    gender: str
    city_tier: str  # "T1", "T2", "T3" 城市等级
    registered_at: str  # ISO 8601 格式，注册时间


class WindowedFeature(TypedDict):
    """单个用户在某个参考日期上的窗口聚合特征。

    这是 compute_windowed_features 的输出——如果熟悉 Spark，
    这就是 groupBy("user_id").agg(...) 的结果中的一行。
    """

    user_id: str
    reference_date: str
    click_count_7d: int
    click_count_30d: int
    purchase_count_7d: int
    purchase_count_30d: int
    total_spend_7d: float
    total_spend_30d: float
    distinct_items_7d: int
    distinct_items_30d: int


class FeatureVector(TypedDict):
    """最终输出：每个用户在每个参考日期上的一条特征向量。

    这是下游 ML 模型直接消费的数据格式。
    包含原始窗口特征 + 衍生特征 + 编码后的类别特征 + 标签。
    """

    user_id: str
    reference_date: str
    # 原始窗口特征
    click_count_7d: int
    click_count_30d: int
    purchase_count_7d: int
    purchase_count_30d: int
    total_spend_7d: float
    total_spend_30d: float
    distinct_items_7d: int
    distinct_items_30d: int
    # 衍生特征：7天相对30天的增长率
    click_growth_7d_to_30d: float
    spend_growth_7d_to_30d: float
    # 编码后的类别特征
    age_group_encoded: int
    city_tier_encoded: int
    # 标签（监督学习用）：未来7天是否有购买
    label: int


class EventSource(Protocol):
    """原始事件数据的抽象数据源。

    Protocol 是 Python 对 Java interface 的回答。
    使用 Protocol（结构化子类型）而非 ABC（名义子类型）的好处是：
    任何拥有这些方法的对象都满足契约，无需显式继承。
    这让依赖注入和 mock 测试变得极其自然。

    在 Spark 中，你不需要这个抽象——因为数据已经在 HDFS/Hive 里了，
    你直接读就行。但在生产级 Python 中，我们用 Protocol 把"从哪读数据"
    和"怎么处理数据"解耦，这样测试时注入 mock 源，不用连真实数据库。
    """

    def fetch_events(self, start_date: str, end_date: str) -> list[RawEvent]:
        """获取 [start_date, end_date) 区间内的所有事件。"""
        ...

    def fetch_distinct_user_ids(self, start_date: str, end_date: str) -> list[str]:
        """获取在指定日期范围内有过活动的所有 user_id。"""
        ...


class ProfileSource(Protocol):
    """用户画像数据的抽象数据源。"""

    def fetch_profiles(self, user_ids: list[str]) -> list[UserProfile]:
        """批量获取指定 user_id 列表的用户画像。"""
        ...
