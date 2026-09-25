import logging
logger = logging.getLogger("sunshine-seulgi")

import os, re, httpx
import hikari, miru, ongaku

from src.utils.embed import *
from src.utils.deezer import get_result_by_url, get_tracklist_by_query
from src.utils.config import init_config
init_config()


class SunshineSeulgi(hikari.GatewayBot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.miru = miru.Client(self)
        self.ongaku = ongaku.Client(self)
        self.ongaku.create_session(
            name="sunshine-seulgi",
            host=str(os.getenv("lavalink_host")),
            password=str(os.getenv("lavalink_pass"))
        )

        self.http = httpx.AsyncClient()

bot = SunshineSeulgi(
    token=str(os.getenv("discord_bot_token")),
    suppress_optimization_warning=True,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT | hikari.Intents.GUILD_MESSAGES
)

@bot.listen()
async def guild_message_create_response(event: hikari.GuildMessageCreateEvent) -> None:
    allowed_channels = [int(x) for x in str(os.getenv("discord_server_allowed_channels")).split(",")]
    if not event.is_human or event.channel_id not in allowed_channels:
        return
    me = bot.get_me()
    content = event.message.content
    content_clean = str(content).replace(f"<@{os.getenv("discord_bot_id")}> ", "").strip()

    match_x = re.search(re.compile(str(os.getenv("x_replace_regex"))), content_clean)
    if match_x:
        async with bot.rest.trigger_typing(event.channel_id):
            x_link = match_x.group(0)
            new_match = x_link.replace("https://x.com", str(os.getenv("x_replace_url")))
            await event.message.respond(new_match, reply=event.message_id, mentions_reply=True)
        return

    match_dz = re.search(re.compile(str(os.getenv("deezer_regex"))), content_clean)
    if match_dz:
        async with bot.rest.trigger_typing(event.channel_id):
            dz_link = match_dz.group(0)
            result = await get_result_by_url(bot.http, dz_link)
            if not result:
                embed = build_unknown_embed()
                await event.message.respond(embed=embed, reply=event.message_id, mentions_reply=True)
                return

        match result.type:
            case "track":
                embed = await build_track_embed(bot.http, result)
            case "album":
                embed = await build_album_embed(bot.http, result)
            case "playlist":
                embed = await build_playlist_embed(bot.http, result)

        await event.message.respond(embed=embed, reply=event.message_id, mentions_reply=True)

    if me.id in event.message.user_mentions_ids: # type: ignore
        async with bot.rest.trigger_typing(event.channel_id):
            parts = content_clean.split(" ")
            command = parts[0]
            args = parts[1:]
            match command:
                case "search":
                    # TODO: Paginated results + Play from results.
                    query = " ".join(args)
                    result = await get_tracklist_by_query(bot.http, query)
                    if not result:
                        embed = build_unknown_embed()
                        await event.message.respond(embed=embed, reply=event.message_id, mentions_reply=True)
                        return

                    await event.message.respond(f"> [WIP!]\n> TODO: Paginated results\n\nSearched Deezer for: `{query}`; Found: {result.total}!",
                        attachment=hikari.files.Bytes(result.model_dump_json(indent=4, exclude_none=True), "info.json"),
                        reply=event.message_id,
                        mentions_reply=True
                    )
                    return
        return

if __name__ == "__main__":
    bot.run()
    pass
