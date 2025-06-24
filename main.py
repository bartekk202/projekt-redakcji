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

def update_redakcja():
    selected = tree_red.selection()
    if not selected:
        return
    item_id = int(selected[0])
    name = entry_red_name.get().strip()
    city = entry_red_city.get().strip()
    if not name or not city:
        messagebox.showerror("Błąd", "Proszę podać nazwę i miasto redakcji.")
        return
    coords = get_coordinates_for_city(city)
    if coords is None:
        messagebox.showerror("Błąd", f"Nie znaleziono współrzędnych GPS dla '{city}'.")
        return
    for r in redakcje:
        if r["id"] == item_id:
            r["name"] = name
            r["city"] = city
            r["coords"] = coords
    tree_red.item(str(item_id), values=(name, city))
    refresh_comboboxes()
    update_map()

def delete_redakcja():
    global redakcje, pracownicy, punkty_dystrybucji
    selected = tree_red.selection()
    if not selected:
        return
    item_id = int(selected[0])
    redakcje = [r for r in redakcje if r["id"] != item_id]
    pracownicy = [p for p in pracownicy if p["redakcja_id"] != item_id]
    punkty_dystrybucji = [d for d in punkty_dystrybucji if d["redakcja_id"] != item_id]
    tree_red.delete(selected[0])
    for tree in [tree_prac, tree_punkt]:
        for item in tree.get_children():
            tree.delete(item)
    for p in pracownicy:
        red = next((r for r in redakcje if r["id"] == p["redakcja_id"]), None)
        tree_prac.insert("", "end", iid=str(p["id"]), values=(p["name"], p["city"], red["name"] if red else "?"))
    for d in punkty_dystrybucji:
        red = next((r for r in redakcje if r["id"] == d["redakcja_id"]), None)
        tree_punkt.insert("", "end", iid=str(d["id"]), values=(d["city"], red["name"] if red else "?"))
    refresh_comboboxes()
    update_map()

# === Funkcje dla Pracowników ===
def add_pracownik():
    global pracownicy, next_pracownik_id
    name = entry_prac_name.get().strip()
    city = entry_prac_city.get().strip()
    redakcja_name = combo_prac_red.get()
    if not name or not city or not redakcja_name:
        messagebox.showerror("Błąd", "Uzupełnij wszystkie dane pracownika.")
        return
    redakcja = next((r for r in redakcje if r["name"] == redakcja_name), None)
    if redakcja is None:
        messagebox.showerror("Błąd", "Wybrana redakcja nie istnieje.")
        return
    coords = get_coordinates_for_city(city)
    if coords is None:
        messagebox.showerror("Błąd", f"Nie znaleziono współrzędnych GPS dla '{city}'.")
        return
    pracownicy.append({"id": next_pracownik_id, "name": name, "city": city, "coords": coords, "redakcja_id": redakcja["id"]})
    tree_prac.insert("", "end", iid=str(next_pracownik_id), values=(name, city, redakcja_name))
    next_pracownik_id += 1
    entry_prac_name.delete(0, tk.END)
    entry_prac_city.delete(0, tk.END)
    combo_prac_red.set('')
    update_map()