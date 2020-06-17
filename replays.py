import sc2reader
import json
import pprint
import math
from datetime import timedelta

replay_dir = '' ## fill in your replay dir
replay_file = replay_dir + 'Ever Dream LE (101).SC2Replay'
# replay_file = replay_dir + 'b-to-gm-on-time.SC2Replay'

replay = sc2reader.load_replay(replay_file)
pp = pprint.PrettyPrinter(indent=4)

print(replay.game_length)
print(replay.expansion)

events_to_exclude = [
    'CameraEvent',
    'TargetPointCommandEvent',
    'SelectionEvent',
    'GetControlGroupEvent',
    'SetControlGroupEvent',
    'TargetUnitCommandEvent'
]

events_to_include = [
    'UnitBornEvent',
    'UnitDiedEvent',
    'UnitInitEvent',
    'UnitDoneEvent'
]

dummy_objects = [
    'Beacon',
    'MineralField',
    'PurifierMineralField',
    'VespeneGeyser',
    'RichVespeneGeyser',
    'DestructibleRock',
    'ShakurasVespeneGeyser',
    'UnbuildableBricksDestructible',
    'ProtossVespeneGeyser',
    'KarakMale',
    'UnbuildablePlatesDestructible',
    'XelNagaTower',
    'KarakFemale'
]

def shouldFilter(event):
    type_name = event.get('unit_type_name', None)
    if (type_name != None):
        for dummy in dummy_objects:
            if (type_name.startswith(dummy)):
                return True
    return False

units_by_user = dict()
units_that_died = set()
units_building = set()
game_time = []
last_printed = []

def pretty_game_time():
    total_seconds = game_time[0]
    delta = timedelta(seconds = total_seconds)
    return str(delta)

def print_current_state():
    print('')
    print(pretty_game_time())
    for user in units_by_user.keys():
        units = units_by_user[user]
        units_by_type = dict()
        for unit in units:
            if unit not in units_that_died:
                unit_type = unit.split('[')[0]
                if unit_type not in units_by_type:
                    units_by_type[unit_type] = 0
                units_by_type[unit_type] = units_by_type[unit_type] + 1
        print(user)
        print(units_by_type)

def compute_units():
    count = 0
    for event in replay.events:
        event_info = event.__dict__
        if (event_info['name'] in events_to_exclude):
            continue
        if (event_info['name'] in events_to_include):
            if (not shouldFilter(event_info)):
                # 1.4 appears to be a magic number from "faster" game speed
                current_time = math.floor(event_info['second'] / 1.4)

                game_time.clear()
                game_time.append(current_time)
                # pp.pprint(event_info)

                print(pretty_game_time() + " " + event_info['name'] + " " + str(event_info['unit']))

                if (event_info['name'] == 'UnitDiedEvent'):
                    units_that_died.add(str(event_info['unit']))
                if (event_info['name'] == 'UnitDoneEvent'):
                    units_building.remove(str(event_info['unit']))

                user = event_info.get('unit_controller', None)
                if (user is None):
                    continue
                if user not in units_by_user.keys():
                    units_by_user[user] = set()
                if (event_info['name'] == 'UnitBornEvent'):
                    units_by_user[user].add(str(event_info['unit']))
                if (event_info['name'] == 'UnitInitEvent'):
                    units_by_user[user].add(str(event_info['unit']))
                    units_building.add(str(event_info['unit']))
                count = count + 1

                if (len(last_printed) == 0):
                    print_current_state()
                    last_printed.append(current_time)
                else:
                    last_time = last_printed[0]
                    if (current_time - last_time >= 20):
                        print_current_state()
                        last_printed.clear()
                        last_printed.append(current_time)

# for event in replay.events:
#     event_info = event.__dict__
#     if ('Spawning' in pp.pformat(event_info)):
#         pp.pprint(event_info)

compute_units()