---
name: "learning-day-closeout"
description: "Closes out a learning day by updating logs, summaries, README, handoff, and GitHub sync. Invoke when the user wants to finish today's learning session cleanly."
---

# Learning Day Closeout

## Purpose
Use this skill at the end of a learning / project day to avoid repeating the same closing conversation every time.

This skill standardizes the day-end workflow for the `AI产品转型学习系统` workspace.

## When To Invoke
Invoke this skill when:
- the user says they want to wrap up today's work
- the user wants to sync today's progress to GitHub
- the user asks to update README / handoff / learning logs together
- the user wants a clean end-of-day summary and artifact update

Do not invoke it for small one-off edits that do not represent a day closeout.

## Scope
This skill is responsible for checking and updating:
- daily learning card
- daily honor wall
- daily learning / run log
- discussion summary or key takeaways if the day contained important concept shifts
- relevant README / handoff / asset list entries
- GitHub sync on the active branch after confirming there are no unexpected unrelated changes

## Closeout Checklist
1. Confirm today's actual output
- What was learned
- What was built
- What was evaluated
- What changed in the user's understanding

2. Update learning artifacts
- `03-学习成果/DayXX-学习卡.md`
- `03-学习成果/DayXX-荣誉墙.md`
- `03-学习成果/DayXX-学习与跑分日志.md` if relevant
- Add a discussion summary if the day included meaningful corrections or concept shifts

3. Update shared project entry files
- `AI产品转型学习系统/README.md`
- `04-接力说明/00-当前进度与接力说明.md`
- `01-学习原始材料/00-全量资产清单.md` if new files were added
- `02-学习计划/01-计划变更记录.md` if the plan or methodology changed

4. Verify code / docs consistency
- If code changed, verify the changed flow still matches the docs
- If evaluation changed, record model, dataset, metrics, and interpretation

5. Git safety check
- Inspect git status
- Do not include unrelated untracked files without explicit user confirmation
- Stop and ask the user if unexpected changes appear

6. Commit and push
- Use a concise commit message that reflects the day’s real output
- Push to the active learning branch

## Output Style
When reporting completion to the user:
- summarize what was updated
- list the main files
- state whether GitHub sync is done
- state any remaining risks / next steps

## Notes For This Workspace
- Keep the explanation simple and PM-facing
- Prefer preserving the current small-card learning mode
- When the day includes architecture or methodology correction, record the correction explicitly as part of the learning output
