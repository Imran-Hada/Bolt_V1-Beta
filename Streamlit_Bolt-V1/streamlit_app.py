from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if SRC_DIR.exists():
    sys.path.append(str(SRC_DIR))

import bolt_app.core as core  # type: ignore
from bolt_app.core import DISPLAY_MATERIALS, Vis, dimensionner, load_tete_vis_table  # type: ignore

# Paths & assets
ASSETS_DIR = ROOT / "assets"


def resource_path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


def safe_rerun() -> None:
    """Relance l'application en utilisant l'API disponible."""
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()  # Compatibilite versions plus anciennes
        except Exception:
            st.warning("Impossible de relancer l'application automatiquement.")


# Point core to packaged assets
core.PAS_STD_FILE = resource_path("assets", "Pas-std.csv")
core.FROTTEMENT_FILE = resource_path("assets", "Frottement.csv")
core.TROU_PASSAGE_FILE = resource_path("assets", "Trou_passage.csv")
core.TETE_VIS_FILE = resource_path("assets", "Tete_vis.csv")

# UI constants & mappings
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


@st.cache_data
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


@st.cache_data
def get_tete_table() -> Tuple[Dict[float, Dict[str, float]], Sequence[str]]:
    try:
        table, head_types = load_tete_vis_table()
        if not head_types:
            head_types = tuple(DEFAULT_HEAD_TYPES)
    except Exception:
        table, head_types = {}, tuple(DEFAULT_HEAD_TYPES)
    return table, head_types


def image_path(filename: str, subfolder: str = "img") -> Optional[str]:
    path = ASSETS_DIR / subfolder / filename
    if path.exists():
        return str(path)
    return None


def head_options(head_types: Sequence[str]) -> List[str]:
    opts = [HEAD_LABEL_MAP.get(name, name) for name in head_types]
    seen: set[str] = set()
    unique: List[str] = []
    for opt in opts:
        if opt not in seen:
            seen.add(opt)
            unique.append(opt)
    if "Autre" not in seen:
        unique.append("Autre")
    return unique


def iso_diam_tete(dn: float, head_label: str, table: Dict[float, Dict[str, float]]) -> Optional[float]:
    if not head_label or head_label.lower() == "autre":
        return None
    target = HEAD_REVERSE_MAP.get(head_label, head_label).lower()
    for name, value in (table.get(dn) or {}).items():
        if name.lower() == target:
            return value
    return None


def parse_optional_float(text: str) -> Optional[float]:
    text = text.strip()
    if not text:
        return None
    return float(text.replace(",", "."))


def friction_inputs(prefix: str = "") -> tuple[str, Optional[float], Optional[float], bool]:
    choice = st.radio(
        "Frottements",
        ["Frottement max.", "Frottement min.", "Saisir les coefficients"],
        index=0,
        key=f"{prefix}_friction_choice",
    )
    manual = choice == "Saisir les coefficients"
    friction_mode = "min" if choice == "Frottement min." else "max"
    mu_filet_manual: Optional[float] = None
    mu_sous_manual: Optional[float] = None
    if manual:
        mu_filet_manual = st.number_input(
            "Frottement des filets",
            min_value=0.0,
            max_value=1.0,
            value=0.10,
            step=0.01,
            key=f"{prefix}_mu_filet",
        )
        mu_sous_manual = st.number_input(
            "Frottement sous tete",
            min_value=0.0,
            max_value=1.0,
            value=0.10,
            step=0.01,
            key=f"{prefix}_mu_sous",
        )
    return friction_mode, mu_filet_manual, mu_sous_manual, manual


def format_couple_value(value: float, unit: str) -> str:
    if unit == "N.m":
        return f"{value / 1000.0:.2f}"
    return f"{value:.0f}"


def default_index(values: Sequence[str], target: str) -> int:
    try:
        return list(values).index(target)
    except ValueError:
        return 0


# Initial data
DIAM_VALUES = load_diametres(core.PAS_STD_FILE)
TETE_TABLE, HEAD_TYPES = get_tete_table()
HEAD_OPTIONS = head_options(HEAD_TYPES)
MATERIALS = sorted(DISPLAY_MATERIALS)
HEAD_IMAGES = {k: image_path(v) for k, v in HEAD_IMAGE_FILES.items()}
MONTAGE_IMAGES_PATH = {k: image_path(v) for k, v in MONTAGE_IMAGES.items()}

st.set_page_config(
    page_title="Bolt V1.0 Beta - Calcul et Dimensionnement de Boulons",
    page_icon=str(ASSETS_DIR / "Bolt_logo.png"),
    layout="wide",
)

st.title("Bolt V1.0 Beta - Calcul et Dimensionnement de Boulons")
tabs = st.tabs(["Calcul", "Construction"])


