"""Gemini API integration for response generation."""
import json
import re
from typing import Optional, List
import requests
from app.core.config import settings


class GeminiService:
    """Service for interacting with Gemini API via REST."""

    def __init__(self):
        """Initialize Gemini API client."""
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.api_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models"
            f"/{self.model}:generateContent"
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate_response(
        self,
        query: str,
        context: List[str],
        chat_history: List[dict] = None,
        confidence_threshold: float = None,
    ) -> dict:
        """Generate a well-structured response using Gemini + RAG context."""
        if confidence_threshold is None:
            confidence_threshold = settings.CONFIDENCE_THRESHOLD

        if not self.api_key:
            return self._generate_offline_response(query, context)

        try:
            context_text = self._format_context(context)
            prompt = self._build_prompt(query, context_text, chat_history)
            response_text = self._call_gemini_rest_api(prompt)

            if not response_text:
                return self._generate_offline_response(query, context)

            confidence = self._calculate_confidence(context)
            return {
                "answer": response_text,
                "confidence_score": confidence,
                "citations": self._extract_citations(context),
                "sources": context,
                "raw_response": response_text,
            }

        except Exception as e:
            print(f"[ERROR] Gemini generate_response failed: {e}")
            return self._generate_offline_response(query, context)

    def generate_ticket_summary(self, description: str) -> str:
        """Generate AI summary for a support ticket."""
        if not self.api_key:
            return "Summary: " + description[:100] + "..."
        try:
            prompt = (
                "Write a concise 2-3 sentence professional summary of this support ticket:\n\n"
                f"{description}\n\nSummary:"
            )
            result = self._call_gemini_rest_api(prompt)
            return result if result else f"Summary: {description[:100]}..."
        except Exception as e:
            return f"Unable to generate summary: {e}"

    def generate_ticket_solution(self, description: str, context: List[str] = None) -> str:
        """Generate a suggested solution for a support ticket."""
        if not self.api_key:
            return "Please contact support for assistance."
        try:
            context_section = ""
            if context:
                context_section = "\n\nRelevant documentation:\n" + "\n".join(
                    f"- {c}" for c in context
                )
            prompt = (
                f"Based on this support ticket, provide a clear step-by-step suggested solution:\n\n"
                f"{description}{context_section}\n\nSuggested Solution:"
            )
            result = self._call_gemini_rest_api(prompt)
            return result if result else "Please contact support for assistance."
        except Exception as e:
            return f"Unable to generate solution: {e}"

    def classify_ticket_category(self, title: str, description: str) -> str:
        """Classify a ticket into billing / technical / general."""
        if not self.api_key:
            return "general"
        try:
            prompt = (
                "Classify this support ticket into exactly one of: billing, technical, general.\n\n"
                f"Title: {title}\nDescription: {description}\n\n"
                "Category (billing/technical/general):"
            )
            result = self._call_gemini_rest_api(prompt)
            if result:
                cat = result.strip().lower()
                return cat if cat in {"billing", "technical", "general"} else "general"
        except Exception:
            pass
        return "general"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _call_gemini_rest_api(self, prompt: str, timeout: int = 90) -> Optional[str]:
        """POST to Gemini REST endpoint and return the text reply."""
        try:
            url = f"{self.api_url}?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.4,
                    "topP": 0.9,
                    "maxOutputTokens": 2048,
                },
            }
            print(f"[INFO] Calling Gemini API ({self.model})…")
            resp = requests.post(url, json=payload, timeout=timeout)

            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text = parts[0].get("text", "").strip()
                        if text:
                            print("[+] Gemini API response received.")
                            return text

            print(f"[ERROR] Gemini returned HTTP {resp.status_code}: {resp.text[:400]}")
            return None

        except requests.Timeout:
            print("[ERROR] Gemini API request timed out.")
            return None
        except Exception as e:
            print(f"[ERROR] Gemini REST call failed: {e}")
            return None

    def _format_context(self, context: List[str]) -> str:
        """Clean and format retrieved context chunks for the prompt."""
        cleaned = []
        for chunk in context:
            # Strip stray page-number artefacts like "148 ص 27"
            text = re.sub(r"\b\d{1,4}\s+ص\s+\d{1,4}\b", "", chunk)
            text = re.sub(r"\s{2,}", " ", text).strip()
            if len(text) > 20:
                cleaned.append(text)
        return "\n\n".join(f"[Source {i+1}]: {t}" for i, t in enumerate(cleaned))

    def _build_prompt(
        self,
        query: str,
        context: str,
        chat_history: List[dict] = None,
    ) -> str:
        """Build the full prompt sent to Gemini."""
        history_block = ""
        if chat_history:
            history_block = "Previous conversation:\n"
            for msg in chat_history[-4:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_block += f"{role}: {msg['content']}\n"
            history_block += "\n"

        return f"""You are a knowledgeable and helpful AI assistant.
Your task is to answer the user's question clearly and in a well-organised way.

Rules:
- Use the provided context as your primary source of information.
- Write in the same language as the user's question (Arabic if asked in Arabic, English if asked in English).
- Structure your answer with clear sections, bullet points, or numbered steps where appropriate.
- Do NOT include raw page numbers, artefacts, or source tags in your answer.
- If the context does not contain enough information, say so politely and suggest the user ask a more specific question.
- Keep the tone professional but approachable.

Context:
{context}

{history_block}User Question: {query}

Answer:"""

    def _calculate_confidence(self, context: List[str]) -> float:
        """Confidence based on how many relevant chunks were retrieved."""
        if not context:
            return 0.0
        return min(len(context) * 0.2, 1.0)

    def _extract_citations(self, context: List[str]) -> List[dict]:
        """Return short citation snippets from context chunks."""
        return [
            {
                "id": i + 1,
                "text": (chunk[:120] + "…") if len(chunk) > 120 else chunk,
            }
            for i, chunk in enumerate(context)
        ]

    def _generate_offline_response(self, query: str, context: List[str]) -> dict:
        """Structured fallback when Gemini is unavailable."""
        if not context:
            answer = (
                f"I don't have enough information to answer your question about "
                f'"{query}". Please try rephrasing or contact support.'
            )
            confidence = 0.0
        else:
            cleaned = []
            for chunk in context[:4]:
                text = re.sub(r"\b\d{1,4}\s+ص\s+\d{1,4}\b", "", chunk)
                text = re.sub(r"\s{2,}", " ", text).strip()
                if len(text) > 30:
                    cleaned.append(text)

            if cleaned:
                lines = "\n".join(f"• {t}" for t in cleaned)
                answer = (
                    f"Here is what the knowledge base contains about your question:\n\n"
                    f"{lines}\n\n"
                    "For a more detailed or precise answer, please ask a more specific question."
                )
            else:
                answer = (
                    "Related information was found, but it could not be formatted into "
                    "a clear answer. Please try rephrasing your question."
                )
            confidence = min(len(context) * 0.15, 0.5)

        return {
            "answer": answer,
            "confidence_score": confidence,
            "citations": self._extract_citations(context),
            "sources": context,
            "raw_response": answer,
        }
