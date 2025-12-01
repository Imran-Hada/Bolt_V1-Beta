from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

# Assure we can import the core logic
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from bolt_app.core import (  # type: ignore
    DISPLAY_MATERIALS,
    Vis,
    dimensionner,
    load_tete_vis_table,
)
import bolt_app.core as core  # type: ignore


ASSETS_DIR = PROJECT_ROOT / "assets"
core.PAS_STD_FILE = ASSETS_DIR / "Pas-std.csv"
core.FROTTEMENT_FILE = ASSETS_DIR / "Frottement.csv"
core.TROU_PASSAGE_FILE = ASSETS_DIR / "Trou_passage.csv"
core.TETE_VIS_FILE = ASSETS_DIR / "Tete_vis.csv"

# Noms d'affichage des têtes et correspondances internes
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


st.set_page_config(
    page_title="Bolt - Calcul & Dimensionnement",
    page_icon=str(ASSETS_DIR / "Bolt_logo.png"),
    layout="wide",
)

# Couleurs de fond : bleu demandé, blocs blancs pour la lisibilité
st.markdown(
    """
    <style>
    body { background-color: #0A66C2; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .card {
        background: #ffffff;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }
    .muted { color: #0A0A0A; opacity: 0.78; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Bolt - Calcul & Dimensionnement")
st.caption("Norme ISO 68-1 - filet à 60° • Version Streamlit")

diam_values = load_diametres(core.PAS_STD_FILE)
materials = sorted(DISPLAY_MATERIALS)

try:
    tete_table, head_types = load_tete_vis_table()
    if not head_types:
        head_types = tuple(DEFAULT_HEAD_TYPES)
except Exception:
    tete_table, head_types = {}, tuple(DEFAULT_HEAD_TYPES)

tab_calcul, tab_dim = st.tabs(["Calcul", "Dimensionnement"])


def get_iso_head_diameter(diam: float, head_label: str) -> Optional[float]:
    head_name = HEAD_REVERSE_MAP.get(head_label, head_label)
    values = tete_table.get(diam, {})
    return values.get(head_name) or values.get(head_name.lower())


with tab_calcul:
    col_left, col_right = st.columns([1.4, 1])
    with col_left:
        st.subheader("Géométrie")
        dn = st.selectbox("Diamètre nominal (M-)", [f"{d:g}" for d in diam_values] or ["8", "10", "12"], index=diam_values.index(12.0) if 12.0 in diam_values else 0)

        head_display_map = {name: HEAD_LABEL_MAP.get(name, name) for name in head_types}
        head_values = [head_display_map[name] for name in head_types] if head_types else list(DEFAULT_HEAD_TYPES)
        if "Autre" not in head_values:
            head_values.append("Autre")
        head_choice = st.selectbox("Tête de vis", head_values)

        iso_dh = None
        try:
            iso_dh = get_iso_head_diameter(float(dn), head_choice if head_choice != "Autre" else "CHC cylindrique")
        except Exception:
            iso_dh = None

        manual_dh = None
        if iso_dh is None:
            manual_dh = st.text_input("Diamètre tête de vis (mm) – saisie manuelle si non ISO", "")
        else:
            st.info(f"Diamètre tête de vis ISO : {iso_dh:g} mm", icon="ℹ️")

        st.markdown("---")
        st.subheader("Matériaux")
        mat_vis = st.selectbox("Vis", materials, index=materials.index("Acier") if "Acier" in materials else 0)
        mat_body = st.selectbox("Pièce taraudée", materials, index=materials.index(mat_vis) if mat_vis in materials else 0)
        is_filet_lub = st.checkbox("Filets lubrifiés", value=False)

        has_under_head = st.checkbox("Autre matériau bloc sous-tête", value=False)
        mat_sous_tete = None
        if has_under_head:
            mat_sous_tete = st.selectbox("Matériau bloc sous-tête", materials, index=materials.index(mat_body) if mat_body in materials else 0)
        is_sous_tete_lub = False
        if has_under_head:
            is_sous_tete_lub = st.checkbox("Sous-tête lubrifiée", value=False)

        has_washer = False
        mat_washer = None
        mat_under_washer = None
        if not has_under_head:
            has_washer = st.checkbox("Présence d'une rondelle", value=False)
            if has_washer:
                mat_washer = st.selectbox("Matériau rondelle", materials, index=materials.index(mat_body) if mat_body in materials else 0)
                mat_under_washer = st.selectbox("Matériau bloc sous-rondelle", materials, index=materials.index(mat_body) if mat_body in materials else 0)

        st.markdown("---")
        st.subheader("Frottements")
        friction_mode = st.radio("Mode", ["max", "min"], index=0, horizontal=True, help="Valeurs CSV: max ou min")
        manual_mu = st.checkbox("Saisir manuellement µ")
        mu_filet_manual = mu_sous_manual = None
        if manual_mu:
            c1, c2 = st.columns(2)
            with c1:
                mu_filet_manual = st.text_input("Frottement des filets", "")
            with c2:
                mu_sous_manual = st.text_input("Frottement sous tête", "")

        st.markdown("---")
        st.subheader("Chargement")
        cpl = st.text_input("Couple", "40")
        unit = st.selectbox("Unités", ["N.mm", "N.m"], index=1)

        st.markdown("---")
        st.subheader("Actions")
        calc_btn = st.button("Calculer")
        reset_btn = st.button("Réinitialiser")

        if reset_btn:
            st.experimental_rerun()

        if calc_btn:
            try:
                dn_val = to_float(dn)
                if iso_dh is not None:
                    dh_val = iso_dh
                else:
                    if not manual_dh:
                        st.error("Pas de taille ISO pour ce diamètre, saisissez une valeur.")
                        st.stop()
                    dh_val = to_float(manual_dh)
                if dh_val <= 0 or dh_val >= 120:
                    st.error("Le diamètre de tête doit être positif et inférieur à 120 mm.")
                    st.stop()
                if dh_val < dn_val:
                    st.error("diametre de tete plus petit que le diametre nominale saisir une valeur valide")
                    st.stop()

                couple = to_float(cpl)
                if unit == "N.m":
                    couple *= 1000.0
                if couple <= 0:
                    st.error("Veuillez saisir un couple positif.")
                    st.stop()

                if manual_mu:
                    if not mu_filet_manual or not mu_sous_manual:
                        st.error("Merci de saisir les deux coefficients de frottement.")
                        st.stop()
                    mu_filet_manual_val = to_float(mu_filet_manual)
                    mu_sous_manual_val = to_float(mu_sous_manual)
                    for value, label in [
                        (mu_filet_manual_val, "Frottement des filets"),
                        (mu_sous_manual_val, "Frottement sous tête"),
                    ]:
                        if value < 0 or value > 1:
                            st.error(f"{label} doit être compris entre 0 et 1.")
                            st.stop()
                    mu_filet_manual_use = mu_filet_manual_val
                    mu_sous_manual_use = mu_sous_manual_val
                else:
                    mu_filet_manual_use = None
                    mu_sous_manual_use = None

                vis = Vis(diam_nominale=dn_val, diam_tete=dh_val, mat_vis=mat_vis)
                effort = vis.effort_serrage(
                    couple,
                    mat_body=mat_body,
                    is_lubrified=is_filet_lub,
                    mat_sous_tete=mat_sous_tete,
                    is_sous_tete_lubrified=is_sous_tete_lub,
                    friction_mode=friction_mode,
                    mu_filet_manual=mu_filet_manual_use,
                    mu_sous_tete_manual=mu_sous_manual_use,
                    has_washer=has_washer,
                    mat_rondelle=mat_washer,
                    mat_sous_rondelle=mat_under_washer,
                )

                st.markdown("___")
                st.subheader("Resultats Pre-chargement et Contraintes")
                st.write("Angle filet : 60° ISO 68-1")
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.text_input("Effort de Serrage Ft (N)", f"{effort:.0f}", key="ft_res", disabled=False)
                    st.text_input("Force de résistance au glissement (N)", f"{vis.force_resistance_glissement:.0f}", disabled=True)
                    st.text_input("Contrainte de Traction dans les filets (MPa)", f"{vis.contrainte_traction:.1f}", disabled=True)
                    st.text_input("Contrainte de Torsion dans les filets (MPa)", f"{vis.contrainte_torsion:.1f}", disabled=True)
                with col_res2:
                    st.text_input("Contrainte Equivalente VM (MPa)", f"{vis.contrainte_vm:.1f}", disabled=True)
                    st.text_input("Pertes de frottement dans les filets (%)", f"{vis.pertes_frottements_filet:.0f}", disabled=True)
                    st.text_input("Pertes de frottement sous la tête (%)", f"{vis.pertes_frottements_tete:.0f}", disabled=True)
                    st.text_input("Pertes totales (%)", f"{vis.pertes_frottements_totale:.0f}", disabled=True)
            except Exception as exc:
                st.error(str(exc))

    with col_right:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Illustration")
            try:
                st.image(str(ASSETS_DIR / "Schema_technique.png"), use_container_width=True)
            except Exception:
                st.info("Illustration indisponible")
            st.caption("Angle filet : 60° • ISO 68-1")
            st.markdown("</div>", unsafe_allow_html=True)


with tab_dim:
    col_a, col_b = st.columns([1.2, 1])
    with col_a:
        st.subheader("Géométrie")
        diam_min = st.selectbox("Diamètre min (M-)", [f"{d:g}" for d in diam_values] or ["8", "10"], index=diam_values.index(12.0) if 12.0 in diam_values else 0)
        diam_max = st.selectbox("Diamètre max (M-)", [f"{d:g}" for d in diam_values] or ["10", "12"], index=diam_values.index(14.0) if 14.0 in diam_values else 0)

        # Vérifie la disponibilité ISO
        diam_candidates = [
            d
            for d in diam_values
            if to_float(diam_min) - 1e-6 <= d <= to_float(diam_max) + 1e-6
        ]
        iso_available = any(tete_table.get(d) for d in diam_candidates)
        manual_dh_dim = None
        if not iso_available:
            manual_dh_dim = st.text_input(
                "Diamètre tête de vis (mm) – requis car pas de taille ISO dans cet intervalle",
                "",
            )

        st.markdown("---")
        st.subheader("Matériaux")
        mat_vis_dim = st.selectbox("Vis", materials, index=materials.index("Acier") if "Acier" in materials else 0)
        mat_body_dim = st.selectbox("Pièce taraudée", materials, index=materials.index(mat_vis_dim) if mat_vis_dim in materials else 0)

        has_under_head_dim = st.checkbox("Autre matériau bloc sous-tête", value=False, key="dim_under")
        mat_sous_dim = None
        if has_under_head_dim:
            mat_sous_dim = st.selectbox("Matériau bloc sous-tête", materials, index=materials.index(mat_body_dim) if mat_body_dim in materials else 0)
        is_filet_lub_dim = st.checkbox("Filets lubrifiés", value=False, key="dim_lub")

        has_washer_dim = False
        mat_washer_dim = None
        mat_under_washer_dim = None
        if not has_under_head_dim:
            has_washer_dim = st.checkbox("Présence d'une rondelle", value=False, key="dim_washer")
            if has_washer_dim:
                mat_washer_dim = st.selectbox("Matériau rondelle", materials, index=materials.index(mat_body_dim) if mat_body_dim in materials else 0)
                mat_under_washer_dim = st.selectbox("Matériau bloc sous-rondelle", materials, index=materials.index(mat_body_dim) if mat_body_dim in materials else 0)

        st.markdown("---")
        st.subheader("Frottements")
        friction_mode_dim = st.radio("Mode", ["max", "min"], index=0, horizontal=True, key="dim_friction_mode")
        manual_mu_dim = st.checkbox("Saisir manuellement µ", key="dim_manual_mu")
        mu_filet_dim = mu_sous_dim = None
        if manual_mu_dim:
            c1, c2 = st.columns(2)
            with c1:
                mu_filet_dim = st.text_input("Frottement des filets", "", key="dim_mu_filet")
            with c2:
                mu_sous_dim = st.text_input("Frottement sous tête", "", key="dim_mu_sous")

        st.markdown("---")
        st.subheader("Chargement")
        effort_cible = st.text_input("Effort de serrage cible (N)", "10000")
        couple_max = st.text_input("Couple maximal constructeur", "40")
        unit_dim = st.selectbox("Unités", ["N.mm", "N.m"], index=1, key="dim_unit")

        st.markdown("---")
        calc_dim_btn = st.button("Calculer (dimensionnement)")
        reset_dim_btn = st.button("Réinitialiser (dimensionnement)")
        if reset_dim_btn:
            st.experimental_rerun()

        if calc_dim_btn:
            try:
                diam_min_val = to_float(diam_min)
                diam_max_val = to_float(diam_max)
                if diam_min_val > diam_max_val:
                    diam_min_val, diam_max_val = diam_max_val, diam_min_val

                effort_cible_val = to_float(effort_cible)
                couple_max_val = to_float(couple_max)
                if unit_dim == "N.m":
                    couple_max_val *= 1000.0
                if effort_cible_val <= 0 or couple_max_val <= 0:
                    st.error("Effort cible et couple max doivent être positifs.")
                    st.stop()

                if not diam_candidates:
                    st.error("Aucun diamètre nominal dans cette plage.")
                    st.stop()

                manual_value = None
                if not iso_available:
                    if not manual_dh_dim:
                        st.error(
                            "Pas de taille ISO pour ce diamètre, saisissez une valeur de diamètre de tête de vis.",
                        )
                        st.stop()
                    manual_value = to_float(manual_dh_dim)
                    if manual_value <= 0 or manual_value >= 120:
                        st.error("Le diamètre de tête doit être positif et inférieur à 120 mm.")
                        st.stop()
                    if manual_value <= max(diam_candidates):
                        st.error("diametre de tete plus petit que le diametre nominale saisir une valeur valide")
                        st.stop()

                if manual_mu_dim:
                    if not mu_filet_dim or not mu_sous_dim:
                        st.error("Merci de saisir les deux coefficients de frottement.")
                        st.stop()
                    mu_filet_manual_val = to_float(mu_filet_dim)
                    mu_sous_manual_val = to_float(mu_sous_dim)
                    for value, label in [
                        (mu_filet_manual_val, "Frottement des filets"),
                        (mu_sous_manual_val, "Frottement sous tête"),
                    ]:
                        if value < 0 or value > 1:
                            st.error(f"{label} doit être compris entre 0 et 1.")
                            st.stop()
                    mu_filet_manual_use = mu_filet_manual_val
                    mu_sous_manual_use = mu_sous_manual_val
                else:
                    mu_filet_manual_use = mu_sous_manual_use = None

                results = dimensionner(
                    diametres=diam_candidates,
                    mat_vis=mat_vis_dim,
                    mat_body=mat_body_dim,
                    effort_cible=effort_cible_val,
                    couple_max=couple_max_val,
                    include_lubrified=is_filet_lub_dim,
                    serie="H13",
                    mat_sous_tete=mat_sous_dim,
                    tete_table=tete_table,
                    manual_diam_tete=manual_value,
                    friction_mode=friction_mode_dim,
                    mu_filet_manual=mu_filet_manual_use,
                    mu_sous_tete_manual=mu_sous_manual_use,
                    has_washer=has_washer_dim,
                    mat_rondelle=mat_washer_dim,
                    mat_sous_rondelle=mat_under_washer_dim,
                )

                st.markdown("___")
                st.subheader("Résultats Dimensionnement")
                if not results:
                    st.warning("Aucun résultat pour cette configuration.")
                else:
                    rows = []
                    for res in results:
                        unit_display = "N.m" if unit_dim == "N.m" else "N.mm"
                        rows.append(
                            {
                                "Diamètre (M-)": f"M{res.diam_nominale:g}",
                                "Couple": f"{format_couple(res.couple, unit_dim)} {unit_display}",
                                "Effort (N)": f"{res.effort:.0f}",
                                "Etat": "Lubrifié" if res.lubrified else "Sec",
                                "Matériau vis": res.mat_vis,
                                "Matériau assemblage": res.mat_body,
                                "Matériau sous tête": res.mat_sous_tete,
                                "Série": res.serie,
                                "Tête de vis": " / ".join(res.head_types) if res.head_types else "-",
                            }
                        )
                    st.dataframe(rows, hide_index=True, use_container_width=True)
                st.caption("Norme ISO 68-1 - filet à 60°")
            except Exception as exc:
                st.error(str(exc))

    with col_b:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Illustration")
            try:
                st.image(str(ASSETS_DIR / "construction_image.png"), use_container_width=True)
            except Exception:
                st.info("Illustration indisponible")
            st.caption("Angle filet : 60° • ISO 68-1")
            st.markdown("</div>", unsafe_allow_html=True)
