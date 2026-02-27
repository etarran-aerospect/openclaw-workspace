# INBOX.md

Purpose: ChatGPT seat drops first-pass outputs here for Claw to process.

## Handoff Template (copy/paste this every time)

### META
- request_id: YYYYMMDD-###
- project: 
- owner: Ethan
- created_at: ISO-8601
- priority: low|normal|high
- due_by: ISO-8601 or null

### OBJECTIVE
(1-3 sentences: what success looks like)

### INPUTS
- links:
- files:
- constraints:
- assumptions:

### OUTPUT_REQUESTED
- deliverable_type: (copy|spec|plan|code-outline|qa-checklist|other)
- format: (markdown|json|bullets)
- audience: (internal|client)

### DRAFT_OUTPUT
(Your first-pass result)

### STRUCTURED_BLOCK_JSON
```json
{
  "request_id": "",
  "project": "",
  "tasks": [
    {"id": "T1", "title": "", "owner": "Claw|Ethan|ChatGPT", "status": "todo", "notes": ""}
  ],
  "artifacts": [
    {"name": "", "type": "doc|code|asset|other", "path_or_link": ""}
  ],
  "acceptance_criteria": [""],
  "risks": [""],
  "open_questions": [""]
}
```

### READY_FOR_CLAW
- [ ] Yes, execute now
- [ ] Needs Ethan review first
