# src/my_project/data/get_data.py
from io import StringIO
import re

from pathlib import Path
import pandas as pd

import zipfile

import requests
from urllib.parse import urlparse

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def download_imf_energy_data(output_dir: str | Path) -> None:
    """Download IMF renewable energy CSV file to the given directory."""
    # ---- sanitize output_dir ----
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"{output_dir} does not exist")
    if not output_dir.is_dir():
        raise ValueError(f"{output_dir} is not a directory")

    output_file_path = output_dir / "imf_renewable_energy.csv"

    url = (
        "https://hub.arcgis.com/api/v3/datasets/"
        "0bfab7fb7e0e4050b82bba40cd7a1bd5_0/downloads/data"
        "?format=csv&spatialRefId=4326&where=1%3D1"
    )

    logger.info(f"Downloading IMF energy data to {output_file_path}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    logger.info("IMF energy data download complete.")

    return output_file_path


def download_iso_codes(output_dir: str | Path) -> None:
    """Fetch ISO country codes and save CSV to the given directory."""
    # ---- sanitize output_dir ----
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"{output_dir} does not exist")
    if not output_dir.is_dir():
        raise ValueError(f"{output_dir} is not a directory")

    output_file_path = output_dir / "iso_country_codes.csv"

    url = "https://www.iban.com/country-codes"
    logger.info(f"Fetching ISO codes from {url}...")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        if not tables or len(tables) == 0:
            raise ValueError("No tables found on the page.")

        iso_df = tables[0]
        # validate
        if iso_df.empty or "Alpha-3 code" not in iso_df.columns:
            raise ValueError("Invalid ISO codes dataset.")

        iso_df.to_csv(output_file_path, index=False)
        logger.info(f"ISO codes saved to {output_file_path}")
    except Exception as e:
        logger.error(f"Error fetching ISO codes: {e}")
        raise

    return output_file_path


def download_natural_earth_data(output_dir: str | Path) -> None:
    """
    Download Natural Earth 110m cultural vectors and unzip to the given directory.
    """
    # ---- sanitize output_dir ----
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"{output_dir} does not exist")
    if not output_dir.is_dir():
        raise ValueError(f"{output_dir} is not a directory")
    
    # create subdirectory for natural_earth
    ne_dir = output_dir / "natural_earth"
    ne_dir.mkdir(parents=True, exist_ok=True)

    zip_file_path = ne_dir / "world_countries.zip"
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"

    logger.info(f"Downloading Natural Earth dataset to {zip_file_path}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(zip_file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info(f"Download complete. Unzipping {zip_file_path}...")
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(ne_dir)

    logger.info(f"Natural Earth data extracted to {ne_dir}.")

    return zip_file_path.parent


def download_from_url(address: str, output_dir: str | Path) -> Path:
    """
    Download a file from a public web URL and save it to the given directory.

    Parameters
    ----------
    address : str
        Publicly accessible URL to the file.
    output_dir : str | Path
        Directory where the file will be saved.

    Returns
    -------
    Path
        Path to the downloaded file.
    """
    # ---- sanitize output_dir ----
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"{output_dir} does not exist")
    if not output_dir.is_dir():
        raise ValueError(f"{output_dir} is not a directory")

    # ---- sanitize and validate URL ----
    if not isinstance(address, str) or not address.strip():
        raise ValueError("address must be a non-empty string")

    parsed_url = urlparse(address)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError("URL must start with http or https")

    if not parsed_url.netloc:
        raise ValueError("Invalid URL: missing network location")

    # ---- extract and sanitize filename ----
    filename = Path(parsed_url.path).name

    if not filename:
        raise ValueError("Cannot determine filename from URL")

    # basic filename hardening (avoid weird chars)
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename)

    output_file_path = output_dir / filename

    logger.info(f"Downloading data from {address} to {output_file_path}...")

    try:
        response = requests.get(address, stream=True, timeout=30)
        response.raise_for_status()

        with open(output_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # avoid keep-alive chunks
                    f.write(chunk)

    except requests.RequestException as e:
        logger.error(f"Download failed: {e}")
        raise

    logger.info("Download complete.")

    return output_file_path


if __name__ == "main":
    pass
