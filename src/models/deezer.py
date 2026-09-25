from __future__ import annotations
from typing import List, Literal, Generic, TypeVar
from enum import IntEnum
from pydantic import BaseModel, ConfigDict, field_validator

T = TypeVar("T")

class ExplicitContent(IntEnum):
    NOT_EXPLICIT = 0
    EXPLICIT = 1
    UNKNOWN = 2
    EDITED = 3
    NO_ADVICE_AVAILABLE = 6

class DeezerModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

def unwrap_data(value):
    """Unwraps collections that use {"data": [...] ...}"""
    if isinstance(value, dict) and "data" in value:
        return value["data"]
    return value

# Generic -----

class GenreInfo(DeezerModel):
    id: int
    name: str
    picture: str
    type: Literal["genre"] = "genre"

class CreatorInfo(DeezerModel):
    id: int
    name: str
    tracklist: str
    type: Literal["user"] = "user"

class HasLink(DeezerModel):
    link: str

class HasShare(DeezerModel):
    share: str

class HasRadio(DeezerModel):
    radio: bool

class HasPictures(DeezerModel):
    picture: str
    picture_small: str
    picture_medium: str
    picture_big: str
    picture_xl: str

class HasRole(DeezerModel):
    role: str

class HasUpc(DeezerModel):
    upc: str

class HasReleaseDate(DeezerModel):
    release_date: str

class HasIsrc(DeezerModel):
    isrc: str

class HasTimeAdd(DeezerModel):
    time_add: int

class HasTrackIndex(DeezerModel):
    track_position: int
    disk_number: int

class HasAvailableCountries(DeezerModel):
    available_countries: List[str]

class HasAudioFeatures(DeezerModel):
    bpm: int
    gain: float

class HasExplicitInfo(DeezerModel):
    explicit_lyrics: bool
    explicit_content_lyrics: ExplicitContent
    explicit_content_cover: ExplicitContent

class HasListMetadata(DeezerModel):
    nb_tracks: int
    fans: int

# Artist -----

class ArtistBase(DeezerModel):
    id: int
    name: str
    tracklist: str
    type: Literal["artist"] = "artist"

class AlbumTrackArtist(ArtistBase):
    """album.track.artist"""
    pass

class AlbumArtist(HasPictures, ArtistBase):
    """album.artist"""
    pass

class PlaylistTrackArtist(HasLink, ArtistBase):
    """playlist.track.artist"""
    pass

class PictureTracklistArtist(HasLink, HasPictures, ArtistBase):
    """playlist.tracklist.data.artist / search.artist"""
    pass

class TrackArtist(HasRadio, HasShare, HasLink, HasPictures, ArtistBase):
    """track.artist"""
    pass

class ContributorArtist(HasRole, TrackArtist):
    """track.contributors"""
    pass

# Album -----

class AlbumBase(DeezerModel):
    id: int
    title: str
    cover: str
    cover_small: str
    cover_medium: str
    cover_big: str
    cover_xl: str
    md5_image: str
    tracklist: str
    type: Literal["album"] = "album"

class TrackAlbum(HasLink, HasReleaseDate, AlbumBase):
    """track.album"""
    pass

class AlbumTrackAlbum(AlbumBase):
    """album.track.album"""
    pass

class PlaylistTrackAlbum(HasUpc, AlbumBase):
    """playlist.track.album"""
    pass

# Tracks -----

class TrackBase(HasExplicitInfo, DeezerModel):
    id: int
    readable: bool
    title: str
    title_short: str
    title_version: str
    link: str
    duration: int
    rank: int
    preview: str
    md5_image: str
    type: Literal["track"] = "track"

class SearchTrack(HasIsrc, TrackBase):
    """GET /search/*"""
    artist: PictureTracklistArtist
    album: AlbumTrackAlbum

class AlbumTrack(TrackBase):
    """album.track"""
    artist: AlbumTrackArtist
    album: AlbumTrackAlbum

class PlaylistTrack(HasIsrc, HasTimeAdd, TrackBase):
    """playlist.track"""
    artist: PlaylistTrackArtist
    album: PlaylistTrackAlbum

class PlaylistTracklistTrack(HasIsrc, HasTimeAdd, TrackBase):
    """GET /playlist/{id}/tracks"""
    artist: PictureTracklistArtist
    album: PlaylistTrackAlbum

class AlbumTracklistTrack(HasIsrc, HasTrackIndex, TrackBase):
    """GET /album/{id}/tracks"""
    artist: ArtistBase

# Full -----

class ArtistFull(TrackArtist):
    """GET /artist/{id}"""
    nb_album: int
    nb_fan: int

class TrackFull(HasIsrc, HasShare, HasTrackIndex, HasReleaseDate, HasAudioFeatures, HasAvailableCountries, TrackBase):
    """GET /track/{id}"""
    contributors: List[ContributorArtist]
    track_token: str
    artist: TrackArtist
    album: TrackAlbum

class AlbumFull(HasUpc, HasLink, HasShare, HasListMetadata, HasReleaseDate, HasExplicitInfo, AlbumBase):
    """GET /album/{id}"""
    genre_id: int
    genres: List[GenreInfo]
    label: str
    duration: int
    record_type: str
    available: bool
    contributors: List[ContributorArtist]
    artist: AlbumArtist
    tracks: List[AlbumTrack]

    @field_validator("tracks", "genres", mode="before")
    @classmethod
    def _unwrap(cls, value):
        return unwrap_data(value)

class TracklistInfo(DeezerModel, Generic[T]):
    """GET /[album, playlist]/{id}/tracks & /search/*"""
    checksum: str | None = None
    data: List[T]
    next: str | None = None # present when another page exists after this one
    total: int
    type: Literal["tracklist"] = "tracklist"

class PlaylistFull(HasListMetadata, HasLink, HasShare, HasPictures, DeezerModel):
    """GET /playlist/{id}"""
    id: int
    title: str
    description: str
    duration: int
    public: bool
    is_loved_track: bool
    collaborative: bool
    checksum: str
    tracklist: str
    creation_date: str
    add_date: str
    mod_date: str
    md5_image: str
    picture_type: str
    creator: CreatorInfo
    type: Literal["playlist"] = "playlist"
    tracks: List[PlaylistTrack]

    @field_validator("tracks", mode="before")
    @classmethod
    def _unwrap(cls, value):
        return unwrap_data(value)
