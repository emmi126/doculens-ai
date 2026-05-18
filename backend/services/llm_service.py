import anthropic
from config import settings
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        """Initialize Claude client when an API key is available."""
        self.client = None
        self.model = "claude-sonnet-4-20250514"
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
        将 OCR 识别的文本整理成格式化笔记
        
        Args:
            ocr_text: OCR 识别的原始文本
            additional_context: 额外的上下文（可选）
        
        Returns:
            str: 整理后的 Markdown 格式笔记
        """
        
        # 构建系统提示词
        system_prompt = """你是一个专业的课堂笔记整理助手。你的任务是将 OCR 识别的课堂笔记文本整理成清晰、结构化的笔记。

请遵循以下规则：
1. **修正 OCR 错误**：识别并修正明显的 OCR 识别错误（拼写错误、字符混淆等）
2. **结构化组织**：
   - 使用清晰的标题层级（# ## ###）
   - 将内容分成逻辑段落
   - 使用列表来组织要点
3. **保留原意**：不要添加 OCR 文本中没有的内容，但可以：
   - 补充必要的连接词使语句通顺
   - 完善不完整的句子
   - 统一术语表达
4. **格式化**：
   - 数学公式使用 LaTeX 格式：$inline$ 或 $$block$$
   - 代码使用代码块：```language```
   - 重要概念使用**粗体**
   - 示例或引用使用 > 引用块
5. **保持简洁**：去除重复内容，但保留所有关键信息

输出纯 Markdown 格式，不要添加任何解释性文字。"""

        # 构建用户提示词
        user_prompt = f"""请整理以下课堂笔记的 OCR 文本：

```
{ocr_text}
```
"""
        
        if additional_context:
            user_prompt += f"\n\n额外上下文：{additional_context}\n"
        
        user_prompt += "\n请输出整理后的笔记（Markdown 格式）："
        
        if self.client is None:
            if settings.enable_demo_ai_fallback:
                logger.warning("Using demo LLM fallback")
                return self.demo_format_note(ocr_text, additional_context)
            raise Exception("Anthropic API key is not configured")

        try:
            # 调用 Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,  # 较低的温度以保持一致性
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # 提取响应文本
            formatted_note = message.content[0].text
            
            logger.info(f"LLM 整理成功，输入 {len(ocr_text)} 字符，输出 {len(formatted_note)} 字符")
            return formatted_note
            
        except Exception as e:
            logger.error(f"LLM 处理失败: {str(e)}")
            if settings.enable_demo_ai_fallback:
                logger.warning("Using demo LLM fallback after formatting failure")
                return self.demo_format_note(ocr_text, additional_context)
            raise Exception(f"笔记整理失败: {str(e)}")

    def format_note_with_rag(
        self,
        ocr_text: str,
        course_name: str,
        historical_context: List[Dict[str, str]] = None,
        additional_context: str = None
    ) -> str:
        """
        使用 RAG 增强的笔记整理：结合历史笔记上下文生成连贯的笔记

        Args:
            ocr_text: OCR 识别的原始文本
            course_name: 课程名称
            historical_context: 历史笔记上下文，格式为 [{"title": str, "content": str, "created_at": str, "similarity": float}]
            additional_context: 额外的上下文（可选）

        Returns:
            str: 整理后的 Markdown 格式笔记（包含历史关联）
        """

        # 构建系统提示词（RAG 增强版本）
        system_prompt = """你是一个专业的课堂笔记整理助手。你的任务是将 OCR 识别的课堂笔记文本整理成清晰、结构化的笔记。

你将获得：
1. 新上传的笔记（OCR 文本）
2. 历史相关笔记（同一门课程的之前内容）

请遵循以下规则：

**基础整理规则**：
1. **修正 OCR 错误**：识别并修正明显的 OCR 识别错误（拼写错误、字符混淆等）
2. **结构化组织**：
   - 使用清晰的标题层级（# ## ###）
   - 将内容分成逻辑段落
   - 使用列表来组织要点
3. **格式化**：
   - 数学公式使用 LaTeX 格式：$inline$ 或 $$block$$
   - 代码使用代码块：```language```
   - 重要概念使用**粗体**
   - 示例或引用使用 > 引用块

