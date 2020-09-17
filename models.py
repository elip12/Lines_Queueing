from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BasePlayer,
    Currency as c,
    currency_range,
)
from otree_redwood.models import Group as RedwoodGroup
from . import config as config_py
import random
import json
from datetime import datetime
from collections import OrderedDict
from jsonfield import JSONField
"""
Eli Pandolfo <epandolf@ucsc.edu>

Notes to ask Kristian:
    state of queue
    num players
    different num players in a group
"""


class Constants(BaseConstants):
    name_in_url = 'Lines_Queueing'
    participation_fee = c(5)
    
    instructions = 'Lines_Queueing/CheatSheet.html'
    instructions_swap = 'Lines_Queueing/CheatSheetSwap.html'
    instructions_tili = 'Lines_Queueing/CheatSheetTili.html'
    instructions_double = 'Lines_Queueing/CheatSheetDouble.html'
    instructions_token = 'Lines_Queueing/CheatSheetToken.html'

    config = config_py.export_data()
    #for g in config:
    #    for r in g:
    #        print(r['settings'])
    #        for p in r['players']:
    #            print(p)
    #        print('\n')
    #print('CONFIG EXPORTED')
    num_rounds = len(config[0])
    print('NUM_ROUNDS:', num_rounds)
    num_players = sum([len(group[0]['players']) for group in config])
    num_players = len(config[0][0]['players'])

    print('NUM PLAYERS: ', num_players)

    players_per_group = len(config[0][0]['players'])

    print('PLAYERS PER GROUP: ', players_per_group)

    #players_per_group = 4

    # these will be displayed to players in the UI. Defined here for consistency and
    # a central location
    alert_messages = {
        'cutting': 'You have cut the line',
        'cutted': 'Someone has cut in front of you',
        'requested': 'You have been requested to swap',
        'tokenRequested': 'You have been requested to swap, for a token',
        'requesting': 'You have requested to swap',
        'accepted': 'Your swap request has been accepted',
        'accepting': 'You have accepted a swap request',
        'declined': 'Your swap request has been declined',
        'declining': 'You have declined a swap request',
        'unv_other': 'Requestee is currently in a trade',
        'next_self': 'You have entered the service room.',
        'next_queue': 'You have advanced one position in the queue',
        'next_queue2': 'You have advanced one position in the queue ',
        'bad_bid': 'Your bid must be between 0 and your current payoff',
        'none': '',
    }



