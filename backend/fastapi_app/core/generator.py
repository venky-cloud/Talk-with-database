from __future__ import annotations
import os
import requests
from typing import List
from .config import settings

class BaseGenerator:
    def generate(
        self,
        prompt: str,
        n: int = 5,
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_tokens: int = 400
    ) -> List[str]:
        raise NotImplementedError

class MixtralOpenRouterAdapter(BaseGenerator):
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.MODEL
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")

    def generate(
        self,
        prompt: str,
        n: int = 5,
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_tokens: int = 400
    ) -> List[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        body = {
            "model": self.model,
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "messages": [
                {"role": "system", "content": "You are a query generator. Output only the final query."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
        }
        r = requests.post(self.BASE_URL, headers=headers, json=body, timeout=60)
        r.raise_for_status()
        data = r.json()
        outs: List[str] = []
        for c in data.get("choices", []):
            content = c.get("message", {}).get("content", "").strip()
            # Strip code fences if present
            if content.startswith("```"):
                content = content.strip("`\n").split("\n", 1)[-1]
            outs.append(content)
        return outs or [""]

class MistralAdapter(BaseGenerator):
    BASE_URL = "https://api.mistral.ai/v1/chat/completions"

    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.model = settings.MODEL
        if not self.api_key:
            raise RuntimeError("MISTRAL_API_KEY not set")

    def generate(
        self,
        prompt: str,
        n: int = 5,
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_tokens: int = 400
    ) -> List[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "messages": [
                {"role": "system", "content": "You are a query generator. Output only the final query."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
        }
        r = requests.post(self.BASE_URL, headers=headers, json=body, timeout=60)
        r.raise_for_status()
        data = r.json()
        outs: List[str] = []
        for c in data.get("choices", []):
            content = c.get("message", {}).get("content", "").strip()
            if content.startswith("```"):
                content = content.strip("`\n").split("\n", 1)[-1]
            outs.append(content)
        return outs or [""]

class LocalFlanAdapter(BaseGenerator):
    def __init__(self):
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        model_name = os.getenv("LOCAL_FLAN_MODEL", "google/flan-t5-base")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def generate(
        self,
        prompt: str,
        n: int = 5,
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_tokens: int = 400
    ) -> List[str]:
        inputs = self.tokenizer([prompt] * n, return_tensors="pt", truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            num_beams=max(n, 4),
            temperature=temperature,
            top_p=top_p,
            do_sample=temperature > 0
        )
        texts = [self.tokenizer.decode(o, skip_special_tokens=True) for o in outputs]
        return texts


def get_generator(provider: str) -> BaseGenerator:
    provider = provider.lower()
    if provider == "mixtral":
        # Prefer native Mistral if key is present; else fall back to OpenRouter
        if settings.MISTRAL_API_KEY:
            return MistralAdapter()
        return MixtralOpenRouterAdapter()
    if provider == "openrouter":
        return MixtralOpenRouterAdapter()
    elif provider == "mistral":
        return MistralAdapter()
    elif provider == "local_flan":
        return LocalFlanAdapter()
    else:
        raise RuntimeError(f"Unknown generator provider: {provider}")
