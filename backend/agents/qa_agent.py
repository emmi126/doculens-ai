"""
QA Agent for Multi-Agent Note Processing System

Responsibilities:
1. Generate review questions based on note content
2. Create flashcard-style knowledge cards
3. Identify and highlight key points
4. Assign difficulty levels

Input: enhanced_content, key_concepts, document_type
Output: qa_items, knowledge_cards, key_points
"""

import time
import logging
import json
import re
from typing import List

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from .state import (
    NoteProcessingState,
    AgentOutput,
    QAItem,
    KnowledgeCard,
    ProcessingStatus
)
from config import settings

logger = logging.getLogger(__name__)


llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=settings.anthropic_api_key,
    temperature=0.5,  # Slightly higher for creativity in questions
    max_tokens=4096
)


QA_GENERATION_PROMPT = """你是一个专业的教育评估专家。基于给定的学习笔记，生成高质量的复习材料。

**任务**：

1. **生成复习问题（3-5个）**：
   - 覆盖笔记的主要概念
   - 问题类型多样：理解型、应用型、分析型
   - 每个问题标注难度（easy/medium/hard）
   - 提供参考答案

2. **创建知识卡片（5-8张）**：
   - 卡片正面：问题、术语或概念
   - 卡片背面：答案、定义或解释
   - 添加相关标签便于分类

3. **提取关键要点（3-5个）**：
   - 笔记中最重要的知识点
   - 用简洁的一句话概括

**输出格式（JSON）**：
```json
{
    "qa_items": [
        {
            "question": "问题内容",
            "answer": "参考答案",
            "difficulty": "easy|medium|hard",
            "concept": "相关概念（可选）"
        }
    ],
    "knowledge_cards": [
        {
            "front": "卡片正面（问题/术语）",
            "back": "卡片背面（答案/定义）",
            "tags": ["标签1", "标签2"],
            "concept": "相关概念（可选）"
        }
    ],
    "key_points": [
        "关键要点1",
        "关键要点2"
    ]
}
```

**要求**：
- 问题应该有助于理解而非死记硬背
- 知识卡片简洁明了，适合快速复习
- 关键要点应该是可独立理解的句子
- 基于笔记内容，不要添加外部知识

只输出 JSON，确保格式正确。"""


def format_key_concepts_for_qa(key_concepts: list) -> str:
    """Format key concepts for QA generation prompt."""
    if not key_concepts:
        return ""

    concepts = []
    for concept in key_concepts[:10]:
        term = getattr(concept, 'term', str(concept))
        definition = getattr(concept, 'definition', None)
        if definition:
            concepts.append(f"- {term}: {definition}")
        else:
            concepts.append(f"- {term}")

    return "已识别的关键概念：\n" + "\n".join(concepts)


def parse_qa_response(response_text: str) -> dict:
    """Parse the LLM response for QA generation."""
    try:
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response_text.strip()

        data = json.loads(json_str)

        # Parse QA items
        qa_items = []
        for item in data.get("qa_items", []):
            qa_items.append(QAItem(
                question=item.get("question", ""),
                answer=item.get("answer", ""),
                difficulty=item.get("difficulty", "medium"),
                concept=item.get("concept")
            ))

        # Parse knowledge cards
        knowledge_cards = []
        for card in data.get("knowledge_cards", []):
            knowledge_cards.append(KnowledgeCard(
                front=card.get("front", ""),
                back=card.get("back", ""),
                tags=card.get("tags", []),
                concept=card.get("concept")
            ))

        # Parse key points
        key_points = data.get("key_points", [])

        return {
            "qa_items": qa_items,
            "knowledge_cards": knowledge_cards,
            "key_points": key_points
        }

    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to parse QA response: {e}")
        return {
            "qa_items": [],
            "knowledge_cards": [],
            "key_points": []
        }


async def qa_agent(state: NoteProcessingState) -> NoteProcessingState:
    """
    QA Agent: Generates review materials from note content.

    This agent:
    1. Checks if QA generation is enabled
    2. Generates review questions with answers
    3. Creates flashcard-style knowledge cards
    4. Extracts key points

    Args:
        state: Current processing state

    Returns:
        Updated state with QA materials
    """
    start_time = time.time()
    agent_name = "qa_agent"

    logger.info(f"[{agent_name}] Starting Q&A generation...")

    state["current_agent"] = agent_name

    # Check if QA generation is enabled
    should_generate_qa = state.get("should_generate_qa", True)
    if not should_generate_qa:
        logger.info(f"[{agent_name}] QA generation disabled, skipping")
        state["qa_items"] = []
        state["knowledge_cards"] = []
        state["key_points"] = []
        state["qa_agent_output"] = AgentOutput(
            success=True,
            data={"skipped": True, "reason": "QA generation disabled"},
            processing_time=0,
            agent_name=agent_name
        )
        return state

    try:
        # Get the best available content
        content = state.get("enhanced_content") or state.get("ocr_corrected_text", "")
        if not content:
            raise ValueError("No content available for Q&A generation")

        key_concepts = state.get("key_concepts", [])
        document_type = state.get("document_type", "notes")

        # Build prompt
        user_content = f"""**文档类型**: {document_type}

**笔记内容**:
```
{content[:3000]}  # Limit content length
```

{format_key_concepts_for_qa(key_concepts)}

请基于以上笔记内容，生成复习材料。输出 JSON 格式。"""

        messages = [
            SystemMessage(content=QA_GENERATION_PROMPT),
            HumanMessage(content=user_content)
        ]

        response = await llm.ainvoke(messages)
        result = parse_qa_response(response.content)

        state["qa_items"] = result["qa_items"]
        state["knowledge_cards"] = result["knowledge_cards"]
        state["key_points"] = result["key_points"]

        # Record success
        processing_time = time.time() - start_time
        state["processing_times"][agent_name] = processing_time
        state["qa_agent_output"] = AgentOutput(
            success=True,
            data={
                "qa_count": len(result["qa_items"]),
                "card_count": len(result["knowledge_cards"]),
                "key_point_count": len(result["key_points"])
            },
            processing_time=processing_time,
            agent_name=agent_name
        )

        logger.info(
            f"[{agent_name}] Completed in {processing_time:.2f}s. "
            f"Questions: {len(result['qa_items'])}, "
            f"Cards: {len(result['knowledge_cards'])}, "
            f"Key points: {len(result['key_points'])}"
        )

    except Exception as e:
        error_msg = f"QA Agent failed: {str(e)}"
        logger.error(f"[{agent_name}] {error_msg}")

        state["errors"].append(error_msg)
        state["qa_items"] = []
        state["knowledge_cards"] = []
        state["key_points"] = []
        state["qa_agent_output"] = AgentOutput(
            success=False,
            data=None,
            error=error_msg,
            processing_time=time.time() - start_time,
            agent_name=agent_name
        )

    return state
