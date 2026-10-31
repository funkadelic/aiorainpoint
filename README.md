# aiorainpoint

Async Python client for the RainPoint Smart+ cloud API. It covers the REST endpoints, the MQTT push channel and the payload decoders for RainPoint valves, sensors and hubs. It is the client behind the [RainPoint Cloud](https://github.com/funkadelic/ha-rainpoint) Home Assistant integration.

This project is not affiliated with or endorsed by RainPoint.

## Install

```sh
pip install aiorainpoint
```

Requires Python 3.13 or later.

## Usage

```python
import asyncio

import aiohttp

from aiorainpoint import RainPointClient


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        # Country calling code without the plus sign, then the RainPoint app login.
        client = RainPointClient("1", "you@example.com", "your-password", session)
        for home in await client.list_homes():
            devices = await client.get_devices_by_hid(home["hid"])
            print(home["homeName"], len(devices))


asyncio.run(main())
```

The client logs in on the first call and refreshes its token as needed. Cloud errors raise `RainPointApiError`. A login refused for rate limiting raises its subclass `RainPointThrottledError`, which carries `retry_after` in seconds. Network errors come through as aiohttp's own exceptions.

## Use a second account

The cloud keeps one session per account, so logging in here can sign out the RainPoint app on the same account. Create a second account, invite it to your home from the app, and give that one to the client.

## License

MIT
