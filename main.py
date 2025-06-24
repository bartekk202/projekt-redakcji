# System zarządzania redakcjami, pracownikami i punktami dystrybucji
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from tkintermapview import TkinterMapView

# === Dane ===
redakcje = []
pracownicy = []
punkty_dystrybucji = []

next_redakcja_id = 1
next_pracownik_id = 1
next_punkt_id = 1

# === Pobieranie współrzędnych z Wikipedii ===
def get_coordinates_for_city(city_name):
    if not city_name:
        return None
    params = {
        'action': 'query',
        'prop': 'coordinates',
        'titles': city_name,
        'format': 'json',
        'formatversion': '2',
        'redirects': '1'
    }
    url = "https://pl.wikipedia.org/w/api.php"
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("query") and data["query"].get("pages"):
            page = data["query"]["pages"][0]
            coords = page.get("coordinates")
            if coords:
                lat = coords[0].get("lat")
                lon = coords[0].get("lon")
                return (lat, lon)
    except:
        return None