class Player(BasePlayer):

    time_Instructions = models.LongStringField()
    time_Queue = models.LongStringField()
    time_Service = models.LongStringField()
    time_BP = models.LongStringField()
    time_Results = models.LongStringField()

    # amount of money player starts with
    endowment = models.FloatField()

    # tokens gained in token mode
    tokens = models.IntegerField(default=0)

    # position in queue player starts at
    start_pos = models.IntegerField()
    end_pos = models.IntegerField()

    # time player takes to get serviced
    service_time = models.FloatField()

    # time player is waiting in the queue before being serviced
    waiting_time = models.FloatField()

    # $ per second player makes after being serviced, for gain mode
    # OR $ per second player loses in waiting & service rooms, for lose mode
    pay_rate = models.FloatField()

    # Adding double action now (which is technically still swapping by bid, but
    # for now will separate the two
    # method by which players swap: bid, swap, or cut
    swap_method = models.StringField()
    # method by which players accumulate money: gain or lose
    pay_method = models.StringField()

    # money player leaves the round with
    round_payoff = models.FloatField()

    # discrete and messaging enabled/disabled
    discrete = models.BooleanField()
    messaging = models.BooleanField()
    # c (cost per time not in service)
    cost = models.FloatField()

    waiting = models.FloatField(default=0)

    def set_payoffs(self):
        self.payoff = self.in_round(
            self.session.vars['pr']).round_payoff
        # self.participant.payoff += self.in_round(
        #     self.session.vars['pr']).round_payoff
        # self.participant.payoff += self.payoff
        print('in set payoffs')
        print(self.participant.payoff)
        print(self.round_payoff)
        self.participant.payoff = self.round_payoff
        print(self.participant.payoff)
    
    # quiz question after the instruction and before the practice round. general quiz.  
    quiz1 = models.StringField(
        choices=[
            'Player user ID',
            'Player position in the line'
        ],
        widget=widgets.RadioSelect,
        label='Question: What does the number mean in each circle on the screen?'
    )

    def quiz1_error_message(self, value):
        if value != 'Player position in the line':
            return 'This is the wrong answer. Please choose the correct one.'
       
    quiz2 = models.StringField(
        choices=[
            'The one in front of you',
            'The one behind you',
            'Both the one in front of and behind you',
            'Anyone in the line'
        ],
        widget=widgets.RadioSelect,
        label='Question: Which player can you interact with in each period?'
    )

    def quiz2_error_message(self, value):
        if value != 'Both the one in front of and behind you':
            return 'This is the wrong answer. Please choose the correct one.'
     
    quiz3 = models.StringField(
        choices=[
            'That player is currently involved in other transactions.',
            'That player rejects everyone’s transactions.',
            'You are not allowed to switch in that period.'
        ],
        widget=widgets.RadioSelect,
        label='Question: In some cases your trade button turns grey and you cannot trade with players in front of you. Why does this happen?'
    )

    def quiz3_error_message(self, value):
        if value != 'That player is currently involved in other transactions.':
            return 'This is the wrong answer. Please choose the correct one.'
        
    quiz4 = models.StringField(
        choices=[
            'Yes;Yes',
            'No;Yes',
            'Yes;No',
            'No;No'
        ],
        widget=widgets.RadioSelect,
        label='Question: Is there anything you can do after you get served? Will your payoff change after you received your service value and leave the service room?'
    )

    def quiz4_error_message(self, value):
        if value != 'No;No':
            return 'This is the wrong answer. Please choose the correct one.'
              
    quiz5 = models.StringField(
        choices=[
            'You get C since n is decreased by 1',
            'You do not have any benefit',
            'You get V immediately if you move forward'
        ],
        widget=widgets.RadioSelect,
        label='Question: What will you earn if you switch forward with someone else?'
    )

    def quiz5_error_message(self, value):
        if value != 'You get C since n is decreased by 1':
            return 'This is the wrong answer. Please choose the correct one.'
        
    # quiz for TILI treatment
    quiz9 = models.StringField(
        choices=[
           '49', '47', '43', '48'
        ],
        widget=widgets.RadioSelect,
        label='Question: Suppose you are playing Take/leave rule with a group of 6 players. Your final position is 4, endowment is 50, value is 10, and cost is 6. Your total gain from transactions is 5 so T=5. What is your final payoff?'
    )

    def quiz9_error_message(self, value):
        if value != '47':
            return 'This is the wrong answer. Please choose the correct one.'
        
    quiz10 = models.StringField(
        choices=[
           '5', '6', 'Any price', 'Depends'
        ],
        widget=widgets.RadioSelect,
        label='Question: Under Take/leave rule, if your cost is 5, what is the maximum amount you can offer to avoid any loss?'
    )

    def quiz10_error_message(self, value):
        if value != '5':
            return 'This is the wrong answer. Please choose the correct one.'
    
    quiz11 = models.StringField(
        choices=[
           '5', '4', 'Any price', 'Depends'
        ],
        widget=widgets.RadioSelect,
        label='Question: Under Take/leave rule, if your cost is 5, what is the minimum amount of offer you can accept to avoid any loss?'
    )

    def quiz11_error_message(self, value):
        if value != '5':
            return 'This is the wrong answer. Please choose the correct one.'
    
    quiz12 = models.StringField(
        choices=[
           '5', '6', '7', '0'
        ],
        widget=widgets.RadioSelect,
        label='Question: Suppose you are playing Take/leave rule, The player behind you proposes to pay 7 to you and you accept it. How much will you receive?'
    )

    def quiz12_error_message(self, value):
        if value != '7':
            return 'This is the wrong answer. Please choose the correct one.'
    
    # quiz for double treatment
    quiz13 = models.StringField(
        choices=[
           '49', '47', '43', '48'
        ],
        widget=widgets.RadioSelect,
        label='Question: Suppose you are playing Double rule with a group of 6 players. Your final position is 4, endowment is 50, value is 10, and cost is 6. Your total gain from transactions is 5 so T=5. What is your final payoff?'
    )

    def quiz13_error_message(self, value):
        if value != '47':
            return 'This is the wrong answer. Please choose the correct one.'
        
    quiz14 = models.StringField(
        choices=[
           '5', '6', 'Any price', 'Depends'
        ],
        widget=widgets.RadioSelect,
        label='Question: Under Double rule, if your cost is 5, what is the maximum amount you can offer to avoid any loss?'
    )

    def quiz14_error_message(self, value):
        if value != '5':
            return 'This is the wrong answer. Please choose the correct one.'
    
    quiz15 = models.StringField(
        choices=[
           '5', '4', 'Any price', 'Depends'
        ],
        widget=widgets.RadioSelect,
        label='Question: Under Double rule, if your cost is 5, what is the minimum amount you need to ask to avoid any loss?'
    )

    def quiz15_error_message(self, value):
        if value != '5':
            return 'This is the wrong answer. Please choose the correct one.'
    
    quiz16 = models.StringField(
        choices=[
           'Yes; 5', 'Yes; 4.5', 'Yes; 4', 'No; 0'
        ],
        widget=widgets.RadioSelect,
        label='Question: Suppose you are playing Double rule, you propose to pay 5 to the player in front of you and they propose to get paid 4. Will the transaction be accepted? How much will you transfer to that player? '
    )

    def quiz16_error_message(self, value):
        if value != 'Yes; 4.5':
            return 'This is the wrong answer. Please choose the correct one.'
        
    # quiz for token treatment        
    quiz18 = models.StringField(
        choices=[
           'Yes', 'No'
        ],
        widget=widgets.RadioSelect,
        label='Question: Under Token rule, does the number of tokens you own affect your final payoff?'
    )

    def quiz18_error_message(self, value):
        if value != 'No':
            return 'This is the wrong answer. Please choose the correct one.'
    
    quiz19 = models.StringField(
        choices=[
           'Yes', 'No'
        ],
        widget=widgets.RadioSelect,
        label='Question: Under Token rule, can you see others number of tokens before transaction?'
    )

    def quiz19_error_message(self, value):
        if value != 'Yes':
            return 'This is the wrong answer. Please choose the correct one.'
    
    quiz20 = models.StringField(
        choices=[
           'When I switch with someone behind me.',
           'When I switch with someone in front of me.'
        ],
        widget=widgets.RadioSelect,
        label='Question: Under Token rule, when will you earn tokens?'
    )

    def quiz20_error_message(self, value):
        if value != 'When I switch with someone behind me.':
            return 'This is the wrong answer. Please choose the correct one.'
        
    quiz21 = models.StringField(
        choices=[
           'When I switch with someone behind me.',
           'When I switch with someone in front of me.'
        ],
        widget=widgets.RadioSelect,
        label='Question: Under Token rule, when will you lose tokens?'
    )

    def quiz21_error_message(self, value):
        if value != 'When I switch with someone in front of me.':
            return 'This is the wrong answer. Please choose the correct one.'


