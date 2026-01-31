import os
from dotenv import load_dotenv

load_dotenv()  # Load .env if present

class Settings:
    DB_TYPE = os.getenv("DB_TYPE", "mysql")
    DB_URI = os.getenv("DB_URI")
    MONGO_URI = os.getenv("MONGO_URI")

    PROVIDER = os.getenv("GENERATOR_PROVIDER", "mixtral")
    MODEL = os.getenv("MIXTRAL_MODEL", "mistralai/mixtral-8x7b-instruct")
    TEMP = float(os.getenv("GENERATOR_TEMPERATURE", "0.2"))
    TOP_P = float(os.getenv("GENERATOR_TOP_P", "0.95"))
    N_CANDIDATES = int(os.getenv("GENERATOR_N_CANDIDATES", "5"))

    SAFETY_BLOCK_DDL = os.getenv("SAFETY_BLOCK_DDL", "true").lower() == "true"
    SAFETY_REQUIRE_WHERE = os.getenv("SAFETY_REQUIRE_WHERE", "true").lower() == "true"
    SELECT_LIMIT_CAP = int(os.getenv("SELECT_LIMIT_CAP", "1000"))

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

settings = Settings()
