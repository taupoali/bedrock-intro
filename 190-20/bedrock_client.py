from __future__ import annotations

import os
import boto3
from botocore.config import Config


class BedrockTextClient:
    """
    Minimal Bedrock text client using the Converse API.
    Note: IAM commonly uses bedrock:InvokeModel even when you call Converse.
    """

    def __init__(self, region: str, model_id: str):
        self.region = region
        self.model_id = model_id

        # Nova can require longer timeouts
        self._config = Config(
            read_timeout=3600,
            connect_timeout=60,
            retries={"max_attempts": 3, "mode": "standard"},
        )

        self._client = boto3.client("bedrock-runtime", region_name=self.region, config=self._config)

    def generate(self, prompt: str, max_tokens: int = 350) -> str:
        resp = self._client.converse(
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": int(max_tokens), "temperature": 0.2},
        )

        parts = resp["output"]["message"].get("content", [])
        return "\n".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
