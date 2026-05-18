"""
LangGraph Workflow for Multi-Agent Note Processing System

This module defines the graph that orchestrates all agents in the
note processing pipeline with conditional branching and error handling.

Flow:
    Start → OCR Agent → Structure Agent → Content Agent → QA Agent → Integration Agent → End
                                              ↓                 ↓
                                    (skip if no course_id)  (skip if disabled)
"""

import logging
from typing import Literal

from langgraph.graph import StateGraph, START, END

from .state import NoteProcessingState, ProcessingStatus, create_initial_state
from .ocr_agent import ocr_agent
from .structure_agent import structure_agent
from .content_agent import content_agent
from .qa_agent import qa_agent
from .integration_agent import integration_agent

logger = logging.getLogger(__name__)


# Define node names as constants
OCR_NODE = "ocr_agent"
STRUCTURE_NODE = "structure_agent"
CONTENT_NODE = "content_agent"
QA_NODE = "qa_agent"
INTEGRATION_NODE = "integration_agent"


def should_continue_after_ocr(state: NoteProcessingState) -> Literal["structure_agent", "__end__"]:
    """
    Conditional edge after OCR Agent.
    Continues to structure analysis if OCR succeeded, otherwise ends.
    """
    ocr_output = state.get("ocr_agent_output")
    if ocr_output and ocr_output.success:
        logger.info("[Router] OCR succeeded, continuing to structure agent")
        return STRUCTURE_NODE
    else:
        logger.warning("[Router] OCR failed, ending workflow")
        state["status"] = ProcessingStatus.FAILED
        return END


def should_continue_after_structure(state: NoteProcessingState) -> Literal["content_agent"]:
    """
    After structure analysis, always continue to content agent.
    Content agent can work with just OCR text if structure failed.
    """
    return CONTENT_NODE


def should_continue_after_content(state: NoteProcessingState) -> Literal["qa_agent", "integration_agent"]:
    """
    Conditional edge after Content Agent.
    Skips QA agent if QA generation is disabled.
    """
    should_generate_qa = state.get("should_generate_qa", True)
    if should_generate_qa:
        logger.info("[Router] QA generation enabled, continuing to QA agent")
        return QA_NODE
    else:
        logger.info("[Router] QA generation disabled, skipping to integration")
        return INTEGRATION_NODE


def should_continue_after_qa(state: NoteProcessingState) -> Literal["integration_agent"]:
    """
    After QA agent, always continue to integration.
    """
    return INTEGRATION_NODE


def create_note_processing_graph() -> StateGraph:
    """
    Create the LangGraph workflow for multi-agent note processing.

    The graph implements the following flow:

    START
      │
      ▼
    OCR Agent ──(fail)──> END
      │
      │ (success)
      ▼
    Structure Agent
      │
      ▼
    Content Agent ──(no RAG)──> (still continues, just without RAG)
      │
      ▼
    ┌─────────────────┐
    │ should_generate │
    │     qa?         │
    └────────┬────────┘
             │
        ┌────┴────┐
        │         │
        ▼         ▼
    QA Agent   (skip)
        │         │
        └────┬────┘
             │
             ▼
    Integration Agent
             │
             ▼
           END

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph with our state type
    workflow = StateGraph(NoteProcessingState)

    # Add all agent nodes
    workflow.add_node(OCR_NODE, ocr_agent)
    workflow.add_node(STRUCTURE_NODE, structure_agent)
    workflow.add_node(CONTENT_NODE, content_agent)
    workflow.add_node(QA_NODE, qa_agent)
    workflow.add_node(INTEGRATION_NODE, integration_agent)

    # Add edges with conditional routing

    # Start -> OCR Agent
    workflow.add_edge(START, OCR_NODE)

    # OCR Agent -> Structure Agent (conditional: only if OCR succeeded)
    workflow.add_conditional_edges(
        OCR_NODE,
        should_continue_after_ocr,
        {
            STRUCTURE_NODE: STRUCTURE_NODE,
            END: END
        }
    )

    # Structure Agent -> Content Agent (always)
    workflow.add_edge(STRUCTURE_NODE, CONTENT_NODE)

    # Content Agent -> QA Agent or Integration Agent (conditional)
    workflow.add_conditional_edges(
        CONTENT_NODE,
        should_continue_after_content,
        {
            QA_NODE: QA_NODE,
            INTEGRATION_NODE: INTEGRATION_NODE
        }
    )

    # QA Agent -> Integration Agent (always)
    workflow.add_edge(QA_NODE, INTEGRATION_NODE)

    # Integration Agent -> End
    workflow.add_edge(INTEGRATION_NODE, END)

    # Compile the graph
    compiled_graph = workflow.compile()

    logger.info("Note processing graph compiled successfully")

    return compiled_graph


async def process_note_with_agents(
    image_bytes: bytes,
    course_id: str = None,
    course_name: str = None,
    additional_context: str = None,
    user_id: str = None,
    generate_qa: bool = True
) -> NoteProcessingState:
    """
    High-level function to process a note using the multi-agent system.

    Args:
        image_bytes: Raw image data
        course_id: Optional course ID for RAG
        course_name: Optional course name
        additional_context: Optional user context
        user_id: Optional user ID
        generate_qa: Whether to generate Q&A materials

    Returns:
        Final processing state with all results
    """
    logger.info(f"Starting multi-agent note processing (course_id={course_id}, generate_qa={generate_qa})")

    # Create initial state
    initial_state = create_initial_state(
        image_bytes=image_bytes,
        course_id=course_id,
        course_name=course_name,
        additional_context=additional_context,
        user_id=user_id,
        generate_qa=generate_qa
    )

    # Create and run the graph
    graph = create_note_processing_graph()

    # Execute the graph asynchronously
    final_state = await graph.ainvoke(initial_state)

    logger.info(
        f"Multi-agent processing completed. "
        f"Status: {final_state.get('status')}, "
        f"Errors: {len(final_state.get('errors', []))}"
    )

    return final_state
