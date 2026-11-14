# Agent board

A Claude Code mod: a live side panel listing every helper agent Claude starts,
with its role (Designer, Developer, Reviewer, Tester, Researcher, Planner,
Writer), a progress bar, what it is doing right now and its last few steps.

It makes no model calls, so it uses no tokens. Progress is exact when an agent
keeps a to-do list and an estimate ("about 40%") otherwise; roles are guessed
from keywords in the agent's type and task.

Claude Code loads it from this folder in sessions on this repository. Open the
panel with `/agent-board` if it is not showing.
