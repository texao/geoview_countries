#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour mettre à jour automatiquement le fichier countries.json
dans le dépôt GitHub à partir de ton dépôt source ou d'une URL externe.
"""

import requests
import os
import sys

# URL du GeoJSON source
# Ici, le fichier que tu as mis sur ton repo GitHub (branche main)
GEOJSON_URL = "https://raw.githubusercontent.com/texao/geoview_countries/main/countries.json"

# Chemin relatif du fichier à mettre à jour dans ton repo
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "countries.json")

def download_geojson(url: str) -> str:
    """Télécharge le contenu du fichier GeoJSON depuis une URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"❌ Erreur lors du téléchargement de {url}: {e}")
        sys.exit(1)

def save_geojson(content: str, output_path: str):
    """Écrit le contenu téléchargé dans le fichier local"""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ countries.json mis à jour avec succès ({output_path})")
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture du fichier: {e}")
        sys.exit(1)

def main():
    print("🔄 Téléchargement du GeoJSON...")
    geojson_content = download_geojson(GEOJSON_URL)
    save_geojson(geojson_content, OUTPUT_FILE)

if __name__ == "__main__":
    main()
