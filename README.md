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
You can try out the prototype at [chubster.duckdns.org](http://chubster.duckdns.org/index.php)

Note that the prototype is hosted on a VM behind a dynamic DNS service - if you are unable to connect to the prototype, please contact me.

## Repo folder structure
Within this repository are a number of folders, which are as follows:

### [/php](php/)
Contains PHP code that is used by the AI Tutor web app but lives *outside* the http-accessible
area under [/www](www/). This prevents a malicious user being able to wget the PHP implementation and gain
access to database credentials or examine the implementation.

[/php/checklogin.php](php/checklogin.php)\
Checks if the user is currently logged in. Updates the 'lastlogin' timestamp in the database if so, otherwise redirects to the login page.

[/php/dbase.php](php/dbase.php)\
Contains all the database support functions used by the PHP code within [/www](www/).

### [/python](python/)
Contains the python code for interacting with the LLM, as well as some utility code used mainly
for testing during prototype development.

[dbase.py](python/dbase.py)\
Included by other python files to connect to the database.

[gemini.py](python/gemini.py)\
Contains the code for communicating with the Google Gemini LLM. This is the LLM
currently used in the AI Tutor prototype. Used by [/www/cgi-bin/aitutor.py](www/cgi-bin/aitutor.py).

[llm_backend.py](python/llm_backend.py)\
Contains the code for communicating with an Ollama-hosted LLM. This provides an
alternative to the Gemini LLM, and enables the AI Tutor to use a model within the
Ollama harness. Used by [/www/cgi-bin/process.py](www/cgi-bin/process.py).

[prompt.py](python/prompt.py)\
Contains the default system prompt, as a fallback in case the AI Tutor app is
unable to find a system prompt in the database.

[reset.py](python/reset.py)\
Used for testing during development only. Resets the AI Tutor database for a
given user, erasing all progress and previous conversation context with the LLM.

[update-prompt.py](python/update-prompt.py)\
Used for prompt engineering of the system prompt/model role during development.
This is a simple command line utility for updating the system prompt in the database
without having to login to the database and make the update manually.

### [/www](www/)
Contains the web app, this would be where the HTTP server would be configured to serve
the web app. This folder contains the following:

[index.php](www/index.php)\
Acts as the dashboard for the AI Tutor web app. Displays the syllabus with
an 'accordion' expand/collapse view of the subtopics in each section. The
user's progress with each topic is displayed.

[login.php](www/login.php)\
Allows the user to create or login to a user account.

[logout.php](www/logout.php)\
Logs out a currently signed-in user.

[topic-test.php](www/topic-test.php)\
Presents the user with a selection of test questions for a given topic.
The user's responses to questions are sent to the backend LLM for evaluation.
Correct responses result in the question being marked as correct. An
incorrect response will result in the explanatory response from the LLM
being displayed in a modal dialogue.

[tutor.php](www/tutor.php)\
Presents the user with a chat-like interface to the AI Tutor. The chat session
begins with the AI Tutor either introducing the topic or continuing to teach a topic.

Hidden prompts are sent to the LLM to direct it as to whether the session is for
a new topic, or whether the LLM should summarise the lesson so far and resume the topic.

### [/www/cgi-bin](www/cgi-bin/)
Contains the python CGI handlers for communicating with the LLM. Note: for production use, this
code needs updating to prevent [cross-site request forgeries](https://en.wikipedia.org/wiki/Cross-site_request_forgery).

[aitutor.py](www/cgi-bin/aitutor.py)\
This is the endpoint called by [/www/js/script.js](www/js/script.js) when a message is
sent to the AI Tutor LLM. This file simply retrieves the message text and userid from
the submitted form data and passes it to Gemini via [/python/gemini.py](python/gemini.py).

[check-answer.py](www/cgi-bin/check-answer.py)\
This endpoint is called when a user answers a test question, and is used to pass
the test question, the expected response, and the user's response to the AI Tutor LLM
so that it can verify the user's answer.

## Database schema
The SQL for recreating the database schema can be found in [/sql](sql/) and it consists
of the following tables:

<dl>
  <dt>context</dt>
  <dd>Used to keep track of the conversational exchanges between each user and the LLM.
    When a user sends a message to the AI Tutor, the history of the conversation (up to
    a maximum of 1000 messages) is prepended to the latest message. This ensures the LLM
    can respond appropriately within the context of the conversation.</dd>
  <dt>progress</dt>
  <dd>Maintains the progress of a user against topics in the syllabus. When a given user
    has an entry for every topic, and each topic entry has a 'mastered' status, then the
    user has completed the course.</dd>
  <dt>prompt</dt>
  <dd>Rather than hardcoding LLM prompts in Python, this table stores the prompts for 
    different situations, e.g. the system prompt, the prompts to begin and resume a
    topic, etc. Having them in a database enables the prompts to be amended without
    needing to edit the code, restart an active session, and so on.</dd>
  <dt>tests</dt>
  <dd>Contains a library of test questions for all the topics in the database.</dd>
  <dt>topics</dt>
  <dd>Contains the topics and subtopics within the lower keystage 2 mathematics syllabus.</dd>
  <dt>user_tests</dt>
  <dd>Users must take a test to 'pass' a given topic. Answering all the test questions
    successfully will result in the topic being marked as 'mastered'. When the user
    first starts a test, a copy of the test questions for the topic in question is
    added to this table for the user. This table keeps track of the user's progress through
    the test and which test questions are correct/incorrect.</dd>
  <dt>users</dt>
  <dd>Contains all the registered users, their passwords (as a hash), their name, and their last login/access time.</dd>
</dl>
