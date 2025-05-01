# AI Tutor Project
## Introduction
This project implements a prototype of an AI-powered schoolteacher for the lower Key Stage 2 mathematics
syllabus in the UK.

The high-level architecture is shown in the figure below:

![Capture](https://github.com/user-attachments/assets/f4241fd0-8fba-498c-ae32-8417fc77be00)

The AI Tutor is implemented as a web app. The student user points their web browser at the AI Tutor URL
and either creates an account or logs into their existing account.

Once logged in, the AI Tutor presents the student with a 'dashboard' that summarises their progress
through the syllabus. The user is able to work through the syllabus topics by clicking on 'Begin' to
start studying a topic, or 'Continue' to pick up a topic where they previously left off.

Once a user has started studying a topic, the dashboard will also present the user with a 'Test'
option, so that they can take the qualifying test and, if they pass the test, that topic will be
marked as 'mastered'.

### Online prototype
You can try out the prototype at [chubster.duckdns.org](http://chubster.duckdns.org/index.php) (If Google doesn't work, try other browsers to see if it helps).

## Repo folder structure
Within this repository are a number of folders, which are as follows:

[/php](php/)\
Contains PHP code that is used by the AI Tutor web app but lives *outside* the http-accessible
area under [/www](www/). This prevents a malicious user being able to wget the PHP implementation and gain
access to database credentials or examine the implementation.

[/python](python/)\
Contains the python code for interacting with the LLM, as well as some utility code used mainly
for testing during prototype development.

[/www](www/)\
Contains the web app, this would be where the HTTP server would be configured to serve
the web app. This folder contains the following:

<dl>
  <dt>index.php</dt>
  <dd>The main page with the learning dashboard.</dd>
  <dt>login.php</dt>
  <dd>Called to handle user login/registration actions.</dd>
  <dt>logout.php</dt>
  <dd>Logs out the currently logged in user.</dd>
  <dt>topic-test.php</dt>
  <dd>Enables users to take a test to pass a given topic.</dd>
  <dt>tutor.php</dt>
  <dd>A chat-like interface to the AI tutor, powered by the backend LLM.</dd>
</dl>

[/www/cgi-bin](www/cgi-bin/)\
Contains the python CGI handlers for communicating with the LLM.
