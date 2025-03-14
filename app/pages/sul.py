import logging
from typing import TypedDict
from urllib.parse import urljoin

import requests
import streamlit as st
from dateparser import parse
from dialog.event import create_event_dialog
from pandas import DataFrame
from streamlit_calendar import calendar

from common.constants import SUL_HOST

st.set_page_config(
    page_title="Swiss Unity league",
    page_icon="👋",
)

st.warning("This is a work in progress, please don't share the link yet.")
# st.stop()


class MTGEvent(TypedDict):
    api_url: str
    name: str
    date: str
    start_time: str
    end_time: str
    format: str
    category: str
    url: str
    description: str
    organizer: str
    results: list


st.title("Swiss Unity league")

if "token" not in st.session_state:
    logging.debug("Init sessions state")
    st.session_state.token = None


def get_api_token(username: str, password: str) -> str:
    """Fetch the API key that can then be used on follow up requests."""
    url = f"{SUL_HOST}/api/auth/"
    data = {"username": username, "password": password}
    resp = requests.post(url, json=data)
    resp.raise_for_status()
    return resp.json()["token"]


@st.cache_data
def list_events() -> list[MTGEvent]:
    headers = {"Authorization": f"Token {st.session_state.token}"}
    url = urljoin(SUL_HOST, "/api/events/")
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    events = resp.json()
    return list(reversed(sorted(events, key=lambda e: e["date"])))


if st.session_state.token is None:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        st.session_state.token = get_api_token(username, password)
        st.rerun()

if st.session_state.token is None:
    st.warning("Please login to access the rest of the app.")
    st.stop()

all_events = list_events()


@st.cache_data
def get_date(event):
    start_time = parse(event["date"])
    end_time = parse(event["date"])
    if "start_time" in event and event["start_time"]:
        start_time = parse(event["date"] + f"T{event['start_time']}")
    if "end_time" in event and event["end_time"]:
        end_time = parse(event["date"] + f"T{event['end_time']}")

    return (start_time, end_time)


calendar_options = {
    "editable": False,
    "selectable": False,
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "listDay,timeGridDay,timeGridWeek,dayGridMonth",
    },
    "slotMinTime": "08:00:00",
    "slotMaxTime": "23:59:59",
    "initialView": "listDay",
    "resources": [
        {"id": "a", "title": "Building A"},
    ],
}


@st.cache_data
def parse_events(events):
    return [
        {
            "title": event["name"],
            "start": get_date(event)[0].isoformat(),
            "end": get_date(event)[1].isoformat(),
            "resourceId": "a",
            "url": event["url"],
        }
        for event in events
    ]


calendar_events = parse_events(all_events)

df = DataFrame(all_events)
st.write(df["category"].value_counts())

calendar = calendar(events=calendar_events, options=calendar_options)

if st.button("Create a new event"):
    create_event_dialog()
