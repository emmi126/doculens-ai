"""
Integration Agent for Multi-Agent Note Processing System

Responsibilities:
1. Combine outputs from all previous agents
2. Generate the final formatted Markdown note
3. Add Q&A section if available
4. Create processing metadata summary

Input: All agent outputs (ocr, structure, content, qa)
Output: final_note, final_metadata
"""

import time
import logging
import json
from typing import List
from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from .state import (
    NoteProcessingState,
    AgentOutput,
    ProcessingStatus
)
from config import settings

logger = logging.getLogger(__name__)


llm = ChatAnthropic(
    model=settings.anthropic_model,
    api_key=settings.anthropic_api_key,
    temperature=0.3,
    max_tokens=8192  # Larger output for final note
)


INTEGRATION_PROMPT = """You are a note-integration specialist. Combine outputs from multiple processing stages into a complete, professional Markdown note.

Use a clear heading hierarchy, logical sections, lists, and tables where appropriate. Format mathematics with LaTeX, code with fenced blocks, important concepts in bold, and quotations as blockquotes. Incorporate useful cross-references naturally. Preserve the source language and do not translate by default.

Return the complete Markdown note directly, without JSON wrapping or process commentary."""


def format_qa_section(qa_items: list, key_points: list) -> str:
    """Format Q&A items into a Markdown section."""
    sections = []

    if key_points:
        sections.append("## 📌 Key Points\n")
        for i, point in enumerate(key_points, 1):
            sections.append(f"{i}. {point}")
        sections.append("")

    if qa_items:
        sections.append("## ❓ Review Questions\n")
        for i, qa in enumerate(qa_items, 1):
            question = getattr(qa, 'question', str(qa))
            answer = getattr(qa, 'answer', '')
            difficulty = getattr(qa, 'difficulty', 'medium')

            difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(difficulty, "🟡")

            sections.append(f"### Q{i} {difficulty_emoji}")
            sections.append(f"**Question**: {question}\n")
            sections.append(f"<details>")
            sections.append(f"<summary>View answer</summary>\n")
            sections.append(f"{answer}")
            sections.append(f"</details>\n")

    return "\n".join(sections)


def format_knowledge_cards(cards: list) -> str:
    """Format knowledge cards into a Markdown section."""
    if not cards:
        return ""

    sections = ["## 📚 Knowledge Cards\n"]
    sections.append("| Front | Back |")
    sections.append("|------|------|")

    for card in cards[:10]:  # Limit to 10 cards
        front = getattr(card, 'front', str(card))
        back = getattr(card, 'back', '')
        # Escape pipe characters for table
        front = front.replace("|", "\\|")
        back = back.replace("|", "\\|")
        sections.append(f"| {front} | {back} |")

    return "\n".join(sections)


def build_integration_prompt(state: NoteProcessingState) -> str:
    """Build the prompt for the integration LLM call."""
    enhanced_content = state.get("enhanced_content") or state.get("ocr_corrected_text", "")

    # Format key concepts
    key_concepts = state.get("key_concepts", [])
    concepts_str = ""
    if key_concepts:
        concept_items = []
        for c in key_concepts[:10]:
            term = getattr(c, 'term', str(c))
            definition = getattr(c, 'definition', None)
            if definition:
                concept_items.append(f"- **{term}**: {definition}")
            else:
                concept_items.append(f"- **{term}**")
        concepts_str = "**Key concepts**:\n" + "\n".join(concept_items)

    # Format cross-references
    cross_refs = state.get("cross_references", [])
    refs_str = ""
    if cross_refs:
        ref_items = []
        for ref in cross_refs:
            if isinstance(ref, dict):
                concept = ref.get("concept", "")
                title = ref.get("reference_title", "")
                relation = ref.get("relationship", "")
                ref_items.append(f"- {concept} → {title}: {relation}")
        if ref_items:
            refs_str = "**Cross-references**:\n" + "\n".join(ref_items)

    # Format related notes summary
    related_notes = state.get("related_notes", [])
    related_str = ""
    if related_notes:
        note_items = []
        for note in related_notes:
            title = getattr(note, 'title', str(note))
            similarity = getattr(note, 'similarity', 0)
            note_items.append(f"- {title} (similarity: {int(similarity*100)}%)")
        related_str = "**Related historical notes**:\n" + "\n".join(note_items)

    prompt = f"""Integrate the following material into a complete Markdown note:

**Enhanced content**:
```
{enhanced_content}
```

{concepts_str}

{refs_str}

{related_str}

Generate a professional, clearly structured Markdown note in the source language."""

    return prompt


