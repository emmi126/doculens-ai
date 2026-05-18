"""
OCR Agent for Multi-Agent Note Processing System

Responsibilities:
1. Call OCR API to extract text from images
2. Use LLM to post-process and correct OCR errors
3. Identify special content (formulas, diagrams, code blocks, tables)

Input: image_bytes
Output: ocr_raw_text, ocr_corrected_text, ocr_confidence, special_contents
"""

import time
import logging
import json
import re
from typing import List

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from .state import NoteProcessingState, AgentOutput, SpecialContent, ProcessingStatus
from services.ocr_service import ocr_service
from config import settings

logger = logging.getLogger(__name__)


# LLM for post-processing OCR results
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=settings.anthropic_api_key,
    temperature=0.2,  # Low temperature for accurate correction
    max_tokens=4096
)


OCR_CORRECTION_PROMPT = """你是一个专业的 OCR 后处理专家。你的任务是分析 OCR 识别的文本，进行纠错和内容识别。

**任务 1：OCR 纠错**
修正常见的 OCR 识别错误：
- 字符混淆（如 0/O, 1/l/I, rn/m）
- 拼写错误
- 标点符号错误
- 断行错误（不该断行的地方断了）
- 格式错误

**任务 2：特殊内容识别**
识别文本中的特殊内容类型：
1. **数学公式**：包含数学符号、方程式、希腊字母等
2. **代码块**：编程代码、伪代码
3. **表格**：结构化数据，对齐的列
4. **图表引用**：提到"图"、"表"、"Figure"等

**输出格式（JSON）**：
```json
{
    "corrected_text": "纠错后的完整文本",
    "special_contents": [
        {
            "type": "formula|code|table|diagram_ref",
            "raw_text": "原始OCR文本片段",
            "processed_text": "处理后的文本（如LaTeX格式的公式）",
            "position": 起始字符位置,
            "confidence": 0.0-1.0
        }
    ],
    "corrections_made": [
        {"original": "错误文本", "corrected": "正确文本", "reason": "原因"}
    ]
}
```

只输出 JSON，不要其他解释。"""


def extract_special_content(text: str) -> List[SpecialContent]:
    """
    Rule-based extraction of special content as fallback.
    Used when LLM extraction fails or for validation.
    """
    special_contents = []

    # Pattern for mathematical formulas (basic detection)
    math_patterns = [
        r'\$[^$]+\$',  # LaTeX inline math
        r'\$\$[^$]+\$\$',  # LaTeX display math
        r'[∑∫∂∇∆√±×÷≤≥≠≈∞∈∉⊂⊃∪∩α-ωΑ-Ω]',  # Math symbols
        r'(?:sin|cos|tan|log|ln|exp|lim|max|min)\s*[\(\[]',  # Functions
    ]

    for pattern in math_patterns:
        for match in re.finditer(pattern, text):
            special_contents.append(SpecialContent(
                content_type="formula",
                raw_text=match.group(),
                processed_text=match.group(),
                position=match.start(),
                confidence=0.8
            ))

    # Pattern for code blocks
    code_patterns = [
        r'```[\s\S]*?```',  # Markdown code blocks
        r'`[^`]+`',  # Inline code
        r'(?:def|class|function|import|from|return|if|else|for|while)\s+\w+',  # Keywords
    ]

    for pattern in code_patterns:
        for match in re.finditer(pattern, text):
            special_contents.append(SpecialContent(
                content_type="code",
                raw_text=match.group(),
                processed_text=match.group(),
                position=match.start(),
                confidence=0.7
            ))

    # Pattern for table structures (aligned columns with | or tabs)
    table_pattern = r'(?:\|[^|\n]+)+\|'
    for match in re.finditer(table_pattern, text):
        special_contents.append(SpecialContent(
            content_type="table",
            raw_text=match.group(),
            processed_text=match.group(),
            position=match.start(),
            confidence=0.6
        ))

    return special_contents


