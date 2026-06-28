#!/bin/bash
# utils.sh — Shared utilities for build scripts

COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_NC='\033[0m'

log_info() {
    echo -e "${COLOR_BLUE}[INFO]${COLOR_NC} $*"
}

log_success() {
    echo -e "${COLOR_GREEN}[SUCCESS]${COLOR_NC} $*"
}

log_warning() {
    echo -e "${COLOR_YELLOW}[WARNING]${COLOR_NC} $*"
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_NC} $*" >&2
}

check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Dependency missing: $1"
        return 1
    fi
    return 0
}

download_file() {
    local url="$1"
    local dest="$2"
    if curl -L -o "$dest" "$url"; then
        log_success "Downloaded: $dest"
        return 0
    else
        log_error "Failed to download: $url"
        return 1
    fi
}

extract_zip() {
    local zip="$1"
    local dest="$2"
    if unzip -q "$zip" -d "$dest"; then
        log_success "Extracted: $zip -> $dest"
        return 0
    else
        log_error "Failed to extract: $zip"
        return 1
    fi
}

get_apk_list() {
    local dir="$1"
    find "$dir" -name "*.apk" -type f 2>/dev/null || echo ""
}
