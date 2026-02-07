import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    api_key: str
    api_secret: str
    testnet: bool = True  # Используй testnet для тестов!
    
    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            api_key=os.getenv("BYBIT_API_KEY", ""),
            api_secret=os.getenv("BYBIT_API_SECRET", ""),
            testnet=os.getenv("BYBIT_TESTNET", "true").lower() == "true",
        )


settings = Settings.from_env()
