"""
ARA - Business Endpoints
"""
import time
import uuid
import logging
from fastapi import APIRouter
from src.models.schemas import ChatRequest, ChatResponse
from src.engine.intent import detect_intent
from src.engine.depth import determine_depth, get_depth_config
from src.engine.reality import build_system_prompt, build_response_prompt
from src.services.ai_client import call_deepseek

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory conversation store (simple MVP)
conversations = {}
metrics = {"total_requests": 0, "response_times": []}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - the core of ARA."""
    start_time = time.time()
    metrics["total_requests"] += 1

    # Get or create conversation
    conv_id = request.conversation_id or str(uuid.uuid4())
    if conv_id not in conversations:
        conversations[conv_id] = {
            "history": [],
            "current_depth": "Level1",
        }

    conv = conversations[conv_id]

    # Step 1: Intent Detection
    intent_result = detect_intent(request.message)

    # Step 2: Adaptive Depth Engine
    depth_result = determine_depth(
        message=request.message,
        intent_confidence=intent_result.confidence,
        current_depth=conv["current_depth"],
    )

    # Update conversation depth
    conv["current_depth"] = depth_result.depth.value

    # Step 3: Reality Modeling Engine
    system_prompt = build_system_prompt(
        depth=depth_result.depth,
        intent=intent_result.intent,
        topic=request.message,
    )
    ai_messages = build_response_prompt(
        message=request.message,
        history=conv["history"],
        depth=depth_result.depth,
    )

    # Step 4: Call AI
    # Adjust max_tokens based on depth to avoid timeout on long responses
    max_tokens_map = {
        "Level0": 1024,
        "Level1": 2048,
        "Level2": 4096,
        "Level3": 4096,
    }
    max_tokens = max_tokens_map.get(depth_result.depth.value, 2048)

    try:
        response_content = await call_deepseek(
            system_prompt=system_prompt,
            messages=ai_messages,
            max_tokens=max_tokens,
        )
    except ValueError as e:
        # API Key error
        logger.error(f"API Key error: {e}")
        return ChatResponse(
            code=1001,
            data={"error": str(e)},
            message="API Key 配置错误",
        )
    except ConnectionError as e:
        # API call failed after retries
        logger.error(f"API call failed: {e}")
        return ChatResponse(
            code=1002,
            data={"error": str(e)},
            message="AI 服务暂时不可用，请稍后重试",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return ChatResponse(
            code=1003,
            data={"error": str(e)},
            message="内部错误",
        )

    # Update history
    conv["history"].append(
        {"role": "user", "content": request.message}
    )
    conv["history"].append(
        {"role": "assistant", "content": response_content}
    )

    # Track metrics
    elapsed = time.time() - start_time
    metrics["response_times"].append(elapsed)

    # Clean up old conversations (keep last 100)
    if len(conversations) > 100:
        oldest_key = next(iter(conversations))
        del conversations[oldest_key]

    depth_config = get_depth_config(depth_result.depth)

    return ChatResponse(
        code=0,
        data={
            "conversation_id": conv_id,
            "response": response_content,
            "intent": intent_result.intent.value,
            "intent_confidence": intent_result.confidence,
            "depth": depth_result.depth.value,
            "depth_reason": depth_result.reason,
            "word_range": depth_config["word_range"],
            "layers_used": depth_config["layers"],
        },
        message="ok",
    )


@router.post("/analyze")
async def analyze(request: ChatRequest):
    """Analyze endpoint - returns intent and depth without calling AI."""
    intent_result = detect_intent(request.message)
    depth_result = determine_depth(
        message=request.message,
        intent_confidence=intent_result.confidence,
    )
    depth_config = get_depth_config(depth_result.depth)

    return ChatResponse(
        code=0,
        data={
            "intent": intent_result.intent.value,
            "intent_confidence": intent_result.confidence,
            "depth": depth_result.depth.value,
            "depth_reason": depth_result.reason,
            "word_range": depth_config["word_range"],
            "layers_used": depth_config["layers"],
        },
        message="ok",
    )
