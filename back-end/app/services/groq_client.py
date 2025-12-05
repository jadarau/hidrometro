import os
from typing import Optional
from app.config.settings import settings

try:
    from groq import Groq  # type: ignore
except Exception:
    Groq = None  # fallback path
import requests

SYSTEM_PROMPT = (
    "Você é um assistente especializado em leituras de hidrômetro. "
    "Receberá imagem ou texto OCR de hidrômetros. "
    "Sua tarefa é identificar com precisão os dígitos da leitura. "
    "Responda apenas com os dígitos exatos da leitura, sem espaços, letras ou símbolos."
)

class GroqService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        key = api_key or settings.groq_api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY não configurada.")
        self.api_key = key
        self.model = model or settings.groq_model or "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.client = None
        # Try initializing official SDK; fallback to raw HTTP if TypeError proxies issue occurs
        if Groq is not None:
            try:
                self.client = Groq(api_key=key)
            except TypeError:
                # Known issue: httpx version mismatch removing 'proxies' arg
                self.client = None

    def _raw_chat(self, prompt: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
        }
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code >= 300:
            raise RuntimeError(f"Erro na chamada Groq API: {resp.status_code} {resp.text}")
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return content

    def extract_digits(self, ocr_text: str) -> str:
        user_prompt = (
            "Extraia apenas os dígitos da leitura do hidrômetro a partir do texto OCR abaixo.\n\n" +
            ocr_text + "\n\nResponda somente os dígitos, sem espaços ou comentários."
        )
        if self.client is not None:
            try:
                chat = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0,
                )
                content = chat.choices[0].message.content.strip()
            except Exception as e:
                # Fallback to raw HTTP; if model is decommissioned, let caller set GROQ_MODEL
                content = self._raw_chat(user_prompt)
        else:
            content = self._raw_chat(user_prompt)
        digits = "".join(ch for ch in content if ch.isdigit())
        if not digits:
            raise RuntimeError("Nenhum dígito encontrado pela IA.")
        return digits

    def extract_digits_from_image_base64(self, image_b64: str) -> str:
        # Use Groq multimodal (vision) with OpenAI-compatible API schema
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Identifique apenas os dígitos da leitura."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                    }
                ]
            }
        ]
        if self.client is not None:
            try:
                chat = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                )
                content = chat.choices[0].message.content.strip()
            except Exception:
                # Raw HTTP fallback for multimodal
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                body = {"model": self.model, "messages": messages, "temperature": 0}
                resp = requests.post(url, headers=headers, json=body, timeout=30)
                if resp.status_code >= 300:
                    raise RuntimeError(f"Erro na chamada Groq API (vision): {resp.status_code} {resp.text}")
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            # Raw HTTP fallback for multimodal
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            body = {"model": self.model, "messages": messages, "temperature": 0}
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            if resp.status_code >= 300:
                raise RuntimeError(f"Erro na chamada Groq API (vision): {resp.status_code} {resp.text}")
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        digits = "".join(ch for ch in content if ch.isdigit())
        if not digits:
            raise RuntimeError("Nenhum dígito encontrado pela IA (vision).")
        return digits
