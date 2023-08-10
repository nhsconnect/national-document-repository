default: help

.PHONY: Install
install:
	cd ./app && npm install

.PHONY: Clean install
clean-install:
	cd ./app && npm ci

.PHONY: Start
start:
	cd ./app && npm start
