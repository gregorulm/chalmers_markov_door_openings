Input Generator for Cooling Cabinet Lab
Gregor Ulm, 2016
Chalmers University of Technology
Computer Science and Engineering Department
Distributed Computing and Systems Research Group

Brief description:
I wrote the Python code in this directory as part of a seed project in real-time
big data analytics, where we explored various approaches for predicting energy
consumption in supermarkets.

My code was used to generate a pseudo-random, but realistic, door opening pattern
of a six-door cooling cabinet, which is, or was, in use at Chalmers. The general
idea is as follows: there are three cooling cabinets, which have two doors each.
An arbitrary number of customers may open those doors at various times. There are
three states: closed, open, and semi-open. Transitions are according to
predetermined probabilities. The angle as well as force of every door opening
follows a uniform random distribution, and so does the duration of each door
opening. The underlying model is a Markov process with three states.

The script produces a CSV file that contains the input for a computer that
controls six robotic arms, which are able to operate independently from each
other. Each line specifies the position of each robot arm at a certain time
stamp.

