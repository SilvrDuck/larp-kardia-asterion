"""
Mapping between captain sonar mecano sheet items and the esp32 pins.

Example mecano sheet at:
https://cdn.arstechnica.net/wp-content/uploads/2016/12/engineer-map-1-640x481.jpg

The code of a given switch/led on the sheet is of the form:
f"{HEADING}{TYPE}{FUNCTION}{NUMBER}"

Where:
    - HEADING is one of North (N), South (S), East (E), West (W)
    - TYPE is one of Fixable (F), Non-Fixable (N)
    - FUNCTION is one of Weapons (W), Radar (R), Silence (S), Nuclear (N)
    - NUMBER starts at 0 and is incremented for each switch/led of the same type

EG: NFW0 is the first fixable weapons switch on the north pannel.

The pins we can use are the following:

23 |       | 13 
22 |       | 14
21 |       | 27
19 | esp32 | 26
18 |       | 25
 5 |       | 33
 4 |       | 32
15 |       |

For testing purposes, it is easier to have a given pair of
switch/led on the same side of the board.
"""

SERVER_IP = "192.168.1.10"

CONTROL_PANEL = "pannel_a"

SWITCH_TOPIC = b"switch"
LED_TOPIC = b"led"

global_config = {
    "pannel_a": [
        {"code": "WFW0G", "switch": 13, "led": 14},
        {"code": "WFS0G", "switch": 27, "led": 26},
        {"code": "WFR0G", "switch": 25, "led": 33},
        {"code": "WNR0N", "switch": 21, "led": 19},
        {"code": "WNN0N", "switch": 4, "led": 15},
        {"code": "ENR0N", "switch": 23, "led": 22},
        {"code": "ENN0N", "switch": 18, "led": 5},
    ],
    "pannel_b": [
        {"code": "NFW0R", "switch": 13, "led": 14},
        {"code": "NFS0R", "switch": 27, "led": 26},
        {"code": "NFS1R", "switch": 25, "led": 33},
        {"code": "NNR0N", "switch": 21, "led": 19},
        {"code": "NNW0N", "switch": 4, "led": 15},
        {"code": "SNN0N", "switch": 23, "led": 22},
        {"code": "SNW0N", "switch": 18, "led": 5},
    ],
    "pannel_c": [
        {"code": "SFW0B", "switch": 13, "led": 14},
        {"code": "SFS0B", "switch": 27, "led": 26},
        {"code": "SFR0B", "switch": 25, "led": 33},
        {"code": "EFR0R", "switch": 4, "led": 15},
        {"code": "EFS0B", "switch": 23, "led": 22},
        {"code": "EFW0G", "switch": 18, "led": 5},

    ],
}

all_codes = [conf["code"] for panel in global_config.values() for conf in panel]
assert len(set(all_codes)) == len(all_codes), "Duplicate codes found in config"

all_pins = lambda panel_name: sum([
    [conf["switch"], conf["led"]] for conf in global_config[panel_name]
], [])
for panel_name in global_config.keys():
    assert len(set(all_pins(panel_name))) == len(all_pins(panel_name)), "Duplicate pins found in config"
