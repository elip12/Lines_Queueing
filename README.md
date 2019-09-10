# Lines_Queueing
Otree experiment written for the LEEPS Lab at the University of California, Santa Cruz.


## Description
This is a real-time economics experiment written in Otree and Otree-redwood (UCSC LEEPS Lab otree websocket extension).
It simulates a queue of people who are waiting to go into a 'service room', where they accumulate money. There are different
modes of play, but in general players are incentivized to enter the service room as soon as possible. They have the ability
to try to swap places with other players in the queue. Sometimes, they are able to offer a portion of their payoff
to the players with whom they want to swap.

models.py defines the data fields that the experiment facilitator will collect after the experiment completes (that is,
the fields that each player will unknowingly enter data into via their actions - attempt to trade or not, accept trades
or not, etc). It also defines a state machine that serves as the backend. For example, when a player enters the service room,
a message is sent to the state machine saying their time in the service room has started. The state machine updates the positions
of all other players in the queue (advancing them by 1), then reboradcasts the new state to every player.

pages.py defines the different screens participants navigate through in the experiment.

templates/Lines_Queueing/ holds the html for each screen (also known as a page). The queue page is written with Vue.js.
When a message is sent from models.py over websockets to the HTML queue page, the Vue machine updates the html, changing
what players see. Following the previous example, each players screen would change to show them having advanced one position
in the queue.

Otree documentation: https://otree.readthedocs.io/en/latest/
Demo server where you can play this a configuration of this app: leeps-otree.ucsc.edu:8000/demo. Click 'lines fork'.

## License
This software is licensed under the MIT license.
Copyright 2019 Eli Pandolfo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
