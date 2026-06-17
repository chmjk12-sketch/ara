"""
ARA - Adaptive Depth Engine
Determines output depth based on question complexity and user request.
"""
from src.models.schemas import DepthLevel, DepthResult
from src.engine.intent import detect_depth_request


# Depth configuration
DEPTH_CONFIG = {
    DepthLevel.LEVEL_0: {
        "word_range": "100~300字",
        "layers": ["conclusion"],
        "description": "Quick Answer - 简单问题的快速回答",
    },
    DepthLevel.LEVEL_1: {
        "word_range": "300~800字",
        "layers": ["conclusion", "evidence", "evolution", "action"],
        "description": "Standard Analysis - 默认模式，适用于90%的问题",
    },
    DepthLevel.LEVEL_2: {
        "word_range": "1000~2000字",
        "layers": ["conclusion", "evidence", "causation", "system", "evolution", "action"],
        "description": "Deep Analysis - 用户明确要求深入分析",
    },
    DepthLevel.LEVEL_3: {
        "word_range": "3000字+",
        "layers": ["conclusion", "evidence", "causation", "system", "evolution", "action"],
        "description": "Full Report - 完整研究报告",
    },
}

# Simple question indicators (trigger Level 0)
SIMPLE_INDICATORS = [
    "是什么", "什么是", "是谁", "叫什么", "多少", "几个",
    "what is", "who is", "how many", "definition", "define",
    "意思", "含义", "翻译",
]


def determine_depth(
    message: str,
    intent_confidence: float = 0.5,
    current_depth: str = "Level1",
) -> DepthResult:
    """Determine the appropriate depth level for the response."""
    text = message.lower()

    # Check if user explicitly requests deeper analysis
    escalated = detect_depth_request(message, current_depth)
    if escalated != current_depth:
        depth = DepthLevel(escalated)
        return DepthResult(
            depth=depth,
            reason=f"用户明确要求深入分析（检测到升级关键词）",
        )

    # Check for simple questions → Level 0
    simple_count = sum(1 for ind in SIMPLE_INDICATORS if ind in text)
    if simple_count > 0 and len(message) < 20:
        return DepthResult(
            depth=DepthLevel.LEVEL_0,
            reason="问题简单，适合快速回答",
        )

    # Default to Level 1
    return DepthResult(
        depth=DepthLevel.LEVEL_1,
        reason="用户未要求详细分析，使用默认深度",
    )


def get_depth_config(depth: DepthLevel) -> dict:
    """Get configuration for a specific depth level."""
    return DEPTH_CONFIG.get(depth, DEPTH_CONFIG[DepthLevel.LEVEL_1])
