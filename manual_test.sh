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
postjson /api/login --data '{"username": "john", "password":"testpassword"}'

postjson /api/register --data '{"username": "john", "password":"abc"}'
postjson /api/register --data '{"username": "jo", "password":"testpassword"}'
postjson /api/register --data '{"username": "john", "password":"testpassword"}'
postjson /api/login --data '{"username": "john", "password":"incorrectpassword"}'
postjson /api/login --data '{"username": "john", "password":"testpassword"}'

postjson /api/whoami

postjson /api/create-restaurant --data '{"title": "Tasty Food Co"}'
postjson /api/restaurants

postjson /api/logout -X POST
postjson /api/whoami

postjson /api/register --data '{"username": "notjohn", "password":"testpassword"}'
NOTJOHN="$(postjson /api/login --data '{"username": "notjohn", "password":"testpassword"}')"

postjson /api/create-restaurant --data '{"title": "Better Food Co"}'
postjson /api/restaurants
postjson "/api/restaurants?owner=$(jq --raw-output .id <<< "$NOTJOHN")"
postjson "/api/restaurants?owner=0"

rm "$COOKIE_FILE"
