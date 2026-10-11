from pathlib import Path
import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

documents = [
    {
        "name": "fao_soil_moisture.pdf",
        "url": "https://www.fao.org/ag/ca/doc/Soil_Moisture.pdf",
    },
    {
        "name": "icar_crop_weather_2021.pdf",
        "url": "https://icar.org.in/sites/default/files/2022-07/CWR-29-09-2021.pdf",
    },
]

for doc in documents:
    destination = RAW_DIR / doc["name"]

    if destination.exists():
        print(f"Already exists: {destination.name}")
        continue

    try:
        print(f"Downloading: {doc['name']}", flush=True)

        response = requests.get(
            doc["url"],
            timeout=60,
            headers={"User-Agent": "SmartAgricultureRAG/1.0"},
        )
        response.raise_for_status()

        if not response.content.startswith(b"%PDF-"):
            print(f"Not a valid PDF: {doc['name']}")
            continue

        destination.write_bytes(response.content)
        print(f"Downloaded successfully: {destination.name}")

    except requests.RequestException as error:
        print(f"Download failed: {doc['name']} - {error}")

print("\nDownload process finished.")
print(f"Output folder: {RAW_DIR}")
