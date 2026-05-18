"""
Multi-Agent System for DocuLens (Phase 5)

This module implements a LangGraph-based multi-agent system for intelligent
note processing. The system coordinates multiple specialized agents:

- OCR Agent: Extracts and corrects text from images
- Structure Agent: Analyzes text structure and identifies key concepts
- Content Agent: Integrates RAG context and optimizes content
- QA Agent: Generates review questions and knowledge cards
- Integration Agent: Assembles the final formatted note

Usage:
    from agents import create_note_processing_graph, NoteProcessingState

    graph = create_note_processing_graph()
    result = await graph.ainvoke(initial_state)
"""

from .state import NoteProcessingState, AgentOutput
from .graph import create_note_processing_graph
from .ocr_agent import ocr_agent
from .structure_agent import structure_agent
from .content_agent import content_agent
from .qa_agent import qa_agent
from .integration_agent import integration_agent

__all__ = [
    "NoteProcessingState",
    "AgentOutput",
    "create_note_processing_graph",
    "ocr_agent",
    "structure_agent",
    "content_agent",
    "qa_agent",
    "integration_agent",
]
