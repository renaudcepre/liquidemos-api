# liquidemos-api

A liquid democracy project manager. Proof of concept, in progress

[![wakatime](https://wakatime.com/badge/user/a13a649f-3dcf-4d43-9798-099e450a805e/project/243518d9-eb63-4a83-8cba-9dd98d188498.svg)](https://wakatime.com/badge/user/a13a649f-3dcf-4d43-9798-099e450a805e/project/243518d9-eb63-4a83-8cba-9dd98d188498)

This project was started initially to level my skills in Django and the DRF. I've been thinking about creating a liquid
democracy based project manager for a long time, and I thought that it will be a good exercise to try doing it with
Django. As the purpose of the project is only the back-end, I just created a REST API.

## Liquid Democraty

The idea of liquid democracy, applied to politics, take its roots in direct democracy, A system where people vote
directly for each law, or projects. This system doesn't work any more as soon as there are too many things to vote for:
People cannot have all the skills and knowledge to give their opinion on each topic, and it becomes too much individual
work.

So, the idea of liquid democracy is to give the possibility to people to vote for each project, but also delegate their
votes for certain topics. For example, for a law concerning public health, a person may consider That he or she does not
have the competence to vote directly. He can then delegate his vote to a third party for the theme "public health". The
delegate now has a "vote weight" of 2 on the "healthcare" topic.

Note a person can delegate his vote for a topic where he himself is delegated, and so on.

## Projects

In our case, my objective was to make a project manager, which may be useful to build a new project, such as a website.
The project managing system is built around a tree of "projects". The top node of this tree is the main project, and
this project can have children. In the long run, the idea is to create a validation system which a project can be
Validated if all her kids get validated.

##### MPT

The project tree is implemented as a custom materialized path node:
Each node has a path encoded as `{parent_node_id} /{child_node_id} /...`
It makes the search for all children of a node in the database very fast:
just query all the node starts with a node path. Retrieving parents is also easy: delete a node identifier from the
path, and it gives it the parent path. I also store the node depth as an integer, for making easy to query nodes with a
certain depth
(e.g: query just the immediate children).

The maximum number of childs for a node is really huge: I encode the node_id in a custom base based on a charset,
see `encoder.py`. The maximum depht of the tree is limited by the maximum lenght of the CharField used, it also depends
of the number of childs, since a child can use more characters (e.g: `0/FFFFFF/`)

*[django-treebeard](https://django-treebeard.readthedocs.io/en/latest/api.html) is a package that provide a good
implentation of MPT.*

## Auth

The project use authentication with JWT, by using `django-allauth`, and `dj-rest-auth` packages. See tests.

## Project on pause

At the time of writing this, I am preparing to spend a month in Benin on a trip, and to search for a job on my return,
so the project is paused.

As I was expecting, building this project with a SQL database is pretty hard, at least to get optimized. Maybe for make
it really efficient, it will be interesting to switch to a graph database like Neo4j.

This project allowed me to see the limits of such a system, and to implement something interesting with Django.