from __future__ import annotations

import csv
import ctypes
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Dict, List, Optional, Sequence

# Import interne (compatible exécution directe ou en paquet)
if __package__ in {None, ""}:
   sys.path.append(str(Path(__file__).resolve().parent.parent))
   from bolt_app.core import DISPLAY_MATERIALS, Vis, DimensionnementResult, dimensionner  # type: ignore
   import bolt_app.core as core  # type: ignore
else:
   from .core import DISPLAY_MATERIALS, Vis, DimensionnementResult, dimensionner
   from . import core


def resource_path(*parts: str) -> Path:
   try:
       base = Path(getattr(sys, "_MEIPASS"))  # type: ignore[attr-defined]
   except Exception:
       base = Path(__file__).resolve().parents[2]
   return base.joinpath(*parts)


PAS_STD_FILE = resource_path("assets", "Pas-std.csv")
ICON_FILE = resource_path("assets", "Bolt_logo.png")
IMG_FILE = resource_path("assets", "Schema_technique.png")
IMG_CONSTRUCTION_FILE = resource_path("assets", "construction_image.png")
TETE_VIS_FILE = resource_path("assets", "Tete_vis.csv")

core.PAS_STD_FILE = PAS_STD_FILE
core.FROTTEMENT_FILE = resource_path("assets", "Frottement.csv")
core.TROU_PASSAGE_FILE = resource_path("assets", "Trou_passage.csv")
core.TETE_VIS_FILE = TETE_VIS_FILE
DEFAULT_HEAD_TYPES = [
   "Hexagonale",
   "CHC cylindrique",
   "CHC fraisee",
   "CHC bombee",
   "Bombee fendue",
   "Bombee Philips",
   "Bombee Pozidriv",
   "Bombee Torx interne",
]
HEAD_LABEL_MAP: Dict[str, str] = {
   "CHC tete fraisee": "CHC fraisee",
   "CHC tete bombee": "CHC bombee",
   "Tete bombee fendue": "Bombee fendue",
   "Tete bombee philips": "Bombee Philips",
   "Tete bombee Pozidriv": "Bombee Pozidriv",
   "Tete bombee Torx interne": "Bombee Torx interne",
}
HEAD_REVERSE_MAP: Dict[str, str] = {v: k for k, v in HEAD_LABEL_MAP.items()}
HEAD_IMAGE_FILES: Dict[str, str] = {
   "hexagonale": "Hexagonale.png",
   "chc cylindrique": "CHC Cylindrique.png",
   "chc fraisee": "CHC fraisee.png",
   "chc bombee": "CHC bombee.png",
   "bombee fendue": "bombee fendue.png",
   "bombee philips": "Vis_bombee_philips_pozidriv.png",
   "bombee pozidriv": "Vis_bombee_philips_pozidriv.png",
   "bombee torx interne": "Bombee Torx.png",
}
MONTAGE_IMAGES = {
   "direct": "Schema_appui_direct.png",
   "rondelle": "Schema_appui_rondelle.png",
}
def _load_images(names_to_files: Dict[str, str]) -> Dict[str, tk.PhotoImage]:
   images: Dict[str, tk.PhotoImage] = {}
   for key, filename in names_to_files.items():
       try:
           img = tk.PhotoImage(file=str(resource_path("assets", "img", filename)))
           images[key] = img
       except Exception:
           continue
   return images

APP_VERSION = "V1.0 Beta"
APP_BG = "#FFFFFF"
APP_FG = "#0A0A0A"
TEXT_FONT = ("Segoe UI", 9)
SMALL_FONT = ("Segoe UI", 8)
BOLD_FONT = ("Segoe UI", 9, "bold")


def enable_dark_title_bar(window: tk.Tk) -> None:
   if sys.platform != "win32":
       return
   try:
       attribute = 20
       if sys.getwindowsversion().build < 17763:
           attribute = 19
       hwnd = window.winfo_id()
       value = ctypes.c_int(1)
       ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value))
   except Exception:
       pass


def load_diametres(path: Path) -> List[float]:
   values: List[float] = []
   try:
       with path.open("r", encoding="utf-8", newline="") as fichier:
           reader = csv.DictReader(fichier, delimiter=";")
           for row in reader:
               cell = (row.get("Diametre nominale") or "").strip()
               if not cell or cell == "-":
                   continue
               try:
                   values.append(float(cell.replace(",", ".")))
               except ValueError:
                   continue
   except FileNotFoundError:
       pass
   return sorted(set(values))


def to_float(text: str) -> float:
   return float(text.strip().replace(",", "."))


def format_couple(value: float, unit: str) -> str:
   if unit == "N.m":
       return f"{value / 1000.0:.2f}"
   return f"{value:.0f}"


def make_scrollable(parent: ttk.Frame) -> ttk.Frame:
   canvas = tk.Canvas(parent, background=APP_BG, highlightthickness=0)
   vbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
   hbar = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
   container = ttk.Frame(canvas, style="App.TFrame")
   window_id = canvas.create_window((0, 0), window=container, anchor="nw")
   show_hbar = {"visible": False}

   def _update_scrollregion(_: object = None) -> None:
       bbox = canvas.bbox("all")
       if bbox:
           canvas.configure(scrollregion=bbox)
       canvas_width = canvas.winfo_width()
       req_width = container.winfo_reqwidth()
       if req_width > canvas_width + 8:
           if not show_hbar["visible"]:
               hbar.grid(row=1, column=0, sticky="ew")
               show_hbar["visible"] = True
           canvas.itemconfigure(window_id, width=req_width)
       else:
           if show_hbar["visible"]:
               hbar.grid_remove()
               show_hbar["visible"] = False
           canvas.itemconfigure(window_id, width=canvas_width)

   container.bind("<Configure>", _update_scrollregion)
   canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
   canvas.grid(row=0, column=0, sticky="nsew")
   vbar.grid(row=0, column=1, sticky="ns")
   parent.columnconfigure(0, weight=1)
   parent.rowconfigure(0, weight=1)

   def _on_mousewheel(event: tk.Event) -> None:
       if sys.platform == "darwin":
           canvas.yview_scroll(-1 * int(event.delta), "units")
       else:
           canvas.yview_scroll(-1 * int(event.delta / 120), "units")

   canvas.bind_all("<MouseWheel>", _on_mousewheel)
   canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
   canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
   return container


def build_image_panel(parent: ttk.Frame, image_ref: tk.PhotoImage | None) -> None:
   img_label = ttk.Label(parent, style="App.TLabel")
   img_label.grid(row=0, column=0, sticky="n")
   if image_ref is not None:
       img_label.configure(image=image_ref)
       img_label.image = image_ref  # type: ignore[attr-defined]
   else:
       img_label.configure(text="Illustration indisponible")

   ttk.Label(
       parent,
       text="Norme ISO 68-1 - filets à 60°",
       style="App.TLabel",
       font=BOLD_FONT,
   ).grid(row=1, column=0, pady=(10, 0), sticky="n")
   ttk.Label(parent, text=f"Version {APP_VERSION}", style="App.TLabel", font=SMALL_FONT).grid(
       row=2, column=0, pady=(4, 0), sticky="n"
   )
   parent.columnconfigure(0, weight=1)


