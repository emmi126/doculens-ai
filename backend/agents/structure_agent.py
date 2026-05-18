"""
Structure Agent for Multi-Agent Note Processing System

Responsibilities:
1. Analyze text structure (paragraphs, sections)
2. Identify heading hierarchy
3. Extract key concepts and terminology
4. Classify document type

Input: ocr_corrected_text
Output: text_blocks, heading_hierarchy, key_concepts, document_type
"""

import time
import logging
import json
import re
from typing import List, Dict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from .state import (
    NoteProcessingState,
    AgentOutput,
    TextBlock,
    KeyConcept,
    ProcessingStatus
)
from config import settings

logger = logging.getLogger(__name__)


llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=settings.anthropic_api_key,
    temperature=0.3,
    max_tokens=4096
)


STRUCTURE_ANALYSIS_PROMPT = """你是一个专业的文档结构分析专家。分析给定的文本，提取其结构信息。

**分析任务**：

1. **文档分块**：将文本分成逻辑块（标题、段落、列表等）
2. **标题层级**：识别文档的标题结构
3. **关键概念**：提取文本中的重要术语和概念
4. **文档类型**：判断文档类型

**文档类型分类**：
- `lecture`: 课堂讲义、教师板书
- `notes`: 学生笔记、手写笔记
- `textbook`: 教科书内容
- `exercise`: 练习题、习题集
- `summary`: 总结、复习材料
- `other`: 其他

**输出格式（JSON）**：
```json
{
    "document_type": "lecture|notes|textbook|exercise|summary|other",
    "text_blocks": [
        {
            "content": "块内容",
            "block_type": "title|heading|paragraph|list|code|quote",
            "level": 0-6,
            "metadata": {"key": "value"}
        }
    ],
    "heading_hierarchy": [
        {
            "text": "标题文本",
            "level": 1-6,
            "position": 0,
            "children": []
        }
    ],
    "key_concepts": [
        {
            "term": "术语",
            "definition": "定义（如有）",
            "context": "出现的上下文",
            "importance": 0.0-1.0
        }
    ]
}
```

只输出 JSON，不要其他解释。确保 JSON 格式正确。"""


def rule_based_structure_analysis(text: str) -> Dict:
    """
    Rule-based fallback for structure analysis.
    """
    lines = text.split('\n')
    text_blocks = []
    heading_hierarchy = []
    key_concepts = []

    current_pos = 0
    for line in lines:
        line = line.strip()
        if not line:
            current_pos += len(line) + 1
            continue

        # Detect headings (lines that are short and don't end with punctuation)
        is_heading = (
            len(line) < 50 and
            not line.endswith(('。', '，', '：', '、', '.', ',', ':', ';')) and
            not line.startswith(('-', '•', '*', '1', '2', '3', '4', '5', '6', '7', '8', '9'))
        )

        # Detect markdown headings
        md_heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if md_heading_match:
            level = len(md_heading_match.group(1))
            heading_text = md_heading_match.group(2)
            text_blocks.append(TextBlock(
                content=heading_text,
                block_type="heading",
                level=level
            ))
            heading_hierarchy.append({
                "text": heading_text,
                "level": level,
                "position": current_pos,
                "children": []
            })
        elif line.startswith(('-', '•', '*')):
            text_blocks.append(TextBlock(
                content=line,
                block_type="list",
                level=1
            ))
        elif line.startswith(tuple('0123456789')):
            text_blocks.append(TextBlock(
                content=line,
                block_type="list",
                level=1
            ))
        elif is_heading:
            text_blocks.append(TextBlock(
                content=line,
                block_type="heading",
                level=2
            ))
            heading_hierarchy.append({
                "text": line,
                "level": 2,
                "position": current_pos,
                "children": []
            })
        else:
            text_blocks.append(TextBlock(
                content=line,
                block_type="paragraph",
                level=0
            ))

        current_pos += len(line) + 1

    # Extract potential key concepts (capitalized terms, quoted terms, bold terms)
    concept_patterns = [
        r'\*\*([^*]+)\*\*',  # Bold text
        r'「([^」]+)」',  # Chinese quotes
        r'"([^"]+)"',  # English quotes
        r'《([^》]+)》',  # Book titles
    ]

    for pattern in concept_patterns:
        for match in re.finditer(pattern, text):
            term = match.group(1).strip()
            if len(term) > 1 and len(term) < 30:
                key_concepts.append(KeyConcept(
                    term=term,
                    context=text[max(0, match.start()-20):min(len(text), match.end()+20)],
                    importance=0.7
                ))

    return {
        "document_type": "notes",
        "text_blocks": text_blocks,
        "heading_hierarchy": heading_hierarchy,
        "key_concepts": key_concepts
    }