def render_images(head_label: str, has_washer: bool) -> None:
    head_key = HEAD_REVERSE_MAP.get(head_label, head_label).lower()
    if head_key == "autre":
        head_key = "chc cylindrique"
    vis_img = HEAD_IMAGES.get(head_key)
    montage_key = "rondelle" if has_washer else "direct"
    montage_img = MONTAGE_IMAGES_PATH.get(montage_key)

    st.markdown("**Vis**")
    if vis_img:
        st.image(vis_img, use_column_width=True)
    else:
        st.write("Illustration indisponible")

    st.markdown("---")
    st.markdown("**Montage**")
    if montage_img:
        st.image(montage_img, use_column_width=True)
    else:
        st.write("Illustration indisponible")

    st.markdown("Norme ISO 68-1 - filet a 60 deg")
    st.caption("Version V1.0 Beta")


with tabs[0]:
    st.subheader("Calcul")
    left, right = st.columns([1.8, 1.2], gap="large")
    with left:
        st.markdown("### Geometrie")
        dn = st.selectbox(
            "Diametre nominal (M-)",
            options=[f"{d:g}" for d in DIAM_VALUES] or ["12"],
            index=default_index([f"{d:g}" for d in DIAM_VALUES], "12"),
        )
        dn_value = float(dn)

        head_choice = st.selectbox("Tete de vis", options=HEAD_OPTIONS, index=0)
        dh_iso = iso_diam_tete(dn_value, head_choice, TETE_TABLE)
        manual_dh_text = ""
        if dh_iso is None:
            st.warning("Pas de taille ISO pour ce diametre, saisissez une valeur :")
            manual_dh_text = st.text_input("Diametre tete de vis (mm)", key="calc_manual_dh")
        else:
            st.info(f"Diametre tete de vis ISO : {dh_iso:g} mm")

        st.markdown("### Materiaux")
        mat_vis = st.selectbox("Vis", options=MATERIALS, index=default_index(MATERIALS, "Acier"))
        mat_body = st.selectbox(
            "Piece taraudee",
            options=MATERIALS,
            index=default_index(MATERIALS, mat_vis),
        )
        is_filet_lub = st.checkbox("Lubrification des filets", key="calc_lub_filet")

        surface_appui = st.checkbox("Surface d'appui (different de piece taraudee)", key="calc_surface")
        mat_sous_tete: Optional[str] = None
        has_washer = False
        mat_rondelle: Optional[str] = None
        mat_sous_rondelle: Optional[str] = None
        if surface_appui:
            mat_sous_tete = st.selectbox(
                "Surface d'appui",
                options=MATERIALS,
                index=default_index(MATERIALS, mat_body),
                key="calc_mat_sous_tete",
            )
        else:
            has_washer = st.checkbox("Presence d'une rondelle", key="calc_washer")
            if has_washer:
                mat_rondelle = st.selectbox(
                    "Rondelle",
                    options=MATERIALS,
                    index=default_index(MATERIALS, mat_body),
                    key="calc_mat_rondelle",
                )
                mat_sous_rondelle = st.selectbox(
                    "Surface d'appui",
                    options=MATERIALS,
                    index=default_index(MATERIALS, mat_body),
                    key="calc_mat_sous_rondelle",
                )

        st.markdown("### Frottements")
        friction_mode, mu_filet_manual, mu_sous_manual, manual_friction = friction_inputs("calc")

        st.markdown("### Chargement")
        couple_input = st.number_input("Couple", min_value=0.0, value=40.0, step=1.0, key="calc_cpl")
        unit_cpl = st.selectbox("Unites", options=["N.mm", "N.m"], index=1, key="calc_units")

        col_btn_calc, col_btn_reset = st.columns(2)
        compute_calc = col_btn_calc.button("Calculer", key="calc_btn")
        if col_btn_reset.button("Reinitialiser", key="calc_reset"):
            st.session_state.clear()
            safe_rerun()

        if compute_calc:
            try:
                dh_value = dh_iso
                if dh_value is None:
                    dh_value = parse_optional_float(manual_dh_text or "")
                    if dh_value is None:
                        st.error("Pas de taille ISO pour ce diametre, saisissez une valeur.")
                        st.stop()
                if dh_value <= 0 or dh_value >= 120:
                    st.error("Le diametre de tete doit etre positif et inferieur a 120 mm.")
                    st.stop()
                if dh_value <= dn_value:
                    st.error("diametre de tete plus petit que le diametre nominale saisir une valeur valide")
                    st.stop()

                couple_value = couple_input * 1000.0 if unit_cpl == "N.m" else couple_input
                if couple_value <= 0:
                    st.error("Veuillez saisir un couple positif.")
                    st.stop()

                mat_sous_tete_value = mat_sous_tete if surface_appui else None
                if surface_appui:
                    has_washer_value = False
                else:
                    has_washer_value = has_washer

                vis = Vis(diam_nominale=dn_value, diam_tete=dh_value, mat_vis=mat_vis)
                effort = vis.effort_serrage(
                    couple_value,
                    mat_body=mat_body,
                    is_lubrified=is_filet_lub,
                    mat_sous_tete=mat_sous_tete_value,
                    is_sous_tete_lubrified=False,
                    friction_mode=friction_mode,
                    mu_filet_manual=mu_filet_manual if manual_friction else None,
                    mu_sous_tete_manual=mu_sous_manual if manual_friction else None,
                    has_washer=has_washer_value,
                    mat_rondelle=mat_rondelle,
                    mat_sous_rondelle=mat_sous_rondelle,
                )

                st.markdown("---")
                st.markdown("### Efforts, Contraintes et Pertes par frottements")
                st.markdown("**1) Effort de serrage (Pre-charge)**")
                st.metric("Ft (N)", f"{effort:.0f}")

                st.markdown("**2) Force de resistance au glissement**")
                st.metric("Force de Cisaillement limite (N)", f"{vis.force_resistance_glissement:.0f}")

                st.markdown("**3) Contraintes**")
                col_c1, col_c2, col_c3 = st.columns(3)
                col_c1.metric("Traction filets (MPa)", f"{vis.contrainte_traction:.1f}")
                col_c2.metric("Torsion filets (MPa)", f"{vis.contrainte_torsion:.1f}")
                col_c3.metric("Contrainte VM (MPa)", f"{vis.contrainte_vm:.1f}")

                st.markdown("**4) Pertes par frottements**")
                col_p1, col_p2, col_p3 = st.columns(3)
                col_p1.metric("Frottement filets (%)", f"{vis.pertes_frottements_filet:.0f}")
                col_p2.metric("Frottement sous tete (%)", f"{vis.pertes_frottements_tete:.0f}")
                col_p3.metric("Pertes totales (%)", f"{vis.pertes_frottements_totale:.0f}")
            except Exception as exc:
                st.error(str(exc))

    with right:
        render_images(head_choice, has_washer)


