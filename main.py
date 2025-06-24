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

def update_pracownik():
    selected = tree_prac.selection()
    if not selected:
        return
    item_id = int(selected[0])
    name = entry_prac_name.get().strip()
    city = entry_prac_city.get().strip()
    redakcja_name = combo_prac_red.get()
    if not name or not city or not redakcja_name:
        messagebox.showerror("Błąd", "Uzupełnij wszystkie dane pracownika.")
        return
    coords = get_coordinates_for_city(city)
    redakcja = next((r for r in redakcje if r["name"] == redakcja_name), None)
    if coords is None or redakcja is None:
        messagebox.showerror("Błąd", "Nieprawidłowe dane.")
        return
    for p in pracownicy:
        if p["id"] == item_id:
            p["name"] = name
            p["city"] = city
            p["coords"] = coords
            p["redakcja_id"] = redakcja["id"]
    tree_prac.item(str(item_id), values=(name, city, redakcja_name))
    update_map()

def delete_pracownik():
    global pracownicy
    selected = tree_prac.selection()
    if not selected:
        return
    item_id = int(selected[0])
    pracownicy = [p for p in pracownicy if p["id"] != item_id]
    tree_prac.delete(selected[0])
    update_map()

# === Funkcje dla Punktów Dystrybucji ===
def add_punkt():
    global punkty_dystrybucji, next_punkt_id
    city = entry_punkt_city.get().strip()
    redakcja_name = combo_punkt_red.get()
    if not city or not redakcja_name:
        messagebox.showerror("Błąd", "Uzupełnij wszystkie dane punktu.")
        return
    redakcja = next((r for r in redakcje if r["name"] == redakcja_name), None)
    if redakcja is None:
        messagebox.showerror("Błąd", "Wybrana redakcja nie istnieje.")
        return
    coords = get_coordinates_for_city(city)
    if coords is None:
        messagebox.showerror("Błąd", f"Nie znaleziono współrzędnych GPS dla '{city}'.")
        return
    punkty_dystrybucji.append({"id": next_punkt_id, "city": city, "coords": coords, "redakcja_id": redakcja["id"]})
    tree_punkt.insert("", "end", iid=str(next_punkt_id), values=(city, redakcja_name))
    next_punkt_id += 1
    entry_punkt_city.delete(0, tk.END)
    combo_punkt_red.set('')
    update_map()

def update_punkt():
    selected = tree_punkt.selection()
    if not selected:
        return
    item_id = int(selected[0])
    city = entry_punkt_city.get().strip()
    redakcja_name = combo_punkt_red.get()
    coords = get_coordinates_for_city(city)
    redakcja = next((r for r in redakcje if r["name"] == redakcja_name), None)
    if not city or not redakcja or coords is None:
        messagebox.showerror("Błąd", "Nieprawidłowe dane.")
        return
    for p in punkty_dystrybucji:
        if p["id"] == item_id:
            p["city"] = city
            p["coords"] = coords
            p["redakcja_id"] = redakcja["id"]
    tree_punkt.item(str(item_id), values=(city, redakcja_name))
    update_map()

def delete_punkt():
    global punkty_dystrybucji
    selected = tree_punkt.selection()
    if not selected:
        return
    item_id = int(selected[0])
    punkty_dystrybucji = [p for p in punkty_dystrybucji if p["id"] != item_id]
    tree_punkt.delete(selected[0])
    update_map()

# === Mapa ===
def update_map():
    map_widget.delete_all_marker()
    for r in redakcje:
        lat, lon = r["coords"]
        map_widget.set_marker(lat, lon, text=f"{r['name']} (redakcja)")
    for p in pracownicy:
        lat, lon = p["coords"]
        map_widget.set_marker(lat, lon, text=p["name"])
    for d in punkty_dystrybucji:
        lat, lon = d["coords"]
        map_widget.set_marker(lat, lon, text="Punkt dystrybucji")

def show_selected_redakcja_on_map():
    selected = tree_red.selection()
    if not selected:
        messagebox.showinfo("Informacja", "Wybierz redakcję.")
        return

    item_id = int(selected[0])
    redakcja = next((r for r in redakcje if r["id"] == item_id), None)
    if not redakcja:
        messagebox.showerror("Błąd", "Nie znaleziono redakcji.")
        return

    related_pracownicy = [p for p in pracownicy if p["redakcja_id"] == item_id]
    related_punkty = [d for d in punkty_dystrybucji if d["redakcja_id"] == item_id]

    map_widget.delete_all_marker()

    lat_r, lon_r = redakcja["coords"]
    map_widget.set_marker(lat_r, lon_r, text=f"{redakcja['name']} (redakcja)")
    map_widget.set_position(lat_r, lon_r)
    map_widget.set_zoom(8)

    for p in related_pracownicy:
        lat, lon = p["coords"]
        map_widget.set_marker(lat, lon, text=f"{p['name']} (pracownik)")

    for d in related_punkty:
        lat, lon = d["coords"]
        map_widget.set_marker(lat, lon, text=f"Punkt dystrybucji ({d['city']})")

# === Comboboxy ===
def refresh_comboboxes():
    names = [r["name"] for r in redakcje]
    combo_prac_red['values'] = names
    combo_punkt_red['values'] = names

# === GUI ===
root = tk.Tk()
root.title("Zarządzanie redakcjami")
root.geometry("1100x700")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

frame_red = ttk.Frame(notebook)
frame_prac = ttk.Frame(notebook)
frame_punkt = ttk.Frame(notebook)
frame_map = ttk.Frame(notebook)
notebook.add(frame_red, text="Redakcje")
notebook.add(frame_prac, text="Pracownicy")
notebook.add(frame_punkt, text="Punkty dystrybucji")
notebook.add(frame_map, text="Mapa")

