import os
from typing import List, Mapping

import requests


QWEN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"


def call_qwen(
    messages: List[Mapping[str, str]],
    model: str = "qwen-plus",
    temperature: float = 0.7,
    timeout: int = 60,
) -> str:
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("未设置 DASHSCOPE_API_KEY 环境变量。")

    response = requests.post(
        QWEN_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
