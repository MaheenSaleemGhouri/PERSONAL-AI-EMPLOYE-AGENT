---
skill_name: file-processor
version: 1.0
tier: bronze
trigger: When a FILE_*.md file appears in /Needs_Action/
---

# Skill: File Processor

## Purpose
Process files dropped into the /Inbox/ folder.

## Input
A metadata file named `FILE_*.md` in `/Needs_Action/`.

## Steps
1. Read the metadata file (original_name, size, received)
2. Determine file type from extension
3. Create a summary in `/Plans/FILE_SUMMARY_<name>.md`
4. Update Dashboard.md with: "File received: <name>"
5. Move the metadata file to /Done/

## Output Files
- `/Plans/FILE_SUMMARY_<name>.md` — What Claude thinks this file is about
- `/Done/FILE_<name>.md` — Archived metadata

## Supported File Types
- `.pdf` — Summarize if readable, tag as "document"
- `.csv` — Note column headers, row count, tag as "data"
- `.txt` — Summarize content, tag as "text"
- `.jpg/.png` — Note filename, tag as "image"
- Other — Tag as "unknown", log for human review
