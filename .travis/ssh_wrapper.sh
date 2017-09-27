#!/usr/bin/env bash

D=${0%/*}
KEY="$D/github_deploy_key"

if [[ ! -e "$KEY" ]]; then
    openssl aes-256-cbc -K $encrypted_ce0626a827e3_key -iv $encrypted_ce0626a827e3_iv -in "$KEY".enc -out "$KEY" -d
    chmod 0400 "$KEY"
fi

exec ssh -i "$KEY" "$@"