with tabs[1]:
    st.subheader("Construction")
    left, right = st.columns([1.3, 1.7], gap="large")
    with left:
        st.markdown("### Geometrie")
        diam_min = st.selectbox(
            "Diametre min.",
            options=[f"{d:g}" for d in DIAM_VALUES] or ["12"],
            index=default_index([f"{d:g}" for d in DIAM_VALUES], "12"),
        )
        diam_max = st.selectbox(
            "Diametre max.",
            options=[f"{d:g}" for d in DIAM_VALUES] or ["14"],
            index=default_index([f"{d:g}" for d in DIAM_VALUES], "14"),
        )
        diam_min_val = float(diam_min)
        diam_max_val = float(diam_max)
        if diam_min_val > diam_max_val:
            diam_min_val, diam_max_val = diam_max_val, diam_min_val

        diam_candidates = [d for d in DIAM_VALUES if diam_min_val - 1e-6 <= d <= diam_max_val + 1e-6]
        iso_available = any(TETE_TABLE.get(d) for d in diam_candidates)
        manual_dh_dim_text = ""
        if not iso_available:
            st.warning("Pas de taille ISO pour ce diametre, saisissez une valeur de diametre de tete de vis")
            manual_dh_dim_text = st.text_input("Diametre tete de vis (mm)", key="dim_manual_dh")

        st.markdown("### Materiaux")
        mat_vis_dim = st.selectbox("Vis", options=MATERIALS, index=default_index(MATERIALS, "Acier"), key="dim_mat_vis")
        mat_body_dim = st.selectbox(
            "Piece taraudee",
            options=MATERIALS,
            index=default_index(MATERIALS, mat_vis_dim),
            key="dim_mat_body",
        )
        surface_appui_dim = st.checkbox(
            "Surface d'appui (different de piece taraudee)",
            key="dim_surface",
        )
        mat_sous_tete_dim: Optional[str] = None
        has_washer_dim = False
        mat_washer_dim: Optional[str] = None
        mat_under_washer_dim: Optional[str] = None
        if surface_appui_dim:
            mat_sous_tete_dim = st.selectbox(
                "Surface d'appui",
                options=MATERIALS,
                index=default_index(MATERIALS, mat_body_dim),
                key="dim_mat_sous_tete",
            )
        else:
            has_washer_dim = st.checkbox("Presence d'une rondelle", key="dim_washer")
            if has_washer_dim:
                mat_washer_dim = st.selectbox(
                    "Rondelle",
                    options=MATERIALS,
                    index=default_index(MATERIALS, mat_body_dim),
                    key="dim_mat_washer",
                )
                mat_under_washer_dim = st.selectbox(
                    "Surface d'appui",
                    options=MATERIALS,
                    index=default_index(MATERIALS, mat_body_dim),
                    key="dim_mat_under_washer",
                )

        is_filet_lub_dim = st.checkbox("Lubrification des filets", key="dim_lub_filet")

        st.markdown("### Frottements")
        friction_mode_dim, mu_filet_manual_dim, mu_sous_manual_dim, manual_friction_dim = friction_inputs("dim")

        st.markdown("### Chargement")
        effort_cible = st.number_input(
            "Effort de serrage cible (N)",
            min_value=0.0,
            value=10000.0,
            step=500.0,
            key="dim_effort",
        )
        couple_max = st.number_input(
            "Couple maximal constructeur",
            min_value=0.0,
            value=40.0,
            step=1.0,
            key="dim_cpl",
        )
        unit_dim = st.selectbox("Unites", options=["N.mm", "N.m"], index=1, key="dim_units")

        col_btn_calc_dim, col_btn_reset_dim = st.columns(2)
        compute_dim = col_btn_calc_dim.button("Calculer", key="dim_btn")
        if col_btn_reset_dim.button("Reinitialiser", key="dim_reset"):
            st.session_state.clear()
            safe_rerun()

        if compute_dim:
            try:
                if not diam_candidates:
                    st.error("Aucun diametre nominal dans cette plage.")
                    st.stop()
                manual_value: Optional[float] = None
                if not iso_available:
                    manual_value = parse_optional_float(manual_dh_dim_text or "")
                    if manual_value is None:
                        st.error(
                            "Pas de taille ISO pour ce diametre, saisissez une valeur de diametre de tete de vis.",
                        )
                        st.stop()
                    if manual_value <= 0 or manual_value >= 120:
                        st.error("Le diametre de tete doit etre positif et inferieur a 120 mm.")
                        st.stop()
                    if manual_value <= max(diam_candidates):
                        st.error("diametre de tete plus petit que le diametre nominale saisir une valeur valide")
                        st.stop()

                couple_max_value = couple_max * 1000.0 if unit_dim == "N.m" else couple_max
                if couple_max_value <= 0 or effort_cible <= 0:
                    st.error("Effort cible et couple max doivent etre positifs.")
                    st.stop()

                results = dimensionner(
                    diametres=diam_candidates,
                    mat_vis=mat_vis_dim,
                    mat_body=mat_body_dim,
                    mat_sous_tete=mat_sous_tete_dim,
                    effort_cible=effort_cible,
                    couple_max=couple_max_value,
                    include_lubrified=is_filet_lub_dim,
                    tete_table=TETE_TABLE,
                    manual_diam_tete=manual_value,
                    friction_mode=friction_mode_dim,
                    mu_filet_manual=mu_filet_manual_dim if manual_friction_dim else None,
                    mu_sous_tete_manual=mu_sous_manual_dim if manual_friction_dim else None,
                    has_washer=has_washer_dim if not surface_appui_dim else False,
                    mat_rondelle=mat_washer_dim,
                    mat_sous_rondelle=mat_under_washer_dim,
                )

                st.markdown("### Choix de vis possible")
                st.markdown("---")
                if not results:
                    if is_filet_lub_dim:
                        st.error("Pas de solution, essayez une autre configuration")
                    else:
                        st.error("Pas de resultat, reessayer le calcul en lubrifiant votre assemblage")
                    st.stop()

                data = []
                has_dry = any(not r.lubrified for r in results)
                has_lube = any(r.lubrified for r in results)
                for res in results:
                    head_types_display = (
                        " / ".join(HEAD_LABEL_MAP.get(ht, ht) for ht in res.head_types) if res.head_types else "-"
                    )
                    data.append(
                        {
                            "Diametre (M-)": f"M{res.diam_nominale:g}",
                            "Couple": f"{format_couple_value(res.couple, unit_dim)} {unit_dim}",
                            "Effort (N)": f"{res.effort:.0f}",
                            "Etat": "Lubrifie" if res.lubrified else "Sec",
                            "Materiau vis": res.mat_vis,
                            "Materiau assemblage": res.mat_body,
                            "Materiau sous tete": res.mat_sous_tete,
                            "Serie": "H12,H13,H14",
                            "Tete de vis": head_types_display,
                        }
                    )

                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                if is_filet_lub_dim and not has_lube:
                    st.error("Pas de solution, essayez une autre configuration")
                elif (not is_filet_lub_dim) and not has_dry:
                    st.error("Pas de resultat, reessayer le calcul en lubrifiant votre assemblage")
            except Exception as exc:
                st.error(str(exc))

    with right:
        st.markdown("Norme ISO 68-1 - filet a 60 deg")
