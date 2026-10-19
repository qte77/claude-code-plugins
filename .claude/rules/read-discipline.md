# Read Discipline

Read/edit hygiene for agent sessions. The read:edit and re-reading points echo the
token-waste patterns [CodeBurn][codeburn] surfaces — it is a usage tracker, not a
ruleset.

- **Know the blast radius before you touch it.** Before renaming or moving a file, or
  changing a heading, anchor or exported name, search for inbound links, references and
  imports so you don't break them. Link checkers and tests are the backstop, not the
  first line of defense.
- **Read enough, not more.** Understand what references a file, then stop — bulk-reading
  "to be safe" fights the 40–60% context target in `context-management.md`. Don't
  re-read a file you already hold; re-reading after a compaction is the exception.
- **Cite precisely.** In prompts — and especially in subagent briefs — name
  `<file>:<lines>`, never "the config doc." Scoped briefs keep fan-out subagents on task.
- **Verify subagent findings before acting.** Treat a subagent's "no coverage" /
  "file doesn't exist" / structural report as *advisory*. Before creating a file,
  deleting, or concluding absence, confirm with your own search + read. Calibrate by
  searching for a string you know exists. Record recurrences per `compound-learning.md`.

[codeburn]: https://github.com/getagentseal/codeburn#optimize
