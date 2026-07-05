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
    model=settings.anthropic_model,
    api_key=settings.anthropic_api_key,
    temperature=0.5,  # Slightly higher for creativity in questions
    max_tokens=4096
)


QA_GENERATION_PROMPT = """You are an educational assessment specialist. Generate high-quality review material from the supplied study note.

Tasks:
1. Generate three to five varied comprehension, application, or analysis questions. Include answers and easy, medium, or hard difficulty labels.
2. Create five to eight concise knowledge cards with useful classification tags.
3. Extract three to five independently understandable key points.
4. Use only the note content, preserve its language, and do not add external knowledge.

**Output format (JSON)**:
```json
{
    "qa_items": [
        {
            "question": "question",
            "answer": "reference answer",
            "difficulty": "easy|medium|hard",
            "concept": "optional related concept"
        }
    ],
    "knowledge_cards": [
        {
            "front": "question or term",
            "back": "answer or definition",
            "tags": ["tag1", "tag2"],
            "concept": "optional related concept"
        }
    ],
    "key_points": [
        "key point 1",
        "key point 2"
    ]
}
```

Return valid JSON only."""


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

    return "Identified key concepts:\n" + "\n".join(concepts)


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
        user_content = f"""**Document type**: {document_type}

**Note content**:
```
{content[:3000]}  # Limit content length
```

{format_key_concepts_for_qa(key_concepts)}

Generate review material from the note above. Return JSON."""

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