class Group(RedwoodGroup):
    
    cache = JSONField(null=True)

    # needed for otree redwood; this should replace the need for the get_timeout_seconds method
    # in pages.QueueService, but for some reason does has no effect. This is essentially a wrapper
    # for the timeout_seconds variable anyway.

    def period_length(self):
        g_index = self.get_player_by_id(
            1).participant.vars[self.round_number]['group']
        return Constants.config[g_index][self.round_number - 1]['settings']['duration']

    # takes in the data transferred back and forth by channels,
    # and generates a list representing the queue, where each element in the list
    # IMPORTANT: this list represents the the entire queue, including players in the service room,
    # organized by when they arrived. This means that the 0th element in the returned list is the
    # first person to have entered the service room, and the last element in the list is the person
    # in the back of the queue.
    def queue_state(self, data):
        queue = {}
        for p in self.get_players():
            pp = data[str(p.id_in_group)]
            queue[pp['pos']] = pp['id']
        return [queue.get(k) for k in sorted(queue)]

    def new_metadata(self, g_index, requester_id, requestee_id, swap_method):
        m = OrderedDict()
        m['subsession_id'] = self.subsession_id
        m['round'] = self.round_number
        m['group_id'] = g_index
        m['requester_id'] = requester_id
        m['requester_pos_init'] = 'N/A'
        m['requester_pos_final'] = 'N/A'
        m['requester_bid'] = 'N/A'
        m['requestee_id'] = requestee_id
        m['requestee_pos_init'] = 'N/A'
        m['requestee_pos_final'] = 'N/A'
        m['requestee_bid'] = 'N/A'
        m['request_timestamp_absolute'] = 'N/A'
        m['response_timestamp_absolute'] = 'N/A'
        m['request_timestamp_relative'] = 'N/A'
        m['response_timestamp_relative'] = 'N/A'
        m['swap_method'] = swap_method
        m['status'] = 'N/A'
        m['message'] = 'N/A'
        m['transaction_price'] = 'N/A'
        return m

    """
        On swap event: this is a method defined by redwood. It is called when channel.send() is
        called in the javascript. That happens when
            1) someone starts a trade request by pressing the trade button,
            2) someone responds to a trade request by pressing the yes or no button,
            3) someone enters the service room and the entire queue moves forward.

        This method essentially defines a state machine. Each player has a state, represented by
        a dictionary with keys:
            id: id in group; a number from 1 to Constants.players_per_group,

            pos: position in queue at time of input; a number from -Constants.players_per_group to
                Constants.players_per_group,

            in_trade: boolean - true if this player has
                1) requested a trade and awaits a response;
                2) has been requested and has not yet responded,

            last_trade_request: timestamp of the last time this player clicked the trade button,

            requested: if this player has been requested to swap, the id of the player who made
                the request; None, or a number from 1 to Constants.players_per_group,

            requesting: if this player has made a request to swap, the id of the player who the
                request was made to; None, or a number from 1 to Constants.players_per_group,

            accepted: status of trade acceptance; 2 if requesting/no response/not in trade,
                1 if accepted, 0 if declined,

            alert: the current alert displayed to a player; a value in Constants.alert_messages,

            num_players_queue: the number of players who have not entered the service room at
                time of input; a number from 0 to Constants.players_per_group,

            num_players_service: the number of players who have entered the service room at
                time of input; a number from 0 to Constants.players_per_group,

            next; boolean: true if someone's service time has just run out, false otherwise;
                this is true when someone has passed into the service room, and everyone in
                the queue should move forward one position.

        The state machine takes in the state of each player, and alters the states of that
        player and other players accordingly.

        Note that upon this method being called, only one player's state can be different than it was
        directly before the method was called; because each time an event occurs,
        (request, response, or next) this method gets called.

        After updating all player's states, sends the data back to the client.

        - Need to ensure that this is true; otherwise, we might need a queue of pending events
    """

    def _on_swap_event(self, event=None, **kwargs):
        duration = self.period_length()
        start_time = event.value['start_time']
        # updates states of all players involved in the most recent event that triggered this
        # method call
        for p in self.get_players():
            """
            fields 'requesting', 'accepted', and 'next' of the player who initiated the event
            will be updated client-side;
            all other fields (the aggregate of which is the player state) are updated here

            player states; every player in the round is in exactly one of these states upon the
            initiation of an event (when this method gets called)

            - reset: no event that involves this player has been initiated by the most recent
                call to this method. There is no case for this, as the player's state
                is not updated.
            - service_clean: this player is not in trade and service time has run out
            - service_dirty: this player is in trade and service time has run out.
                This is an extension of service_clean.
            - service_other: other player's service time has run out
            - requesting_clean: player is not in_trade and requesting someone who is not in_trade
            - requesting_dirty: player is not in_trade and requesting someone who is in_trade
                the JS should make this impossible (disable trade button)
            - accepting: player is in_trade and accepting
            - declining: player is in_trade and declining
            """

            # gets this player's dict from the transmitted event
            p1 = event.value[str(p.id_in_group)]
            g_index = p.participant.vars[self.round_number]['group']
            swap_method = Constants.config[g_index][self.round_number - 1]['settings'][
                'swap_method'
            ]

            # someone has entered the service room
            if p1['next'] == True:
                if p1['pos'] == 0:
                    # service_clean
                    p1['alert'] = Constants.alert_messages['next_self']
                    # service_dirty
                    if p1['in_trade']:
                        p2_id = str(p1['requested'])
                        p2 = event.value[p2_id]
                        metadata = self.new_metadata(g_index, p2['id'], p1['id'], swap_method)
                        metadata['request_timestamp_absolute'] = p2['last_trade_request']

                        p1['in_trade'] = False
                        p2['in_trade'] = False
                        p1['requested'] = None
                        p2['requesting'] = None
                        p1['accepted'] = 2  # this should be unnecessary
                        p1['bid'] = None
                        p2['bid'] = None

                        metadata['transaction_price'] = 0

                        metadata['status'] = 'cancelled'
                        metadata['requester_pos_final'] = p2['pos']
                        metadata['requestee_pos_final'] = p1['pos']
                        timestamp = datetime.now().strftime('%s')
                        metadata['response_timestamp_absolute'] = timestamp
                        p2['last_trade_request'] = None
                        event.value[p2_id] = p2
                        event.value[str(p.id_in_group)] = p1
                        #metadata['queue'] = self.queue_state(event.value)
                        self.subsession.dump_metadata(duration, start_time, metadata)
                # service_other
                elif p1['pos'] > 0:
                    # this is the only case I know of where you can get the same alert twice in a row (except none)
                    # if you get the same alert twice in a row the alert will not display because the watch function
                    # that displays alerts only get called when the alert changes.
                    if p1['alert'] == Constants.alert_messages['next_queue']:
                        p1['alert'] = Constants.alert_messages['next_queue2']
                    else:
                        p1['alert'] = Constants.alert_messages['next_queue']
                else:
                    p1['alert'] = Constants.alert_messages['none']
                p1['next'] = False

            # someone has initiated a trade request
            elif not p1['in_trade'] and p1['requesting'] != None:
                p2 = event.value[str(p1['requesting'])]
                metadata = self.new_metadata(g_index, p1['id'], p2['id'], swap_method)
                metadata['requester_pos_init'] = p1['pos']
                metadata['requestee_pos_init'] = p2['pos']
                timestamp = p1['last_trade_request']
                metadata['request_timestamp_absolute'] = timestamp
                if swap_method == 'cut':
                    temp = p2['pos']
                    for i in event.value:
                        if i != 'metadata' and i != str(p.id_in_group):
                            if (
                                event.value[i]['pos'] < p1['pos']
                                and event.value[i]['pos'] >= p2['pos']
                            ):
                                event.value[i]['alert'] = Constants.alert_messages[
                                    'cutted'
                                ]
                                event.value[i]['pos'] += 1

                    p1['pos'] = temp
                    p1['alert'] = Constants.alert_messages['cutting']
                    metadata['requester_pos_final'] = p1['pos']
                    metadata['requestee_pos_final'] = p2['pos']
                    metadata['status'] = 'cut'
                    p1['requesting'] = None
                    p1['last_trade_request'] = None
                    event.value[str(p.id_in_group)] = p1
                    self.subsession.dump_metadata(duration, start_time, metadata)
                else:
                    # requesting_clean
                    if not p2['in_trade']:
                        # print('CORRECT ')
                        message = p1.get('message')
                        # print(message)
                        p1['in_trade'] = True
                        p2['in_trade'] = True
                        p2['requested'] = p1['id']

                        # reworked double auction
                        if swap_method == 'double':
                            p2['other_bid'] = p1['bid']
                        else:
                            p2['bid'] = p1['bid']

                        p2['message'] = message
                        p1['alert'] = Constants.alert_messages['requesting']
                        p2['alert'] = Constants.alert_messages['requested']
                        event.value[str(p1['requesting'])] = p2
                        self.subsession.dump_metadata(duration, start_time, metadata)
                    # requesting_dirty; the js should prevent the logic from ever reaching this
                    else:
                        p1['requesting'] = None
                        p1['alert'] = Constants.alert_messages['unv_other']

            # someone has responded to a trade request
            elif p1['in_trade'] and p1['requested'] != None:
                if p1['accepted'] != 2:

                    p2_id = str(p1['requested'])
                    p2 = event.value[p2_id]
                    metadata = self.new_metadata(g_index, p2_id, p1['id'], swap_method)
                    metadata['request_timestamp_absolute'] = p2['last_trade_request']
                    timestamp = datetime.now().strftime('%s')
                    metadata['response_timestamp_absolute'] = int(timestamp) * 1000

                    metadata['requester_bid'] = p2.get('bid', 'N/A')
                    metadata['requestee_bid'] = p1.get('bid', 'N/A')
                    # declining
                    if p1['accepted'] == 0:
                        p1['in_trade'] = False
                        p2['in_trade'] = False
                        p1['requested'] = None
                        p2['requesting'] = None
                        p1['accepted'] = 2
                        p1['alert'] = Constants.alert_messages['declining']
                        p2['alert'] = Constants.alert_messages['declined']
                        p2['bid'] = None
                        p1['bid'] = None
                        metadata['status'] = 'declined'

                    # accepting
                    elif p1['accepted'] == 1:

                        p1['in_trade'] = False
                        p2['in_trade'] = False
                        p1['requested'] = None
                        p2['requesting'] = None
                        p1['accepted'] = 2
                        temp = p1['pos']
                        p1['pos'] = p2['pos']
                        p2['pos'] = temp
                        p1['alert'] = Constants.alert_messages['accepting']
                        p2['alert'] = Constants.alert_messages['accepted']

                        # fix for typeError when accepting a swap during which
                        # the swapMethod is 'swap'
                        if swap_method == 'swap':
                            p2['bid'] = None

                        elif swap_method == 'token':

                            p2['tokens'] -= 1
                            p1['tokens'] += 1

                            p2['bid'] = -float(p1['bid'])

                        elif swap_method == 'take/Leave':
                            p2['bid'] = -float(p1['bid'])

                        else:
                            # reworked double auction
                            p2['other_bid'] = p1['bid']
                            av_bid = ( float(p1['bid']) + float(p2['bid']) ) / 2 
                            p2['average_bid'] = -av_bid
                            p1['average_bid'] = av_bid

                        metadata['status'] = 'accepted'

                    metadata['requester_pos_final'] = p2['pos']
                    metadata['requestee_pos_final'] = p1['pos']
                    message = p1.get('message', 'N/A')
                    if message == '':
                        message = 'N/A'
                    metadata['message'] = message
                    if swap_method == 'take/Leave':
                        metadata['transaction_price'] = p1.get('bid')
                    elif swap_method == 'double':
                        metadata['transaction_price'] = p1.get('average_bid')
                    else:
                        metadata['transaction_price'] = 'N/A'
                    p2['last_trade_request'] = None
                    event.value[p2_id] = p2
                    event.value[str(p.id_in_group)] = p1
                    self.subsession.dump_metadata(duration, start_time, metadata)

            event.value[str(p.id_in_group)] = p1  # partially redundant
        
        # broadcast the updated data out to all subjects
        self.send('swap', event.value)
        # cache state of queue so that client pages will not reset on reload
        self.cache = event.value
        # manually save all updated fields to db. otree redwood thing
        self.save()

