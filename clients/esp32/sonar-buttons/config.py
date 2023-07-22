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
"""

SERVER_IP = "192.168.1.40"

SWITCH_TOPIC = "switch"
LED_TOPIC = "led"

global_config = {
    "pannel_a": [
        {"code": "WFW0", "switch": 4, "led": 23},
        {"code": "WFS0", "switch": 18, "led": 19},
        {"code": "WFR0", "switch": 14, "led": 26},
        {"code": "WNR0", "switch": 13, "led": 27},
        {"code": "WNN0", "switch": 25, "led": 32},
        {"code": "ENR0", "switch": 34, "led": 21},
        {"code": "ENN0", "switch": 35, "led": 22},
    ],
    "pannel_b": [
        {"code": "NFW0", "switch": 4, "led": 23},
        {"code": "NFS0", "switch": 13, "led": 25},
        {"code": "NFS1", "switch": 14, "led": 26},
        {"code": "NNR0", "switch": 18, "led": 27},
        {"code": "NNW0", "switch": 19, "led": 32},
        {"code": "SNN0", "switch": 21, "led": 34},
        {"code": "SNW0", "switch": 22, "led": 35},
    ],
    "pannel_c": [
        {"code": "SFW0", "switch": 4, "led": 23},
        {"code": "SFS0", "switch": 13, "led": 25},
        {"code": "SFR0", "switch": 14, "led": 26},
        {"code": "EFR0", "switch": 18, "led": 27},
        {"code": "EFS0", "switch": 19, "led": 32},
        {"code": "EFW0", "switch": 21, "led": 34},

    ],
}

all_codes = [conf["code"] for panel in global_config.values() for conf in panel]
assert len(set(all_codes)) == len(all_codes), "Duplicate codes found in config"








