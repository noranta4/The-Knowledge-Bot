# The Knowledge Bot
 Telegram chatbot able to answer to questions about general culture (querying) and able to learn by asking questions itself (enriching).
 
 Final project of the Natural Language Processing course, prof. Roberto Navigli.
 
 University project • 2017 - Natural Language Processing - MSc in Computer Science, I year
 
The source code is is accompanied by a report (`Anotnio_Norelli_final_report.pdf`), I highly reccomend you read it to understand the methods.

## Introduction
The goal of the project is to build a Telegram chatbot able to answer to questions about general culture
(querying) and able to learn by asking questions itself (enriching). This result is achieved using a knowledge
database. Every entry in the dataset is composed by a couple of concepts, the linking relation and a query-
answer couple that expresses this information. Breaking down the problem:

- In the querying modality the bot should be able to detect the key concept in the question, detect the
    relation associated to the question and search in the dataset an appropriate answer.
- In the enriching modality the bot should be able to find a concept-relation couple that makes
    sense and absent in the dataset, build a proper question from it, collect the answer from the user,
    detect the key concept in the answer of the user and store it, in order to update the dataset.

Additionally, the chatbot should be provided with a basic human computer interface, composed by a
proper design of the conversations and eventually by the usage of the Telegram chatbot perks (commands,
custom keyboards, text formatting...).

## Human computer interface

In order to simplify and make more straightforward the interaction with the user, a gold rule for chatbots
is to guide the conversation. So, taking this design choice, the chatbot begins to ask which is the preferred
domain of knowledge the user want to talk about, then it asks about the modality (querying or enriching)
and finally according to the modality it waits for a question or asks itself a first question. A custom
keyboard is implemented for all the choices to makes them faster and simplify the management of the
answers. As in the majority of chatbots, the bot messages are in natural language, this makes the user
interaction very natural and simple. The only command implemented by the chatbot is _/start_ , that is used
to begin the interaction or to reset it if the user wants to change domain or modality.

The following screenshots show a standard querying interaction.

<img src="https://github.com/noranta4/The-Knowledge-Bot/blob/master/img/photo5881876262568438195.jpg?raw=true" width="250"> <img src="https://github.com/noranta4/The-Knowledge-Bot/blob/master/img/photo5881876262568438204.jpg?raw=true" width="250"> <img src="https://github.com/noranta4/The-Knowledge-Bot/blob/master/img/photo5881876262568438205.jpg?raw=true" width="250">


## Comments and Conclusions
The chatbot models and implementation work properly, in particular the entity detection and the relation
recognition performance is satisfying (in a well-defined question, entities are identified in the 84% of
cases, the f1 score of the relation identifier on all classes is 85%). The speed of the bot is remarkable
despite the heavy use of APIs and the searches in the dataset. On the other hand, the quality of the dataset
has proved to be poor, less than 80% of entries are well-defined, some makes no sense, some have
incorrect relations and entities tags. The wide range of knowledge considered permits the inclusion of
very specific entries, that are the major part of the KBS, on the other hand this wide inclusion makes the
described entity-relation couples very sparse in the universe of all possible couples, so during a regular
user experience most of the time the chatbot answer is “Sorry, I have not an answer for this question”. A
dataset restricted to certain domains and with a better coverage seems more suitable.

See the report for a detailed discussion of the Chatbot and the performance evaluation.
