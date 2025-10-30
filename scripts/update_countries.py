#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime

# Natural Earth pour les frontières
GEOJSON_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"

# REST Countries pour données à jour
API_URL = "https://raw.githubusercontent.com/mledoze/countries/master/dist/countries.json"

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "countries.json")

def main():
    print("🔄 Téléchargement Natural Earth GeoJSON...")
    geojson_response = requests.get(GEOJSON_URL)
    geojson_response.raise_for_status()
    geojson = geojson_response.json()
    
    print("🔄 Téléchargement REST Countries API...")
    api_response = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0 (compatible; GeoViewBot/1.0)"})
    api_response.raise_for_status()
    countries_api = api_response.json()

    
    # Créer un dictionnaire pour accès rapide par code ISO
    api_dict = {c.get('cca3'): c for c in countries_api if c.get('cca3')}
    
    enriched = 0
    
    print("🔄 Enrichissement des données...")
    for feature in geojson['features']:
        props = feature['properties']
        iso_code = props.get('iso_a3') or props.get('adm0_a3')
        
        if iso_code in api_dict:
            api_country = api_dict[iso_code]
            
            # Ajouter les données API (plus récentes)
            props['population_updated'] = api_country.get('population')
            props['population_year'] = datetime.now().year
            
            # Capitale
            if api_country.get('capital'):
                props['capital_updated'] = api_country['capital'][0]
            
            # Langues
            if api_country.get('languages'):
                props['languages'] = list(api_country['languages'].values())
            
            # Monnaies
            if api_country.get('currencies'):
                currencies = []
                for code, data in api_country['currencies'].items():
                    currencies.append({
                        'code': code,
                        'name': data.get('name'),
                        'symbol': data.get('symbol', '')
                    })
                props['currencies'] = currencies
            
            # Région
            props['region'] = api_country.get('region', props.get('region'))
            props['subregion'] = api_country.get('subregion', props.get('subregion'))
            
            enriched += 1
    
    # Ajouter métadonnées de mise à jour
    geojson['metadata'] = {
        'last_updated': datetime.now().isoformat(),
        'source_geojson': 'Natural Earth',
        'source_data': 'REST Countries API',
        'countries_enriched': enriched
    }
    
    print(f"✅ {enriched}/{len(geojson['features'])} pays enrichis")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Sauvegardé dans {OUTPUT_FILE}")
    print(f"📅 Date de mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
