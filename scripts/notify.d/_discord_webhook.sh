#!/usr/bin/env bash
set -euo pipefail

resolve_discord_webhook_url() {
  local webhook_env_name="$1"
  local secret_file="$2"
  local webhook_url="${!webhook_env_name:-}"

  if [[ -z "$webhook_url" && -f "$secret_file" ]]; then
    # shellcheck disable=SC1090
    source "$secret_file"
    webhook_url="${!webhook_env_name:-}"
  fi

  if [[ -z "$webhook_url" ]]; then
    echo "discord notify: $webhook_env_name is required" >&2
    return 2
  fi

  printf '%s' "$webhook_url"
}

build_discord_payload() {
  local message="$1"
  local title="$2"
  local event="$3"
  local source_name="$4"
  local username="$5"
  local avatar_url="$6"
  local provenance='[`'"$event"'`]'

  if [[ -n "$source_name" ]]; then
    provenance='[`'"$event"'` from `'"$source_name"'`]'
  fi

  local content="$message"$'\n'"$provenance"
  if [[ -n "$title" ]]; then
    content="**$title**"$'\n'"$content"
  fi

  CONTENT="$content" \
  USERNAME="$username" \
  AVATAR_URL="$avatar_url" \
  python3 -c 'import json, os; payload = {"content": os.environ["CONTENT"]}; username = os.environ.get("USERNAME"); avatar_url = os.environ.get("AVATAR_URL");  # noqa: E702
if username: payload["username"] = username
if avatar_url: payload["avatar_url"] = avatar_url
print(json.dumps(payload, ensure_ascii=False))'
}

post_discord_payload() {
  local webhook_url="$1"
  local payload="$2"
  local http_code

  if ! http_code="$(
    curl \
      --silent \
      --show-error \
      --output /dev/null \
      --write-out '%{http_code}' \
      --header 'Content-Type: application/json' \
      --data "$payload" \
      "$webhook_url"
  )"; then
    echo "discord notify: webhook POST failed" >&2
    return 1
  fi

  if [[ ! "$http_code" =~ ^2[0-9][0-9]$ ]]; then
    echo "discord notify: webhook POST failed with HTTP $http_code" >&2
    return 1
  fi
}

send_discord_webhook_notification() {
  local webhook_env_name="$1"
  local secret_file="$2"
  local webhook_url
  webhook_url="$(resolve_discord_webhook_url "$webhook_env_name" "$secret_file")"

  local message="${NOTIFY_MESSAGE:-}"
  if [[ -z "$message" ]]; then
    message="$(cat)"
  fi

  local title="${NOTIFY_TITLE:-}"
  local event="${NOTIFY_EVENT:-generic}"
  local source_name="${NOTIFY_SOURCE:-}"
  local username="${DISCORD_WEBHOOK_USERNAME:-}"
  local avatar_url="${DISCORD_WEBHOOK_AVATAR_URL:-}"
  local payload
  payload="$(build_discord_payload "$message" "$title" "$event" "$source_name" "$username" "$avatar_url")"

  post_discord_payload "$webhook_url" "$payload"
}
