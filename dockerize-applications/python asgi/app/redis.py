import asyncio
import aioredis

loop = asyncio.get_event_loop()


class Connection:
    def __init__(self):
        self.__connection = None

    async def __create_connection(self):
        self.__connection = await aioredis.create_connection(
            'redis://localhost', loop=loop
        )

    async def __call__(self, method, *args, **kwargs):
        if not self.__connection:
            await self.__create_connection()
        value = await getattr(self.__connection, method)(*args, **kwargs)
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        return value

    async def close(self):
        if self.__connection:
            self.__connection.close()
            await self.__connection.wait_closed()


connection = Connection()
