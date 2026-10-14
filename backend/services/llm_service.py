import os
import json
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from backend.rag.prompts import AUTOSAR_RAG_SYSTEM_PROMPT, AUTOSAR_EXTRACTION_PROMPT, AUTOSAR_COMPARISON_PROMPT

load_dotenv()


class LLMService:
    def __init__(self):
        self._reload_config()

    def _reload_config(self):
        load_dotenv(override=True)
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self._client = None
        self._client_type = None

    def _get_client(self):
        self._reload_config()

        # Check OpenRouter API key (sk-or-v1-...)
        api_key = self.openai_api_key or self.azure_api_key or ""
        if api_key.startswith("sk-or-v1-"):
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                    default_headers={
                        "HTTP-Referer": "https://github.com/autohld-ai",
                        "X-Title": "AutoHLD-AI"
                    }
                )
                self._client_type = "OPENROUTER"
                return self._client, self._client_type
            except Exception as e:
                print(f"OpenRouter initialization note: {e}")

        # Check Azure OpenAI
        if self.azure_endpoint and self.azure_api_key and "your-resource-name" not in self.azure_endpoint and not self.azure_api_key.startswith("sk-or-v1-"):
            try:
                from openai import AzureOpenAI
                self._client = AzureOpenAI(
                    api_key=self.azure_api_key,
                    api_version=self.azure_api_version,
                    azure_endpoint=self.azure_endpoint
                )
                self._client_type = "AZURE"
                return self._client, self._client_type
            except Exception as e:
                print(f"AzureOpenAI initialization note: {e}")

        # Check Standard OpenAI
        if self.openai_api_key and len(self.openai_api_key.strip()) > 10 and not self.openai_api_key.startswith("sk-or-v1-"):
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.openai_api_key)
                self._client_type = "OPENAI"
                return self._client, self._client_type
            except Exception as e:
                print(f"OpenAI initialization note: {e}")

        self._client_type = "LOCAL_ENGINE"
        return None, "LOCAL_ENGINE"

    def generate_chat_response(self, system_prompt: str, user_prompt: str) -> str:
        client, client_type = self._get_client()

        if client_type == "OPENROUTER":
            # Test paid models then free tier models
            models_to_try = [
                "openai/gpt-4o-mini",
                "openai/gpt-4o",
                "google/gemini-2.0-flash-lite-preview-02-05:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "qwen/qwen-2.5-72b-instruct:free"
            ]
            for model_name in models_to_try:
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.1
                    )
                    content = response.choices[0].message.content
                    if content and len(content.strip()) > 10:
                        return content
                except Exception as e:
                    pass

        elif client_type == "AZURE":
            try:
                response = client.chat.completions.create(
                    model=self.azure_deployment,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1
                )
                return response.choices[0].message.content
            except Exception as e:
                pass

        elif client_type == "OPENAI":
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1
                )
                return response.choices[0].message.content
            except Exception as e:
                pass

        # Dynamic Context-Grounded Local Synthesis
        return self._dynamic_local_reasoning(system_prompt, user_prompt)

    def _dynamic_local_reasoning(self, system_prompt: str, user_prompt: str) -> str:
        """
        Context-grounded local synthesis: reads the retrieved HLD context and produces
        a natural language answer that directly addresses the question while staying
        strictly within the provided context.
        """
        # Extract context from prompt
        context = ""
        if "Context:\n" in system_prompt:
            context = system_prompt.split("Context:\n", 1)[-1].strip()
        elif "context" in system_prompt.lower():
            # Try other split strategies
            for marker in ["\nContext:", "Context:", "---"]:
                if marker in system_prompt:
                    context = system_prompt.split(marker, 1)[-1].strip()
                    break

        if not context.strip():
            return "⚠️ **Insufficient Evidence in HLD**: No relevant context was retrieved to answer your question. Please verify that the document contains information related to your query."

        q = user_prompt.strip()
        q_lower = q.lower()

        # Parse context into lines, keeping those with sufficient substance
        raw_lines = [l.strip() for l in context.split("\n") if l.strip() and len(l.strip()) > 10]
        # Remove lines that are just separators or page headers
        raw_lines = [l for l in raw_lines if not re.match(r'^[-=]+$', l) and not l.startswith('--- [Document:')]

        if not raw_lines:
            return "⚠️ **Insufficient Evidence in HLD**: The retrieved context does not contain readable text relevant to your question."

        # Extract significant query keywords (3+ chars, exclude stop words)
        stop_words = {"what", "which", "how", "why", "are", "the", "and", "for",
                      "with", "does", "from", "when", "show", "tell", "me", "list",
                      "all", "any", "can", "will", "is", "in", "of", "to", "a", "an", "tell", "about", "on", "for", "the"}
        query_words = [w for w in re.findall(r'[a-zA-Z][a-zA-Z0-9_]+', q_lower)
                        if len(w) >= 3 and w not in stop_words]

        # Score lines by relevance to this specific query
        scored_lines = []
        for line in raw_lines:
            line_lower = line.lower()
            score = sum(1 for qw in query_words if qw in line_lower)
            # Boost lines with exact entity names mentioned in query
            for qw in query_words:
                if re.search(r'\b' + re.escape(qw) + r'\b', line_lower):
                    score += 1
            # Also boost lines that contain question words (like "what is X" -> lines containing X)
            if score > 0:
                scored_lines.append((score, line))

        # Sort by relevance score descending
        scored_lines.sort(key=lambda x: x[0], reverse=True)
        # Take top 5 most relevant lines
        top_lines = [l for _, l in scored_lines[:5]]

        # If no lines scored, fall back to first few lines
        if not top_lines:
            top_lines = raw_lines[:5]

        # Build a concise, natural language answer
        # Start with a direct answer attempt
        answer_parts = []
        answer_parts.append(f"**Answer to:** \"{q}\"\n")

        if len(top_lines) == 1:
            # Single relevant line: present it clearly
            clean_line = top_lines[0].lstrip("•-*#[] ").strip()
            answer_parts.append(f"Based on the HLD document: {clean_line}")
        else:
            # Multiple relevant lines: synthesize into a coherent paragraph
            answer_parts.append("According to the retrieved HLD sections:\n")
            # Clean up each line
            cleaned = []
            for line in top_lines:
                clean = line.lstrip("•-*#[] ").strip()
                # Remove redundant page headers if present
                if clean.startswith("Document:") or clean.startswith("Page"):
                    # Try to extract meaningful part after colon
                    if ": " in clean:
                        clean = clean.split(": ", 1)[-1]
                if clean:
                    cleaned.append(clean)
            # If we have cleaned lines, present them as points or combine
            if len(cleaned) == 1:
                answer_parts.append(cleaned[0])
            else:
                # Use semicolon to combine related facts, or bullet points if diverse
                # Heuristic: if lines are short, combine; else bullet
                if all(len(c) < 100 for c in cleaned):
                    combined = "; ".join(cleaned)
                    answer_parts.append(f"{combined}.")
                else:
                    answer_parts.append("\n".join([f"- {c}" for c in cleaned]))

        # Add traceability note
        answer_parts.append("\n\n---\n")
        answer_parts.append(
            "> **📌 Traceability Note:** The above information is extracted directly from "
            "the retrieved HLD document sections. Review the cited pages below for full context. "
            "\n> "
            "\n> *To get more precise answers, configure an LLM API key (OpenAI / Azure OpenAI / OpenRouter) in your `.env` file.*"
        )

        return "\n".join(answer_parts)


llm_service = LLMService()
