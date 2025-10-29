
import requests

url = "https://raw.githubusercontent.com/texao/geoview_countries/main/countries.json"
r = requests.get(url)
r.raise_for_status()

with open("countries.json", "w", encoding="utf-8") as f:
    f.write(r.text)

print("✅ countries.json mis à jour")