**RAG 增强规则（关键）**：
1. **建立关联**：如果新笔记引用了历史笔记中的概念，添加简短的说明
   - 例如："（回顾：上节课讨论的XX概念）"
2. **补充上下文**：如果新内容是历史概念的延续或应用，简要提及承上启下的关系
3. **保持真实性**：只基于 OCR 文本和提供的历史笔记，不要添加笔记外的知识
4. **概念标注**：当新笔记中的术语在历史笔记中已定义，可标注"（已学）"

**重要**：
- 输出纯 Markdown 格式，不要添加解释性文字
- 不要过度引用历史内容，保持新笔记的独立性
- 历史上下文仅用于理解，不要大段复制历史笔记内容

输出纯 Markdown 格式的整理笔记。"""

        # 构建用户提示词
        user_prompt = f"""**课程名称**：{course_name}

"""

        # 添加历史笔记上下文（如果有）
        if historical_context and len(historical_context) > 0:
            user_prompt += "**相关历史笔记**（供参考，了解课程脉络）：\n\n"
            for i, ctx in enumerate(historical_context, 1):
                similarity_pct = int(ctx['similarity'] * 100)
                user_prompt += f"### 历史笔记 {i}：{ctx['title']} \n"
                user_prompt += f"*日期: {ctx['created_at']} | 相关度: {similarity_pct}%*\n\n"

                # 限制历史笔记长度，避免 prompt 过长
                content_preview = ctx['content'][:800]
                if len(ctx['content']) > 800:
                    content_preview += "\n...(内容已截断)"

                user_prompt += f"{content_preview}\n\n"
                user_prompt += "---\n\n"

        # 添加新笔记 OCR 文本
        user_prompt += f"""**新上传的笔记**（OCR 识别文本）：

```
{ocr_text}
```
"""

        if additional_context:
            user_prompt += f"\n\n**额外上下文**：{additional_context}\n"

        user_prompt += """

**任务**：
1. 整理新笔记为结构化 Markdown
2. 如果新内容与历史笔记相关，添加简短的关联说明（但不要过度引用）
3. 补充必要的承上启下内容
4. 保留原始信息，不添加笔记外的知识

请输出整理后的笔记（Markdown 格式）："""

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
            # 调用 Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,  # 较低的温度以保持一致性
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # 提取响应文本
            formatted_note = message.content[0].text

            logger.info(
                f"RAG 增强整理成功 - 输入: {len(ocr_text)} 字符, "
                f"历史上下文: {len(historical_context) if historical_context else 0} 篇, "
                f"输出: {len(formatted_note)} 字符"
            )
            return formatted_note

        except Exception as e:
            logger.error(f"RAG 增强整理失败: {str(e)}")
            if settings.enable_demo_ai_fallback:
                logger.warning("Using demo LLM fallback after RAG formatting failure")
                return self.demo_format_note(
                    ocr_text=ocr_text,
                    additional_context=additional_context,
                    course_name=course_name,
                    historical_context=historical_context
                )
            # Fallback to basic formatting if RAG fails
            logger.info("回退到基础笔记整理...")
            return self.format_note(ocr_text, additional_context)

    def enhance_note_with_qa(self, formatted_note: str) -> dict:
        """
        基于整理后的笔记生成复习问题（Phase 5 功能预留）
        
        Returns:
            dict: {"note": str, "questions": list[str]}
        """
        system_prompt = """你是一个教育助手。基于给定的笔记，生成 3-5 个复习问题，帮助学生巩固知识。

问题应该：
1. 覆盖笔记的主要概念
2. 有助于理解而非死记硬背
3. 难度适中

输出格式：
Q1: [问题1]
Q2: [问题2]
..."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.5,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"笔记内容：\n\n{formatted_note}\n\n请生成复习问题："}
                ]
            )
            
            qa_text = message.content[0].text
            
            # 解析问题
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
            logger.error(f"生成问题失败: {str(e)}")
            return {
                "note": formatted_note,
                "questions": []
            }

# 创建单例
llm_service = LLMService()