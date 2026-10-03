import os
import httpx
from mcp.server.fastmcp import FastMCP

PORT = int(os.environ.get("PORT", "8000"))
mcp = FastMCP("binance-readonly", host="0.0.0.0", port=PORT)
FAPI = "https://fapi.binance.com"


async def get(path, params=None):
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(FAPI + path, params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def price(symbol: str = "BTCUSDT") -> dict:
    """Mark price, index price and funding rate for a futures symbol."""
    return await get("/fapi/v1/premiumIndex", {"symbol": symbol.upper()})


@mcp.tool()
async def klines(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 200) -> list:
    """Candles as [open_time, open, high, low, close, volume]. Intervals: 5m 15m 1h 4h 1d."""
    rows = await get("/fapi/v1/klines", {"symbol": symbol.upper(), "interval": interval, "limit": min(limit, 500)})
    return [[r[0], r[1], r[2], r[3], r[4], r[5]] for r in rows]


@mcp.tool()
async def order_book(symbol: str = "BTCUSDT", limit: int = 50) -> dict:
    """Order book depth (bids and asks)."""
    return await get("/fapi/v1/depth", {"symbol": symbol.upper(), "limit": limit})


@mcp.tool()
async def open_interest(symbol: str = "BTCUSDT", period: str = "1h", limit: int = 30) -> dict:
    """Current open interest plus its history."""
    now = await get("/fapi/v1/openInterest", {"symbol": symbol.upper()})
    hist = await get("/futures/data/openInterestHist", {"symbol": symbol.upper(), "period": period, "limit": limit})
    return {"current": now, "history": hist}


@mcp.tool()
async def funding_history(symbol: str = "BTCUSDT", limit: int = 20) -> list:
    """Recent funding rates."""
    return await get("/fapi/v1/fundingRate", {"symbol": symbol.upper(), "limit": limit})


@mcp.tool()
async def long_short_ratio(symbol: str = "BTCUSDT", period: str = "1h", limit: int = 30) -> list:
    """Global long/short account ratio history."""
    return await get("/futures/data/globalLongShortAccountRatio", {"symbol": symbol.upper(), "period": period, "limit": limit})


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
