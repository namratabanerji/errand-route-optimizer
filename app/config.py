import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ORS_API_KEY = os.getenv("ORS_API_KEY", "")
    ORS_BASE_URL = "https://api.openrouteservice.org"
    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
    USER_AGENT = "errand-route-optimizer/0.1"


settings = Settings()
