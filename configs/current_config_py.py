import random
import math
import json


# [ all data:
#     [ group list
#         { round object
#             settings object
#             players list[
#                 player object
#             ]
#         }
#     ]
# ]

data = [[
    {  # Type 1: double, no communication, 8 players
        #
        "settings": {
            "duration": 1800,
            "swap_method": "token",
            "pay_method": "gain",
            "k": [0.1,0.1,0.1,0.7],
            "service_distribution": 1,
            "discrete": True,
            "messaging": False,
            #"tokenSwap": True,
        },
        "players": [
            {"pay_rate": 4, "endowment": 4, "c": random.random()},
            {"pay_rate": 4, "endowment": 4, "c": random.random()},
            {"pay_rate": 4, "endowment": 4, "c": random.random()},
            {"pay_rate": 4, "endowment": 4, "c": random.random()},
            #{"pay_rate": 4, "endowment": 4, "c": random.random()},
            #{"pay_rate": 4, "endowment": 4, "c": random.random()},
        ],
    } for i in range(4)

] ]
# data[1][1]['settings']['messaging'] = False
data[0][1]['settings']['swap_method'] = "swap"
data[0][2]['settings']['swap_method'] = "take/Leave"
data[0][3]['settings']['swap_method'] = "double"


