import io, httpx, logging
logger = logging.getLogger("tools")

from PIL import Image

async def color_average(client: httpx.AsyncClient, url: str) -> tuple[int, int, int]:
    response = await client.get(url)
    if not response.is_success:
        logger.error("[-] Failed to get image to build embed!")
        logger.debug(f"[#] Code: {response.status_code} | URL: {url}")
        return (254, 243, 139)
    data = response.read()
    image = Image.open(io.BytesIO(data)).convert("RGB")
    return image.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0)) # type: ignore

def calc_duration(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"
