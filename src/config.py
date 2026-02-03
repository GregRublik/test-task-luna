from aiohttp import ClientSession
from pydantic_settings import BaseSettings, SettingsConfigDict


class SessionManager:
    _session: ClientSession | None = None

    @classmethod
    async def get_session(cls) -> ClientSession:
        """Возвращает сессию aiohttp, создавая её при первом вызове."""
        if cls._session is None or cls._session.closed:
            cls._session = ClientSession()
        return cls._session

    @classmethod
    async def close_session(cls):
        """Закрывает сессию, если она существует."""
        if cls._session is not None:
            await cls._session.close()
            cls._session = None

class DbSettings(BaseSettings):
    host: str
    user: str
    password: str
    name: str
    port: int

    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")

    @property
    def dsn_asyncpg(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

class Settings(BaseSettings):
    port: int
    host: str
    api_key: str

    db: DbSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore"
    )

settings = Settings(
    db=DbSettings(),
)
