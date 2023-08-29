## National Document Repository User Interface

### Intro
 
The National Document Repository user interface (UI) has been developed with React. This is a developer's guide to run the UI and tools locally. 

### Requirements

- Node: Version 16.0 or greater.
- NPM: this should come installed with Node but if not version 8.3.1 or greater is recommended.
- Browser: Of your choice, Chrome tends to have better development tools. 

### Running the app

To run the UI, the team has created a Makefile in the route directory, on your first run you will need to install the required node packages for the app through a command line interface (CLI)..

    make install  

Once the packages have been installed, you can then run the app through the following command

	make start

Once everything is up and running you should see a prompt in the CLI that the app is running on http://localhost:3000. You should now be able to visit the site in a browser of your choice. 

### Testing

There are two test paths through the app. 
The first is unit testing. To run the unit tests within the project, you can run the following command via the CLI on the route directory…

	make test

You will see the output from the tests in the CLI.

The second is E2E / component testing through Cypress. Firstly you must have the app running through the “running the app steps”. Secondly you will want a second CLI terminal to be apple to run the following command…

	make cypress-open

This will open the cypress testing UI. At the time of writing, we would recommend following the UI through the E2E selection options to view and run the E2E tests if this is your first time using Cypress.  

