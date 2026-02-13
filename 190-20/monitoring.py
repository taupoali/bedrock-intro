from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


class Monitoring:
    """
    Writes:
      - CloudWatch Logs (structured JSON)
      - CloudWatch custom metrics

    If DISABLE_CW=1 is set, monitoring becomes a no-op (useful for local debugging).
    """

    def __init__(self, region: str, log_group: str, log_stream: str, metric_namespace: str):
        self.region = region
        self.log_group = log_group
        self.log_stream = log_stream
        self.metric_namespace = metric_namespace

        self.disabled = os.environ.get("DISABLE_CW", "0") == "1"

        self._cfg = Config(
            read_timeout=30,
            connect_timeout=10,
            retries={"max_attempts": 3, "mode": "standard"},
        )

        self._logs = None
        self._cw = None
        self._sequence_token: Optional[str] = None

        if not self.disabled:
            self._logs = boto3.client("logs", region_name=self.region, config=self._cfg)
            self._cw = boto3.client("cloudwatch", region_name=self.region, config=self._cfg)
            self._ensure_log_group_and_stream()

    def _ensure_log_group_and_stream(self) -> None:
        assert self._logs is not None

        try:
            self._logs.create_log_group(logGroupName=self.log_group)
        except self._logs.exceptions.ResourceAlreadyExistsException:
            pass

        try:
            self._logs.create_log_stream(logGroupName=self.log_group, logStreamName=self.log_stream)
        except self._logs.exceptions.ResourceAlreadyExistsException:
            pass

        # Try to get sequence token if stream already exists
        try:
            resp = self._logs.describe_log_streams(
                logGroupName=self.log_group, logStreamNamePrefix=self.log_stream, limit=1
            )
            streams = resp.get("logStreams", [])
            if streams:
                self._sequence_token = streams[0].get("uploadSequenceToken")
        except ClientError:
            self._sequence_token = None

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def log_event(self, obj: Dict[str, Any]) -> None:
        if self.disabled:
            return
        assert self._logs is not None

        payload = dict(obj)
        payload.setdefault("ts", self._now_iso())

        event = {"timestamp": int(time.time() * 1000), "message": json.dumps(payload, ensure_ascii=False)}
        args = {
            "logGroupName": self.log_group,
            "logStreamName": self.log_stream,
            "logEvents": [event],
        }
        if self._sequence_token:
            args["sequenceToken"] = self._sequence_token

        try:
            resp = self._logs.put_log_events(**args)
            self._sequence_token = resp.get("nextSequenceToken")
        except self._logs.exceptions.InvalidSequenceTokenException:
            # Refresh token and retry once
            self._ensure_log_group_and_stream()
            args.pop("sequenceToken", None)
            if self._sequence_token:
                args["sequenceToken"] = self._sequence_token
            resp = self._logs.put_log_events(**args)
            self._sequence_token = resp.get("nextSequenceToken")

    # -------- Metrics helpers --------

    def _put_metric(self, metric_name: str, value: float, unit: str, dimensions: list[dict]) -> None:
        if self.disabled:
            return
        assert self._cw is not None
        self._cw.put_metric_data(
            Namespace=self.metric_namespace,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Value": float(value),
                    "Unit": unit,
                    "Dimensions": dimensions,
                }
            ],
        )

    def metric_request_total(self, model_id: str) -> None:
        dims = [{"Name": "ModelId", "Value": model_id}]
        self._put_metric("RequestsTotal", 1.0, "Count", dims)

    def metric_succeeded(self, model_id: str, latency_ms: float) -> None:
        dims = [{"Name": "ModelId", "Value": model_id}, {"Name": "Result", "Value": "Success"}]
        self._put_metric("RequestsSucceeded", 1.0, "Count", dims)
        self._put_metric("LatencyMs", latency_ms, "Milliseconds", dims)

    def metric_blocked(self, model_id: str, category: str, latency_ms: Optional[float] = None) -> None:
        dims = [
            {"Name": "ModelId", "Value": model_id},
            {"Name": "Result", "Value": "Blocked"},
            {"Name": "Category", "Value": category},
        ]
        self._put_metric("RequestsBlocked", 1.0, "Count", dims)
        if latency_ms is not None:
            self._put_metric("LatencyMs", latency_ms, "Milliseconds", dims)

    def metric_failed(self, model_id: str) -> None:
        dims = [{"Name": "ModelId", "Value": model_id}, {"Name": "Result", "Value": "Error"}]
        self._put_metric("RequestsFailed", 1.0, "Count", dims)
