"""
ARA - Intent Detection Module
Identifies the type of user question.
"""
from src.models.schemas import IntentType, IntentResult


# Keywords mapping for intent classification
INTENT_KEYWORDS = {
    IntentType.REALITY: [
        "为什么", "原因", "怎么回事", "为什么是", "为何", "如何理解",
        "what is", "why", "how does", "reason", "cause", "explain",
        "是什么", "怎么回事", "真相", "本质",
    ],
    IntentType.DECISION: [
        "值得", "选择", "应该", "要不要", "好不好", "哪个", "是否",
        "should i", "is it worth", "which one", "better to", "choose",
        "值得吗", "该不该", "还是", "比较",
    ],
    IntentType.OPTIMIZATION: [
        "优化", "瓶颈", "停滞", "下降", "问题", "改善", "提升",
        "improve", "optimize", "bottleneck", "stuck", "decline",
        "增长", "效率", "降低", "减少",
    ],
    IntentType.INNOVATION: [
        "创新", "机会", "创业", "新方向", "趋势", "未来", "风口",
        "innovation", "opportunity", "startup", "new trend", "future",
        "蓝海", "突破口", "颠覆",
    ],
}

# Depth escalation keywords
DEPTH_ESCALATION_KEYWORDS = {
    "Level2": [
        "详细分析", "深入分析", "展开讲讲", "展开", "详细说说",
        "为什么", "具体分析", "深入", "详细", "多说点",
        "详细讲", "分析一下", "deep dive", "elaborate", "detail",
        "继续分析", "多说说", "深入讲讲",
    ],
    "Level3": [
        "完整报告", "研究报告", "咨询报告", "白皮书", "全面分析",
        "完整分析", "全面", "系统分析", "深度报告",
        "full report", "research report", "whitepaper", "comprehensive",
        "完整版", "全面分析",
    ],
}


def detect_intent(message: str) -> IntentResult:
    """Detect the intent type of a user message."""
    text = message.lower()
    scores = {}

    for intent_type, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[intent_type] = score

    # Find the best match
    best_intent = max(scores, key=scores.get)
    total_score = sum(scores.values())

    if total_score == 0:
        # Default to Reality if no keywords match
        return IntentResult(intent=IntentType.REALITY, confidence=0.5)

    confidence = round(scores[best_intent] / total_score, 2)
    # Boost confidence if score is dominant
    if scores[best_intent] > 1:
        confidence = min(confidence + 0.2, 0.98)

    return IntentResult(intent=best_intent, confidence=confidence)


def detect_depth_request(message: str, current_depth: str = "Level1") -> str:
    """Detect if user is requesting a deeper analysis."""
    text = message.lower()

    # Check Level 3 keywords first (they take priority)
    for kw in DEPTH_ESCALATION_KEYWORDS["Level3"]:
        if kw in text:
            return "Level3"

    # Check Level 2 keywords
    for kw in DEPTH_ESCALATION_KEYWORDS["Level2"]:
        if kw in text:
            if current_depth in ("Level0", "Level1"):
                return "Level2"
            elif current_depth == "Level2":
                return "Level3"

    return current_depth
