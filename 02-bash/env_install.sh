#!/usr/bin/env bash
#
# env_install.sh - set up a Python + Jupyter development environment.
#
# Usage: ./env_install.sh [--dry-run] [--verbose] [--quiet] [--uninstall] [--help]
#
# Works on Linux (apt / dnf / yum), macOS (Homebrew) and Windows Git Bash (winget).

# --- Strict mode (bonus) ------------------------------------------------------
# -e: stop on the first failing command
# -u: using an unset variable is an error
# -o pipefail: a pipeline fails if ANY command in it fails (not only the last one)
set -euo pipefail

# --- Settings -----------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/env_install.log"

DRY_RUN=false
VERBOSE=false
QUIET=false
UNINSTALL=false

# ANSI colors (bonus). Turned off when output is not a terminal (e.g. CI logs).
if [[ -t 1 ]]; then
    GREEN=$'\033[0;32m'; YELLOW=$'\033[0;33m'; RED=$'\033[0;31m'; BLUE=$'\033[0;34m'; RESET=$'\033[0m'
else
    GREEN=""; YELLOW=""; RED=""; BLUE=""; RESET=""
fi

# --- Functions ----------------------------------------------------------------

# Write a timestamped line to the log file (bonus: logging).
log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG_FILE"
}

# Feature 1: pretty printing. Blank line before and after, printf for portability.
# $1 = message, $2 = level (info | success | warn | error), default info.
pretty_print() {
    local message="$1"
    local level="${2:-info}"
    local color="$BLUE"

    case "$level" in
        success) color="$GREEN" ;;
        warn)    color="$YELLOW" ;;
        error)   color="$RED" ;;
    esac

    # (tr instead of ${level^^}: macOS still ships bash 3.2)
    log "$(printf '%s' "$level" | tr '[:lower:]' '[:upper:]'): ${message}"

    # --quiet hides everything except warnings and errors
    if [[ "$QUIET" == true && "$level" != "warn" && "$level" != "error" ]]; then
        return 0
    fi

    printf '\n%s%s%s\n\n' "$color" "$message" "$RESET"
}

# Run a command, or only show it with --dry-run. Logs success or failure.
run_cmd() {
    if [[ "$DRY_RUN" == true ]]; then
        printf '  [dry-run] %s\n' "$*"
        log "DRY-RUN: $*"
        return 0
    fi

    [[ "$VERBOSE" == true ]] && printf '  $ %s\n' "$*"
    log "RUN: $*"

    if "$@" >> "$LOG_FILE" 2>&1; then
        log "OK: $*"
    else
        local status=$?
        log "FAILED ($status): $*"
        pretty_print "Command failed: $* (see $LOG_FILE)" error
        return "$status"
    fi
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [options]

Installs Python 3, checks pip and installs Jupyter Notebook.

Options:
  --dry-run     show what would be done, change nothing
  --verbose     print every command before running it
  --quiet       only print warnings and errors
  --uninstall   remove what this script installed (Jupyter Notebook)
  -h, --help    show this help
EOF
}

# Feature 2: detect the OS with $OSTYPE and pick the package manager.
detect_os() {
    case "${OSTYPE:-unknown}" in
        linux*)          OS="linux" ;;
        darwin*)         OS="macos" ;;
        msys*|cygwin*)   OS="windows" ;;
        *)               OS="unknown" ;;
    esac

    PKG=""
    case "$OS" in
        linux)
            if   command -v apt-get >/dev/null 2>&1; then PKG="apt"
            elif command -v dnf     >/dev/null 2>&1; then PKG="dnf"
            elif command -v yum     >/dev/null 2>&1; then PKG="yum"
            fi ;;
        macos)   command -v brew   >/dev/null 2>&1 && PKG="brew" ;;
        windows) command -v winget >/dev/null 2>&1 && PKG="winget" ;;
    esac

    pretty_print "Detected OS: ${OS} (OSTYPE=${OSTYPE:-unset}), package manager: ${PKG:-none}"
}

# Find a working Python 3 command (python3 on Linux/macOS, often python on Windows).
find_python() {
    PYTHON=""
    local candidate
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1 \
           && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)' >/dev/null 2>&1; then
            PYTHON="$candidate"
            return 0
        fi
    done
    return 1
}

