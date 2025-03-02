# 1 Zopandrel, Hunger Dominus (ONE) 195
import re
from typing import Optional, TypedDict

from pydantic import BaseModel


REGEX_MOXFIELD = r"^(?:(?P<count>\d+) )?(?P<name>[^\<\[\(\n]*)\b(?: \((?P<set>[^\<\[\(\n]*)\))(?: (?P<num>[A-Z1-9]*-?\d+))$"
# 1 Agonasaur Rex
REGEX_MTGAO = r"^(?:(?P<count>\d+) )?(?P<name>[^\<\[\(]*)$"
# 1 Ertai Resurrected <showcase> [DMU] (F)
REGEX_MTG_GOLDFISH = r"^(?:(?P<count>\d+) )?(?P<name>[^\<\[\(\n]*)\b(?: <(?P<special>[^\<\[\(\n]*)>)?(?: \[(?P<set>[^\<\[\(\n]*)\])?(?: \((?P<foil>[^\<\[\(\n]*)\))?$"

# Order is important as the first match will be used
regex_types = [
    (REGEX_MTGAO, "mtgao"),
    (REGEX_MOXFIELD, "moxfield"),
    (REGEX_MTG_GOLDFISH, "mtggoldfish"),
]


class CardSearch(TypedDict):
    count: Optional[int] = None
    name: str
    set: Optional[str] = None
    num: Optional[str] = None
    special: Optional[str] = None
    foil: Optional[str] = None


def get_appropriate_regex(deck_list: list[str]):
    first_line = deck_list[0]
    for regex, name in regex_types:
        if re.match(regex, first_line):
            return (regex, name)

    raise ValueError(f"Could not find a matching regex, example: {first_line}")


def parse_deck_list(deck_list: list[str], regex: str):
    for line in deck_list:
        match = re.match(regex, line)
        if match:
            card_info = match.groupdict()
            card_info["count"] = (
                int(card_info.get("count")) if card_info.get("count") else None
            )
            yield card_info


def parse_deck_string(deck_list: str, given_name: Optional[str] = None):
    deck_list = [item.strip() for item in deck_list.split("\n") if item.strip()]

    if given_name:
        for regex, name in regex_types:
            if name == given_name:
                regex, name = regex, name
                break
        else:
            raise ValueError(f"Could not find a matching regex for {given_name}")
    else:
        regex, name = get_appropriate_regex(deck_list)

    return {
        "regex": name,
        "deck_list": list(parse_deck_list(deck_list, regex)),
    }
