from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvSettings(BaseSettings):
    zhipu_api_key: str
    zhipu_base_url: str = "https://open.bigmodel.cn/api/paas/v4/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


if __name__ == "__main__":
    settings = EnvSettings()
    print(settings.zhipu_api_key)