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

    if me.id in event.message.user_mentions_ids: # type: ignore
        await event.message.respond("Pong!", reply=event.message_id, mentions_reply=True)
        return

if __name__ == "__main__":
    bot.run()
    pass
