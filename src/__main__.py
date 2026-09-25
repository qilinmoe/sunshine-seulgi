import logging
logger = logging.getLogger("sunshine-seulgi")

import os, re, httpx
import hikari, miru, ongaku

import src.embeds as embeds
import src.views as views
from src.utils.deezer import get_result_by_url, get_tracks_by_query
from src.utils.config import init_config
init_config()

class SunshineSeulgi(hikari.GatewayBot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.ongaku = ongaku.Client(self)
        self.ongaku.create_session(
            name="sunshine-seulgi",
            host=str(os.getenv("lavalink_host")),
            password=str(os.getenv("lavalink_pass"))
        )
        self.miru = miru.Client(self)
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

    # X Replace -----
    match_x = re.search(re.compile(str(os.getenv("x_replace_regex"))), content_clean)
    if match_x:
        async with bot.rest.trigger_typing(event.channel_id):
            x_link = match_x.group(0)
            new_match = x_link.replace("https://x.com", str(os.getenv("x_replace_url")))
            await event.message.respond(new_match, reply=event.message_id, mentions_reply=True)
        return

    # DZ Links -----

    match_dz = re.search(re.compile(str(os.getenv("deezer_regex"))), content_clean)
    if match_dz:
        async with bot.rest.trigger_typing(event.channel_id):
            dz_link = match_dz.group(0)
            result = await get_result_by_url(bot.http, dz_link)
            if not result:
                embed = embeds.build_unknown_embed()
                await event.message.respond(embed=embed, reply=event.message_id, mentions_reply=True)
                return

        match result.type:
            case "track":
                embed = await embeds.build_track_embed(bot.http, result)
            case "album":
                embed = await embeds.build_album_embed(bot.http, result)
            case "playlist":
                embed = await embeds.build_playlist_embed(bot.http, result)

        view = views.PlayView(info=result)
        await event.message.respond(embed=embed, components=view, reply=event.message_id, mentions_reply=True)
        bot.miru.start_view(view)
        return

    # Commands -----

    if me.id in event.message.user_mentions_ids: # type: ignore
        parts = content_clean.split(" ")
        command = parts[0]
        args = parts[1:]
        match command:
            case "search":
                # TODO: Paginated results + Play from results.
                query = " ".join(args)
                async with bot.rest.trigger_typing(event.channel_id):
                    result = await get_tracks_by_query(bot.http, query)
                    if not result:
                        embed = embeds.build_unknown_embed()
                        await event.message.respond(embed=embed, reply=event.message_id, mentions_reply=True)
                        return

                await event.message.respond(f"> [WIP!]\n> TODO: Modal with paginated results\n\nSearched Deezer for: `{query}`; Found: {result.total}!",
                    attachment=hikari.files.Bytes(result.model_dump_json(indent=4, exclude_none=True), "info.json"),
                    reply=event.message_id,
                    mentions_reply=True
                )
                return
        return

if __name__ == "__main__":
    bot.run()