def add_separator(frame: ttk.Frame, row: int, pady: tuple[int, int] = (10, 14)) -> None:
   sep = ttk.Separator(frame, orient="horizontal")
   sep.grid(row=row, column=0, sticky="ew", pady=pady)


def build_friction_block(
   parent: ttk.Frame,
   rowi: int,
   label_pady: tuple[int, int],
   field_pady: tuple[int, int],
) -> tuple[int, dict[str, object]]:
   ttk.Label(parent, text="Frottements", style="Section.TLabel").grid(row=rowi, column=0, sticky="w", pady=(0, 6))
   rowi += 1

   mode_var = tk.StringVar(value="max")
   chk_max_var = tk.BooleanVar(value=True)
   chk_min_var = tk.BooleanVar(value=False)
   manual_var = tk.BooleanVar(value=False)
   mu_filet_var = tk.StringVar(value="")
   mu_sous_var = tk.StringVar(value="")

   def set_max() -> None:
       chk_max_var.set(True)
       chk_min_var.set(False)
       mode_var.set("max")
       manual_var.set(False)

   def set_min() -> None:
       chk_min_var.set(True)
       chk_max_var.set(False)
       mode_var.set("min")
       manual_var.set(False)

   ttk.Checkbutton(parent, text="Frottement max.", variable=chk_max_var, command=set_max, style="App.TCheckbutton").grid(
       row=rowi, column=0, sticky="w", pady=field_pady
   )
   rowi += 1
   ttk.Checkbutton(parent, text="Frottement min.", variable=chk_min_var, command=set_min, style="App.TCheckbutton").grid(
       row=rowi, column=0, sticky="w", pady=field_pady
   )
   rowi += 1

   manual_label_filet = ttk.Label(parent, text="Frottement des filets", style="App.TLabel")
   manual_entry_filet = ttk.Entry(parent, textvariable=mu_filet_var)
   manual_label_sous = ttk.Label(parent, text="Frottement sous tete", style="App.TLabel")
   manual_entry_sous = ttk.Entry(parent, textvariable=mu_sous_var)

   ttk.Checkbutton(
       parent,
       text="Saisir les coefficients",
       variable=manual_var,
       style="App.TCheckbutton",
   ).grid(row=rowi, column=0, sticky="w", pady=field_pady)
   rowi += 1
   manual_start = rowi

   def refresh_manual() -> None:
       base_row = manual_start
       if manual_var.get():
           manual_label_filet.grid(row=base_row, column=0, sticky="w", pady=label_pady)
           manual_entry_filet.grid(row=base_row + 1, column=0, sticky="ew", pady=field_pady)
           manual_label_sous.grid(row=base_row + 2, column=0, sticky="w", pady=label_pady)
           manual_entry_sous.grid(row=base_row + 3, column=0, sticky="ew", pady=field_pady)
       else:
           manual_label_filet.grid_remove()
           manual_entry_filet.grid_remove()
           manual_label_sous.grid_remove()
           manual_entry_sous.grid_remove()
           mu_filet_var.set("")
           mu_sous_var.set("")

   def refresh_state(*_: object) -> None:
       if manual_var.get():
           chk_max_var.set(False)
           chk_min_var.set(False)
       else:
           if not chk_max_var.get() and not chk_min_var.get():
               chk_max_var.set(True)
               mode_var.set("max")
       refresh_manual()

   manual_var.trace_add("write", refresh_state)
   chk_max_var.trace_add("write", lambda *_: refresh_state())
   chk_min_var.trace_add("write", lambda *_: refresh_state())
   refresh_state()
   rowi = manual_start + 4

   state = {
       "mode_var": mode_var,
       "manual_var": manual_var,
       "mu_filet_var": mu_filet_var,
       "mu_sous_var": mu_sous_var,
       "chk_max": chk_max_var,
       "chk_min": chk_min_var,
   }
   return rowi, state


def build_results_block(parent: ttk.Frame) -> tuple[ttk.Frame, dict[str, tk.StringVar]]:
   res_frame = ttk.Frame(parent, padding=(0, 8), style="App.TFrame")
   res_frame.columnconfigure(0, weight=1)
   labels = {
       "ft": tk.StringVar(value=""),
       "glissement": tk.StringVar(value=""),
       "traction": tk.StringVar(value=""),
       "torsion": tk.StringVar(value=""),
       "vm": tk.StringVar(value=""),
       "pertes_filet": tk.StringVar(value=""),
       "pertes_tete": tk.StringVar(value=""),
       "pertes_total": tk.StringVar(value=""),
   }

   ttk.Separator(res_frame, orient="horizontal").grid(row=0, column=0, sticky="ew", pady=(0, 4))
   ttk.Label(
       res_frame,
       text="Efforts, Contraintes et Pertes par frottements",
       style="Result.TLabel",
       font=("Segoe UI", 10, "bold"),
   ).grid(row=1, column=0, sticky="w", pady=(0, 8))

   section_row = 2
   ttk.Label(res_frame, text="1) Effort de serrage (Pre-charge)", style="App.TLabel", font=BOLD_FONT).grid(
       row=section_row, column=0, sticky="w", pady=(0, 4)
   )
   section_row += 1
   ttk.Label(res_frame, text="Ft (N)", style="App.TLabel").grid(
       row=section_row, column=0, sticky="w", pady=(0, 2)
   )
   section_row += 1
   ttk.Entry(res_frame, textvariable=labels["ft"], state="readonly").grid(
       row=section_row, column=0, sticky="ew", pady=(0, 8)
   )
   section_row += 1

   ttk.Label(res_frame, text="2) Force de resistance au glissement", style="App.TLabel", font=BOLD_FONT).grid(
       row=section_row, column=0, sticky="w", pady=(0, 4)
   )
   section_row += 1
   ttk.Label(res_frame, text="Force de Cisaillement limite (N)", style="App.TLabel").grid(
       row=section_row, column=0, sticky="w", pady=(0, 2)
   )
   section_row += 1
   ttk.Entry(res_frame, textvariable=labels["glissement"], state="readonly").grid(
       row=section_row, column=0, sticky="ew", pady=(0, 8)
   )
   section_row += 1

   ttk.Label(res_frame, text="3) Contraintes", style="App.TLabel", font=BOLD_FONT).grid(
       row=section_row, column=0, sticky="w", pady=(0, 4)
   )
   section_row += 1
   for key, text in [
       ("traction", "Contrainte de Traction dans les filets (MPa)"),
       ("torsion", "Contrainte de Torsion dans les filets (MPa)"),
       ("vm", "Contrainte Equivalente VM (MPa)"),
   ]:
       ttk.Label(res_frame, text=text, style="App.TLabel").grid(row=section_row, column=0, sticky="w", pady=(0, 2))
       section_row += 1
       ttk.Entry(res_frame, textvariable=labels[key], state="readonly").grid(
           row=section_row, column=0, sticky="ew", pady=(0, 8)
       )
       section_row += 1

   ttk.Label(res_frame, text="4) Pertes par frottements", style="App.TLabel", font=BOLD_FONT).grid(
       row=section_row, column=0, sticky="w", pady=(0, 4)
   )
   section_row += 1
   ttk.Label(res_frame, text="Pertes de frottement dans les filets (%)", style="App.TLabel").grid(
       row=section_row, column=0, sticky="w", pady=(0, 2)
   )
   section_row += 1
   ttk.Entry(res_frame, textvariable=labels["pertes_filet"], state="readonly").grid(
       row=section_row, column=0, sticky="ew", pady=(0, 6)
   )
   section_row += 1
   ttk.Label(res_frame, text="Pertes de frottement sous la tete (%)", style="App.TLabel").grid(
       row=section_row, column=0, sticky="w", pady=(0, 2)
   )
   section_row += 1
   ttk.Entry(res_frame, textvariable=labels["pertes_tete"], state="readonly").grid(
       row=section_row, column=0, sticky="ew", pady=(0, 6)
   )
   section_row += 1
   ttk.Label(res_frame, text="Pertes totales (%)", style="App.TLabel").grid(
       row=section_row, column=0, sticky="w", pady=(0, 2)
   )
   section_row += 1
   ttk.Entry(res_frame, textvariable=labels["pertes_total"], state="readonly").grid(
       row=section_row, column=0, sticky="ew", pady=(0, 6)
   )

   return res_frame, labels


