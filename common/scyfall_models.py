from datetime import date
from typing import Dict, List, Literal, Optional

from pydantic import UUID4, AnyUrl, BaseModel

Color = Literal["W", "U", "B", "R", "G"]


class CardFace(BaseModel):
    artist: Optional[str]
    artist_ids: Optional[List[str]]
    attraction_lights: Optional[List[str]]
    booster: bool
    border_color: str
    card_back_id: UUID4
    collector_number: str
    content_warning: Optional[bool]
    digital: bool
    finishes: List[str]
    flavor_name: Optional[str]
    flavor_text: Optional[str]
    frame_effects: Optional[List[str]]
    frame: str
    full_art: bool
    games: List[str]
    highres_image: bool
    illustration_id: Optional[UUID4]
    image_status: str
    image_uris: Optional[Dict[str, AnyUrl]]
    oversized: bool
    prices: Dict[str, Optional[str]]
    printed_name: Optional[str]
    printed_text: Optional[str]
    printed_type_line: Optional[str]
    promo: bool
    promo_types: Optional[List[str]]
    purchase_uris: Optional[Dict[str, AnyUrl]]
    rarity: str
    related_uris: Dict[str, AnyUrl]
    released_at: date
    reprint: bool
    scryfall_set_uri: AnyUrl
    set_name: str
    set_search_uri: AnyUrl
    set_type: str
    set_uri: AnyUrl
    set: str
    set_id: UUID4
    story_spotlight: bool
    textless: bool
    variation: bool
    variation_of: Optional[UUID4]
    security_stamp: Optional[str]
    watermark: Optional[str]
    preview_previewed_at: Optional[date]
    preview_source_uri: Optional[AnyUrl]
    preview_source: Optional[str]


class RelatedCard(BaseModel):
    id: UUID4
    object: str
    component: str
    name: str
    type_line: str
    uri: AnyUrl


class CoreCard(BaseModel):
    arena_id: Optional[int]
    id: UUID4
    lang: str
    mtgo_id: Optional[int]
    mtgo_foil_id: Optional[int]
    multiverse_ids: Optional[List[int]]
    tcgplayer_id: Optional[int]
    tcgplayer_etched_id: Optional[int]
    cardmarket_id: Optional[int]
    object: str
    layout: str
    oracle_id: Optional[UUID4]
    prints_search_uri: AnyUrl
    rulings_uri: AnyUrl
    scryfall_uri: AnyUrl
    uri: AnyUrl


class GameplayCard(CoreCard):
    all_parts: Optional[List[RelatedCard]] = None
    card_faces: Optional[List[CardFace]] = None
    cmc: float
    color_identity: List[Color]
    color_indicator: Optional[List[Color]] = None
    colors: Optional[List[Color]] = None
    defense: Optional[str] = None
    edhrec_rank: Optional[int] = None
    hand_modifier: Optional[str] = None
    keywords: List[str]
    legalities: dict
    life_modifier: Optional[str] = None
    loyalty: Optional[str] = None
    mana_cost: Optional[str] = None
    name: str
    oracle_text: Optional[str] = None
    penny_rank: Optional[int] = None
    power: Optional[str] = None
    produced_mana: Optional[List[str]] = None
    reserved: bool
    toughness: Optional[str] = None
    type_line: str


class PrintedCard(GameplayCard):
    artist: Optional[str]
    artist_ids: Optional[List[str]]
    attraction_lights: Optional[List[str]]
    booster: bool
    border_color: str
    card_back_id: UUID4
    collector_number: str
    content_warning: Optional[bool]
    digital: bool
    finishes: List[str]
    flavor_name: Optional[str]
    flavor_text: Optional[str]
    frame_effects: Optional[List[str]]
    frame: str
    full_art: bool
    games: List[str]
    highres_image: bool
    illustration_id: Optional[UUID4]
    image_status: str
    image_uris: Optional[Dict[str, AnyUrl]]
    oversized: bool
    prices: Dict[str, Optional[str]]
    printed_name: Optional[str]
    printed_text: Optional[str]
    printed_type_line: Optional[str]
    promo: bool
    promo_types: Optional[List[str]]
    purchase_uris: Optional[Dict[str, AnyUrl]]
    rarity: str
    related_uris: Dict[str, AnyUrl]
    released_at: str
    reprint: bool
    scryfall_set_uri: AnyUrl
    set_name: str
    set_search_uri: AnyUrl
    set_type: str
    set_uri: AnyUrl
    set: str
    set_id: UUID4
    story_spotlight: bool
    textless: bool
    variation: bool
    variation_of: Optional[UUID4]
    security_stamp: Optional[str]
    watermark: Optional[str]
    preview_previewed_at: Optional[str]
    preview_source_uri: Optional[AnyUrl]
    preview_source: Optional[str]
