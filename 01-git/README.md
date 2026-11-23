# 01 · Git workflow

> Slide 26: https://gist.github.com/bdallard/8bdbdd70f234f94823c0c2cde9515388

The full exercise (Parts 1–11 with every command, its real output and the reflection questions) is in its own repo, as the exercise asks:
**https://github.com/mathislepoutre1/bash-installer** (see `ANSWERS.md`).

`install.sh` here is the script built on the `feature-install` branch in that exercise.

## Commands I used the most

| Goal | Command |
|---|---|
| Set identity | `git config --global user.name "..."` / `user.email "..."` |
| New repo | `git init` |
| What changed? | `git status`, `git diff` |
| Save a snapshot | `git add <file>` then `git commit -m "message"` |
| History | `git log --oneline --graph` |
| Branches | `git branch`, `git switch -c feature-x`, `git switch main` |
| Merge | `git merge feature-x`, then `git branch -d feature-x` |
| GitHub | `git remote add origin <url>`, `git push -u origin main`, `git clone <url>` |

## How this repo is organised in Git

Each exercise folder was built on its own `feat/...` branch and merged into `main` with `git merge --no-ff`, so each exercise shows up as its own merge in the history:

```bash
git log --oneline --graph
```
