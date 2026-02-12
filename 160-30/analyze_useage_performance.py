"""
Lab 7: Analyze usage and performance data from CloudWatch

This script queries the custom metrics emitted in Lab 6 and prints:
- Total requests, successes, blocks, failures in a time window
- Latency p50 / p90 / p99 (based on CloudWatch percentiles)

Run:
  export AWS_REGION=us-east-1
  export BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
  python lab7_analyze_usage_and_performance.py

Optional:
  export HOURS=24
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import boto3
from botocore.config import Config

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")
NAMESPACE = os.environ.get("CW_METRIC_NAMESPACE", "Bedrock/Labs")
HOURS = int(os.environ.get("HOURS", "24"))

BOTO_CONFIG = Config(
    read_timeout=60,
    connect_timeout=30,
    retries={"max_attempts": 3, "mode": "standard"},
)


def utc_now():
    return datetime.now(timezone.utc)


def query_metric_data(cw, start, end):
    """
    We query:
      - BedrockRequestsTotal (Sum)
      - BedrockRequestsSucceeded (Sum)
      - BedrockRequestsBlocked (Sum)
      - BedrockRequestsFailed (Sum)
      - BedrockLatencyMs (p50/p90/p99)
    All metrics include dimensions: ModelId=<MODEL_ID> and Result=<...>

    Note: Request totals are emitted with a Result dimension too (Success/Blocked/Error),
    so we sum across all Result values for "total".
    """
    period = 60  # 1 minute granularity

    def md(metric_name, stat, result_value=None, id_suffix=""):
        dims = [{"Name": "ModelId", "Value": MODEL_ID}]
        if result_value is not None:
            dims.append({"Name": "Result", "Value": result_value})

        return {
            "Id": f"{metric_name.lower()}{id_suffix}".replace("-", ""),
            "MetricStat": {
                "Metric": {
                    "Namespace": NAMESPACE,
                    "MetricName": metric_name,
                    "Dimensions": dims,
                },
                "Period": period,
                "Stat": stat,
            },
            "ReturnData": True,
        }

    queries = [
        # Totals: sum across the three Result values we emit
        md("BedrockRequestsTotal", "Sum", "Success", id_suffix="_succ"),
        md("BedrockRequestsTotal", "Sum", "Blocked", id_suffix="_bloc"),
        md("BedrockRequestsTotal", "Sum", "Error", id_suffix="_err"),

        md("BedrockRequestsSucceeded", "Sum", "Success", id_suffix="_succ"),
        md("BedrockRequestsBlocked", "Sum", "Blocked", id_suffix="_bloc"),
        md("BedrockRequestsFailed", "Sum", "Error", id_suffix="_err"),

        # Latency percentiles (use any one Result; Success is usually most useful)
        md("BedrockLatencyMs", "p50", "Success", id_suffix="_p50"),
        md("BedrockLatencyMs", "p90", "Success", id_suffix="_p90"),
        md("BedrockLatencyMs", "p99", "Success", id_suffix="_p99"),
    ]

    return cw.get_metric_data(
        MetricDataQueries=queries,
        StartTime=start,
        EndTime=end,
        ScanBy="TimestampAscending",
        MaxDatapoints=10000,
    )


def sum_values(metric_result):
    return sum(metric_result.get("Values", []) or [])


def last_value(metric_result):
    vals = metric_result.get("Values", []) or []
    return vals[-1] if vals else None


def main():
    cw = boto3.client("cloudwatch", region_name=AWS_REGION, config=BOTO_CONFIG)

    end = utc_now()
    start = end - timedelta(hours=HOURS)

    resp = query_metric_data(cw, start, end)
    results = {r["Id"]: r for r in resp.get("MetricDataResults", [])}

    # Totals
    total = (
        sum_values(results.get("bedrockrequeststotal_succ", {})) +
        sum_values(results.get("bedrockrequeststotal_bloc", {})) +
        sum_values(results.get("bedrockrequeststotal_err", {}))
    )
    succ = sum_values(results.get("bedrockrequestssucceeded_succ", {}))
    bloc = sum_values(results.get("bedrockrequestsblocked_bloc", {}))
    fail = sum_values(results.get("bedrockrequestsfailed_err", {}))

    # Latency (take the most recent percentile datapoint as a simple summary)
    p50 = last_value(results.get("bedrocklatencyms_p50", {}))
    p90 = last_value(results.get("bedrocklatencyms_p90", {}))
    p99 = last_value(results.get("bedrocklatencyms_p99", {}))

    print("\n=== Lab 7: Usage & Performance Analysis ===")
    print(f"Region     : {AWS_REGION}")
    print(f"Namespace  : {NAMESPACE}")
    print(f"ModelId    : {MODEL_ID}")
    print(f"Window     : last {HOURS} hour(s)")
    print(f"Start (UTC): {start.isoformat()}")
    print(f"End   (UTC): {end.isoformat()}")
    print()

    print("Request counts:")
    print(f"  Total     : {total:.0f}")
    print(f"  Succeeded : {succ:.0f}")
    print(f"  Blocked   : {bloc:.0f}")
    print(f"  Failed    : {fail:.0f}")

    if total > 0:
        print("\nRates:")
        print(f"  Success % : {(succ/total)*100:.1f}%")
        print(f"  Blocked % : {(bloc/total)*100:.1f}%")
        print(f"  Failed  % : {(fail/total)*100:.1f}%")

    print("\nLatency (ms) — latest percentiles from CloudWatch:")
    print(f"  p50 : {p50:.1f}" if p50 is not None else "  p50 : (no data yet)")
    print(f"  p90 : {p90:.1f}" if p90 is not None else "  p90 : (no data yet)")
    print(f"  p99 : {p99:.1f}" if p99 is not None else "  p99 : (no data yet)")

    print("\nTip: If you see '(no data yet)', run Lab 6 for a few minutes and try again.\n")


if __name__ == "__main__":
    main()
