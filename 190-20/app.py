from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Dict, Tuple

from flask import Flask, render_template, request

from bedrock_client import BedrockTextClient
from filters import check_input, check_output, fallback_message
from monitoring import Monitoring
from prompts import build_prompt

APP_ROOT = Path(__file__).parent
DOCS_DIR = APP_ROOT / "docs"

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")

# App logging/metrics destinations
LOG_GROUP = os.environ.get("CW_LOG_GROUP", "/bedrock/labs/support-assistant")
LOG_STREAM = os.environ.get("CW_LOG_STREAM", "webapp")
METRIC_NAMESPACE = os.environ.get("CW_METRIC_NAMESPACE", "Bedrock/Labs")

# Whether to show block categories in the UI (useful for learning)
SHOW_DEBUG = os.environ.get("SHOW_DEBUG", "1") == "1"


app = Flask(__name__)

bedrock = BedrockTextClient(region=AWS_REGION, model_id=MODEL_ID)
mon = Monitoring(
    region=AWS_REGION,
    log_group=LOG_GROUP,
    log_stream=LOG_STREAM,
    metric_namespace=METRIC_NAMESPACE,
)


def load_docs(docs_dir: Path) -> Dict[str, str]:
    """
    Loads all .txt files from docs_dir and returns {filename: content}.
    """
    docs: Dict[str, str] = {}
    for p in sorted(docs_dir.glob("*.txt")):
        docs[p.name] = p.read_text(encoding="utf-8")
    return docs


@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    category = ""
    reason = ""
    blocked = False
    used_sources = []

    user_question = ""
    if request.method == "POST":
        user_question = (request.form.get("question") or "").strip()

        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        # Metric: total requests seen by the app
        mon.metric_request_total(model_id=MODEL_ID)

        # 1) Input filtering
        in_res = check_input(user_question)
        if not in_res.allowed:
            blocked = True
            category = in_res.category
            reason = in_res.reason
            answer = fallback_message(category)

            mon.log_event(
                {
                    "request_id": request_id,
                    "stage": "input_filter",
                    "allowed": False,
                    "category": category,
                    "reason": reason,
                    "question_preview": user_question[:250],
                    "model_id": MODEL_ID,
                }
            )
            mon.metric_blocked(model_id=MODEL_ID, category=category)

            return render_template(
                "index.html",
                question=user_question,
                answer=answer,
                blocked=blocked,
                category=(category if SHOW_DEBUG else ""),
                reason=(reason if SHOW_DEBUG else ""),
                sources=[],
            )

        # 2) Load docs and build grounded prompt
        docs = load_docs(DOCS_DIR)
        used_sources = list(docs.keys())

        prompt = build_prompt(docs=docs, user_question=user_question)

        # 3) Call Bedrock
        try:
            model_text = bedrock.generate(prompt, max_tokens=350)
            latency_ms = (time.perf_counter() - start) * 1000.0
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000.0
            blocked = True
            category = "error"
            reason = "Model invocation failed"
            answer = "Sorry — I couldn’t generate a response right now. Please try again."

            mon.log_event(
                {
                    "request_id": request_id,
                    "stage": "model_call",
                    "result": "Error",
                    "error": str(e),
                    "latency_ms": round(latency_ms, 2),
                    "question_preview": user_question[:250],
                    "model_id": MODEL_ID,
                }
            )
            mon.metric_failed(model_id=MODEL_ID)

            return render_template(
                "index.html",
                question=user_question,
                answer=answer,
                blocked=blocked,
                category=(category if SHOW_DEBUG else ""),
                reason=(reason if SHOW_DEBUG else ""),
                sources=[],
            )

        # 4) Output filtering
        out_res = check_output(model_text)
        if not out_res.allowed:
            blocked = True
            category = "output_unsafe"
            reason = out_res.reason
            answer = fallback_message(category)

            mon.log_event(
                {
                    "request_id": request_id,
                    "stage": "output_filter",
                    "result": "BlockedOutput",
                    "category": out_res.category,
                    "reason": out_res.reason,
                    "latency_ms": round(latency_ms, 2),
                    "question_preview": user_question[:250],
                    "response_preview": model_text[:250],
                    "model_id": MODEL_ID,
                }
            )
            mon.metric_blocked(model_id=MODEL_ID, category="output_unsafe", latency_ms=latency_ms)

            return render_template(
                "index.html",
                question=user_question,
                answer=answer,
                blocked=blocked,
                category=(category if SHOW_DEBUG else ""),
                reason=(reason if SHOW_DEBUG else ""),
                sources=[],
            )

        # 5) Success
        answer = model_text
        mon.log_event(
            {
                "request_id": request_id,
                "stage": "success",
                "result": "Success",
                "latency_ms": round(latency_ms, 2),
                "question_preview": user_question[:250],
                "response_preview": model_text[:250],
                "model_id": MODEL_ID,
            }
        )
        mon.metric_succeeded(model_id=MODEL_ID, latency_ms=latency_ms)

    return render_template(
        "index.html",
        question=user_question,
        answer=answer,
        blocked=blocked,
        category=(category if SHOW_DEBUG else ""),
        reason=(reason if SHOW_DEBUG else ""),
        sources=used_sources,
    )


if __name__ == "__main__":
    # TODO (learner): If port 5000 is in use, change it (e.g., 8080)
    app.run(host="0.0.0.0", port=5000, debug=True)
