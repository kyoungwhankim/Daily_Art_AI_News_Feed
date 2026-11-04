#!/usr/bin/env python3
"""
Custom conversation launcher for Antigravity scheduled sidecars.
Replicates `agentapi new-conversation` while allowing explicit reasoning-effort
models such as `Gemini 3.8 Flash (High)` (MODEL_PLACEHOLDER_M318).
"""

import json
import os
import sys
import urllib.error
import urllib.request

MODEL_ALIASES = {
    "argon-high": "MODEL_PLACEHOLDER_M417",
    "gemini-4-argon-high": "MODEL_PLACEHOLDER_M417",
    "argon": "MODEL_PLACEHOLDER_M416",
    "gemini-4-argon-medium": "MODEL_PLACEHOLDER_M416",
    "flash-high": "MODEL_PLACEHOLDER_M318",
    "gemini-3.8-flash-high": "MODEL_PLACEHOLDER_M318",
    "flash": "MODEL_PLACEHOLDER_M319",
    "flash-medium": "MODEL_PLACEHOLDER_M319",
    "gemini-3.8-flash-medium": "MODEL_PLACEHOLDER_M319",
    "flash_lite": "MODEL_PLACEHOLDER_M320",
    "pro-high": "MODEL_PLACEHOLDER_M37",
    "gemini-3.1-pro-high": "MODEL_PLACEHOLDER_M37",
    "pro": "MODEL_PLACEHOLDER_M36",
    "pro-low": "MODEL_PLACEHOLDER_M36",
    "gemini-3.1-pro-low": "MODEL_PLACEHOLDER_M36",
}


def parse_args(argv):
    model = "MODEL_PLACEHOLDER_M318"  # Default: Gemini 3.8 Flash (High)
    title = ""
    profile = ""
    prompt_parts = []
    after_double_dash = False

    i = 0
    while i < len(argv):
        arg = argv[i]
        if after_double_dash:
            prompt_parts.append(arg)
        elif arg == "--":
            after_double_dash = True
        elif arg.startswith("--model="):
            raw = arg.split("=", 1)[1].strip()
            model = MODEL_ALIASES.get(raw.lower(), raw)
        elif arg == "--model" and i + 1 < len(argv):
            i += 1
            raw = argv[i].strip()
            model = MODEL_ALIASES.get(raw.lower(), raw)
        elif arg.startswith("--title="):
            title = arg.split("=", 1)[1]
        elif arg.startswith("--profile="):
            profile = arg.split("=", 1)[1]
        elif arg in ("new-conversation", "agentapi"):
            pass
        else:
            prompt_parts.append(arg)
        i += 1

    prompt = " ".join(prompt_parts).strip()
    return model, title, profile, prompt


def call_ls_rpc(ls_address, csrf_token, method, payload):
    url = f"http://{ls_address}/exa.language_server_pb.LanguageServerService/{method}"
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Connect-Protocol-Version": "1",
        "x-codeium-csrf-token": csrf_token,
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def main():
    model, title, profile, prompt = parse_args(sys.argv[1:])
    if not prompt:
        sys.stderr.write("Error: prompt is required\n")
        sys.exit(1)

    ls_address = os.environ.get("ANTIGRAVITY_LS_ADDRESS", "").strip()
    csrf_token = os.environ.get("ANTIGRAVITY_CSRF_TOKEN", "").strip()
    source_metadata_raw = os.environ.get("ANTIGRAVITY_SOURCE_METADATA", "").strip()
    project_id = os.environ.get("ANTIGRAVITY_PROJECT_ID", "").strip()

    if not ls_address or not csrf_token:
        sys.stderr.write(
            "Error: ANTIGRAVITY_LS_ADDRESS and ANTIGRAVITY_CSRF_TOKEN must be set\n"
        )
        sys.exit(1)

    source_metadata = None
    sidecar_id = ""
    if source_metadata_raw:
        try:
            source_metadata = json.loads(source_metadata_raw)
            sidecar_id = (
                source_metadata.get("sidecar", {}).get("sidecarId", "")
                if isinstance(source_metadata, dict)
                else ""
            )
        except Exception as e:
            sys.stderr.write(f"Warning: failed to parse ANTIGRAVITY_SOURCE_METADATA: {e}\n")

    try:
        start_req = {
            "source": "CORTEX_TRAJECTORY_SOURCE_AGENT_API",
            "trajectoryType": "CORTEX_TRAJECTORY_TYPE_CASCADE",
            "customAgentSpec": {
                "codingAgent": {
                    "googleMode": True,
                },
                "commandExecutionPolicy": "eager",
                "enforcedWorkspaceValidation": False,
                "cascadeConfig": {
                    "plannerConfig": {
                        "planModel": model,
                    }
                },
            },
        }
        if source_metadata:
            start_req["sourceMetadata"] = source_metadata
        if project_id:
            start_req["projectEnvConfig"] = {
                "projectId": project_id,
                "defaultProjectEnvironment": {},
            }
        if profile:
            start_req["activeProfile"] = profile

        start_resp = call_ls_rpc(ls_address, csrf_token, "StartCascade", start_req)
        cascade_id = start_resp.get("cascadeId", "")
        if not cascade_id:
            raise RuntimeError(f"StartCascade did not return cascadeId: {start_resp}")

        if title:
            call_ls_rpc(
                ls_address,
                csrf_token,
                "UpdateConversationAnnotations",
                {
                    "cascadeId": cascade_id,
                    "title": title,
                    "titleGenerationMethod": "TITLE_GENERATION_METHOD_AGENT_API",
                },
            )

        call_ls_rpc(
            ls_address,
            csrf_token,
            "SendUserCascadeMessage",
            {
                "cascadeId": cascade_id,
                "items": [{"text": prompt}],
            },
        )

        if sidecar_id:
            call_ls_rpc(
                ls_address,
                csrf_token,
                "RecordSidecarEvent",
                {
                    "sidecarId": sidecar_id,
                    "payload": {
                        "newConversation": {
                            "prompt": prompt,
                            "conversationId": cascade_id,
                        }
                    },
                },
            )

        output = {
            "response": {
                "newConversation": {
                    "prompt": prompt,
                    "conversationId": cascade_id,
                }
            }
        }
        print(json.dumps(output, ensure_ascii=False))

    except Exception as exc:
        err_msg = f"failed to start conversation: {exc}"
        if sidecar_id:
            try:
                call_ls_rpc(
                    ls_address,
                    csrf_token,
                    "RecordSidecarEvent",
                    {
                        "sidecarId": sidecar_id,
                        "error": err_msg,
                    },
                )
            except Exception:
                pass
        sys.stderr.write(err_msg + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
