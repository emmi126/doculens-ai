import anthropic
from config import settings
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        """Initialize Claude client when an API key is available."""
        self.client = None
        self.model = settings.anthropic_model
        if settings.anthropic_api_key:
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        elif settings.enable_demo_ai_fallback:
            logger.warning("ANTHROPIC_API_KEY not set; demo LLM fallback enabled")

    def demo_format_note(
        self,
        ocr_text: str,
        additional_context: str = None,
        course_name: str = None,
        historical_context: List[Dict[str, str]] = None
    ) -> str:
        """Return deterministic Markdown for local demos without Anthropic credentials."""
        title = course_name or "Demo Processed Note"
        context = additional_context.strip() if additional_context else "No additional context provided."
        related_count = len(historical_context or [])

        return f"""# {title} Demo Note

## Extracted Text

{ocr_text.strip()}

## Clean Summary

- This note was generated using DocuLens AI local demo fallback.
- The uploaded image reached the backend successfully.
- OCR and formatting fallbacks are active because cloud AI credentials are not configured or a provider call failed.

## Context

{context}

## Related Course Context

Found {related_count} related historical notes for this demo request.

## Next Steps

1. Confirm that the note saved under the selected course.
2. Open the document view and check Markdown rendering.
3. Edit and save the note to verify CRUD behavior.
"""
    
    def format_note(self, ocr_text: str, additional_context: str = None) -> str:
        """
        Convert OCR-recognized text into a formatted note.
        
        Args:
            ocr_text: Raw text recognized by OCR.
            additional_context: Optional additional context.
        
        Returns:
            str: The formatted Markdown note.
        """
        
        # Build the system prompt.
        system_prompt = """You are a professional classroom-note editor. Convert OCR-extracted text into clear, structured notes.

Follow these rules:
1. Correct only obvious OCR errors, such as spelling mistakes or confused characters.
2. Organize the content with appropriate Markdown headings, paragraphs, and lists.
3. Preserve the original meaning. Do not invent facts or expand beyond the source text.
4. You may add minimal connecting words, complete clearly truncated sentences, and normalize terminology when the intended wording is unambiguous.
5. Format mathematical expressions with LaTeX, code with fenced code blocks, important concepts in bold, and quotations as blockquotes.
6. Keep the result concise while retaining all source information.
7. Write in the same language as the OCR source text unless the user's additional context explicitly requests another language. Do not translate the note by default.

Return only the formatted Markdown note, without commentary about your process."""

        # Build the user prompt.
        user_prompt = f"""Format the following OCR-extracted classroom note:

```
{ocr_text}
```
"""
        
        if additional_context:
            user_prompt += f"\n\nAdditional context: {additional_context}\n"
        
        user_prompt += "\nReturn the formatted note as Markdown:"
        
        if self.client is None:
            if settings.enable_demo_ai_fallback:
                logger.warning("Using demo LLM fallback")
                return self.demo_format_note(ocr_text, additional_context)
            raise Exception("Anthropic API key is not configured")

        try:
            # Call the Claude API.
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,  # Use a lower temperature for consistency.
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract response text.
            formatted_note = message.content[0].text
            
            logger.info(f"LLM formatting succeeded: {len(ocr_text)} input characters, {len(formatted_note)} output characters")
            return formatted_note
            
        except Exception as e:
            logger.error(f"LLM processing failed: {str(e)}")
            if settings.enable_demo_ai_fallback:
                logger.warning("Using demo LLM fallback after formatting failure")
                return self.demo_format_note(ocr_text, additional_context)
            raise Exception(f"Note formatting failed: {str(e)}")

    def format_note_with_rag(
        self,
        ocr_text: str,
        course_name: str,
        historical_context: List[Dict[str, str]] = None,
        additional_context: str = None
    ) -> str:
        """
        Format notes with RAG by incorporating historical context into a coherent note.

        Args:
            ocr_text: Raw text recognized by OCR.
            course_name: Course name.
            historical_context: Historical note context as title, content, date, and similarity records.
            additional_context: Optional additional context.

        Returns:
            str: The formatted Markdown note with historical connections.
        """

        # Build the RAG-enhanced system prompt.
        system_prompt = """You are a professional classroom-note editor. Convert a newly uploaded OCR transcript into a clear, structured Markdown note. You will also receive related notes from the same course as optional historical context.

Formatting rules:
1. Correct only obvious OCR errors.
2. Use appropriate Markdown headings, paragraphs, and lists.
3. Format mathematics with LaTeX, code with fenced blocks, important concepts in bold, and quotations as blockquotes.
4. Preserve the meaning and information in the newly uploaded note.
5. Write in the same language as the new OCR text unless the user explicitly requests another language. Do not translate by default.

Historical-context rules:
1. Use historical notes only to disambiguate terminology or identify a genuinely useful connection.
2. Do not add a historical-reference sentence merely because a similar note was retrieved.
3. Do not copy substantial historical content into the new note.
4. Do not introduce knowledge that is absent from the new note and supplied context.
5. Keep the new note independently understandable and concise.

Return only the formatted Markdown note, without commentary about your process."""

        # Build the user prompt.
        user_prompt = f"""**Course**: {course_name}

"""

        # Add historical note context when available.
        if historical_context and len(historical_context) > 0:
            user_prompt += "**Related historical notes** (optional context):\n\n"
            for i, ctx in enumerate(historical_context, 1):
                similarity_pct = int(ctx['similarity'] * 100)
                user_prompt += f"### Historical note {i}: {ctx['title']}\n"
                user_prompt += f"*Date: {ctx['created_at']} | Similarity: {similarity_pct}%*\n\n"

                # Limit historical note length to keep the prompt manageable.
                content_preview = ctx['content'][:800]
                if len(ctx['content']) > 800:
                    content_preview += "\n...(content truncated)"

                user_prompt += f"{content_preview}\n\n"
                user_prompt += "---\n\n"

        # Add the new note's OCR text.
        user_prompt += f"""**Newly uploaded note** (OCR text):

```
{ocr_text}
```
"""

        if additional_context:
            user_prompt += f"\n\n**Additional context**: {additional_context}\n"

        user_prompt += """

**Task**:
1. Format the newly uploaded note as structured Markdown.
2. Preserve its source language and original information.
3. Use historical context only when it materially clarifies the new note.
4. Do not add unsupported knowledge.

Return the formatted Markdown note:"""

        if self.client is None:
            if settings.enable_demo_ai_fallback:
                logger.warning("Using demo LLM fallback for RAG formatting")
                return self.demo_format_note(
                    ocr_text=ocr_text,
                    additional_context=additional_context,
                    course_name=course_name,
                    historical_context=historical_context
                )
            raise Exception("Anthropic API key is not configured")

        try:
            # Call the Claude API.
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,  # Use a lower temperature for consistency.
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Extract response text.
            formatted_note = message.content[0].text

            logger.info(
                f"RAG formatting succeeded: {len(ocr_text)} input characters, "
                f"{len(historical_context) if historical_context else 0} historical notes, "
                f"{len(formatted_note)} output characters"
            )
            return formatted_note

        except Exception as e:
            logger.error(f"RAG formatting failed: {str(e)}")
            if settings.enable_demo_ai_fallback:
                logger.warning("Using demo LLM fallback after RAG formatting failure")
                return self.demo_format_note(
                    ocr_text=ocr_text,
                    additional_context=additional_context,
                    course_name=course_name,
                    historical_context=historical_context
                )
            # Fallback to basic formatting if RAG fails
            logger.info("Falling back to basic note formatting...")
            return self.format_note(ocr_text, additional_context)

    def enhance_note_with_qa(self, formatted_note: str) -> dict:
        """
        Generate review questions from the formatted note (reserved for Phase 5).
        
        Returns:
            dict: {"note": str, "questions": list[str]}
        """
        system_prompt = """You are an educational assistant. Generate three to five review questions from the supplied note.

The questions should cover its main concepts, promote understanding rather than memorization, and have moderate difficulty. Use the same language as the note.

Output format:
Q1: [question]
Q2: [question]
..."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.5,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"Note content:\n\n{formatted_note}\n\nGenerate review questions:"}
                ]
            )
            
            qa_text = message.content[0].text
            
            # Parse generated questions.
            questions = []
            for line in qa_text.split('\n'):
                if line.strip().startswith('Q'):
                    question = line.split(':', 1)[1].strip() if ':' in line else line
                    questions.append(question)
            
            return {
                "note": formatted_note,
                "questions": questions
            }
            
        except Exception as e:
            logger.error(f"Question generation failed: {str(e)}")
            return {
                "note": formatted_note,
                "questions": []
            }

# Create the singleton service instance.
llm_service = LLMService()
