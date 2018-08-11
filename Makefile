# http://clarkgrubb.com/makefile-style-guide

MAKEFLAGS += --warn-undefined-variables --no-print-directory
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := deploy
.DELETE_ON_ERROR:
.SUFFIXES:

deploy:
	chcon -Rt svirt_sandbox_file_t .
	sam package --template-file template.yaml --output-template-file $@.yaml --s3-bucket EDITME
	aws cloudformation deploy --template-file $@.yaml \
		--stack-name snssqs \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides TopicArn=EDITME