async def integration_agent(state: NoteProcessingState) -> NoteProcessingState:
    """
    Integration Agent: Assembles the final formatted note.

    This agent:
    1. Collects outputs from all previous agents
    2. Uses LLM to create a cohesive final note
    3. Adds Q&A and knowledge card sections
    4. Generates processing metadata

    Args:
        state: Current processing state with all agent outputs

    Returns:
        Updated state with final note and metadata
    """
    start_time = time.time()
    agent_name = "integration_agent"

    logger.info(f"[{agent_name}] Starting final integration...")

    state["current_agent"] = agent_name

    try:
        # Step 1: Generate main note content via LLM
        user_prompt = build_integration_prompt(state)

        messages = [
            SystemMessage(content=INTEGRATION_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        response = await llm.ainvoke(messages)
        main_note = response.content

        # Step 2: Add Q&A section if available
        qa_items = state.get("qa_items", [])
        key_points = state.get("key_points", [])
        qa_section = format_qa_section(qa_items, key_points)

        # Step 3: Add knowledge cards if available
        knowledge_cards = state.get("knowledge_cards", [])
        cards_section = format_knowledge_cards(knowledge_cards)

        # Step 4: Combine all parts
        final_parts = [main_note]

        if qa_section:
            final_parts.append("\n---\n")
            final_parts.append(qa_section)

        if cards_section:
            final_parts.append("\n---\n")
            final_parts.append(cards_section)

        final_note = "\n".join(final_parts)
        state["final_note"] = final_note

        # Step 5: Generate metadata
        total_processing_time = sum(state.get("processing_times", {}).values())
        errors = state.get("errors", [])

        metadata = {
            "processing_time_total": round(total_processing_time, 2),
            "processing_times": {k: round(v, 2) for k, v in state.get("processing_times", {}).items()},
            "ocr_confidence": state.get("ocr_confidence", 0),
            "document_type": state.get("document_type", "notes"),
            "related_notes_count": len(state.get("related_notes", [])),
            "key_concepts_count": len(state.get("key_concepts", [])),
            "qa_items_count": len(qa_items),
            "knowledge_cards_count": len(knowledge_cards),
            "special_contents_count": len(state.get("special_contents", [])),
            "errors": errors,
            "agents_run": list(state.get("processing_times", {}).keys()),
            "used_rag": len(state.get("related_notes", [])) > 0,
            "generated_qa": len(qa_items) > 0,
            "timestamp": datetime.now().isoformat()
        }
        state["final_metadata"] = metadata

        # Step 6: Update status
        if errors:
            state["status"] = ProcessingStatus.COMPLETED  # Completed with warnings
            logger.warning(f"[{agent_name}] Completed with {len(errors)} errors/warnings")
        else:
            state["status"] = ProcessingStatus.COMPLETED

        # Record success
        processing_time = time.time() - start_time
        state["processing_times"][agent_name] = processing_time
        state["integration_agent_output"] = AgentOutput(
            success=True,
            data={
                "final_note_length": len(final_note),
                "sections_included": {
                    "main": True,
                    "qa": bool(qa_section),
                    "cards": bool(cards_section)
                }
            },
            processing_time=processing_time,
            agent_name=agent_name
        )

        logger.info(
            f"[{agent_name}] Completed in {processing_time:.2f}s. "
            f"Final note: {len(final_note)} chars. "
            f"Total time: {total_processing_time:.2f}s"
        )

    except Exception as e:
        error_msg = f"Integration Agent failed: {str(e)}"
        logger.error(f"[{agent_name}] {error_msg}")

        # Fallback: use enhanced content or OCR text
        fallback_content = state.get("enhanced_content") or state.get("ocr_corrected_text", "")
        state["final_note"] = fallback_content
        state["final_metadata"] = {"error": error_msg}
        state["errors"].append(error_msg)
        state["status"] = ProcessingStatus.FAILED

        state["integration_agent_output"] = AgentOutput(
            success=False,
            data=None,
            error=error_msg,
            processing_time=time.time() - start_time,
            agent_name=agent_name
        )

    return state
