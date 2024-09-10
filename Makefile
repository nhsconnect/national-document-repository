PYTHON_VERSION=3.11

REQUIREMENTS_PATH=lambdas/requirements
LAMBDA_LAYER_REQUIREMENTS_PATH=$(REQUIREMENTS_PATH)/layers

GITHUB_REQUIREMENTS=$(REQUIREMENTS_PATH)/requirements_github_runner.txt
TEST_REQUIREMENTS=$(REQUIREMENTS_PATH)/requirements_test.txt
CORE_REQUIREMENTS=$(LAMBDA_LAYER_REQUIREMENTS_PATH)/requirements_core_lambda_layer.txt
DATA_REQUIREMENTS=$(LAMBDA_LAYER_REQUIREMENTS_PATH)/requirements_data_lambda_layer.txt
EDGE_REQUIREMENTS=$(REQUIREMENTS_PATH)/requirements_edge_lambda.txt

LAMBDAS_BUILD_PATH=build/lambdas
LAMBDA_LAYERS_BUILD_PATH=build/lambda_layers
LAMBDA_LAYER_PYTHON_PATH=python/lib/python$(PYTHON_VERSION)/site-packages

ZIP_BASE_PATH = ./$(LAMBDAS_BUILD_PATH)/$(lambda_name)/tmp
ZIP_COMMON_FILES = lambdas/utils lambdas/models lambdas/services lambdas/repositories lambdas/enums

default: help

clean: clean-build clean-py clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-py:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	find . -name '.pytest_cache' -exec rm -fr {} +
	find . -name '.coverage' -exec rm -fr {} +
	find . -name 'htmlcov' -exec rm -fr {} +
	find . -name '.cache' -exec rm -fr {} +

format:
	./lambdas/venv/bin/python3 -m isort --profile black lambdas/
	./lambdas/venv/bin/python3 -m black lambdas/
	./lambdas/venv/bin/ruff check lambdas/ --fix

sort-requirements:
	sort -o $(TEST_REQUIREMENTS) $(TEST_REQUIREMENTS)
	sort -o $(CORE_REQUIREMENTS) $(CORE_REQUIREMENTS)
	sort -o $(DATA_REQUIREMENTS) $(DATA_REQUIREMENTS)

check-packages:
	./lambdas/venv/bin/pip-audit -r $(TEST_REQUIREMENTS)
	./lambdas/venv/bin/pip-audit -r $(CORE_REQUIREMENTS)
	./lambdas/venv/bin/pip-audit -r $(DATA_REQUIREMENTS)

test-unit:
	cd ./lambdas && ./venv/bin/python3 -m pytest tests/

test-unit-coverage:
	cd ./lambdas && ./venv/bin/python3 -m pytest --cov=. --cov-report xml:coverage.xml

test-unit-coverage-html:
	cd ./lambdas && coverage run --source=. --omit="tests/*" -m pytest -v tests && coverage report && coverage html

test-unit-collect:
	cd ./lambdas && ./venv/bin/python3 -m pytest tests/ --collect-only

env:
	rm -rf lambdas/venv || true
	python3 -m venv ./lambdas/venv
	./lambdas/venv/bin/pip3 install --upgrade pip
	./lambdas/venv/bin/pip3 install -r $(TEST_REQUIREMENTS)
	./lambdas/venv/bin/pip3 install -r $(CORE_REQUIREMENTS)
	./lambdas/venv/bin/pip3 install -r $(DATA_REQUIREMENTS)

github_env:
	rm -rf lambdas/venv || true
	python3 -m venv ./lambdas/venv
	./lambdas/venv/bin/pip3 install --upgrade pip
	./lambdas/venv/bin/pip3 install -r $(GITHUB_REQUIREMENTS)

edge_env:
	rm -rf lambdas/venv || true
	python3 -m venv ./lambdas/venv
	./lambdas/venv/bin/pip3 install --upgrade pip
	./lambdas/venv/bin/pip3 install -r $(GITHUB_REQUIREMENTS)
	./lambdas/venv/bin/pip3 install -r $(EDGE_REQUIREMENTS)

zip:
	echo $(LAMBDAS_BUILD_PATH)/$(lambda_name)
	rm -rf ./$(LAMBDAS_BUILD_PATH)/$(lambda_name) || true
	mkdir -p $(ZIP_BASE_PATH)/handlers
	cp lambdas/handlers/$(lambda_name).py $(ZIP_BASE_PATH)/handlers
	cp -r $(ZIP_COMMON_FILES) $(ZIP_BASE_PATH)
	cd $(ZIP_BASE_PATH) ; zip -r ../$(lambda_name).zip .
	rm -rf $(ZIP_BASE_PATH)

edge_zip: zip
	mkdir -p $(ZIP_BASE_PATH)/python
	cp -r lambdas/venv/lib/python*/site-packages/* $(ZIP_BASE_PATH)
	cd $(ZIP_BASE_PATH) ; zip -r ../$(lambda_name).zip .
	rm -rf $(ZIP_BASE_PATH)

lambda_layer_zip:
	rm -rf ./$(LAMBDA_LAYERS_BUILD_PATH)/$(layer_name) || true
	mkdir -p ./$(LAMBDA_LAYERS_BUILD_PATH)/$(layer_name)
	./lambdas/venv/bin/pip3 install --platform manylinux2014_x86_64 --only-binary=:all: --implementation cp  -r $(LAMBDA_LAYER_REQUIREMENTS_PATH)/requirements_$(layer_name).txt -t ./$(LAMBDA_LAYERS_BUILD_PATH)/$(layer_name)/tmp/$(LAMBDA_LAYER_PYTHON_PATH)
	cd ./$(LAMBDA_LAYERS_BUILD_PATH)/$(layer_name)/tmp; zip -r ../$(layer_name).zip .
	rm -rf ./$(LAMBDA_LAYERS_BUILD_PATH)/$(layer_name)/tmp
	cd ../..

package: format zip

install:
	npm --prefix ./app install --legacy-peer-deps

clean-install:
	npm --prefix ./app ci --legacy-peer-deps

start:
	npm --prefix ./app start

storybook:
	npm --prefix ./app run storybook

test-ui:
	npm --prefix ./app run test-all

test-ui-coverage:
	npm --prefix ./app run test-all:coverage

build:
	npm --prefix ./app run build

build-env-check:
	npm --prefix ./app run build-env-check

docker-up:
	docker-compose -f ./app/docker-compose.yml up -d

docker-up-rebuild:
	docker-compose -f ./app/docker-compose.yml up -d --build --force-recreate

docker-down:
	docker-compose -f ./app/docker-compose.yml down

cypress-open:
	TZ=GMT npm --prefix ./app run cypress

cypress-run:
	TZ=GMT npm --prefix ./app run cypress-run

cypress-report:
	TZ=GMT npm --prefix ./app run cypress-report
