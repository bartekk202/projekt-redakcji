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

# === Funkcje dla Redakcji ===
def add_redakcja():
    global redakcje, next_redakcja_id
    name = entry_red_name.get().strip()
    city = entry_red_city.get().strip()
    if not name or not city:
        messagebox.showerror("Błąd", "Proszę podać nazwę i miasto redakcji.")
        return
    for r in redakcje:
        if r["name"].lower() == name.lower():
            messagebox.showerror("Błąd", f"Redakcja '{name}' już istnieje.")
            return
    coords = get_coordinates_for_city(city)
    if coords is None:
        messagebox.showerror("Błąd", f"Nie znaleziono współrzędnych GPS dla '{city}'.")
        return
    redakcje.append({"id": next_redakcja_id, "name": name, "city": city, "coords": coords})
    tree_red.insert("", "end", iid=str(next_redakcja_id), values=(name, city))
    next_redakcja_id += 1
    entry_red_name.delete(0, tk.END)
    entry_red_city.delete(0, tk.END)
    refresh_comboboxes()
    update_map()
