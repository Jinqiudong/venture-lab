"""Run one agent role with the Claude Code CLI in print mode.

Mirrors the openai/codex-action contract used by the workflows: a prompt file,
a permission profile, an optional JSON Schema plus output file, and a
`final-message` step output.
"""

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

CLI_PACKAGE = "@anthropic-ai/claude-code"

# Inspect-only roles may read the checkout and run read-only git commands.
READ_ONLY_TOOLS = [
    "Read",
    "Grep",
    "Glob",
    "Bash(git diff:*)",
    "Bash(git log:*)",
    "Bash(git show:*)",
    "Bash(git status:*)",
    "Bash(ls:*)",
    "Bash(cat:*)",
]

# Research roles (Product Brain) may also search and read the public web, but still edit nothing.
RESEARCH_TOOLS = [*READ_ONLY_TOOLS, "WebSearch", "WebFetch"]

# Editing roles get the full workspace, but publishing stays with the workflow.
WORKSPACE_DISALLOWED_TOOLS = ["Bash(git push:*)", "Bash(gh:*)"]


def fail(message: str) -> None:
    print(f"::error::{message}", file=sys.stderr)
    sys.exit(1)


def set_output(name: str, value: str) -> None:
    delimiter = f"EOF_{uuid.uuid4().hex}"
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
        fh.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


def build_command(prompt: str, profile: str, schema: str, effort: str) -> list[str]:
    cmd = ["npx", "-y", CLI_PACKAGE, "-p", prompt, "--output-format", "json"]
    if profile == ":read-only":
        cmd += ["--permission-mode", "default", "--allowedTools", *READ_ONLY_TOOLS]
    elif profile == ":research":
        cmd += ["--permission-mode", "default", "--allowedTools", *RESEARCH_TOOLS]
    elif profile == ":workspace":
        cmd += ["--permission-mode", "bypassPermissions", "--disallowedTools", *WORKSPACE_DISALLOWED_TOOLS]
    else:
        fail(f"Unsupported permission-profile: {profile!r}")
    if schema:
        cmd += ["--json-schema", schema]
    if effort:
        cmd += ["--effort", effort]
    return cmd


def normalize_secret(name: str) -> None:
    # Long tokens copied from a wrapped terminal often pick up line breaks or spaces.
    value = "".join(os.environ.get(name, "").split())
    if value:
        os.environ[name] = value
    else:
        os.environ.pop(name, None)


def main() -> None:
    normalize_secret("CLAUDE_CODE_OAUTH_TOKEN")
    normalize_secret("ANTHROPIC_API_KEY")
    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            fail("Neither CLAUDE_CODE_OAUTH_TOKEN nor ANTHROPIC_API_KEY is configured.")

    workspace = Path(os.environ["GITHUB_WORKSPACE"])
    prompt = (workspace / os.environ["PROMPT_FILE"]).read_text(encoding="utf-8")
    schema_file = os.environ.get("SCHEMA_FILE", "")
    schema = Path(schema_file).read_text(encoding="utf-8") if schema_file else ""
    output_file = os.environ.get("OUTPUT_FILE", "")
    if output_file and not schema:
        fail("output-file requires output-schema-file.")

    cmd = build_command(prompt, os.environ["PERMISSION_PROFILE"], schema, os.environ.get("EFFORT", ""))
    proc = subprocess.run(cmd, cwd=workspace / os.environ["AGENT_DIR"], capture_output=True, text=True)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print(proc.stdout)
        fail(f"Claude Code did not return JSON (exit {proc.returncode}).")

    final_message = result.get("result") or ""
    print(final_message)
    if result.get("is_error") or proc.returncode != 0:
        fail(f"Claude Code failed (exit {proc.returncode}): {final_message or result.get('subtype', 'unknown error')}")

    if output_file:
        structured = result.get("structured_output")
        if structured is None:
            fail("Claude Code returned no structured output for the requested schema.")
        Path(output_file).write_text(json.dumps(structured, ensure_ascii=False), encoding="utf-8")
        final_message = final_message or json.dumps(structured, ensure_ascii=False)

    set_output("final-message", final_message)


if __name__ == "__main__":
    main()
