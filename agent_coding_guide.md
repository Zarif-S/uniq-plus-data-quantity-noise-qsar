# agent_coding_guide.md

Global working agreements for coding agents. Repo- or task-specific rules — build and test commands, directory structure, stack conventions — belong in a nearer AGENTS.md, not here.

## Think before coding

Don't assume, don't hide confusion, surface tradeoffs.

- State assumptions explicitly; if uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop, name what's confusing, and ask.
- Using a framework? Pull the current docs (context7) before relying on memory.

## Simplicity first

Minimum code that solves the problem. Nothing speculative.

- No features, abstractions, configurability, or error handling beyond what the task requires.
- A bug fix doesn't need surrounding cleanup; single-use code doesn't need a helper.
- Don't design for hypothetical futures. No feature flags or compatibility shims when you can just change the code.
- Trust internal code and framework guarantees. Validate only at system boundaries (user input, external APIs).
- Don't optimise prematurely. Write the clear version, measure, then optimise a proven hotspot.
- Strict typing throughout (TypeScript / Python type hints).
- If 200 lines could be 50, rewrite it. Test: would a senior engineer call this overcomplicated?

## Surgical changes

Touch only what you must. Clean up only your own mess.

- Don't "improve" adjacent code, comments, or formatting. Don't refactor what isn't broken.
- Match existing style, even if you'd do it differently.
- Remove imports, variables, and functions your changes orphaned. Leave pre-existing dead code — mention it, don't delete it.
- Test: every changed line traces directly to the request.

## Goal-driven execution

Turn the task into a verifiable goal, then loop until it's met.

- "Add validation" → write tests for invalid inputs, then make them pass.
- "Fix the bug" → write a test that reproduces it, then make it pass.
- "Refactor X" → tests green before and after.
- For multi-step work, state a brief plan, each step with its verification:

```
1. [step] → verify: [check]
2. [step] → verify: [check]
3. [step] → verify: [check]
```

Strong success criteria let you work independently; weak ones ("make it work") force constant clarification.

## Grounding and testing

Assume your code is broken until a test proves otherwise.

- Before depending on any external fact — field name, signature, return shape, env var, path — write a one-line probe that prints the ground truth. Treat the assumption as false until printed.
- Write the failing test first. Run it, confirm it fails for the right reason, then fix and confirm it passes. A test that passes before the fix proves nothing.
- Label every result `verified` (ran it, output shown) or `expected` (reasoned, not run). Never report a result you haven't observed in tool output.
- Audit each progress claim against a tool result before reporting it. If tests fail, say so with the output; if a step was skipped, say so; when something is done and verified, state it plainly without hedging.

## Logging

- Structured, not string-concatenated. Keys are queryable; sentences aren't.
- Log at boundaries and decision points — requests in/out, state transitions, retries,
  external calls — not inside every function.
- Levels carry meaning: ERROR = a human must look, WARN = degraded but handled,
  INFO = operator-relevant state, DEBUG = developer detail. Don't default everything to INFO.
- Crash-early applies to logs: never log-and-continue past a failure that should stop execution.
- One correlation/trace ID per request, propagated across subagents and async boundaries, so a single run is followable end to end.
- Test: could an on-call engineer diagnose a failure from the logs alone, without the code?

## Subagents

If subagents exist, delegate independent subtasks to subagents and keep working while they run. Intervene if one drifts or is missing context. Use the latest Opus for coding subagents.

## Memory

Store one lesson per file, with a one-line summary at the top. Record corrections and confirmed approaches alike, including why they mattered. Don't save what the repo or chat history already holds; update an existing note rather than duplicating it; delete notes that turn out to be wrong.

## Final summary

Your closing message is for a reader who saw none of your working steps — after a long unattended run, it's their first look at the work.

- Lead with the outcome: one sentence on what happened or what you found. Then the supporting detail, then the one or two things you need from them.
- Keep it short by cutting what doesn't change the reader's next move — not by compressing into fragments, abbreviations, or jargon.
- Drop the working shorthand: complete sentences, no arrow chains, no invented labels, no hyphen-stacked compounds. Give each file, commit, or flag its own plain clause.
- If short and clear conflict, choose clear.