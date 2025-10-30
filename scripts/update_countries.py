#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime

# Natural Earth pour les frontières
GEOJSON_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"

# API alternative avec structure différente
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

    # Créer un dictionnaire pour accès rapide par code ISO
    api_dict = {}
    for country in countries_api:
        # Cette API utilise 'cca3' pour le code ISO
        iso_code = country.get('cca3')
        if iso_code:
            api_dict[iso_code] = country
    
    enriched = 0
    
    print("🔄 Enrichissement des données...")
    for feature in geojson['features']:
        props = feature['properties']
        iso_code = (props.get('iso_a3') or props.get('adm0_a3') or '').upper()
        
        if iso_code in api_dict:
            api_country = api_dict[iso_code]
            
            # Population
            props['population_updated'] = api_country.get('population')
            props['population_year'] = datetime.now().year
            
            # Capitale - cette API stocke directement la capitale
            if api_country.get('capital'):
                # Dans cette API, capital est déjà une liste
                props['capital'] = api_country['capital'][0] if api_country['capital'] else 'N/A'
            
            # Langues - cette API a une structure différente
            if api_country.get('languages'):
                # languages est un dict {code: nom}
                lang_dict = api_country['languages']
                if lang_dict:
                    props['languages'] = list(lang_dict.values())[0]  # Première langue
            
            # Monnaies - structure différente
            if api_country.get('currencies'):
                currencies_dict = api_country['currencies']
                if currencies_dict:
                    # Prendre la première devise
                    for code, data in currencies_dict.items():
                        props['currency_name'] = data.get('name', 'N/A')
                        props['currency_symbol'] = data.get('symbol', '')
                        break
            
            # Nom du pays (plus fiable)
            props['name_updated'] = api_country.get('name', {}).get('common', props.get('NAME'))
            
            # Continent
            props['continent_updated'] = api_country.get('region', props.get('REGION_UN'))
            
            enriched += 1
    
    # Ajouter métadonnées de mise à jour
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
