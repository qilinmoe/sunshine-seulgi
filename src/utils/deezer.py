import os, httpx, logging
logger = logging.getLogger("deezer")

from src.models.deezer import AlbumFull, PlaylistFull, TrackFull, TracklistInfo

async def get_playlist_by_id(client: httpx.AsyncClient, id: int) -> PlaylistFull|None:
    response = await client.get(f"{os.getenv("deezer_url")}/playlist/{id}")
    if not response.is_success:
        logger.error("Failed to get playlist with id %s!", id)
        logger.debug("Response code: %s", response.status_code)
        return

    return PlaylistFull.model_validate(response.json())

async def get_album_by_id(client: httpx.AsyncClient, id: int) -> AlbumFull|None:
    response = await client.get(f"{os.getenv("deezer_url")}/album/{id}")
    if not response.is_success:
        logger.error(f"Failed to get album with id %s!", id)
        logger.debug("Response code: %s", response.status_code)
        return

    return AlbumFull.model_validate(response.json())

async def get_track_by_id(client: httpx.AsyncClient, id: int) -> TrackFull|None:
    response = await client.get(f"{os.getenv("deezer_url")}/track/{id}")
    if not response.is_success:
        logger.error(f"Failed to get track with id %s!", id)
        logger.debug("Response code: %s", response.status_code)
        return

    return TrackFull.model_validate(response.json())

async def get_tracklist_by_url(client: httpx.AsyncClient, url: str) -> TracklistInfo|None:
    response = await client.get(url)
    if not response.is_success:
        logger.error(f"Failed to get tracklist with id %s!", id)
        logger.debug("Response code: %s", response.status_code)
        return

    return TracklistInfo.model_validate(response.json())

async def get_tracklist_by_query(client: httpx.AsyncClient, query: str) -> TracklistInfo|None:
    response = await client.get(f"{os.getenv("deezer_url")}/search",
        params={
            "q": query,
            "order": "TRACK_ASC",
            "strict": "on"
        })
    if not response.is_success:
        logger.error("Failed to search for %s!", query)
        logger.debug("Response code: %s", response.status_code)
        return

    return TracklistInfo.model_validate(response.json())

async def get_result_by_url(client: httpx.AsyncClient, url: str) -> TrackFull|AlbumFull|PlaylistFull|None:
    if "/s/" in url:
        response = await client.get(url, follow_redirects=True) # By using follow_redirects, the special sharing links work (because they redirect to the normal links).
        url = str(response.url).split("?")[0]

    type, id = url.split("/")[-2:]

    match type:
        case "playlist":
            return await get_playlist_by_id(client, int(id))
        case "album":
            return await get_album_by_id(client, int(id))
        case "track":
            return await get_track_by_id(client, int(id))
        case _:
            return
