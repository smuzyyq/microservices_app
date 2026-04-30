#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "ERROR: .env file not found at ${ENV_FILE}"
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

required_vars=(
  AUTH_DATABASE_URL
  PRODUCT_DATABASE_URL
  ORDER_DATABASE_URL
  USER_DATABASE_URL
  CHAT_DATABASE_URL
  JWT_SECRET
  PRODUCT_SERVICE_URL
  ORDER_SERVICE_URL
  POSTGRES_USER
  POSTGRES_PASSWORD
)

missing=0
for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "ERROR: Required variable ${var_name} is missing or empty."
    missing=1
  fi
done

check_prefix() {
  local name="$1"
  local expected="$2"
  local value="${!name:-}"
  if [[ -n "${value}" && "${value}" != ${expected}* ]]; then
    echo "ERROR: ${name} must start with '${expected}'. Current value: ${value}"
    missing=1
  fi
}

check_contains() {
  local name="$1"
  local expected="$2"
  local value="${!name:-}"
  if [[ -n "${value}" && "${value}" != *"${expected}"* ]]; then
    echo "ERROR: ${name} must contain '${expected}'. Current value: ${value}"
    missing=1
  fi
}

check_prefix "AUTH_DATABASE_URL" "postgresql://"
check_prefix "PRODUCT_DATABASE_URL" "postgresql://"
check_prefix "ORDER_DATABASE_URL" "postgresql://"
check_prefix "USER_DATABASE_URL" "postgresql://"
check_prefix "CHAT_DATABASE_URL" "postgresql://"
check_prefix "PRODUCT_SERVICE_URL" "http://"
check_prefix "ORDER_SERVICE_URL" "http://"

check_contains "AUTH_DATABASE_URL" "@auth-db:5432/"
check_contains "PRODUCT_DATABASE_URL" "@product-db:5432/"
check_contains "ORDER_DATABASE_URL" "@order-db:5432/"
check_contains "USER_DATABASE_URL" "@auth-db:5432/"
check_contains "CHAT_DATABASE_URL" "@chat-db:5432/"

if [[ ${missing} -ne 0 ]]; then
  echo "Environment validation failed."
  exit 1
fi

echo "Environment validation passed."
