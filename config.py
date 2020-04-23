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
            "duration": 60,
            "swap_method": "token",
            "pay_method": "gain",
            "k": [1-(3/60),(1/60),(1/60),(1/60)],
            "service_distribution": 1,
            "discrete": True,
            "messaging": False,
            #"tokenSwap": True,
            "block": 1,
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


def shuffle(data):
    for i, group in enumerate(data):
        for j, period in enumerate(group):
            if "start_pos" not in data[i][j]["players"][0]:
                positions = [n for n in range(1, len(period["players"]) + 1)]
                random.shuffle(positions)
                for k, player in enumerate(period["players"]):
                    data[i][j]["players"][k]["start_pos"] = positions[k]
            random.shuffle(
                data[i][j]["players"]
            )  # shuffle order of players within periods
        random.shuffle(data[i])  # shuffle order of periods withing groups
    random.shuffle(data)  # shuffle order of groups

    return data


# exports data to a csv format
def export_csv(fname, data):
    pass


# exports data to models.py
# formats data to make it easier for models.py to parse it
def export_data():
    # error handling & filling defaults

    for i, group in enumerate(data):
        for j, period in enumerate(group):
            if "settings" not in period:
                raise ValueError("Each period must contain settings dict")

            if "players" not in period:
                raise ValueError("Each period must contain players dict")

            settings = period["settings"]
            players = period["players"]

            if "duration" not in settings:
                raise ValueError("Each period settings must have a duration")

            if "swap_method" not in settings:
                raise ValueError(
                    "Each period settings must have a swap_method variable"
                )

            # For now, will comment out this swap_method check to allow for testing
            # of the double auction
            """
            if settings['swap_method'] not in ['cut', 'swap', 'bid']:
                raise ValueError('Each period settings swap_method variable \
                    must be either \'bid\', \'swap\' or \'cut\'')
            """

            if "pay_method" not in settings:
                raise ValueError(
                    "Each period settings must have a pay_method variable")

            if settings["pay_method"] not in ["gain", "lose"]:
                raise ValueError(
                    "Each period settings pay_method variable \
                    must be either 'gain' or 'lose'"
                )
            if "pay_rate" not in players[0]:
                raise ValueError("Players must have pay_rates")

            if "service_time" not in players[0]:
                if "k" not in settings:
                    raise ValueError(
                        "Period settings must have a k variable if players \
                        do not define service ti"
                    )

                if "service_distribution" not in settings:
                    data[i][j]["settings"]["service_distribution"] = 1

                sd = settings["service_distribution"]
                t = settings["duration"]
                k = settings["k"]

                vals = [random.randrange(sd) + 1 for p in players]
                vals = [v / sum(vals) for v in vals]
                # vals = [round(v * k * t) for v in vals]
                # vals = [round(vals[i] * k[i] * t) for i in range(len(k))]
                vals = [round(k[i] * t) for i in range(len(k))]
                # print(vals)
                positions = [n for n in range(1, len(period["players"]) + 1)]
                for k, _ in enumerate(players):
                    data[i][j]["players"][k]["service_time"] = vals
                    data[i][j]["players"][k]["start_pos"] = positions[k]

    print("exported data is")
    print(data[0][0])
    # data.append(data[0])
    with open('older.json', 'w') as outfile:
        json.dump(data, outfile)

    return data
