#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime
import unicodedata

# URLs
GEOJSON_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
API_URL = "https://raw.githubusercontent.com/mledoze/countries/master/dist/countries.json"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "countries.json")

def normalize_name(name):
    return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII').lower()

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
        iso_code = (props.get('ISO_A3') or props.get('ADM0_A3') or '').upper()
        api_country = api_dict.get(iso_code)


        # fallback sur le nom si pas de code ISO correspondant
        if not api_country:
            name = props.get('NAME') or props.get('ADMIN') or ''
            name_norm = normalize_name(name)
            for c in countries_api:
                common_name = normalize_name(c.get('name', {}).get('common', ''))
                official_name = normalize_name(c.get('name', {}).get('official', ''))
                if name_norm in [common_name, official_name]:
                    api_country = c
                    break

        # Si aucun match, on passe au pays suivant
        if not api_country:
            continue

        # CODES ISO (POUR L'API WORLD BANK) 
        # Code ISO A2 (2 lettres) - pour l'API World Bank
        props['iso_a2'] = api_country.get('cca2', '')
        # Code ISO A3 (3 lettres) - pour référence
        props['iso_a3'] = api_country.get('cca3', '')

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

        # Superficie
        props['area'] = api_country.get('area')

        # Membre de l'ONU
        props['unMember'] = api_country.get('unMember', False)
   
        enriched += 1

    # Ajouter métadonnées
    geojson['metadata'] = {
        'last_updated': datetime.now().isoformat(),
        'source_geojson': 'Natural Earth',
        'source_data': 'mledoze/countries',
        'countries_enriched': enriched
    }

    print(f"✅ {enriched}/{len(geojson['features'])} pays enrichis")

    # Sauvegarde
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"💾 Sauvegardé dans {OUTPUT_FILE}")
    print(f"📅 Date de mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
