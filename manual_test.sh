#!/usr/bin/env bash

set -eux
shopt -s failglob

COOKIE_FILE="$(mktemp)"

function postjson {
	curl \
		--header "Content-Type: application/json" \
		-b "$COOKIE_FILE" \
		-c "$COOKIE_FILE" \
		"http://localhost:3000$1" \
		"${@:2}"
}

make init-db

postjson /api/whoami
postjson /api/login --data '{"username": "john", "password":"ham"}'

postjson /api/register --data '{"username": "john", "password":"ham"}'
postjson /api/login --data '{"username": "john", "password":"notham"}'
postjson /api/login --data '{"username": "john", "password":"ham"}'

postjson /api/whoami

postjson /api/create-restaurant --data '{"title": "Tasty Food Co"}'
postjson /api/restaurants

rm "$COOKIE_FILE"
