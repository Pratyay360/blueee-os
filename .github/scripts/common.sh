#!/usr/bin/env bash
# Shared helpers for the ISO workflow scripts. Source this; never run it directly.
# Contract: every script sets -euo pipefail and sources this file first.

set -euo pipefail

log() { printf '%s\n' "$*"; }
warn() { printf '::warning::%s\n' "$*"; }
error() { printf '::error::%s\n' "$*" >&2; }

die() {
  error "$*"
  exit 1
}

# require_env NAME [NAME...] - fail with one clear message per missing variable.
require_env() {
  local name
  for name in "$@"; do
    [[ -n "${!name:-}" ]] || die "Missing required environment variable: $name"
  done
}

# github_output "key=value" - write a step output when running in Actions,
# print it locally otherwise.
github_output() {
  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    printf '%s\n' "$1" >> "$GITHUB_OUTPUT"
  else
    log "[output] $1"
  fi
}

# step_summary "line" - append a line to the job summary when running in
# Actions, print it locally otherwise.
step_summary() {
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    printf '%s\n' "$1" >> "$GITHUB_STEP_SUMMARY"
  else
    log "$1"
  fi
}
