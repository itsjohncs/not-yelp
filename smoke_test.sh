#!/usr/bin/env bash

set -eu
shopt -s failglob

COOKIE_FILE="$(mktemp)"

function expect {
	echo -- expect "${@}" 1>&2
	RESPONSE="$(curl \
		--silent \
		--header "Content-Type: application/json" \
		-b "$COOKIE_FILE" \
		-c "$COOKIE_FILE" \
		"http://localhost:3000$2" \
		"${@:3}")"
	echo "$RESPONSE"
	if [[ "$(jq --raw-output .result <<< "$RESPONSE")" != "$1" ]]; then
		echo FAILED EXPECT 1>&2
		return 1
	fi
}

make init-db

expect error /api/whoami
expect error /api/login --data '{"username": "john", "password":"testpassword"}'

expect error /api/register --data '{"username": "john", "password":"abc"}'
expect error /api/register --data '{"username": "jo", "password":"testpassword"}'
expect success /api/register --data '{"username": "john", "password":"testpassword"}'
expect error /api/login --data '{"username": "john", "password":"incorrectpassword"}'
expect success /api/login --data '{"username": "john", "password":"testpassword"}'

expect success /api/whoami

expect success /api/create-restaurant --data '{"title": "Tasty Food Co"}'
expect success /api/restaurants

expect success /api/logout -X POST
expect error /api/whoami

expect success /api/register --data '{"username": "notjohn", "password":"testpassword"}'
NOTJOHN="$(expect success /api/login --data '{"username": "notjohn", "password":"testpassword"}')"

BETTER_FOOD_CO="$(expect success /api/create-restaurant --data '{"title": "Better Food Co"}')"
expect success /api/restaurants
expect success "/api/restaurants?owner=$(jq --raw-output .id <<< "$NOTJOHN")"
expect success "/api/restaurants?owner=0"

BETTER_FOOD_CO_ID="$(jq --raw-output .id <<< "$BETTER_FOOD_CO")"
expect error /api/create-review --data '{"visit_date": "2020-01-01", "rating": 7, "restaurant": "'"$BETTER_FOOD_CO_ID"'"}'
expect error /api/create-review --data '{"visit_date": "2020-01-01", "comment": "great", "rating": 7, "restaurant": "'"$BETTER_FOOD_CO_ID"'"}'
expect error /api/create-review --data '{"visit_date": "2020-01-01", "comment": "", "rating": 5, "restaurant": "'"$BETTER_FOOD_CO_ID"'"}'
expect error /api/create-review --data '{"visit_date": "1899-01-01", "comment": "great", "rating": 5, "restaurant": "'"$BETTER_FOOD_CO_ID"'"}'
expect error /api/create-review --data '{"visit_date": "3000-01-01", "comment": "great", "rating": 5, "restaurant": "'"$BETTER_FOOD_CO_ID"'"}'
expect success /api/create-review --data '{"visit_date": "2020-01-01", "comment": "great", "rating": 5, "restaurant": "'"$BETTER_FOOD_CO_ID"'"}'

rm "$COOKIE_FILE"
