from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str
    

    @property
    def DATABASE_URL(self):
        # print(self.DB_PORT)
        return f"{self.DB_URL}"
    

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