def build_calcul_tab(
   parent: ttk.Frame,
   image_ref: tk.PhotoImage | None,
   diam_values: Sequence[float],
   materials: Sequence[str],
   tete_table: Dict[float, Dict[str, float]],
   head_types: Sequence[str],
) -> None:
   head_images = _load_images(HEAD_IMAGE_FILES)
   montage_images = _load_images(MONTAGE_IMAGES)
   container = make_scrollable(parent)
   left = ttk.Frame(container, padding=12, style="App.TFrame")
   right = ttk.Frame(container, padding=12, style="App.TFrame")
   left.grid(row=0, column=0, sticky="nsw")
   right.grid(row=0, column=1, sticky="nsew")
   container.columnconfigure(1, weight=1)

   rowi = 0
   label_pady = (0, 2)
   field_pady = (0, 8)

   ttk.Label(left, text="Géometrie", style="Section.TLabel").grid(row=rowi, column=0, sticky="w", pady=(0, 6))
   rowi += 1
   ttk.Label(left, text="Diametre nominal (M-)", style="App.TLabel").grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   cb_diam = ttk.Combobox(left, values=[f"{d:g}" for d in diam_values] or ["8", "10", "12"], state="readonly")
   cb_diam.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   default_dn = 12.0
   cb_diam.set(f"{default_dn:g}")
   rowi += 1

   head_display_map = {name: HEAD_LABEL_MAP.get(name, name) for name in head_types}
   head_type_values = [head_display_map[name] for name in head_types] if head_types else list(DEFAULT_HEAD_TYPES)
   if "Autre" not in head_type_values:
       head_type_values = list(dict.fromkeys(head_type_values + ["Autre"]))
   ttk.Label(left, text="Tete de vis", style="App.TLabel").grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   cb_head_type = ttk.Combobox(left, values=head_type_values, state="readonly")
   cb_head_type.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   if head_type_values:
       cb_head_type.set(head_type_values[0])
   rowi += 1

   dh_info_var = tk.StringVar(value="")
   dh_info_label = ttk.Label(left, textvariable=dh_info_var, style="App.TLabel")
   info_row = rowi
   warn_row = info_row
   manual_label_row = info_row + 1
   manual_entry_row = info_row + 2

   warn_label = ttk.Label(
       left,
       text="Pas de taille ISO pour ce diametre, saisissez une valeur :",
       style="App.TLabel",
       foreground="#CC0000",
   )
   manual_dh_var = tk.StringVar(value="")
   manual_label = ttk.Label(left, text="Diametre tete de vis (mm)", style="App.TLabel")
   ent_dh = ttk.Entry(left, textvariable=manual_dh_var)

   def _lookup_iso_dh() -> Optional[float]:
       try:
           dn_value = to_float(cb_diam.get())
       except Exception:
           return None
       head_value = cb_head_type.get().strip()
       if head_value.lower() == "autre":
           return None
       if not head_value:
           return None
       table = tete_table or core.load_tete_vis_table()[0]
       target_head = HEAD_REVERSE_MAP.get(head_value, head_value).lower()
       for diam_key, heads in table.items():
           if abs(diam_key - dn_value) <= 1e-6:
               for name, value in heads.items():
                   if name.lower() == target_head:
                       return value
       return None

   def refresh_diam_tete(*_: object) -> None:
       dh_iso = _lookup_iso_dh()
       if dh_iso is not None:
           dh_info_var.set(f"Diametre tete de vis ISO : {dh_iso:g} mm")
           dh_info_label.grid(row=info_row, column=0, sticky="w", pady=(0, 6))
           warn_label.grid_remove()
           manual_label.grid_remove()
           ent_dh.grid_remove()
           manual_dh_var.set("")
       else:
           dh_info_var.set("")
           dh_info_label.grid_remove()
           warn_label.grid(row=warn_row, column=0, sticky="w", pady=(0, 2))
           manual_label.grid(row=manual_label_row, column=0, sticky="w", pady=label_pady)
           ent_dh.grid(row=manual_entry_row, column=0, sticky="ew", pady=field_pady)

   def _on_head_change(*_: object) -> None:
       refresh_diam_tete()
       update_images()

   cb_diam.bind("<<ComboboxSelected>>", refresh_diam_tete)
   cb_head_type.bind("<<ComboboxSelected>>", _on_head_change)
   refresh_diam_tete()
   rowi = manual_entry_row + 1

   add_separator(left, rowi)
   rowi += 1

   ttk.Label(left, text="Matériaux", style="Section.TLabel").grid(row=rowi, column=0, sticky="w", pady=(0, 6))
   rowi += 1
   is_filet_lub = tk.BooleanVar(value=False)
   has_under_head = tk.BooleanVar(value=False)
   has_washer = tk.BooleanVar(value=False)

   default_mat = "Acier" if "Acier" in materials else (materials[0] if materials else "")
   ttk.Label(left, text="Vis", style="App.TLabel").grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   cb_mat_vis = ttk.Combobox(left, values=list(materials), state="readonly")
   cb_mat_vis.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   cb_mat_vis.set(default_mat)
   rowi += 1

   ttk.Label(left, text="Pièce taraudée", style="App.TLabel").grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   cb_mat_body = ttk.Combobox(left, values=list(materials), state="readonly")
   cb_mat_body.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   cb_mat_body.set(default_mat)
   rowi += 1

   ttk.Checkbutton(left, text="Lubrification des filets", variable=is_filet_lub, style="App.TCheckbutton").grid(
       row=rowi, column=0, sticky="w", pady=field_pady
   )
   rowi += 1

   chk_under_head = ttk.Checkbutton(
       left,
       text="Surface d'appui (différent de pièce taraudée)",
       variable=has_under_head,
       style="App.TCheckbutton",
   )
   chk_under_head.grid(row=rowi, column=0, sticky="w", pady=field_pady)
   rowi += 1

   under_head_label = ttk.Label(left, text="Surface d'appui", style="App.TLabel")
   under_head_label.grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   cb_mat_sous_tete = ttk.Combobox(left, values=list(materials), state="disabled")
   cb_mat_sous_tete.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   cb_mat_sous_tete.set(default_mat)
   rowi += 1

   # Rondelle
   chk_washer = ttk.Checkbutton(left, text="Presence d'une rondelle", variable=has_washer, style="App.TCheckbutton")
   chk_washer.grid(row=rowi, column=0, sticky="w", pady=field_pady)
   rowi += 1

   washer_label = ttk.Label(left, text="Rondelle", style="App.TLabel")
   cb_mat_washer = ttk.Combobox(left, values=list(materials), state="disabled")
   cb_mat_washer.set(default_mat)
   washer_under_label = ttk.Label(left, text="Surface d'appui", style="App.TLabel")
   cb_mat_under_washer = ttk.Combobox(left, values=list(materials), state="disabled")
   cb_mat_under_washer.set(default_mat)

   washer_base_row = rowi

   def toggle_washer() -> None:
       if has_washer.get():
           washer_label.grid(row=washer_base_row, column=0, sticky="w", pady=label_pady)
           cb_mat_washer.grid(row=washer_base_row + 1, column=0, sticky="ew", pady=field_pady)
           washer_under_label.grid(row=washer_base_row + 2, column=0, sticky="w", pady=label_pady)
           cb_mat_under_washer.grid(row=washer_base_row + 3, column=0, sticky="ew", pady=field_pady)
           cb_mat_washer.configure(state="readonly")
           cb_mat_under_washer.configure(state="readonly")
       else:
           washer_label.grid_remove()
           cb_mat_washer.grid_remove()
           washer_under_label.grid_remove()
           cb_mat_under_washer.grid_remove()
           cb_mat_washer.configure(state="disabled")
           cb_mat_under_washer.configure(state="disabled")
   chk_washer.configure(command=lambda: (toggle_washer(), update_support_washer_visibility()))
   toggle_washer()
   rowi += 4

   def sync_under_head_material(*_: object) -> None:
       if not has_under_head.get():
           cb_mat_sous_tete.set(cb_mat_body.get())

   def sync_under_head_state() -> None:
       if has_under_head.get():
           cb_mat_sous_tete.configure(state="readonly")
       else:
           cb_mat_sous_tete.configure(state="disabled")
           cb_mat_sous_tete.set(cb_mat_body.get())

   def update_support_washer_visibility() -> None:
       if has_under_head.get():
           if has_washer.get():
               has_washer.set(False)
               toggle_washer()
           chk_washer.grid_remove()
       else:
           chk_washer.grid()

       if has_washer.get():
           if has_under_head.get():
               has_under_head.set(False)
               sync_under_head_state()
           chk_under_head.grid_remove()
           under_head_label.grid_remove()
           cb_mat_sous_tete.grid_remove()
       else:
           chk_under_head.grid()
           under_head_label.grid()
           cb_mat_sous_tete.grid()
           sync_under_head_state()

   chk_under_head.configure(command=lambda: (sync_under_head_state(), update_support_washer_visibility()))
   cb_mat_body.bind("<<ComboboxSelected>>", sync_under_head_material)
   sync_under_head_state()
   update_support_washer_visibility()

   image_title_font = ("Segoe UI", 14, "bold", "italic")
   title_color = "#0A2E5C"
   vis_title = ttk.Label(right, text="Vis", style="App.TLabel", font=image_title_font, foreground=title_color)
   vis_title.grid(row=0, column=0, sticky="n", pady=(0, 6))
   vis_img_label = ttk.Label(right, style="App.TLabel")
   vis_img_label.grid(row=1, column=0, sticky="n", pady=(0, 12))
   sep_images = ttk.Separator(right, orient="horizontal")
   sep_images.grid(row=2, column=0, sticky="ew", pady=(4, 8))
   montage_title = ttk.Label(right, text="Montage", style="App.TLabel", font=image_title_font, foreground=title_color)
   montage_title.grid(row=3, column=0, sticky="n", pady=(0, 6))
   montage_img_label = ttk.Label(right, style="App.TLabel")
   montage_img_label.grid(row=4, column=0, sticky="n", pady=(0, 8))
   iso_label_calc = ttk.Label(
       right,
       text="Norme ISO 68-1 - filet à 60°",
       style="App.TLabel",
       font=BOLD_FONT,
   )
   iso_label_calc.grid(row=5, column=0, sticky="n", pady=(6, 0))
   right.columnconfigure(0, weight=1)

   def update_images(*_: object) -> None:
       head_value = cb_head_type.get().strip()
       head_key = HEAD_REVERSE_MAP.get(head_value, head_value).lower()
       # Fallback "Autre" -> CHC cylindrique
       head_lookup = head_value.lower()
       if head_lookup == "autre":
           head_lookup = "chc cylindrique"
           head_key = head_lookup
       head_img = head_images.get(head_lookup) or head_images.get(head_key) or image_ref
       if head_img is not None:
           try:
               scaled = head_img.zoom(7, 7).subsample(10, 10)  # ~70 %
               head_img_use = scaled
           except Exception:
               head_img_use = head_img
           vis_img_label.configure(image=head_img_use, text="")
           vis_img_label.image = head_img_use  # type: ignore[attr-defined]
       else:
           vis_img_label.configure(image="", text="")
       montage_key = "rondelle" if has_washer.get() else "direct"
       montage_img = montage_images.get(montage_key) or image_ref
       if montage_img is not None:
           montage_img_label.configure(image=montage_img, text="")
           montage_img_label.image = montage_img  # type: ignore[attr-defined]
       else:
           montage_img_label.configure(image="", text="")

   chk_under_head.configure(command=lambda: (sync_under_head_state(), update_support_washer_visibility(), update_images()))
   chk_washer.configure(command=lambda: (toggle_washer(), update_support_washer_visibility(), update_images()))
   update_images()

   add_separator(left, rowi)
   rowi += 1

   rowi, friction_state = build_friction_block(left, rowi, label_pady, field_pady)

   add_separator(left, rowi)
   rowi += 1

   ttk.Label(left, text="Chargement", style="Section.TLabel").grid(row=rowi, column=0, sticky="w", pady=(0, 6))
   rowi += 1
   ttk.Label(left, text="Couple", style="App.TLabel").grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   ent_cpl = ttk.Entry(left)
   ent_cpl.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   ent_cpl.insert(0, "40")
   rowi += 1

   ttk.Label(left, text="Unités", style="App.TLabel").grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   cb_units = ttk.Combobox(left, values=["N.mm", "N.m"], state="readonly")
   cb_units.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   cb_units.set("N.m")
   rowi += 1

   add_separator(left, rowi)
   rowi += 1

   ttk.Label(left, text="Actions", style="Section.TLabel").grid(row=rowi, column=0, sticky="w", pady=(0, 6))
   rowi += 1
   btn_calc = ttk.Button(left, text="Calculer")
   btn_calc.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   rowi += 1
   btn_reset = ttk.Button(left, text="Réinitialiser")
   btn_reset.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   rowi += 1

   sep_label = ttk.Separator(left, orient="horizontal")
   results_frame, result_vars = build_results_block(left)
   results_visible = False

   def show_results() -> None:
       nonlocal results_visible
       if not results_visible:
           sep_label.grid(row=rowi, column=0, sticky="ew", pady=(8, 4))
           results_frame.grid(row=rowi + 1, column=0, sticky="ew")
           results_visible = True

   def hide_results() -> None:
       nonlocal results_visible
       if results_visible:
           sep_label.grid_remove()
           results_frame.grid_remove()
           results_visible = False
       for var in result_vars.values():
           var.set("")

   def compute() -> None:
       try:
           dn = to_float(cb_diam.get())
           head_type = cb_head_type.get().strip()
           lookup_name = HEAD_REVERSE_MAP.get(head_type, head_type)
           dh_iso = tete_table.get(dn, {}).get(lookup_name)
           if dh_iso is None:
               manual_value = manual_dh_var.get().strip()
               if not manual_value:
                   messagebox.showerror(
                       "Erreur",
                       "Pas de taille ISO pour ce diametre, saisissez une valeur :",
                   )
                   return
               dh = to_float(manual_value)
               if dh <= 0 or dh >= 120:
                   messagebox.showerror("Erreur", "Le diametre de tete doit etre positif et inferieur a 120 mm.")
                   return
           else:
               dh = dh_iso
           if dh < dn:
               messagebox.showerror(
                   "Erreur",
                   "diametre de tete plus petit que le diametre nominale saisir une valeur valide",
               )
               return
           mat_vis = cb_mat_vis.get().strip()
           mat_body = cb_mat_body.get().strip()
           couple = to_float(ent_cpl.get())
           if cb_units.get() == "N.m":
               couple *= 1000.0
           if couple <= 0:
               messagebox.showerror("Erreur", "Veuillez saisir un couple positif.")
               return

           has_under_head_value = has_under_head.get()
           sous_tete_value = cb_mat_sous_tete.get().strip() if has_under_head_value else None
           has_washer_value = has_washer.get() if not has_under_head_value else False
           mat_washer_value: Optional[str] = None
           mat_under_washer_value: Optional[str] = None
           if has_washer_value:
               mat_washer_value = cb_mat_washer.get().strip()
               mat_under_washer_value = cb_mat_under_washer.get().strip()
               if not mat_washer_value or not mat_under_washer_value:
                   messagebox.showerror("Erreur", "Merci de renseigner les materiaux de la rondelle.")
                   return
           friction_mode = str(friction_state["mode_var"].get())
           mu_filet_manual = None
           mu_sous_manual = None
           if friction_state["manual_var"].get():
               text_filet = friction_state["mu_filet_var"].get().strip()
               text_sous = friction_state["mu_sous_var"].get().strip()
               if not text_filet or not text_sous:
                   messagebox.showerror("Erreur", "Merci de saisir les deux coefficients de frottement.")
                   return
               mu_filet_manual = to_float(text_filet)
               mu_sous_manual = to_float(text_sous)
               for value, label in [(mu_filet_manual, "Frottement des filets"), (mu_sous_manual, "Frottement sous tete")]:
                   if value < 0 or value > 1:
                       messagebox.showerror("Erreur", f"{label} doit etre compris entre 0 et 1.")
                       return

           vis = Vis(diam_nominale=dn, diam_tete=dh, mat_vis=mat_vis)
           effort = vis.effort_serrage(
               couple,
               mat_body=mat_body,
               is_lubrified=is_filet_lub.get(),
               mat_sous_tete=sous_tete_value,
               is_sous_tete_lubrified=False,
               friction_mode=friction_mode,
               mu_filet_manual=mu_filet_manual,
               mu_sous_tete_manual=mu_sous_manual,
               has_washer=has_washer_value,
               mat_rondelle=mat_washer_value,
               mat_sous_rondelle=mat_under_washer_value,
           )

           result_vars["ft"].set(f"{effort:.0f}")
           result_vars["glissement"].set(f"{vis.force_resistance_glissement:.0f}")
           result_vars["traction"].set(f"{vis.contrainte_traction:.1f}")
           result_vars["torsion"].set(f"{vis.contrainte_torsion:.1f}")
           result_vars["vm"].set(f"{vis.contrainte_vm:.1f}")
           result_vars["pertes_filet"].set(f"{vis.pertes_frottements_filet:.0f}")
           result_vars["pertes_tete"].set(f"{vis.pertes_frottements_tete:.0f}")
           result_vars["pertes_total"].set(f"{vis.pertes_frottements_totale:.0f}")
           show_results()
       except Exception as exc:
           messagebox.showerror("Erreur", str(exc))

   def reset() -> None:
       hide_results()

   btn_calc.configure(command=compute)
   btn_reset.configure(command=reset)
   left.columnconfigure(0, weight=1)


