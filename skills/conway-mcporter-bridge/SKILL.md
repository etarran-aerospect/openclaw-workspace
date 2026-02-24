---
name: conway-mcporter-bridge
description: Use Conway MCP tools (conway-terminal) from OpenClaw via mcporter and the conway-mcp wrapper. Use when the user asks to run Conway actions like sandbox_create, sandbox_list, sandbox_exec, sandbox_write_file, credits_balance, or any Conway MCP tool call, especially when OpenClaw config does not support mcpServers.
---

Use Conway through the local wrapper CLI:

- Wrapper: `~/.local/bin/conway-mcp`
- mcporter config: `~/.mcporter/mcporter.json`
- Server name: `conway`

## Fast path

List tools/schemas:

```bash
conway-mcp list --schema
```

Call a tool:

```bash
conway-mcp call <tool_name> key=value key2=value2 --output json
```

Examples:

```bash
conway-mcp call credits_balance --output json
conway-mcp call sandbox_list --output json
conway-mcp call sandbox_create name=mybox region=us-east --output json
conway-mcp call sandbox_exec sandbox_id=<id> command='echo hello' --output json
conway-mcp call sandbox_write_file sandbox_id=<id> path=/root/hello.txt content='hi' --output json
```

## Notes

- Prefer `--output json` for machine-readable results.
- If shell quoting is annoying, use the helper script `scripts/conway_call.sh`.
- Secrets: Conway API key is stored locally in `~/.conway/config.json` and referenced by mcporter; do not print it.
