default: help

.PHONY: Install
install:
	cd ./app && npm install

.PHONY: Start
start:
	cd ./app && npm start