def build_dimensionnement_tab(
   parent: ttk.Frame,
   image_ref: tk.PhotoImage | None,
   diam_values: Sequence[float],
   materials: Sequence[str],
   tete_table: Dict[float, Dict[str, float]],
) -> None:
   style = ttk.Style()
   label_style = "Construction.TLabel"
   section_style = "Construction.Section.TLabel"
   check_style = "Construction.TCheckbutton"
   entry_style = "Construction.TEntry"
   combo_style = "Construction.TCombobox"
   button_style = "Construction.TButton"
   base_colors = {"background": APP_BG, "foreground": APP_FG}
   style.configure(label_style, font=("Segoe UI", 10), **base_colors)
   style.configure(section_style, font=("Segoe UI", 18, "bold"), foreground="#0c5da5", background=APP_BG)
   style.configure(check_style, font=("Segoe UI", 10), **base_colors)
   style.configure(entry_style, font=("Segoe UI", 10))
   style.configure(combo_style, font=("Segoe UI", 10))
   style.configure(button_style, font=("Segoe UI", 10))

   container = make_scrollable(parent)
   left = ttk.Frame(container, padding=12, style="App.TFrame")
   right = ttk.Frame(container, padding=12, style="App.TFrame")
   left.grid(row=0, column=0, sticky="nw")
   right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
   container.columnconfigure(0, weight=0)
   container.columnconfigure(1, weight=1)

   rowi = 0
   label_pady = (0, 2)
   field_pady = (0, 8)
   default_mat = "Acier" if "Acier" in materials else (materials[0] if materials else "")

   ttk.Label(left, text="Géométrie", style="Section.TLabel").grid(row=rowi, column=0, sticky="w", pady=(0, 6))
   rowi += 1
   ttk.Label(left, text="Intervalle de diametre", style=label_style).grid(row=rowi, column=0, sticky="w", pady=(0, 6))
   rowi += 1
   interval_frame = ttk.Frame(left, style="App.TFrame")
   interval_frame.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   interval_frame.columnconfigure(0, weight=1)
   interval_frame.columnconfigure(1, weight=1)
   ttk.Label(interval_frame, text="Diametre min.", style=label_style).grid(row=0, column=0, sticky="w", pady=label_pady)
   ttk.Label(interval_frame, text="Diametre max.", style=label_style).grid(row=0, column=1, sticky="w", pady=label_pady)
   cb_diam_min = ttk.Combobox(interval_frame, values=[f"{d:g}" for d in diam_values] or ["8", "10", "12"], state="readonly", style=combo_style)
   cb_diam_min.grid(row=1, column=0, sticky="ew", padx=(0, 4))
   cb_diam_min.set("12")
   cb_diam_max = ttk.Combobox(interval_frame, values=[f"{d:g}" for d in diam_values] or ["10", "12", "16"], state="readonly", style=combo_style)
   cb_diam_max.grid(row=1, column=1, sticky="ew", padx=(4, 0))
   cb_diam_max.set("14")
   rowi += 1

   manual_dh_dim = tk.StringVar(value="")
   manual_required = {"value": False}
   manual_row = rowi
   non_iso_label = ttk.Label(
       left,
       text="Pas de taille ISO pour ce diametre, saisissez une valeur de diametre de tete de vis",
       style=label_style,
       foreground="#CC0000",
   )
   manual_label_dim = ttk.Label(left, text="Diametre tete de vis (mm)", style=label_style)
   ent_dh_dim = ttk.Entry(left, textvariable=manual_dh_dim, style=entry_style)

   def update_manual_field(*_: object) -> None:
       try:
           diam_min_val = to_float(cb_diam_min.get())
           diam_max_val = to_float(cb_diam_max.get())
       except Exception:
           non_iso_label.grid_remove()
           manual_label_dim.grid_remove()
           ent_dh_dim.grid_remove()
           return
       if diam_min_val > diam_max_val:
           diam_min_val, diam_max_val = diam_max_val, diam_min_val
       candidates = [d for d in diam_values if diam_min_val - 1e-6 <= d <= diam_max_val + 1e-6]
       table = tete_table or core.load_tete_vis_table()[0]
       iso_available = any(table.get(d) for d in candidates)
       manual_required["value"] = not iso_available
       if iso_available:
           non_iso_label.grid_remove()
           manual_label_dim.grid_remove()
           ent_dh_dim.grid_remove()
           manual_dh_dim.set("")
       else:
           non_iso_label.grid(row=manual_row, column=0, sticky="w", pady=(0, 2))
           manual_label_dim.grid(row=manual_row + 1, column=0, sticky="w", pady=label_pady)
           ent_dh_dim.grid(row=manual_row + 2, column=0, sticky="ew", pady=field_pady)

   cb_diam_min.bind("<<ComboboxSelected>>", update_manual_field)
   cb_diam_max.bind("<<ComboboxSelected>>", update_manual_field)
   update_manual_field()
   rowi += 3

   add_separator(left, rowi)
   rowi += 1

   ttk.Label(left, text="Matériaux", style=section_style).grid(row=rowi, column=0, sticky="w", pady=(0, 6))
   rowi += 1

   ttk.Label(left, text="Vis", style=label_style).grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   cb_mat_vis_dim = ttk.Combobox(left, values=list(materials), state="readonly", style=combo_style)
   cb_mat_vis_dim.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   cb_mat_vis_dim.set(default_mat)
   rowi += 1

   ttk.Label(left, text="Pièce taraudée", style=label_style).grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   cb_mat_body_dim = ttk.Combobox(left, values=list(materials), state="readonly", style=combo_style)
   cb_mat_body_dim.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   cb_mat_body_dim.set(default_mat)
   rowi += 1

   has_under_head_dim = tk.BooleanVar(value=False)
   chk_under_head_dim = ttk.Checkbutton(
       left,
       text="Surface d'appui (différent de pièce taraudée)",
       variable=has_under_head_dim,
       style=check_style,
   )
   chk_under_head_dim.grid(row=rowi, column=0, sticky="w", pady=field_pady)
   rowi += 1

   under_head_label_dim = ttk.Label(left, text="Surface d'appui", style=label_style)
   under_head_label_dim.grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   cb_mat_sous_tete_dim = ttk.Combobox(left, values=list(materials), state="disabled", style=combo_style)
   cb_mat_sous_tete_dim.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   cb_mat_sous_tete_dim.set(default_mat)
   rowi += 1

   def sync_under_head_dim(*_: object) -> None:
       if has_under_head_dim.get():
           cb_mat_sous_tete_dim.configure(state="readonly")
       else:
           cb_mat_sous_tete_dim.configure(state="disabled")
           cb_mat_sous_tete_dim.set(cb_mat_body_dim.get())

   def update_support_washer_dim() -> None:
       if has_under_head_dim.get():
           if has_washer_dim.get():
               has_washer_dim.set(False)
               toggle_washer_dim()
           chk_washer_dim.grid_remove()
       else:
           chk_washer_dim.grid()

       if has_washer_dim.get():
           if has_under_head_dim.get():
               has_under_head_dim.set(False)
               sync_under_head_dim()
           chk_under_head_dim.grid_remove()
           under_head_label_dim.grid_remove()
           cb_mat_sous_tete_dim.grid_remove()
       else:
           chk_under_head_dim.grid()
           under_head_label_dim.grid()
           cb_mat_sous_tete_dim.grid()
           sync_under_head_dim()

   chk_under_head_dim.configure(command=lambda: (sync_under_head_dim(), update_support_washer_dim()))
   cb_mat_body_dim.bind("<<ComboboxSelected>>", sync_under_head_dim)
   sync_under_head_dim()

   is_filet_lub_dim = tk.BooleanVar(value=False)
   ttk.Checkbutton(
       left,
       text="Lubrification des filets",
       variable=is_filet_lub_dim,
       style=check_style,
   ).grid(row=rowi, column=0, sticky="w", pady=field_pady)
   rowi += 1
   has_washer_dim = tk.BooleanVar(value=False)
   chk_washer_dim = ttk.Checkbutton(left, text="Presence d'une rondelle", variable=has_washer_dim, style=check_style)
   chk_washer_dim.grid(row=rowi, column=0, sticky="w", pady=field_pady)
   rowi += 1
   washer_label_dim = ttk.Label(left, text="Rondelle", style=label_style)
   cb_mat_washer_dim = ttk.Combobox(left, values=list(materials), state="disabled", style=combo_style)
   cb_mat_washer_dim.set(default_mat)
   washer_under_label_dim = ttk.Label(left, text="Surface d'appui", style=label_style)
   cb_mat_under_washer_dim = ttk.Combobox(left, values=list(materials), state="disabled", style=combo_style)
   cb_mat_under_washer_dim.set(default_mat)
   washer_base_row_dim = rowi

   def toggle_washer_dim() -> None:
       if has_washer_dim.get():
           washer_label_dim.grid(row=washer_base_row_dim, column=0, sticky="w", pady=label_pady)
           cb_mat_washer_dim.grid(row=washer_base_row_dim + 1, column=0, sticky="ew", pady=field_pady)
           washer_under_label_dim.grid(row=washer_base_row_dim + 2, column=0, sticky="w", pady=label_pady)
           cb_mat_under_washer_dim.grid(row=washer_base_row_dim + 3, column=0, sticky="ew", pady=field_pady)
           cb_mat_washer_dim.configure(state="readonly")
           cb_mat_under_washer_dim.configure(state="readonly")
       else:
           washer_label_dim.grid_remove()
           cb_mat_washer_dim.grid_remove()
           washer_under_label_dim.grid_remove()
           cb_mat_under_washer_dim.grid_remove()
           cb_mat_washer_dim.configure(state="disabled")
           cb_mat_under_washer_dim.configure(state="disabled")

   chk_washer_dim.configure(command=lambda: (toggle_washer_dim(), update_support_washer_dim()))
   toggle_washer_dim()
   update_support_washer_dim()
   rowi += 4

   add_separator(left, rowi)
   rowi += 1

   rowi, friction_state_dim = build_friction_block(left, rowi, label_pady, field_pady)

   add_separator(left, rowi)
   rowi += 1

   ttk.Label(left, text="Chargement", style=section_style).grid(row=rowi, column=0, sticky="w", pady=(0, 6))
   rowi += 1
   ttk.Label(left, text="Effort de serrage cible (N)", style=label_style).grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   ent_ft_cible = ttk.Entry(left, style=entry_style)
   ent_ft_cible.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   ent_ft_cible.insert(0, "10000")
   rowi += 1

   ttk.Label(left, text="Couple maximal constructeur", style=label_style).grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   ent_cpl_dim = ttk.Entry(left, style=entry_style)
   ent_cpl_dim.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   ent_cpl_dim.insert(0, "40")
   rowi += 1

   ttk.Label(left, text="Unités", style=label_style).grid(row=rowi, column=0, sticky="w", pady=label_pady)
   rowi += 1
   cb_units_dim = ttk.Combobox(left, values=["N.mm", "N.m"], state="readonly", style=combo_style)
   cb_units_dim.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   cb_units_dim.set("N.m")
   rowi += 1

   add_separator(left, rowi)
   rowi += 1

   ttk.Label(left, text="Actions", style=section_style).grid(row=rowi, column=0, sticky="w", pady=(0, 6))
   rowi += 1
   btn_calc_dim = ttk.Button(left, text="Calculer", style=button_style)
   btn_calc_dim.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   rowi += 1
   btn_reset_dim = ttk.Button(left, text="Réinitialiser", style=button_style)
   btn_reset_dim.grid(row=rowi, column=0, sticky="ew", pady=field_pady)
   rowi += 1

   sep_label = ttk.Separator(right, orient="horizontal")

   choix_label = ttk.Label(right, text="Choix de vis possible", style=label_style, font=BOLD_FONT)

   tree_frame = ttk.Frame(right, style="App.TFrame")
   tree = ttk.Treeview(
       tree_frame,
       columns=("diam", "couple", "effort", "etat", "matvis", "matbody", "matsoustete", "serie", "tetes"),
       show="headings",
       height=10,
   )
   tree.heading("diam", text="Diametre (M-)")
   tree.heading("couple", text="Couple")
   tree.heading("effort", text="Effort (N)")
   tree.heading("etat", text="Etat")
   tree.heading("matvis", text="Materiau vis")
   tree.heading("matbody", text="Materiau assemblage")
   tree.heading("matsoustete", text="Materiau sous tete")
   tree.heading("serie", text="Serie")
   tree.heading("tetes", text="Tête de vis")
   tree.column("diam", width=110, anchor="center")
   tree.column("couple", width=110, anchor="center")
   tree.column("effort", width=120, anchor="center")
   tree.column("etat", width=90, anchor="center")
   tree.column("matvis", width=130, anchor="center")
   tree.column("matbody", width=150, anchor="center")
   tree.column("matsoustete", width=150, anchor="center")
   tree.column("serie", width=140, anchor="center")
   tree.column("tetes", width=520, minwidth=500, anchor="w", stretch=True)
   tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
   tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
   tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
   tree.grid(row=0, column=0, sticky="nsew")
   tree_scroll_y.grid(row=0, column=1, sticky="ns")
   tree_scroll_x.grid(row=1, column=0, sticky="ew")
   tree_frame.columnconfigure(0, weight=1)
   tree_frame.rowconfigure(0, weight=1)

   right.columnconfigure(0, weight=1)
   right.rowconfigure(2, weight=1)
   right.rowconfigure(3, weight=0)
   right.rowconfigure(4, weight=0)

   status_var = tk.StringVar(value="")
   status_label = ttk.Label(right, textvariable=status_var, style=label_style, foreground="#CC0000")
   iso_label_dim = ttk.Label(
       right,
       text="Norme ISO 68-1 - filet à 60°",
       style=label_style,
       font=BOLD_FONT,
   )

   results_visible = False

   def show_results() -> None:
       nonlocal results_visible
       if not results_visible:
           choix_label.grid(row=0, column=0, sticky="w", pady=(4, 4))
           sep_label.grid(row=1, column=0, sticky="ew", pady=(8, 6))
           tree_frame.grid(row=2, column=0, sticky="nsew")
           status_label.grid(row=3, column=0, sticky="w", pady=(4, 0))
           iso_label_dim.grid(row=4, column=0, sticky="s", pady=(8, 0))
           results_visible = True

   def hide_results() -> None:
       nonlocal results_visible
       for item in tree.get_children():
           tree.delete(item)
       status_var.set("")
       if results_visible:
           choix_label.grid_remove()
           sep_label.grid_remove()
           tree_frame.grid_remove()
           status_label.grid_remove()
           iso_label_dim.grid_remove()
           results_visible = False

   def compute_dimensionnement() -> None:
       try:
           diam_min = to_float(cb_diam_min.get())
           diam_max = to_float(cb_diam_max.get())
           if diam_min > diam_max:
               diam_min, diam_max = diam_max, diam_min
           effort_cible = to_float(ent_ft_cible.get())
           couple_max = to_float(ent_cpl_dim.get())
           if cb_units_dim.get() == "N.m":
               couple_max *= 1000.0
           if effort_cible <= 0 or couple_max <= 0:
               messagebox.showerror("Erreur", "Effort cible et couple max doivent etre positifs.")
               return

           mat_vis = cb_mat_vis_dim.get().strip()
           mat_body = cb_mat_body_dim.get().strip()
           has_under_head_value = has_under_head_dim.get()
           mat_sous_tete = cb_mat_sous_tete_dim.get().strip() if has_under_head_value else None
           has_washer_value = has_washer_dim.get() if not has_under_head_value else False
           mat_washer_value: Optional[str] = None
           mat_under_washer_value: Optional[str] = None
           if has_washer_value:
               mat_washer_value = cb_mat_washer_dim.get().strip()
               mat_under_washer_value = cb_mat_under_washer_dim.get().strip()
               if not mat_washer_value or not mat_under_washer_value:
                   messagebox.showerror("Erreur", "Merci de renseigner les materiaux de la rondelle.")
                   return

           diam_candidates = [d for d in diam_values if diam_min - 1e-6 <= d <= diam_max + 1e-6]
           if not diam_candidates:
               messagebox.showerror("Erreur", "Aucun diametre nominal dans cette plage.")
               return
           iso_available = any(tete_table.get(d) for d in diam_candidates)
           manual_required["value"] = not iso_available
           manual_value: Optional[float] = None
           if manual_required["value"]:
               manual_text = manual_dh_dim.get().strip()
               if not manual_text:
                   messagebox.showerror(
                       "Erreur",
                       "Pas de taille ISO pour ce diametre, saisissez une valeur de diametre de tete de vis.",
                   )
                   return
               manual_value = to_float(manual_text)
               if manual_value <= 0 or manual_value >= 120:
                   messagebox.showerror("Erreur", "Le diametre de tete doit etre positif et inferieur a 120 mm.")
                   return
               if manual_value <= max(diam_candidates):
                   messagebox.showerror(
                       "Erreur",
                       "diametre de tete plus petit que le diametre nominale saisir une valeur valide",
                   )
                   return

           friction_mode = str(friction_state_dim["mode_var"].get())
           mu_filet_manual = None
           mu_sous_manual = None
           if friction_state_dim["manual_var"].get():
               text_filet = friction_state_dim["mu_filet_var"].get().strip()
               text_sous = friction_state_dim["mu_sous_var"].get().strip()
               if not text_filet or not text_sous:
                   messagebox.showerror("Erreur", "Merci de saisir les deux coefficients de frottement.")
                   return
               mu_filet_manual = to_float(text_filet)
               mu_sous_manual = to_float(text_sous)
               for value, label in [(mu_filet_manual, "Frottement des filets"), (mu_sous_manual, "Frottement sous tete")]:
                   if value < 0 or value > 1:
                       messagebox.showerror("Erreur", f"{label} doit etre compris entre 0 et 1.")
                       return

           results = dimensionner(
               diametres=diam_candidates,
               mat_vis=mat_vis,
               mat_body=mat_body,
               mat_sous_tete=mat_sous_tete,
               effort_cible=effort_cible,
               couple_max=couple_max,
               include_lubrified=is_filet_lub_dim.get(),
               tete_table=tete_table,
               manual_diam_tete=manual_value,
               friction_mode=friction_mode,
               mu_filet_manual=mu_filet_manual,
               mu_sous_tete_manual=mu_sous_manual,
               has_washer=has_washer_value,
               mat_rondelle=mat_washer_value,
               mat_sous_rondelle=mat_under_washer_value,
           )

           hide_results()
           if not results:
               if is_filet_lub_dim.get():
                   status_var.set("Pas de solution, essayez une autre configuration")
               else:
                   status_var.set("Pas de resultat, reessayer le calcul en lubrifiant votre assemblage")
               show_results()
               return

           has_dry = any(not r.lubrified for r in results)
           has_lube = any(r.lubrified for r in results)

           for res in results:
               unit = cb_units_dim.get()
               head_types_display = " / ".join(HEAD_LABEL_MAP.get(ht, ht) for ht in res.head_types) if res.head_types else "-"
               tree.insert(
                   "",
                   "end",
                   values=(
                       f"M{res.diam_nominale:g}",
                       f"{format_couple(res.couple, unit)} {unit}",
                       f"{res.effort:.0f}",
                       "Lubrifie" if res.lubrified else "Sec",
                       res.mat_vis,
                       res.mat_body,
                       res.mat_sous_tete,
                       "H12,H13,H14",
                       head_types_display,
                   ),
               )

           if is_filet_lub_dim.get() and not has_lube:
               status_var.set("Pas de solution, essayez une autre configuration")
           elif (not is_filet_lub_dim.get()) and not has_dry:
               status_var.set("Pas de resultat, reessayer le calcul en lubrifiant votre assemblage")
           else:
               status_var.set("")
           show_results()
       except Exception as exc:
           messagebox.showerror("Erreur", str(exc))

   def reset_dimensionnement() -> None:
       hide_results()

   btn_calc_dim.configure(command=compute_dimensionnement)
   btn_reset_dim.configure(command=reset_dimensionnement)
   left.columnconfigure(0, weight=1)


