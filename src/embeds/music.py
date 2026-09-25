import httpx, logging
logger = logging.getLogger("embeds")

from hikari.embeds import Embed

from src.models.deezer import TrackFull, AlbumFull, PlaylistFull
from src.utils.tools import color_average, calc_duration

async def build_track_embed(client: httpx.AsyncClient, track: TrackFull) -> Embed:
    return Embed(
        title = track.title,
        description = f"⋮ Disc: {track.disk_number}\n⋮ Index: {track.track_position}\n⋮ Duration: {calc_duration(track.duration)}\n⋮ Release Date: {track.release_date}\n⋮ ˙ . ꒷ 🍰 . 𖦹˙—",
        url = track.link,
        color = await color_average(client, track.album.cover_small)
    ).set_author(
        name = track.contributors[0].name,
        url = track.contributors[0].link,
        icon = track.contributors[0].picture_medium
    ).set_footer(
        text = f"Type: Track | DZ ID: {track.id} | ISRC: {track.isrc}"
    ).set_thumbnail(track.album.cover_big)

async def build_album_embed(client: httpx.AsyncClient, album: AlbumFull) -> Embed:
    return Embed(
        title = album.title,
        description = f"⋮ Kind: {album.record_type.capitalize()}\n⋮ Tracks: {album.nb_tracks}\n⋮ Duration: {calc_duration(album.duration)}\n⋮ Release Date: {album.release_date}\n⋮ ˙ . ꒷ 🍰 . 𖦹˙—",
        url = album.link,
        color = await color_average(client, album.cover_small)
    ).set_author(
        name = album.contributors[0].name,
        url = album.contributors[0].link,
        icon = album.contributors[0].picture_medium
    ).set_footer(
        text = f"Type: Album | DZ ID: {album.id}"
    ).set_thumbnail(album.cover_big)

async def build_playlist_embed(client: httpx.AsyncClient, playlist: PlaylistFull) -> Embed:
    return Embed(
        title = playlist.title,
        description = f"⋮ Description: {playlist.description if playlist.description else "None :("}\n⋮ Tracks: {playlist.nb_tracks}\n⋮ Duration: {calc_duration(playlist.duration)}\n⋮ Created at: {playlist.creation_date}\n⋮ Last Updated: {playlist.mod_date}\n⋮ ˙ . ꒷ 🍰 . 𖦹˙—",
        url = playlist.link,
        color = await color_average(client, playlist.picture_small)
    ).set_author(
        name = playlist.creator.name
    ).set_footer(
        text = f"Type: Playlist | DZ ID: {playlist.id}"
    ).set_thumbnail(playlist.picture_big)