install_python() {
    case "$PKG" in
        apt)    run_cmd sudo apt-get update
                run_cmd sudo apt-get install -y python3 python3-pip python3-venv ;;
        dnf)    run_cmd sudo dnf install -y python3 python3-pip ;;
        yum)    run_cmd sudo yum install -y python3 python3-pip ;;
        brew)   run_cmd brew install python ;;
        winget) run_cmd winget install -e --id Python.Python.3.13 ;;
        *)      pretty_print "No supported package manager found: install Python 3 manually." error
                return 1 ;;
    esac
}

# Feature 3: check Python, install it if missing, else show the version.
check_python() {
    if find_python; then
        pretty_print "Python found: $("$PYTHON" --version 2>&1)" success
        return 0
    fi

    pretty_print "Python 3 not found, installing it..." warn
    install_python

    if [[ "$DRY_RUN" == true ]]; then
        PYTHON="python3"
    elif find_python; then
        pretty_print "Python installed: $("$PYTHON" --version 2>&1)" success
    else
        pretty_print "Python still not available after install (open a new terminal?)" error
        return 1
    fi
}

# Feature 4: check pip.
check_pip() {
    if "$PYTHON" -m pip --version >/dev/null 2>&1; then
        pretty_print "pip found: $("$PYTHON" -m pip --version)" success
    else
        pretty_print "pip not found, installing it with ensurepip..." warn
        run_cmd "$PYTHON" -m ensurepip --upgrade
    fi
}

# Feature 5: install Jupyter Notebook (command differs per OS).
install_jupyter() {
    if "$PYTHON" -m notebook --version >/dev/null 2>&1; then
        pretty_print "Jupyter Notebook already installed ($("$PYTHON" -m notebook --version))" success
        return 0
    fi

    pretty_print "Installing Jupyter Notebook..."
    case "$OS" in
        linux)
            # Recent Debian/Ubuntu block system-wide pip installs (PEP 668), use the OS package there.
            if [[ "$PKG" == "apt" ]]; then
                run_cmd sudo apt-get install -y jupyter-notebook
            else
                run_cmd "$PYTHON" -m pip install --user notebook
            fi ;;
        macos)
            run_cmd brew install jupyterlab ;;
        *)
            run_cmd "$PYTHON" -m pip install --user notebook ;;
    esac
    pretty_print "Jupyter Notebook installed: start it with 'jupyter notebook'" success
}

# Feature 6: on macOS, check Homebrew is healthy.
macos_health_check() {
    [[ "$OS" == "macos" ]] || return 0
    pretty_print "Running brew doctor..."
    # brew doctor exits non-zero for simple warnings: report them, don't stop the script.
    if ! run_cmd brew doctor; then
        pretty_print "brew doctor reported issues, see $LOG_FILE" warn
    fi
}

# Bonus: undo what the script installed. Python itself is left alone on purpose
# (the system and other programs may need it).
uninstall() {
    pretty_print "Uninstalling Jupyter Notebook..." warn
    case "$OS" in
        linux)
            if [[ "$PKG" == "apt" ]]; then
                run_cmd sudo apt-get remove -y jupyter-notebook
            else
                run_cmd "$PYTHON" -m pip uninstall -y notebook
            fi ;;
        macos) run_cmd brew uninstall jupyterlab ;;
        *)     run_cmd "$PYTHON" -m pip uninstall -y notebook ;;
    esac
    pretty_print "Uninstall complete" success
}

# --- Main ---------------------------------------------------------------------
main() {
    local arg
    for arg in "$@"; do
        case "$arg" in
            --dry-run)   DRY_RUN=true ;;
            --verbose)   VERBOSE=true ;;
            --quiet)     QUIET=true ;;
            --uninstall) UNINSTALL=true ;;
            -h|--help)   usage; exit 0 ;;
            *)           printf 'Unknown option: %s\n\n' "$arg" >&2; usage >&2; exit 2 ;;
        esac
    done

    log "===== env_install.sh started (args: $*) ====="
    pretty_print "Starting environment setup$([[ "$DRY_RUN" == true ]] && echo ' (dry run)')"

    detect_os
    check_python

    if [[ "$UNINSTALL" == true ]]; then
        uninstall
        exit 0
    fi

    check_pip
    install_jupyter
    macos_health_check

    pretty_print "All done! Your environment is ready." success
    log "===== finished ====="
}

main "$@"
