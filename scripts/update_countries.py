#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime
from unidecode import unidecode

GEOJSON_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
API_URL = "https://raw.githubusercontent.com/mledoze/countries/master/dist/countries.json"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "countries.json")

def main():
    print("🔄 Téléchargement Natural Earth GeoJSON...")
    geojson_response = requests.get(GEOJSON_URL)
    geojson_response.raise_for_status()
    geojson = geojson_response.json()
    
    print("🔄 Téléchargement API Countries...")
    api_response = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    api_response.raise_for_status()
    countries_api = api_response.json()

    # Dictionnaire pour accès rapide par code ISO
    api_dict = {c['cca3']: c for c in countries_api if c.get('cca3')}
    
    enriched = 0
    print("🔄 Enrichissement des données...")

    for feature in geojson['features']:
        props = feature['properties']
        iso_code = (props.get('iso_a3') or props.get('adm0_a3') or '').upper()
        api_country = api_dict.get(iso_code)

    # fallback sur le nom si pas de code ISO correspondant
    if not api_country:
        name = props.get('NAME') or props.get('ADMIN') or ''
        name_norm = unidecode(name).lower()  # supprimer accents
        for c in countries_api:
            common_name = unidecode(c.get('name', {}).get('common', '')).lower()
            official_name = unidecode(c.get('name', {}).get('official', '')).lower()
            if name_norm in [common_name, official_name]:
                api_country = c
                break

        # Si aucun match, on passe au pays suivant
        if not api_country:
            continue
        
        # Population
        props['population_updated'] = api_country.get('population')
        props['population_year'] = datetime.now().year
        
        # Capitale
        if api_country.get('capital'):
            props['capital'] = api_country['capital'][0] if api_country['capital'] else 'N/A'
        
        # Langues
        if api_country.get('languages'):
            lang_dict = api_country['languages']
            if lang_dict:
                props['languages'] = list(lang_dict.values())[0]
        
        # Monnaies
        if api_country.get('currencies'):
            currencies_dict = api_country['currencies']
            if currencies_dict:
                for code, data in currencies_dict.items():
                    props['currency_name'] = data.get('name', 'N/A')
                    props['currency_symbol'] = data.get('symbol', '')
                    break
        
        # Nom et continent
        props['name_updated'] = api_country.get('name', {}).get('common', props.get('NAME'))
        props['flag'] = api_country.get('flag', '')  # emoji du drapeau
        props['continent_updated'] = api_country.get('region', props.get('REGION_UN'))
        
        enriched += 1

    geojson['metadata'] = {
        'last_updated': datetime.now().isoformat(),
        'source_geojson': 'Natural Earth',
        'source_data': 'mledoze/countries',
        'countries_enriched': enriched
    }

    print(f"✅ {enriched}/{len(geojson['features'])} pays enrichis")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Sauvegardé dans {OUTPUT_FILE}")
    print(f"📅 Date de mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
