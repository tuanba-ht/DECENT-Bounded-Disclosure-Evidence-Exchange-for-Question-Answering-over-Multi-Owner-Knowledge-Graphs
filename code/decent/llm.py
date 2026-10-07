"""Local LLM backend for the agent roles (parser, verbaliser).

One process holds one model; every role shares the same weights and decoding
parameters so that arms differ only in the protocol, never in the model.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

# Model weights are read from DECENT_MODEL_DIR if set, otherwise from ./models.
_MODEL_DIR = os.environ.get("DECENT_MODEL_DIR", "models")
DEFAULT_MODEL = os.path.join(_MODEL_DIR, "qwen3-8b")


@dataclass
class LLMConfig:
    model_path: str = DEFAULT_MODEL
    load_in_4bit: bool = True
    max_new_tokens: int = 96
    temperature: float = 0.0
    batch_size: int = 16
    seed: int = 0


class LocalLLM:
    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig()
        self._model = None
        self._tokenizer = None

    def _ensure(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
        kwargs: dict[str, Any] = {"dtype": torch.bfloat16, "device_map": "cuda:0"}
        if self.config.load_in_4bit:
            from transformers import BitsAndBytesConfig

            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
        self._tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token
        self._tokenizer.padding_side = "left"
        self._model = AutoModelForCausalLM.from_pretrained(self.config.model_path, **kwargs)
        self._model.eval()

    def chat_counted(
        self, prompts: list[str], system: str | None = None, max_new_tokens: int | None = None
    ) -> tuple[list[str], list[int]]:
        """Like chat(), but also returns the number of generated tokens per prompt.

        Tokens are counted after stripping padding, so a short answer in a padded batch
        is not charged for the longest sequence in the batch.
        """
        import torch

        self._ensure()
        outputs: list[str] = []
        counts: list[int] = []
        limit = max_new_tokens or self.config.max_new_tokens
        pad_id = self._tokenizer.pad_token_id
        eos_id = self._tokenizer.eos_token_id
        for start in range(0, len(prompts), self.config.batch_size):
            chunk = prompts[start : start + self.config.batch_size]
            texts = [
                self._tokenizer.apply_chat_template(
                    ([{"role": "system", "content": system}] if system else [])
                    + [{"role": "user", "content": prompt}],
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                )
                for prompt in chunk
            ]
            batch = self._tokenizer(texts, return_tensors="pt", padding=True).to(self._model.device)
            with torch.no_grad():
                generated = self._model.generate(
                    **batch,
                    max_new_tokens=limit,
                    do_sample=self.config.temperature > 0,
                    temperature=self.config.temperature if self.config.temperature > 0 else None,
                    pad_token_id=pad_id,
                )
            prompt_len = batch["input_ids"].shape[1]
            for row in generated:
                new_tokens = row[prompt_len:]
                kept = [int(t) for t in new_tokens if int(t) not in (pad_id, eos_id)]
                counts.append(len(kept))
                outputs.append(self._tokenizer.decode(new_tokens, skip_special_tokens=True).strip())
        return outputs, counts

    def chat(self, prompts: list[str], system: str | None = None) -> list[str]:
        import torch

        self._ensure()
        outputs: list[str] = []
        for start in range(0, len(prompts), self.config.batch_size):
            chunk = prompts[start : start + self.config.batch_size]
            texts = [
                self._tokenizer.apply_chat_template(
                    ([{"role": "system", "content": system}] if system else [])
                    + [{"role": "user", "content": prompt}],
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                )
                for prompt in chunk
            ]
            batch = self._tokenizer(texts, return_tensors="pt", padding=True).to(self._model.device)
            with torch.no_grad():
                generated = self._model.generate(
                    **batch,
                    max_new_tokens=self.config.max_new_tokens,
                    do_sample=self.config.temperature > 0,
                    temperature=self.config.temperature if self.config.temperature > 0 else None,
                    pad_token_id=self._tokenizer.pad_token_id,
                )
            for index in range(len(chunk)):
                new_tokens = generated[index][batch["input_ids"].shape[1] :]
                outputs.append(self._tokenizer.decode(new_tokens, skip_special_tokens=True).strip())
        return outputs
