import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from dotenv import load_dotenv
import json
from pathlib import Path
import re

# Load environment variables
load_dotenv()
API_KEY = os.getenv("EMBER_API")
BASE_URL = os.getenv("EMBER_BASE_URL", "https://api.ember-energy.org")

# for defining output file paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# logging directory
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "ember_api_requests.log"),  # save to file
        logging.StreamHandler()                     # print to console
    ]
)
logger = logging.getLogger(__name__)

class EmberAPI:
    """
    client for interacting with the Ember Energy API
    """

    def __init__(self, api_key: str = API_KEY, base_url: str = BASE_URL):
        if api_key is None:
            raise ValueError("EMBER_API key not found in environment variables.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        
        # create session
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1)
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        logger.info("Initialized EmberAPI client with base URL: %s", self.base_url)

    @staticmethod
    def _sanitize(value):
        """Sanitize strings for safe filenames."""
        return re.sub(r"[^A-Za-z0-9_-]", "_", str(value))

    def _request(self, endpoint: str, params: dict = None):
        """
        Internal helper to send GET requests to Ember API.
        """
        url = f"{self.base_url}{endpoint}"

        # Add API key to query params
        params = params or {}
        params["api_key"] = self.api_key

        # Create a copy for logging without the API key
        safe_params = {k: v for k, v in params.items() if k != "api_key"}

        logger.info("Requesting: %s", url)
        if safe_params:
            logger.info("Parameters used: %s", safe_params)
        else:
            logger.info("No filters applied — fetching full dataset")

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            logger.error(
                "API request failed (%s): %s",
                response.status_code,
                response.text[:300]
            )
            raise RuntimeError(
                f"API request failed: {response.status_code}\n{response.text}"
            )

        logger.info("Request successful: %s", url)
        return response.json()

    def fetch_and_cache(self, endpoint_name: str, fetch_func, params=None):
        """
        Fetch data from API and cache it locally.
        If cache exists, load from file instead of calling API.
        """
        CACHE_DIR = PROJECT_ROOT / "data" / "raw"
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Build cache filename based on endpoint + params
        params = params or {}
        param_str = "_" + "_".join(
            f"{self._sanitize(k)}-{self._sanitize(v)}"
            for k, v in params.items()
        )
        cache_file = CACHE_DIR / f"{endpoint_name}{param_str}.json"

        # If cached file exists, load it
        if cache_file.exists():
            logger.info("Loading cached data from %s", cache_file)
            with open(cache_file, "r") as f:
                return json.load(f)

        # Otherwise fetch from API
        logger.info("Cache not found. Fetching from API...")
        data = fetch_func(**(params or {}))

        # Save to cache
        with open(cache_file, "w") as f:
            json.dump(data, f)

        logger.info("Saved API response to %s", cache_file)
        return data

    # -------------------------
    # Dataset Endpoints
    # -------------------------
    def electricity_generation_yearly(self, **params):
        """
        Fetch yearly electricity generation data.
        Example params:
            entity_code="BRA"
            start_date=2000
            is_aggregate_series=False
        """
        logger.info("Fetching yearly electricity generation dataset")
        return self._request("/v1/electricity-generation/yearly", params)

    def electricity_generation_monthly(self, **params):
        """
        Fetch monthly electricity generation data
        """
        logger.info("Fetching monthly electricity generation dataset")
        return self._request("/v1/electricity-generation/monthly", params)

    def electricity_capacity_monthly(self, **params):
        """
        Fetch monthly electricity installed capacity data.
        Example params:
            entity_code="BRA"
            start_date=2000
            is_aggregate_series=False
        """
        logger.info("Fetching monthly electricity capacity dataset")
        return self._request("/v1/installed-capacity/monthly", params)

    # -------------------------
    # Options Endpoints
    # -------------------------
    def options(self, dataset: str, temporal_resolution: str, filter_name: str):
        """
        Fetch available options for a dataset.
        Example:
            api.options("electricity-generation", "monthly", "entity")
        """
        logger.info(
            "Fetching options for dataset=%s, temporal_resolution=%s, filter_name=%s",
            dataset, temporal_resolution, filter_name
        )

        endpoint = f"/v1/options/{dataset}/{temporal_resolution}/{filter_name}"
        return self._request(endpoint)


# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    api = EmberAPI()

    # Example: Fetch Brazil yearly generation since 2000
    data = api.electricity_generation_yearly(
        entity_code="BRA",
        start_date=2000,
        is_aggregate_series=False
    )

    # Example: fetch & cache data
    # params = {
    #     "entity_code":"BRA",
    #     "start_date": 2000,
    #     "is_aggregate_series": False
    # }
    # data = api.fetch_and_cache(
    #     endpoint_name="electricity_generation_yearly",
    #     fetch_func=api.electricity_generation_yearly,
    #     params=params
    # )

    logger.info("Fetched %d records", len(data.get("data", [])))
    print("Sample data:", data.get("data", [])[:3])

