#@ Variables
SHELL := /usr/bin/env bash
VERSION := 0.11.0

#@ Repo initialization
.PHONY: repo-pre-commit repo-deps repo-env repo-init

 # Install pre-commit in repository
repo-pre-commit:
	pre-commit install
	pre-commit install -t commit-msg

# Install dependencies in repository
repo-deps:
	poetry install

# Configure environment variables in repository
repo-env:
	cat .test.env  > .env
	echo "dotenv" > .envrc

# Initialize repository
repo-init: repo-pre-commit repo-deps repo-env-init

#@ Research
.PHONY:	jupyter

# Run jupyter lab
jupyter:
	poetry run jupyter lab

#@ Checks
.PHONY:	mypy

# Run type checker
mypy:
	poetry run mypy

#@ Datasets
.PHONY:	get_lj_speech

# LJ Speech for ASR
get_lj_speech:
	chmod +x ./scripts/datasets.sh
	sh ./scripts/datasets.sh get_lj_speech_dataset

#@ Clean garbage
