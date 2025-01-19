from dataclasses import dataclass
from datetime import date, time
from enum import Enum
from typing import Optional, TypedDict

import requests
import streamlit as st

from common.constants import SUL_HOST


class Ranking(Enum):
    WINNER = 1
    FINALIST = 2
    SEMI_FINALIST = 4
    QUARTER_FINALIST = 8


class EventFormat(Enum):
    LIMITED = "Limited"
    MODERN = "Modern"
    LEGACY = "Legacy"
    PIONEER = "Pioneer"
    STANDARD = "Standard"
    EDH = "Commander/EDH"
    DUEL_COMMANDER = "Duel Commander"
    PAUPER = "Pauper"
    OLD_SCHOOL = "Old School"
    PRE_MODERN = "Premodern"
    VINTAGE = "Vintage"
    MULTIFORMAT = "Multi-Format"


class Category(Enum):
    LOCAL = "Local"
    REGIONAL = "Regional"
    PREMIER = "Premier"
    # NATIONAL = "National"
    # QUALIFIER = "Qualifier"
    # GRAND_PRIX = "Grand Prix"
    OTHER = "Other"


class Result(TypedDict):
    player: str
    single_elimination_result: Ranking
    win_count: int
    loss_count: int
    draw_count: int


@dataclass
class NewEvent:
    name: str
    date: date
    start_time: time
    end_time: time
    format: EventFormat
    category: Category
    url: str
    description: str

    def to_api(self):
        return {
            "name": self.name,
            "date": self.date.isoformat(),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "format": self.format.name,
            "category": self.category.name,
            "url": self.url,
            "description": self.description,
        }


class EventResult(TypedDict):
    event_url: str
    results: Optional[list[Result]]


def create_event(new_event: NewEvent):
    headers = {"Authorization": f"Token {st.session_state.token}"}
    url = f"{SUL_HOST}/api/events/"
    resp = requests.post(url, json=new_event.to_api(), headers=headers)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        st.error(resp.json())
        raise e
    return resp.json()


@st.dialog("Create a new event")
def create_event_dialog():
    st.write("New MTG Geneva event")

    name = st.text_input("Name")
    date = st.date_input("Date")
    start_time = st.time_input("Start time", value=time(17, 0))
    duration = st.number_input("Duration (m)", value=180, step=15)
    st.write(
        f"End time: {start_time.hour + duration // 60:0>2}:{start_time.minute + duration % 60:0>2}"
    )
    end_time = time(start_time.hour + duration // 60, start_time.minute + duration % 60)
    format = st.selectbox("Format", EventFormat, format_func=lambda f: f.value)
    category = st.selectbox("Category", Category, format_func=lambda f: f.value)
    url = st.text_input("URL")
    description = st.text_area("Description")

    if st.button("Create"):
        new_event = NewEvent(
            name=name,
            date=date,
            start_time=start_time,
            end_time=end_time,
            format=format,
            category=category,
            url=url,
            description=description,
        )
        st.json(new_event.to_api())
        create_event(new_event)
        st.success("Event created!")
        st.stop()