def parse_structure_response(response_text: str, raw_text: str) -> Dict:
    """
    Parse the LLM response for structure analysis.
    """
    try:
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response_text.strip()

        data = json.loads(json_str)

        # Parse text blocks
        text_blocks = []
        for block in data.get("text_blocks", []):
            text_blocks.append(TextBlock(
                content=block.get("content", ""),
                block_type=block.get("block_type", "paragraph"),
                level=block.get("level", 0),
                metadata=block.get("metadata", {})
            ))

        # Parse key concepts
        key_concepts = []
        for concept in data.get("key_concepts", []):
            key_concepts.append(KeyConcept(
                term=concept.get("term", ""),
                definition=concept.get("definition"),
                context=concept.get("context"),
                importance=concept.get("importance", 0.5)
            ))

        return {
            "document_type": data.get("document_type", "notes"),
            "text_blocks": text_blocks,
            "heading_hierarchy": data.get("heading_hierarchy", []),
            "key_concepts": key_concepts
        }

    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to parse structure response: {e}")
        return rule_based_structure_analysis(raw_text)


async def structure_agent(state: NoteProcessingState) -> NoteProcessingState:
    """
    Structure Agent: Analyzes text structure and extracts key information.

    This agent:
    1. Parses the text into logical blocks
    2. Identifies heading hierarchy
    3. Extracts key concepts and terminology
    4. Classifies the document type

    Args:
        state: Current processing state with ocr_corrected_text

    Returns:
        Updated state with structure analysis results
    """
    start_time = time.time()
    agent_name = "structure_agent"

    logger.info(f"[{agent_name}] Starting structure analysis...")

    state["current_agent"] = agent_name

    # Check if OCR agent succeeded
    ocr_output = state.get("ocr_agent_output")
    if ocr_output and not ocr_output.success:
        error_msg = "Structure Agent skipped: OCR Agent failed"
        logger.warning(f"[{agent_name}] {error_msg}")
        state["structure_agent_output"] = AgentOutput(
            success=False,
            data=None,
            error=error_msg,
            processing_time=0,
            agent_name=agent_name
        )
        return state

    try:
        text = state.get("ocr_corrected_text", "")
        if not text:
            raise ValueError("No text available for structure analysis")

        # Use LLM for structure analysis
        try:
            messages = [
                SystemMessage(content=STRUCTURE_ANALYSIS_PROMPT),
                HumanMessage(content=f"请分析以下文本的结构：\n\n```\n{text}\n```")
            ]

            response = await llm.ainvoke(messages)
            result = parse_structure_response(response.content, text)

        except Exception as llm_error:
            logger.warning(f"[{agent_name}] LLM analysis failed: {llm_error}. Using rule-based analysis.")
            result = rule_based_structure_analysis(text)

        # Update state
        state["text_blocks"] = result["text_blocks"]
        state["heading_hierarchy"] = result["heading_hierarchy"]
        state["key_concepts"] = result["key_concepts"]
        state["document_type"] = result["document_type"]

        # Record success
        processing_time = time.time() - start_time
        state["processing_times"][agent_name] = processing_time
        state["structure_agent_output"] = AgentOutput(
            success=True,
            data={
                "document_type": result["document_type"],
                "block_count": len(result["text_blocks"]),
                "heading_count": len(result["heading_hierarchy"]),
                "concept_count": len(result["key_concepts"])
            },
            processing_time=processing_time,
            agent_name=agent_name
        )

        logger.info(
            f"[{agent_name}] Completed in {processing_time:.2f}s. "
            f"Type: {result['document_type']}, "
            f"Blocks: {len(result['text_blocks'])}, "
            f"Concepts: {len(result['key_concepts'])}"
        )

    except Exception as e:
        error_msg = f"Structure Agent failed: {str(e)}"
        logger.error(f"[{agent_name}] {error_msg}")

        state["errors"].append(error_msg)
        state["structure_agent_output"] = AgentOutput(
            success=False,
            data=None,
            error=error_msg,
            processing_time=time.time() - start_time,
            agent_name=agent_name
        )

    return state
