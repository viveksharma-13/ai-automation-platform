from __future__ import annotations

from openai import OpenAI

from app.workflow.context import ExecutionContext, NodeResult
from app.workflow.dsl import WorkflowNodeDSL
from app.workflow.nodes.base import NodeHandler


class LlmHandler(NodeHandler):
    def execute(self, node: WorkflowNodeDSL, ctx: ExecutionContext) -> NodeResult:
        data = self.resolve_input(node, ctx)
        cfg = data["config"]
        prompt = cfg.get("prompt")
        if not prompt:
            return NodeResult(status="failed", error="llm node requires config.prompt")

        api_key = ctx.openai_api_key
        credential_id = cfg.get("credential_id")
        if credential_id and credential_id in ctx.credentials:
            api_key = ctx.credentials[credential_id].get("api_key") or api_key
        if not api_key:
            return NodeResult(
                status="failed",
                error="No OpenAI API key configured (OPENAI_API_KEY or credential_id)",
            )

        model = cfg.get("model") or ctx.openai_default_model
        temperature = float(cfg.get("temperature") if cfg.get("temperature") is not None else 0.2)
        system = cfg.get("system") or "You are a helpful automation assistant."

        try:
            client = OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": str(prompt)},
                ],
            )
            text = completion.choices[0].message.content or ""
            usage = completion.usage
            return NodeResult(
                status="completed",
                output={
                    "text": text,
                    "model": model,
                    "usage": {
                        "prompt_tokens": getattr(usage, "prompt_tokens", None),
                        "completion_tokens": getattr(usage, "completion_tokens", None),
                    },
                },
                logs=[f"LLM {model} completed"],
            )
        except Exception as exc:  # noqa: BLE001
            return NodeResult(status="failed", error=str(exc), logs=["LLM call failed"])
