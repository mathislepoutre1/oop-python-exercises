# 02 · Bash script: set up a dev environment

> Slide 18: https://courses.dallard.tech/linux/bash_exo/

## Part 1: Shell

```bash
echo $0        # the shell that is running right now (e.g. bash)
echo $SHELL    # my *login* shell, the default one for my user (e.g. /bin/bash)
```

They can differ: if my login shell is zsh and I type `bash`, `$0` says `bash` but `$SHELL` still says `/bin/zsh`.

**Shell framework.** For bash it's [Oh My Bash](https://github.com/ohmybash/oh-my-bash) (for zsh, Oh My Zsh). After installing it I picked a theme with `OSH_THEME="..."` in `~/.bashrc`, and enabled the git plugin by adding `git` to the plugin list:

```bash
plugins=(
  git
)
```

then reloaded the config:

```bash
source ~/.bashrc
```

**What is `source` for?** It runs a file *inside the current shell* instead of starting a new one. Variables, aliases and functions defined in the file therefore stay available in my session. That's how you apply changes to `~/.bashrc` without closing the terminal. (`./script.sh` would run in a child shell and everything it defines would disappear when it ends.)

**Git aliases** from the plugin: `gst` = `git status`, `gl` = `git pull`, `gp` = `git push`, `glog` = `git log --oneline --graph`.

## Part 2: Python

```bash
python3 --version   # always python3, `python` can still be Python 2 on old systems
```

## Part 3: The script: [`env_install.sh`](env_install.sh)

```bash
chmod +x env_install.sh      # without this: "Permission denied"
./env_install.sh --help
./env_install.sh --dry-run   # shows what it would do, changes nothing
./env_install.sh
```

Structure: shebang, then strict mode and settings, then functions, then `main`.

| Required feature | Function |
|---|---|
| 1. Pretty print with `printf` and blank lines | `pretty_print` |
| 2. OS detection with `$OSTYPE` | `detect_os` (Linux / macOS / Windows Git Bash) |
| 3. Check Python, install if missing, else show version | `check_python` |
| 4. Check pip version | `check_pip` |
| 5. Install Jupyter Notebook (per OS) | `install_jupyter` |
| 6. `brew doctor` on macOS | `macos_health_check` |

Bonus challenges, all done:

- **Colors:** green for success, yellow for warnings, red for errors (disabled when the output isn't a terminal).
- **Logging:** every action goes to `env_install.log` with a timestamp, the command, and OK/FAILED.
- **Strict mode:** `set -euo pipefail`.
- **Arguments:** `--dry-run`, `--verbose`, `--quiet`.
- **Uninstall:** `--uninstall` removes Jupyter. It leaves Python on purpose because other programs depend on it.

Best practices: every variable is quoted, comments explain *why*, and every command goes through `run_cmd`, which checks it succeeded and writes the error to the log.

## Part 4: Verification

- [x] `python3 --version` → 3.x
- [x] `python3 -m pip --version` → shows pip
- [x] `jupyter notebook` starts
- [x] `./env_install.sh --dry-run` runs without errors (also checked by the CI on Ubuntu, see `.github/workflows/tests.yml`)
