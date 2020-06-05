from ._builtin import Page, WaitPage
from .models import Constants
import json
from datetime import datetime
import pandas as pd
import numpy as np
"""
Eli Pandolfo <epandolf@ucsc.edu>
"""


class Welcome(Page):
    def is_displayed(self):
        return self.round_number == 1

class Instructions(Page):

    form_model = 'player'
    form_fields = ['time_Instructions']

    def is_displayed(self):
        return self.round_number == 1

class PracticeRound(Page):

    def is_displayed(self):
        return self.round_number == 1

    form_model = 'player'
    form_fields = [ ]

    def get_timeout_seconds(self):
        g_index = self.participant.vars[self.round_number]['group']
        return Constants.config[g_index][self.round_number - 1]['settings']['duration']

    def vars_for_template(self):
        g_index = self.participant.vars[self.round_number]['group']
        if self.group.cache is None:
            g_data = self.session.vars[self.round_number][g_index]
            g_data['start_time'] = int(datetime.now().strftime('%s')) + 1
            self.group.cache = g_data
        else:
            g_data = self.group.cache
        self.player.discrete = Constants.config[g_index][self.round_number -
                                                         1]['settings']['discrete']
        self.player.messaging = Constants.config[g_index][self.round_number -
                                                          1]['settings']['messaging']
        self.player.cost = self.participant.vars[self.round_number]['c']

        # if this block number is equal to the one before it
        # if this round number > 1
        # keep yo tokens

        if self.round_number > 1:

            previous_block = Constants.config[g_index][self.round_number - 2]['settings']['block_id']
            current_block = Constants.config[g_index][self.round_number - 1]['settings']['block_id']

            if current_block == previous_block:

                self.player.tokens = self.participant.vars[self.round_number-1]['tokens']

            else:

                self.player.tokens = 0

        total_service_time = 0
        players = Constants.config[g_index][self.round_number - 1]['players']
        for p in players:
            total_service_time += p['service_time']

        return {
            'round_time_': Constants.config[g_index][self.round_number - 1]['settings'][
                'duration'
            ],
            'first_time_': int(Constants.config[g_index][self.round_number - 1]['settings']['duration'] -
                total_service_time),
            'block_': Constants.config[g_index][self.round_number - 1]['settings']['block_id'],
            'pay_rate_': self.participant.vars[self.round_number]['pay_rate'],
            'c_': self.participant.vars[self.round_number]['c'],
            'service_time_': self.participant.vars[self.round_number]['service_time'],
            'start_pos_': self.participant.vars[self.round_number]['start_pos'],
            'round_': self.round_number,
            'num_players_': Constants.num_players,
            'data': g_data,
            'raw': self.session.vars,
            'id': self.player.id_in_group,
            'swap_method_': Constants.config[g_index][self.round_number - 1][
                'settings'
            ]['swap_method'],
            'pay_method_': Constants.config[g_index][self.round_number - 1]['settings'][
                'pay_method'
            ],
            'discrete': self.player.discrete,
            'messaging': self.player.messaging,
            'endowment_': self.participant.vars[self.round_number]['endowment'],
            'tokens_': self.player.tokens,
        }

    def before_next_page(self):
        if self.round_number == self.session.vars['pr']:
            self.player.set_payoffs()

class QueueServiceWaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number > 1
    pass

class PracticeRoundWaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number == 1
    pass


# queue room and service room. Because of otree-redwood's period_length
# requirement, and because the total time in both rooms is set but the time
# each player spends in each room varies, I think the best way to represent
# the rooms is with one page, and using JS to show both rooms.
class QueueService(Page):

    form_model = 'player'
    form_fields = [
        'time_Queue',
        'time_Service',
        'start_pos',
        'service_time',
        'pay_rate',
        'round_payoff',
        'endowment',
        'swap_method',
        'pay_method',
        'waiting_time',
        'end_pos',
        'tokens',
    ]

    def is_displayed(self):
        return self.round_number > 1

    def get_timeout_seconds(self):
        g_index = self.participant.vars[self.round_number]['group']
        return Constants.config[g_index][self.round_number - 1]['settings']['duration']

    def vars_for_template(self):
        g_index = self.participant.vars[self.round_number]['group']
        if self.group.cache is None:
            g_data = self.session.vars[self.round_number][g_index]
            g_data['start_time'] = int(datetime.now().strftime('%s')) + 1
            self.group.cache = g_data
        else:
            g_data = self.group.cache
        self.player.discrete = Constants.config[g_index][self.round_number -
                                                         1]['settings']['discrete']
        self.player.messaging = Constants.config[g_index][self.round_number -
                                                          1]['settings']['messaging']
        self.player.cost = self.participant.vars[self.round_number]['c']

        # if this block number is equal to the one before it
        # if this round number > 1
        # keep yo tokens

        if self.round_number > 1:

            previous_block = Constants.config[g_index][self.round_number - 2]['settings']['block_id']
            current_block = Constants.config[g_index][self.round_number - 1]['settings']['block_id']

            if current_block == previous_block:

                self.player.tokens = self.participant.vars[self.round_number-1]['tokens']

            else:

                self.player.tokens = 0

        total_service_time = 0
        players = Constants.config[g_index][self.round_number - 1]['players']
        for p in players:
            total_service_time += p['service_time']

        return {
            'round_time_': Constants.config[g_index][self.round_number - 1]['settings'][
                'duration'
            ],
            'first_time_': int(Constants.config[g_index][self.round_number - 1]['settings']['duration'] -
                total_service_time),
            'block_': Constants.config[g_index][self.round_number - 1]['settings']['block_id'],
            'pay_rate_': self.participant.vars[self.round_number]['pay_rate'],
            'c_': self.participant.vars[self.round_number]['c'],
            'service_time_': self.participant.vars[self.round_number]['service_time'],
            'start_pos_': self.participant.vars[self.round_number]['start_pos'],
            'round_': self.round_number,
            'num_players_': Constants.num_players,
            'data': g_data,
            'raw': self.session.vars,
            'id': self.player.id_in_group,
            'swap_method_': Constants.config[g_index][self.round_number - 1][
                'settings'
            ]['swap_method'],
            'pay_method_': Constants.config[g_index][self.round_number - 1]['settings'][
                'pay_method'
            ],
            'discrete': self.player.discrete,
            'messaging': self.player.messaging,
            'endowment_': self.participant.vars[self.round_number]['endowment'],
            'tokens_': self.player.tokens,
        }

    def before_next_page(self):
        if self.round_number == self.session.vars['pr']:
            self.player.set_payoffs()


