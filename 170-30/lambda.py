import json
import urllib.parse
import urllib.request

SWAPI_BASE = "https://swapi.dev/api"

def _http_get(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "bedrock-agent-lab"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        status = resp.status
        body = resp.read().decode("utf-8")
        return status, json.loads(body)

def _get_param(parameters, name: str):
    for p in parameters or []:
        if p.get("name") == name:
            return p.get("value")
    return None

def lambda_handler(event, context):
    # Bedrock Agents -> Lambda input format when using an API schema:
    # includes: apiPath, httpMethod, parameters, inputText, actionGroup, etc. :contentReference[oaicite:5]{index=5}
    api_path = event.get("apiPath")
    http_method = (event.get("httpMethod") or "").upper()
    params = event.get("parameters", [])
    action_group = event.get("actionGroup", "swapi")

    try:
        if http_method != "GET":
            return _bedrock_response(action_group, api_path, http_method, 405, {"error": "Method not allowed"})

        # Operation 1: search people
        if api_path == "/people":
            search = _get_param(params, "search") or ""
            url = f"{SWAPI_BASE}/people/?{urllib.parse.urlencode({'search': search})}"
            status, data = _http_get(url)

            # Return a trimmed response to keep tokens down
            results = []
            for item in (data.get("results") or [])[:5]:
                results.append({
                    "name": item.get("name"),
                    "birth_year": item.get("birth_year"),
                    "gender": item.get("gender"),
                    "url": item.get("url"),
                })

            return _bedrock_response(action_group, api_path, http_method, status, {"count": data.get("count"), "results": results})

        # Operation 2: get person by id
        if api_path == "/people/{id}":
            pid = _get_param(params, "id")
            if not pid:
                return _bedrock_response(action_group, api_path, http_method, 400, {"error": "Missing required parameter: id"})
            url = f"{SWAPI_BASE}/people/{pid}/"
            status, data = _http_get(url)

            # Trim response
            trimmed = {
                "name": data.get("name"),
                "height": data.get("height"),
                "mass": data.get("mass"),
                "hair_color": data.get("hair_color"),
                "skin_color": data.get("skin_color"),
                "eye_color": data.get("eye_color"),
                "birth_year": data.get("birth_year"),
                "gender": data.get("gender"),
            }
            return _bedrock_response(action_group, api_path, http_method, status, trimmed)

        return _bedrock_response(action_group, api_path, http_method, 404, {"error": f"Unknown apiPath: {api_path}"})

    except Exception as e:
        return _bedrock_response(action_group, api_path or "", http_method or "", 500, {"error": str(e)})

def _bedrock_response(action_group: str, api_path: str, http_method: str, status_code: int, body_obj: dict):
    # Bedrock expects this response envelope for API-schema action groups :contentReference[oaicite:6]{index=6}
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action_group,
            "apiPath": api_path,
            "httpMethod": http_method,
            "httpStatusCode": int(status_code),
            "responseBody": {
                "application/json": {
                    "body": json.dumps(body_obj)
                }
            }
        }
    }
