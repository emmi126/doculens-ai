#!/usr/bin/env python
"""
Test script for Multi-Agent Note Processing System (Phase 5)

This script tests the LangGraph-based multi-agent workflow:
1. Graph compilation and structure
2. Individual agent functions
3. Full pipeline execution
4. API endpoint integration

Usage:
    python scripts/test_multi_agent.py [--with-api] [--image PATH]

Options:
    --with-api    Also test the API endpoint (requires server running)
    --image PATH  Use a specific test image (default: test_pictures/sample.jpg)
"""

import asyncio
import sys
import os
import argparse
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60 + "\n")


def print_result(name: str, success: bool, details: str = ""):
    """Print a test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status} - {name}")
    if details:
        print(f"         {details}")


async def test_graph_compilation():
    """Test 1: Graph compilation"""
    print_section("Test 1: Graph Compilation")

    try:
        from agents.graph import create_note_processing_graph

        graph = create_note_processing_graph()
        print_result("Graph creation", True)

        # Check nodes
        nodes = list(graph.nodes.keys())
        expected_nodes = ["ocr_agent", "structure_agent", "content_agent", "qa_agent", "integration_agent"]
        all_present = all(node in nodes for node in expected_nodes)
        print_result("All nodes present", all_present, f"Found: {nodes}")

        return True

    except Exception as e:
        print_result("Graph compilation", False, str(e))
        return False


async def test_state_creation():
    """Test 2: State initialization"""
    print_section("Test 2: State Initialization")

    try:
        from agents.state import create_initial_state, ProcessingStatus

        state = create_initial_state(
            image_bytes=b"test_image_data",
            course_id="test-course-id",
            course_name="Test Course",
            additional_context="Test context",
            user_id="test-user-id",
            generate_qa=True
        )

        # Check required fields
        print_result("image_bytes set", state["image_bytes"] == b"test_image_data")
        print_result("course_id set", state["course_id"] == "test-course-id")
        print_result("should_use_rag True", state["should_use_rag"] == True)
        print_result("should_generate_qa True", state["should_generate_qa"] == True)
        print_result("status is PENDING", state["status"] == ProcessingStatus.PENDING)

        # Test without course_id
        state2 = create_initial_state(
            image_bytes=b"test",
            course_id=None
        )
        print_result("should_use_rag False (no course)", state2["should_use_rag"] == False)

        return True

    except Exception as e:
        print_result("State creation", False, str(e))
        return False


async def test_individual_agents(image_bytes: bytes):
    """Test 3: Individual agent functions"""
    print_section("Test 3: Individual Agent Functions")

    results = []

    try:
        from agents.state import create_initial_state
        from agents.ocr_agent import ocr_agent

        # Test OCR Agent
        print("\n  Testing OCR Agent...")
        state = create_initial_state(image_bytes=image_bytes)
        state = await ocr_agent(state)

        ocr_success = state.get("ocr_agent_output") and state["ocr_agent_output"].success
        print_result("OCR Agent", ocr_success,
                    f"Extracted {len(state.get('ocr_corrected_text', ''))} chars")
        results.append(ocr_success)

        if not ocr_success:
            print("    Skipping remaining agents (OCR failed)")
            return False

        # Test Structure Agent
        from agents.structure_agent import structure_agent

        print("\n  Testing Structure Agent...")
        state = await structure_agent(state)

        struct_success = state.get("structure_agent_output") and state["structure_agent_output"].success
        print_result("Structure Agent", struct_success,
                    f"Found {len(state.get('key_concepts', []))} concepts")
        results.append(struct_success)

        # Test Content Agent (without RAG for speed)
        from agents.content_agent import content_agent

        print("\n  Testing Content Agent (no RAG)...")
        state["should_use_rag"] = False
        state = await content_agent(state)

        content_success = state.get("content_agent_output") and state["content_agent_output"].success
        print_result("Content Agent", content_success,
                    f"Enhanced content: {len(state.get('enhanced_content', ''))} chars")
        results.append(content_success)

        # Test QA Agent
        from agents.qa_agent import qa_agent

        print("\n  Testing QA Agent...")
        state = await qa_agent(state)

        qa_success = state.get("qa_agent_output") and state["qa_agent_output"].success
        print_result("QA Agent", qa_success,
                    f"Generated {len(state.get('qa_items', []))} questions")
        results.append(qa_success)

        # Test Integration Agent
        from agents.integration_agent import integration_agent

        print("\n  Testing Integration Agent...")
        state = await integration_agent(state)

        int_success = state.get("integration_agent_output") and state["integration_agent_output"].success
        print_result("Integration Agent", int_success,
                    f"Final note: {len(state.get('final_note', ''))} chars")
        results.append(int_success)

        return all(results)

    except Exception as e:
        print_result("Individual agents", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_full_pipeline(image_bytes: bytes):
    """Test 4: Full pipeline execution"""
    print_section("Test 4: Full Pipeline Execution")

    try:
        from agents.graph import process_note_with_agents
        from agents.state import ProcessingStatus

        print("  Running full multi-agent pipeline...")
        print("  (This may take 30-60 seconds)\n")

        final_state = await process_note_with_agents(
            image_bytes=image_bytes,
            course_id=None,  # No RAG for faster testing
            course_name=None,
            additional_context="This is a test note",
            user_id=None,
            generate_qa=True
        )

        # Check results
        status = final_state.get("status")
        success = status == ProcessingStatus.COMPLETED

        print_result("Pipeline completed", success, f"Status: {status}")

        if success:
            metadata = final_state.get("final_metadata", {})
            print(f"\n  📊 Processing Summary:")
            print(f"     Total time: {metadata.get('processing_time_total', 0):.2f}s")
            print(f"     Agents run: {metadata.get('agents_run', [])}")
            print(f"     OCR confidence: {metadata.get('ocr_confidence', 0):.2f}")
            print(f"     Document type: {metadata.get('document_type', 'unknown')}")
            print(f"     Q&A items: {metadata.get('qa_items_count', 0)}")
            print(f"     Knowledge cards: {metadata.get('knowledge_cards_count', 0)}")
            print(f"     Key concepts: {metadata.get('key_concepts_count', 0)}")

            # Print sample of final note
            final_note = final_state.get("final_note", "")
            if final_note:
                print(f"\n  📝 Final Note Preview (first 500 chars):")
                print("  " + "-" * 40)
                preview = final_note[:500].replace("\n", "\n     ")
                print(f"     {preview}...")

        else:
            errors = final_state.get("errors", [])
            print(f"  Errors: {errors}")

        return success

    except Exception as e:
        print_result("Full pipeline", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoint(image_path: str):
    """Test 5: API endpoint (optional)"""
    print_section("Test 5: API Endpoint")

    try:
        import requests

        print("  Testing /process-note-agents endpoint...")

        # Check if server is running
        try:
            health = requests.get("http://localhost:8000/health", timeout=5)
            if health.status_code != 200:
                print_result("Server health check", False, "Server not healthy")
                return False
        except requests.exceptions.ConnectionError:
            print_result("Server connection", False, "Server not running (start with: python main.py)")
            return False

        print_result("Server health check", True)

        # Send test request
        with open(image_path, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            data = {
                'additional_context': 'API test',
                'generate_qa': 'true'
            }

            print("  Sending test image to /process-note-agents...")
            response = requests.post(
                "http://localhost:8000/process-note-agents",
                files=files,
                data=data,
                timeout=120
            )

        if response.status_code == 200:
            result = response.json()
            success = result.get("success", False)
            print_result("API request", success)

            if success:
                metadata = result.get("metadata", {})
                print(f"\n  📊 API Response Summary:")
                print(f"     Processing time: {metadata.get('processing_time_total', 0):.2f}s")
                print(f"     Q&A items: {len(result.get('qa_items', []))}")
                print(f"     Knowledge cards: {len(result.get('knowledge_cards', []))}")
                print(f"     Key concepts: {len(result.get('key_concepts', []))}")
            else:
                print(f"  Error: {result.get('error', 'Unknown')}")

            return success
        else:
            print_result("API request", False, f"Status {response.status_code}")
            return False

    except Exception as e:
        print_result("API endpoint", False, str(e))
        return False


async def main():
    parser = argparse.ArgumentParser(description="Test Multi-Agent System")
    parser.add_argument("--with-api", action="store_true", help="Also test API endpoint")
    parser.add_argument("--image", type=str, default=None, help="Test image path")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print(" Multi-Agent System Test Suite (Phase 5)")
    print("=" * 60)

    # Find test image
    if args.image:
        image_path = args.image
    else:
        # Look for test images
        test_dirs = [
            "test_pictures",
            "uploads",
        ]
        image_path = None
        for dir_path in test_dirs:
            full_path = Path(__file__).parent.parent / dir_path
            if full_path.exists():
                for ext in ['*.jpg', '*.jpeg', '*.png']:
                    images = list(full_path.glob(ext))
                    if images:
                        image_path = str(images[0])
                        break
            if image_path:
                break

    if not image_path or not os.path.exists(image_path):
        print("\n⚠️  No test image found. Creating a simple test image...")
        # Create a simple test image with text
        try:
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new('RGB', (800, 400), color='white')
            draw = ImageDraw.Draw(img)

            # Add sample text
            text = """Machine Learning Notes

Chapter 1: Introduction
- ML is a subset of AI
- Types: Supervised, Unsupervised, Reinforcement

Key Concepts:
1. Training Data
2. Model Parameters
3. Loss Function"""

            draw.text((50, 50), text, fill='black')

            image_path = "/tmp/test_note.png"
            img.save(image_path)
            print(f"  Created test image: {image_path}")

        except ImportError:
            print("  ❌ Cannot create test image (Pillow not available)")
            print("  Please provide a test image with --image PATH")
            return

    print(f"\n📷 Using test image: {image_path}")

    # Load image bytes
    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    results = []

    # Run tests
    results.append(await test_graph_compilation())
    results.append(await test_state_creation())
    results.append(await test_individual_agents(image_bytes))
    results.append(await test_full_pipeline(image_bytes))

    if args.with_api:
        results.append(await test_api_endpoint(image_path))

    # Summary
    print_section("Test Summary")

    passed = sum(results)
    total = len(results)
    all_passed = all(results)

    print(f"  Passed: {passed}/{total}")

    if all_passed:
        print("\n  🎉 All tests passed!")
    else:
        print("\n  ⚠️  Some tests failed. Check the output above for details.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