def main() -> None:
    root = tk.Tk()
    root.title(f"Bolt {APP_VERSION} - Calcul et Dimensionnement de Boulons")
    root.configure(bg=APP_BG)
    root.geometry("1200x850")
    root.option_add("*Font", "{Segoe UI} 9")
    enable_dark_title_bar(root)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("App.TFrame", background=APP_BG)
    style.configure("App.TLabel", background=APP_BG, foreground=APP_FG, font=TEXT_FONT)
    style.configure("App.TCheckbutton", background=APP_BG, foreground=APP_FG, font=TEXT_FONT)
    style.configure("App.TButton", font=TEXT_FONT)
    style.configure("Section.TLabel", background=APP_BG, foreground="#0c5da5", font=("Segoe UI", 18, "bold"))
    style.configure("Result.TLabel", background=APP_BG, foreground=APP_FG, font=BOLD_FONT)
    style.configure("SeparatorText.TLabel", background=APP_BG, foreground=APP_FG, font=TEXT_FONT)
    style.configure("Treeview", rowheight=22, font=TEXT_FONT)
    style.configure("Treeview.Heading", font=BOLD_FONT)
    style.configure("TNotebook", background=APP_BG, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(12, 6))
    style.map("TNotebook.Tab", background=[("selected", "#0c7bd9")], foreground=[("selected", "#ffffff")])

    try:
        icon = tk.PhotoImage(file=str(ICON_FILE))
        root.iconphoto(False, icon)
        root._icon_image = icon  # type: ignore[attr-defined]
    except Exception:
        pass

    image_ref = None
    image_construction = None

    diam_values = load_diametres(PAS_STD_FILE)
    materials = sorted(DISPLAY_MATERIALS)
    try:
        tete_table, head_types = core.load_tete_vis_table()
        if not head_types:
            head_types = tuple(DEFAULT_HEAD_TYPES)
    except Exception:
        tete_table, head_types = {}, tuple(DEFAULT_HEAD_TYPES)

    notebook = ttk.Notebook(root)
    notebook.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    tab_calc = ttk.Frame(notebook, style="App.TFrame")
    tab_dim = ttk.Frame(notebook, style="App.TFrame")
    notebook.add(tab_calc, text="Calcul")
    notebook.add(tab_dim, text="Construction")

    build_calcul_tab(tab_calc, image_ref, diam_values, materials, tete_table, head_types)
    build_dimensionnement_tab(tab_dim, image_construction, diam_values, materials, tete_table)

    def on_close() -> None:
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
