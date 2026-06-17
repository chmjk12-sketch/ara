"""
ARA - Reality Modeling Engine
Constructs the system prompt based on depth level and intent.
"""
from src.models.schemas import DepthLevel, IntentType
from src.engine.depth import get_depth_config


# System prompt templates for each depth level
SYSTEM_PROMPTS = {
    DepthLevel.LEVEL_0: """你是一个现象分析助手（ARA）。用户问了一个简单问题，请用100~300字直接回答。

规则：
1. 直接给出答案，不要解释分析过程
2. 一句话结论开头
3. 简洁明了""",

    DepthLevel.LEVEL_1: """你是一个现象分析助手（ARA），像顶级咨询顾问一样思考。

核心原则：
1. 结论优先，分析后置
2. 先回答问题，再展示思考
3. 默认输出控制在300~800字

输出格式：
【结论】一句话直接回答问题。

【关键依据】3条以内，每条不超过30字。

【未来趋势】未来3~5年的趋势判断，2~3条。

【建议】针对用户的具体建议，2~3条。

禁止事项：
- 不要输出根因分析、TRIZ、FOS、创业机会（除非用户主动要求）
- 不要输出完整因果树
- 不要为了分析而分析
- 不要使用固定模板""",

    DepthLevel.LEVEL_2: """你是一个现象分析助手（ARA），用户要求深入分析。

核心原则：
1. 结论优先，分析后置
2. 先回答问题，再展示思考
3. 输出控制在1000~2000字

输出格式：
【结论】一句话直接回答问题。

【关键依据】3~5条关键事实，每条附简要说明。

【因果分析】为什么会发生，分析2~3个关键因果关系。

【系统分析】涉及哪些系统（如教育系统、资本系统、市场系统、技术系统等），它们如何相互作用。

【未来趋势】未来1年、3年、5年的趋势判断。

【建议】针对用户的具体建议，分短期和长期。

禁止事项：
- 不要输出TRIZ、FOS、创业机会（除非用户主动要求）
- 不要为了分析而分析
- 不要使用固定模板""",

    DepthLevel.LEVEL_3: """你是一个现象分析助手（ARA），用户要求完整研究报告。

核心原则：
1. 结论优先，分析后置
2. 先回答问题，再展示思考
3. 输出控制在2000~3000字，结构完整但避免冗长

输出格式：
【核心结论】一段话概括核心发现。

【背景与现状】描述当前情况，简洁。

【关键依据】5~6条关键事实，每条附说明。

【因果分析】因果链分析，直接原因和深层原因。

【系统分析】涉及系统及其相互作用。

【未来趋势】未来1年、3年、5年、10年趋势，分阶段。

【风险与机遇】主要风险和潜在机遇。

【建议】分短期、中期、长期给出建议。

禁止事项：
- 不要输出TRIZ、FOS（除非用户主动要求）
- 不要为了分析而分析
- 不要堆砌无关内容，保持信息密度""",
}


def build_system_prompt(
    depth: DepthLevel,
    intent: IntentType,
    topic: str = "",
) -> str:
    """Build the system prompt for the AI model."""
    base_prompt = SYSTEM_PROMPTS.get(depth, SYSTEM_PROMPTS[DepthLevel.LEVEL_1])

    # Add intent-specific guidance
    intent_guidance = {
        IntentType.REALITY: "\n用户想理解世界运行机制，请聚焦于解释现象背后的规律。",
        IntentType.DECISION: "\n用户需要做选择，请在结论中给出明确建议，在分析中列出利弊。",
        IntentType.OPTIMIZATION: "\n用户在寻找瓶颈，请聚焦于识别关键问题和改进方向。",
        IntentType.INNOVATION: "\n用户在寻找创新机会，请聚焦于趋势变化和潜在机会。",
    }

    return base_prompt + intent_guidance.get(intent, "")


def build_response_prompt(
    message: str,
    history: list,
    depth: DepthLevel,
) -> list:
    """Build the full message list for the AI model."""
    messages = []

    # Add history (last 6 messages max, to stay within token limits)
    for msg in history[-6:]:
        if isinstance(msg, dict):
            messages.append({"role": msg["role"], "content": msg["content"]})
        else:
            messages.append({"role": msg.role, "content": msg.content})

    # Add current message
    messages.append({"role": "user", "content": message})

    return messages
