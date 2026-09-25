from __future__ import annotations
import hikari, miru, ongaku
from typing import TYPE_CHECKING, cast
from src.utils.deezer import get_album_tracks, get_playlist_tracks
from src.models.deezer import (
    AlbumFull,
    AlbumTracklistTrack,
    PlaylistFull,
    TrackFull,
    TracklistInfo
)

if TYPE_CHECKING:
    from src.__main__ import SunshineSeulgi

class DisabledPlayView(miru.View):
    @miru.button(label="Play", style=hikari.ButtonStyle.SUCCESS, disabled=True)
    async def disabled_play(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        return
    @miru.button(label="Info", style=hikari.ButtonStyle.SECONDARY, disabled=True)
    async def disabled_info(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        return
    @miru.button(label="Close", style=hikari.ButtonStyle.DANGER, disabled=True)
    async def disabled_stop(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        return

class PlayView(miru.View):
    def __init__(self, info: TrackFull|AlbumFull|PlaylistFull|TracklistInfo) -> None:
        super().__init__(timeout=120)
        self.info = info
        self.type = self.info.type

    @miru.button(label="Play", style=hikari.ButtonStyle.SUCCESS)
    async def play_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        bot = cast("SunshineSeulgi", ctx.client.app)
        await ctx.edit_response(components=DisabledPlayView())
        self.stop()

        if not ctx.guild_id:
            return
        voice_state = ctx.client.cache.get_voice_state(ctx.guild_id, ctx.author.id)
        if not voice_state or not voice_state.channel_id:
            await ctx.message.respond("You are not in a voice channel!", reply=ctx.message, mentions_reply=True)
            return

        try:
            player = bot.ongaku.fetch_player(ctx.guild_id)
        except ongaku.PlayerMissingError:
            player = bot.ongaku.create_player(ctx.guild_id)
        if not player:
            return
        if player.connected is False:
                await player.connect(voice_state.channel_id)

        press_play: bool = False
        if len(player.queue) == 0:
            press_play = True

        match self.type:
            case "track":
                if not isinstance(self.info, TrackFull):
                    return
                result = await bot.ongaku.rest.load_track(f"dzisrc:{self.info.isrc}")
                if not result:
                    return
                player.add(result)
                if press_play == True:
                    await player.play()
            case "album":
                if not isinstance(self.info, AlbumFull):
                    return
                result = await get_album_tracks(bot.http, self.info.id)
                if not result:
                    return
                tracks = result.data
                for track in tracks:
                    result = await bot.ongaku.rest.load_track(f"dzisrc:{track.isrc}")
                    if not result:
                        return
                    player.add(result)
                    if press_play == True:
                        await player.play()
                        press_play = False
            case "playlist":
                if not isinstance(self.info, PlaylistFull):
                    return
                for track in self.info.tracks:
                    result = await bot.ongaku.rest.load_track(f"dzisrc:{track.isrc}")
                    if not result:
                        return
                    player.add(result)
                    if press_play == True:
                        await player.play()
                        press_play = False
        return

    @miru.button(label="Info", style=hikari.ButtonStyle.SECONDARY)
    async def info_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await ctx.message.respond(attachment=hikari.files.Bytes(self.info.model_dump_json(indent=4, exclude_none=True), "info.json"))
        return

    @miru.button(label="Close", style=hikari.ButtonStyle.DANGER)
    async def stop_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await ctx.edit_response(components=DisabledPlayView())
        self.stop()
        return