# round debrief, displayed after queue service page. Has no specific data yet
class BetweenPages(Page):
    form_model = 'player'
    form_fields = ['time_BP']

    def is_displayed(self):
        return self.round_number >= 1

    def vars_for_template(self):
        g_index = self.participant.vars[self.round_number]['group']

        start = {}
        # {id: start_pos}
        for player_id in range(1, Constants.players_per_group + 1):
            player = self.group.get_player_by_id(player_id)
            # since p_data in session vars doesn't change from starting pos
            start[player_id] = self.session.vars[self.round_number][g_index][player_id]['pos']
        # sorted by value (start_pos/pos)
        start = {k: v for k, v in sorted(start.items(), key=lambda item: item[1])}
        # dict_keys of list of id's in starting line order
        # first element is first player id
        startLine = start.keys()

        # the last cache data
        endLine = self.group.queue_state(self.group.cache)

        self.participant.vars[self.round_number]['tokens'] = self.player.tokens

        fname = self.session.vars['data_fname'] + '_metadata.csv'
        data = pd.read_csv(fname)

        history = {}

        # gets all transactions from round that just occurred
        past_round = data.loc[(data['round'] == self.round_number) & (pd.isnull(data['status']) == False) &
                (data['group_id'] == g_index)]
        for row_index in range(len(past_round)):
            current_row = past_round.iloc[[row_index]]
            history[row_index] = {}
            history[row_index]['requestee_id'] = int(current_row['requestee_id'])
            history[row_index]['requester_id'] = int(current_row['requester_id'])
            history[row_index]['status'] = current_row['status'].iloc[0]
            transaction = current_row['transaction_price'].values[0]
            if transaction == None or transaction == 'N/A' or np.isnan(transaction) == True:
                history[row_index]['transaction_price'] = 0.0
            else:
                history[row_index]['transaction_price'] = float(current_row['transaction_price'])
            history[row_index]['message'] = current_row['message'].iloc[0]

        """

        print('start line is: ', str(startLine))

        for i in range(len(startLine)):
            displayStartLine.append(startLine[str(i + 1)])

        print('displaystartline is: ', displayStartLine)
        """

        return {
            'round': self.round_number,
            # lists are reversed to match the layout of line
            # [1,2,3,4]
            # player 4 is first, 3 is second, 2 is third, 1 is last
            'startLine': [a for a in reversed(list(startLine))],
            'endLine': [a for a in reversed(endLine)],
            'numPlayers': Constants.players_per_group,
            'history': history,
            'id': self.player.id_in_group,
            'tokens': self.player.tokens,
            'roundpayoff': self.player.round_payoff,
            'group': self.group,
            'Asdf': self.group.get_players
        }

    # def before_next_page(self):
    #     self.group.cache = 'N/A'

class AfterService(WaitPage):
    def is_displayed(self):
        return self.round_number >= 1

# displays experiment results
class Results(Page):
    form_model = 'player'
    form_fields = ['time_Results']

    def vars_for_template(self):

        return {
            'payoffRound': Constants.payoff_round_number,
            'payoffAmount': self.participant.payoff
        }

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


# order in which pages are displayed. A page's is_displayed method
# can override this, and not all pages defined above need to be included
page_sequence = [
#    Instructions,
    Welcome,
    PracticeRoundWaitPage,
    PracticeRound,
    QueueServiceWaitPage,
    QueueService,
    AfterService,
    BetweenPages,
    Results,
]
