from __future__ import annotations

import httpx

from app.workflow.context import ExecutionContext, NodeResult
from app.workflow.dsl import WorkflowNodeDSL
from app.workflow.nodes.base import NodeHandler


class HttpRequestHandler(NodeHandler):
    def execute(self, node: WorkflowNodeDSL, ctx: ExecutionContext) -> NodeResult:
        data = self.resolve_input(node, ctx)
        cfg = data["config"]
        method = str(cfg.get("method", "GET")).upper()
        url = cfg.get("url")
        if not url:
            return NodeResult(status="failed", error="http_request node requires config.url")
        headers = dict(cfg.get("headers") or {})
        credential_id = cfg.get("credential_id")
        if credential_id and credential_id in ctx.credentials:
            secret = ctx.credentials[credential_id]
            if secret.get("header_name"):
                headers[str(secret["header_name"])] = str(secret.get("header_value") or secret.get("api_key") or "")
            elif secret.get("api_key"):
                headers["Authorization"] = f"Bearer {secret['api_key']}"
        timeout = float(cfg.get("timeout_seconds") or 30)
        body = cfg.get("body")
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                response = client.request(method, url, headers=headers, json=body if isinstance(body, (dict, list)) else None)
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                parsed: object
                try:
                    parsed = response.json()
                except Exception:
                    parsed = response.text
            else:
                parsed = response.text
            ok = 200 <= response.status_code < 400
            output = {
                "status_code": response.status_code,
                "body": parsed,
                "headers": dict(response.headers),
                "ok": ok,
            }
            if not ok and cfg.get("fail_on_http_error", True):
                return NodeResult(
                    status="failed",
                    output=output,
                    error=f"HTTP {response.status_code} from {url}",
                    logs=[f"{method} {url} -> {response.status_code}"],
                )
            return NodeResult(status="completed", output=output, logs=[f"{method} {url} -> {response.status_code}"])
        except httpx.HTTPError as exc:
            return NodeResult(status="failed", error=str(exc), logs=[f"{method} {url} failed"])
