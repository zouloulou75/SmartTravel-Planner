from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Travel ML API"


settings = Settings()
