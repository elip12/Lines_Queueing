from ._builtin import Page, WaitPage
from .models import Constants
import json
from datetime import datetime
"""
Eli Pandolfo <epandolf@ucsc.edu>
"""


class Instructions(Page):

    form_model = 'player'
    form_fields = ['time_Instructions']

    def is_displayed(self):
        return self.round_number == 1


class QueueServiceWaitPage(WaitPage):
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

        return {
            'round_time_': Constants.config[g_index][self.round_number - 1]['settings'][
                'duration'
            ],
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
        if self.round_number == Constants.payoff_round_number:
            self.player.set_payoffs()


# round debrief, displayed after queue service page. Has no specific data yet
class BetweenPages(Page):
    form_model = 'player'
    form_fields = ['time_BP']

    def vars_for_template(self):
        all_players = self.group.get_players()
        # print('len of all_players is: ', len(all_players))
        # print('all_players is: ', all_players)

        endLine = {}
        displayStartLine = []

        for p in all_players:
            # print('p.start_pos is: ', p.start_pos)
            endLine[str(p.start_pos)] = p.id_in_group

        self.participant.vars[self.round_number]['tokens'] = self.player.tokens

        """

        print('start line is: ', str(startLine))

        for i in range(len(startLine)):
            displayStartLine.append(startLine[str(i + 1)])

        print('displaystartline is: ', displayStartLine)
        """

        return {
            'round': self.round_number,
            'endLine': sorted(endLine),
            'numPlayers': len(all_players),
            'id': self.player.id_in_group,
            'tokens': self.player.tokens,
            'roundpayoff': self.player.round_payoff,
            'group': self.group,
            'Asdf': self.group.get_players
        }


class AfterService(WaitPage):
    def after_all_players_arrive(self):
        self.group.cache = 'N/A'

# displays experiment results. Has no specific data set yet.
class Results(Page):
    form_model = 'player'
    form_fields = ['time_Results']

    def vars_for_template(self):
        return {}

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


# order in which pages are displayed. A page's is_displayed method
# can override this, and not all pages defined above need to be included
page_sequence = [
#    Instructions,
    QueueServiceWaitPage,
    QueueService,
    AfterService,
    BetweenPages,
    Results,
]