def parse_llm_response(response_text: str, raw_ocr_text: str) -> tuple:
    """
    Parse the LLM response for OCR correction.

    Returns:
        tuple: (corrected_text, special_contents)
    """
    try:
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to parse the entire response as JSON
            json_str = response_text.strip()

        data = json.loads(json_str)

        corrected_text = data.get("corrected_text", raw_ocr_text)

        special_contents = []
        for item in data.get("special_contents", []):
            special_contents.append(SpecialContent(
                content_type=item.get("type", "unknown"),
                raw_text=item.get("raw_text", ""),
                processed_text=item.get("processed_text", ""),
                position=item.get("position", 0),
                confidence=item.get("confidence", 0.5)
            ))

        return corrected_text, special_contents

    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to parse LLM response as JSON: {e}")
        # Fallback: use raw text and rule-based extraction
        return raw_ocr_text, extract_special_content(raw_ocr_text)


async def ocr_agent(state: NoteProcessingState) -> NoteProcessingState:
    """
    OCR Agent: Extracts and processes text from images.

    This agent:
    1. Calls Google Cloud Vision OCR API
    2. Uses LLM to correct OCR errors
    3. Identifies special content (formulas, code, tables)

    Args:
        state: Current processing state with image_bytes

    Returns:
        Updated state with OCR results
    """
    start_time = time.time()
    agent_name = "ocr_agent"

    logger.info(f"[{agent_name}] Starting OCR processing...")

    state["current_agent"] = agent_name
    state["status"] = ProcessingStatus.PROCESSING

    try:
        # Step 1: Extract text using OCR service
        image_bytes = state.get("image_bytes")
        if not image_bytes:
            raise ValueError("No image data provided")

        ocr_text, confidence = ocr_service.extract_text(image_bytes)

        if not ocr_text or len(ocr_text.strip()) == 0:
            raise ValueError("OCR failed to extract any text from the image")

        state["ocr_raw_text"] = ocr_text
        state["ocr_confidence"] = confidence

        logger.info(f"[{agent_name}] OCR extracted {len(ocr_text)} characters with {confidence:.2f} confidence")

        # Step 2: Use LLM for post-processing
        try:
            messages = [
                SystemMessage(content=OCR_CORRECTION_PROMPT),
                HumanMessage(content=f"请处理以下 OCR 识别结果：\n\n```\n{ocr_text}\n```")
            ]

            response = await llm.ainvoke(messages)
            response_text = response.content

            corrected_text, special_contents = parse_llm_response(response_text, ocr_text)

            state["ocr_corrected_text"] = corrected_text
            state["special_contents"] = special_contents

            logger.info(f"[{agent_name}] LLM correction completed. Found {len(special_contents)} special contents.")

        except Exception as llm_error:
            logger.warning(f"[{agent_name}] LLM post-processing failed: {llm_error}. Using raw OCR text.")
            state["ocr_corrected_text"] = ocr_text
            state["special_contents"] = extract_special_content(ocr_text)

        # Record success
        processing_time = time.time() - start_time
        state["processing_times"][agent_name] = processing_time
        state["ocr_agent_output"] = AgentOutput(
            success=True,
            data={
                "text_length": len(state["ocr_corrected_text"]),
                "confidence": confidence,
                "special_content_count": len(state["special_contents"])
            },
            processing_time=processing_time,
            agent_name=agent_name
        )

        logger.info(f"[{agent_name}] Completed in {processing_time:.2f}s")

    except Exception as e:
        error_msg = f"OCR Agent failed: {str(e)}"
        logger.error(f"[{agent_name}] {error_msg}")

        state["errors"].append(error_msg)
        state["status"] = ProcessingStatus.FAILED
        state["ocr_agent_output"] = AgentOutput(
            success=False,
            data=None,
            error=error_msg,
            processing_time=time.time() - start_time,
            agent_name=agent_name
        )

    return state
