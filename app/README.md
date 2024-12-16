## National Document Repository User Interface

### Intro

The National Document Repository user interface (UI) has been developed with React. This is a developer's guide to run the UI and tools locally.

## Table Of Contents

1. [Setup](#setup)
2. [Running Locally](#running-locally)
3. [Testing](#testing)
4. [Accessibility](#accessibility)
5. [Design](#design)

### Requirements

-   Node: Version 18.0
-   NPM: this should come installed with Node but if not version 8.3.1 or greater is recommended.
-   Browser: Of your choice, although Chrome has better development tools.

## Setup

### 1. Set Env Variables

In the app/ directory create a `.env` file by duplicating [.env.template](.env.template) and adding any missing values. This file is sourced to
your shell env so make sure it doesn't have any extra whitespace, comments etc.
The `local` environment variable will allow your local app to bypass auth and mock most lambda requests.

### 2. Local

To run the UI, the team has created a Makefile in the route directory, on your first run you will need to install the required node packages for the app through a command line interface (CLI)..

```bash
make install
```

Once the packages have been installed, you can then run the app through the following command

```bash
make start
```

Once everything is up and running you should see a prompt in the CLI that the app is running on http://localhost:xxxx, where xxxx is the value of PORT specified in `.env` file. You should now be able to visit the site in a browser of your choice.

## Testing

### 1. UI Tests

You can run the unit tests for the app [Jest](https://jestjs.io/) by running

```bash
make test-ui
```

These tests are run against each \*.test.tsx file, which should generally be written per component when extending the app.
The applications unit tests will also run automatically every-time a push is made via git.

### 2. E2E Tests

There are also Cypress end-to-end tests written against each user journey and it's functionality.

Before running the E2E tests, please make sure you have got the value `CYPRESS_BASE_URL=http://localhost:xxxx` set up in your .env file.  
You can then start the E2E tests by running

```bash
make cypress-open
```

If you wish to run a CLI only test run, you can use the following command

```bash
make cypress-run
```

This will open a new Chromium window with the options to either run the E2E tests or Component tests

## Accessibility

-   [WAVE Chrome extension](https://chrome.google.com/webstore/detail/wave-evaluation-tool/jbbplnpkjmmeebjpijfedlgcdilocofh)
-   Use a screen reader
-   Use keyboard navigation
-   Use NHS components rather than custom styling

## Design

The UI follows the guidelines specified in the [NHS Service Manual](https://service-manual.nhs.uk/). To help achieve
this, we utilise the UI components provided by the [nhsuk-frontend](https://github.com/nhsuk/nhsuk-frontend) package.
