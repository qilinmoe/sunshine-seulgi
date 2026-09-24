from __future__ import annotations
from datetime import date, datetime
from enum import IntEnum
from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator

class ExplicitContent(IntEnum):
    NOT_EXPLICIT = 0
    EXPLICIT = 1
    UNKNOWN = 2
    EDITED = 3
    NO_ADVICE_AVAILABLE = 6

class DeezerModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

class BaseArtistInfo(DeezerModel):
    id: int
    name: str
    tracklist: HttpUrl

class ArtistInfo(BaseArtistInfo):
    link: HttpUrl | None = None # /artist and /track exclusive
    share: HttpUrl | None = None # /artist and /track exclusive
    picture: HttpUrl
    picture_small: HttpUrl
    picture_medium: HttpUrl
    picture_big: HttpUrl
    picture_xl: HttpUrl
    nb_album: int | None = None # /artist exclusive
    nb_fan: int | None = None # /artist exclusive
    radio: bool | None = None # Not in album.artist
    role: str | None = None # /track exclusive

class GenreInfo(DeezerModel):
    id: int
    name: str
    picture: HttpUrl

class BaseAlbumInfo(DeezerModel):
    id: int
    title: str
    cover: HttpUrl
    cover_small: HttpUrl
    cover_medium: HttpUrl
    cover_big: HttpUrl
    cover_xl: HttpUrl
    md5_image: str
    tracklist: HttpUrl

class AlbumInfo(BaseAlbumInfo):
    upc: str # Number as str
    link: HttpUrl
    share: HttpUrl
    genre_id: int
    genres: list[GenreInfo]
    label: str
    nb_tracks: int
    duration: int # Seconds
    fans: int
    release_date: date # yyyy-mm-dd
    record_type: str
    available: bool
    explicit_lyrics: bool
    explicit_content_lyrics: ExplicitContent
    explicit_content_cover: ExplicitContent
    contributors: list[ArtistInfo]
    artist: ArtistInfo
    tracks: list[AlbumTrackInfo] | None = None # /album exclusive

    @field_validator("tracks", "genres", mode="before")
    @classmethod
    def unwrap_data(cls, value):
        """Flattens tracks and genres for the sake of simplicity."""
        if isinstance(value, dict) and "data" in value:
            return value["data"]
        return value

class TracklistInfo(DeezerModel):
    data: list[AlbumTrackInfo]
    total: int
    next: HttpUrl | None = None # /search exclusive

class BaseTrackInfo(DeezerModel):
    id: int
    readable: bool
    title: str
    title_short: str
    title_version: str | None = None # Sometimes absent from /search
    isrc: str | None = None # /track and /tracklist exclusive
    link: HttpUrl
    share: HttpUrl | None = None # /track exclusive
    duration: int
    track_position: int | None = None # /track and /tracklist exclusive
    disk_number: int | None = None # /track and /tracklist exclusive
    rank: int
    release_date: date | None = None # YYYY-MM-DD | /track exclusive
    explicit_lyrics: bool
    explicit_content_lyrics: ExplicitContent
    explicit_content_cover: ExplicitContent
    preview: HttpUrl
    bpm: int | None = None # /track exclusive
    gain: float | None = None # /track exclusive
    available_countries: list[str] | None = None # /track exclusive
    contributors: list[ArtistInfo] | None = None # /track exclusive
    md5_image: str
    time_add: int | None = None # Unix time | /playlist exclusive
    track_token: str | None = None # /track exclusive
    artist: ArtistInfo | BaseArtistInfo

class AlbumTrackInfo(BaseTrackInfo):
    pass

class TrackInfo(BaseTrackInfo):
    album: AlbumInfo | BaseAlbumInfo | None = None # Not in tracklist.data.*

class PlaylistInfo(DeezerModel):
    id: int
    title: str
    description: str
    duration: int # Seconds
    public: bool
    is_loved_track: bool
    collaborative: bool
    nb_tracks: int
    fans: int
    link: HttpUrl
    share: HttpUrl
    picture: HttpUrl
    picture_small: HttpUrl
    picture_medium: HttpUrl
    picture_big: HttpUrl
    picture_xl: HttpUrl
    checksum: str
    tracklist: HttpUrl
    creation_date: datetime # YYYY-MM-DD hh:mm:ss
    add_date: datetime # YYYY-MM-DD hh:mm:ss
    mod_date: datetime # YYYY-MM-DD hh:mm:ss
    md5_image: str
    picture_type: str
    creator: BaseArtistInfo
    tracks: list[TrackInfo]

    @field_validator("tracks", mode="before")
    @classmethod
    def unwrap_data(cls, value):
        """Flattens tracks for the sake of simplicity."""
        if isinstance(value, dict) and "data" in value:
            return value["data"]
        return value
