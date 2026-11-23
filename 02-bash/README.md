# 02 - Bash script

## Part 1 - Shell

```bash
echo $0       # shell running right now
echo $SHELL   # default login shell
```

I installed Oh My Bash, picked a theme and added `git` to the plugins in `~/.bashrc`, then ran `source ~/.bashrc`.

`source` runs the file in the current shell instead of a new one, so the changes apply right away without opening a new terminal.

Git aliases from the plugin: `gst` (git status), `gl` (git pull), `gp` (git push).

## Part 2 - Python

```bash
python3 --version
```

## Part 3 - The script

```bash
chmod +x env_install.sh
./env_install.sh --dry-run   # shows what it would do
./env_install.sh
```

What it does:
1. `pretty_print` function to print messages with `printf`
2. detects the OS with `$OSTYPE`
3. checks if python3 is installed, installs it if not
4. checks pip
5. installs Jupyter Notebook
6. runs `brew doctor` on macOS

I also did the bonus: colors, a log file (`env_install.log`), strict mode (`set -euo pipefail`), the `--dry-run`, `--verbose` and `--quiet` options, and `--uninstall`.
