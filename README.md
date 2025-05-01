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

## Repo folder structure
Within this repository are a number of folders, which are as follows:

[/php](php/)
