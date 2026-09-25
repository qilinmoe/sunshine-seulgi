import logging
logger = logging.getLogger("embeds")

from hikari.embeds import Embed

def build_unknown_embed() -> Embed:
    return Embed(
        title = "(・–・;)ゞ No Results",
        description = "⋮ I couldn't find anything...\n⋮ ˙ . ꒷ 🍰 . 𖦹˙—",
        color = (254, 243, 139)
    ).set_thumbnail("https://i.pinimg.com/originals/81/46/0f/81460f80f7787de5b8dd6ed74a457e27.jpg")