class Subsession(BaseSubsession):
    
    def dump_metadata(self, duration=None, start_time=None, metadata=None):
        if metadata == None:
            s = ','.join([
                'subsession_id',
                'round',
                'group_id',
                'requester_id',
                'requester_pos_init',
                'requester_pos_final',
                'requester_bid',
                'requestee_id',
                'requestee_pos_init',
                'requestee_pos_final',
                'requestee_bid',
                'request_timestamp_absolute',
                'response_timestamp_absolute',
                'request_timestamp_relative',
                'response_timestamp_relative',
                'swap_method',
                'status',
                'message',
                'transaction_price',
            ])
        else:
            if metadata['request_timestamp_absolute'] != 'N/A':
                metadata['request_timestamp_relative'] = \
                    int(metadata['request_timestamp_absolute']) / 1000 - start_time
            if metadata['response_timestamp_absolute'] != 'N/A':
                metadata['response_timestamp_relative'] = \
                    int(metadata['response_timestamp_absolute']) / 1000 - start_time
            strvals = (str(e) for e in metadata.values())
            s = ','.join(strvals)
        fname = self.session.vars['data_fname'] + '_metadata.csv'
        with open(fname, 'a+') as f:
            f.write(s + '\n')

    def creating_session(self):
        if self.round_number == 1:

            data_fname = f'Lines_Queueing/data/lines_queueing_{self.session.code}'
            self.session.vars['metadata'] = {}
            self.session.vars['metadata_requests'] = {}
            self.session.vars['data_fname'] = data_fname

            non_practice_rounds = []

            # Constants.config[group number][round]
            group0 = Constants.config[0]
            for round_num, period in enumerate(group0):
                if period['settings']['block_id'] is not 0:
                    non_practice_rounds.append(round_num+1)

            self.session.vars['pr'] = random.choice(non_practice_rounds)
            # self.session.vars['pr'] = random.randint(2, Constants.num_rounds)

            # just dump header
            self.dump_metadata()

        self.group_randomly()

        self.session.vars[self.round_number] = [{}
                                                for i in range(len(self.get_groups()))]
        for g_index, g in enumerate(self.get_groups()):
            g_data = Constants.config[g_index][self.round_number - 1]['players']
            # sets up each player's starting values
            for p in g.get_players():
                p.participant.vars[self.round_number] = {}
                p.participant.vars[self.round_number]['pay_rate'] = g_data[
                    p.id_in_group - 1
                ]['pay_rate']
                p.participant.vars[self.round_number]['c'] = g_data[p.id_in_group - 1][
                    'c'
                ]
                p.participant.vars[self.round_number]['service_time'] = g_data[
                    p.id_in_group - 1
                ]['service_time']
                p.participant.vars[self.round_number]['start_pos'] = g_data[
                    p.id_in_group - 1
                ]['start_pos']
                p.participant.vars[self.round_number]['endowment'] = g_data[
                    p.id_in_group - 1
                ]['endowment']
                p.participant.vars[self.round_number]['group'] = g_index
                p_data = {
                    'id': p.id_in_group,
                    'pos': p.participant.vars[self.round_number]['start_pos'],
                    'in_trade': False,
                    'last_trade_request': None,
                    'requested': None,
                    'requesting': None,
                    'bid': None,
                    'accepted': 2,
                    'alert': Constants.alert_messages['none'],
                    'num_players_queue': Constants.num_players,
                    'num_players_service': 0,
                    'next': False,
                    'tokens': 0,
                }

                self.session.vars[self.round_number][g_index][p.id_in_group] = p_data

"""
metadata structure:
    { 'timestamp': {'bid': None/$, status': 'accepted/declined/cancelled/cut', 'requester': #, 'requestee': #, 'queue': [#,#,#...]}, ... }
"""
