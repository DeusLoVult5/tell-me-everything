# TELL-ME-EVERYTHING / 告诉我一切

English | [中文](README_CN.md)

> **WTF.** You're still feeding AI one-liners and praying?
>
> Open Claude Code. "Build me an expense tracker." Boom — 800 lines. Looks solid. Tomorrow's the deadline, so you hit run without thinking twice. Crash. Debug till 2 AM. Crash again. Sun's up, nothing works, and you're one bad decision away from rage-quitting programming altogether.
>
> It's not the AI. You handed it a single vague sentence and made it guess a hundred decisions — tech stack, architecture, coding style, testing, deployment. It nailed three. Whiffed ninety-seven. Then confidently baked all ninety-seven screw-ups into 800 lines of code. The crash wasn't a bug. It was inevitable.
>
> And that's just the warm-up. Even after you brute-force the first version into something that kinda runs, the AI forgets every rule you set the moment the conversation stretches long. You said "ask me before touching anything." Context compresses. Poof. You say "add an export button." It silently rewrites five files, pulls in some random library you've never heard of, and you don't find out until it's way too late for `git revert` to save you.
>
> The real problem isn't your prompting. You know exactly what you want — you just didn't realize the AI knows nothing until you spell it out. What's missing is a layer that grabs the AI by the collar every single time it's about to touch a file and says: *hold up. ask first.* Not once. Every. Single. Time.
>
> **TELL-ME-EVERYTHING** is that layer. It sits between you and the AI — a translation layer made of multiple-choice questions. You click, done. No typing required. Tech stack, architecture, coding conventions, security boundaries — all the stuff you forgot to mention because you assumed the AI just knew. It spits out a CLAUDE.md that the AI reads at the start of every session. And it doesn't go to sleep after the first release — scale gates on new features, security checks on deploy, mandatory review prompts, logs that block the next step until they're written. Rules live in files. Files don't forget.

---

## What It Does

**TELL-ME-EVERYTHING** puts a translation layer between you and the AI. During setup, it fires multiple-choice questions — tech stack, architecture, coding style, security boundaries. You click, done. No typing. It generates a CLAUDE.md that the AI reads at the start of every session, so it stops guessing what you want. And it doesn't clock out after v1.0 — new features go through scale gates, deploys trigger security checks, code changes require review, and the session can't wrap until the change log is written. Every gate is backed by a file on disk. Context compresses. Files don't.

## Why Use It

Give an AI a one-liner and it'll guess a hundred decisions. Most of them wrong. Get the first version limping along and it seems fine — until the conversation grows long, the context window stretches, and every rule you set evaporates. The AI slides right back into guessing mode. This isn't a skill issue on your end. It's a missing structural layer — something that stops the AI before every write and forces the conversation that should have happened first. Not a one-time reminder. A gate. Rules written to disk, checked every time, immune to context drift. That's the difference between "why does this keep breaking" and "oh, that's exactly what I wanted."

---

## How It Works

```
You: "build me an expense tracker"
  ↓
Skill fires multiple-choice: privacy? tech stack? architecture? coding style? testing? deploy?
  ↓
You click through (no typing). Skill generates CLAUDE.md ← AI reads it every session
  ↓
AI no longer gets a vague one-liner — it gets structured input you confirmed
  ↓
Less guessing. More nailing it.
```

**Doesn't clock out after v1.0.** New features, bug fixes, deploys — gates stay up:

| Phase | Gate |
|------|------|
| Before touching code | Scale assessment (one-line tweak or a whole new module?) → you confirm |
| Writing code | AI operates within confirmed boundaries |
| After writing | Auto-prompted review → change log must be written before switching back to "discuss mode" |
| Anytime | AI nudges "ready to start?" and gets shut down twice → locked. Can't ask again |

---

## Install

```bash
git clone https://github.com/DeusLoVult5/tell-me-everything.git \
  ~/.claude/skills/tell-me-everything
```

---

## Triggers

- **New project**: open Claude Code in an empty directory → auto-trigger
- **Manual**: type `/tell-me-everything`
- **Vague request**: your first prompt is too thin → auto-loads
- **Release / open-source**: you say "ship it" / "release" → loads security checklist

---

## Design

| Mechanism | What It Solves |
|-----------|---------------|
| **15-dimension tiered interview** | S-tier (security/privacy/paths) gets asked no matter what. A-tier (tech stack/architecture) asked once. B-tier (style/logging) asked once, skipped if you don't care |
| **43 default parameters** | Coding style, log format, version control... defaults handle the boring stuff, you override anytime |
| **Hybrid state gate** | Signal words control the gate — "implement" = go, "go ahead" = pop a confirmation, "hold up" = stay in discuss mode. No guessing |
| **Anti-push counter** | AI nudges "ready to start?" and gets rejected twice → locked out of asking. You say the signal word to unlock |
| **Decision atomicity** | One question per popup. "What to do" and "who does it" are two separate questions |
| **Log hard gate** | Can't flip IMPLEMENT→PLAN without writing the change log. AI can forget. CLAUDE.md won't. Next session catches it |
| **Maintain / extend / release** | v1.0 isn't the finish line. New features go through scale gates, deploys go through security checks |
| **Implicit signal reading** | Doesn't ask "did I do a good job?" Reads direction from your behavior instead |
| **Hook hardening** | Not relying on AI self-discipline. Platform-level PreToolUse hooks — no scale declaration, no file writes. Writes outside project directory get blocked |

---

## Acknowledgments

Design inspired by [Codex Startup Pressure Test Skill](https://github.com/Kappaemme-git/codex-startup-pressure-test-skill) (template paradigm / Modes pattern) and [World-Model Method](https://github.com/Renhuai123/world-model-method) (path comparison / render-separate-from-plan / self-check loop).

## License

MIT

## Updates

[CHANGELOG.md](CHANGELOG.md)
