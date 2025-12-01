# Outil Bolt V1.0 Beta

## Objectif
- Application de bureau Tkinter (Windows) qui calcule l effort de serrage Ft d un boulon via la formule de Kellerman-Klein et derive les contraintes et pertes par frottement.
- Second onglet de recherche ("Construction") pour proposer des combinaisons vis/couple satisfaisant un effort cible sous contrainte de couple maxi constructeur.
- Version UI et logique actuelle : "Bolt V1.0 Beta" (icones Bolt_logo, fond blanc, scrollbars verticales/horizontales, deux onglets Calcul/Construction).

## Arborescence principale
- `src/bolt_app/core.py` : coeur metier (dataclass Vis, calculs, lecture CSV, dimensionnement).
- `src/bolt_app/gui.py` : interface Tkinter, logique formulaire + affichage resultats, binding des assets et des CSV.
- `assets/` : donnees et images (CSV de pas, frottement, trous de passage, tete_vis, icones, schemas et photos).
- `build/bolt.spec` : spec PyInstaller pour produire l exe "Bolt" en embarquant tous les assets.
- `dist/Bolt/` : sortie generee par PyInstaller (exe et assets copies).
- `Requirements.txt` : dependance principale `pyinstaller` (Tkinter et csv sont dans la stdlib).

## Donnees d entree (assets)
### assets/Pas-std.csv
Pas ISO par diametre nominal (mm) utilises pour initier l objet Vis et alimenter les listes deroulantes.
```
Diametre nominale;Pas
1;0.25
2;0.4
3;0.5
4;0.7
5;0.8
6;1.0
7;1.0
8;1.25
10;1.5
12;1.75
14;2.0
16;2.0
18;2.5
20;2.5
22;2.5
24;3.0
27;3.0
30;3.5
33;3.5
36;4.0
39;4.0
42;4.5
45;4.5
48;5.0
52;5.0
56;5.5
60;5.5
64;6.0
```

### assets/Trou_passage.csv
Diametre de trou de passage par serie ISO (H12, H13, H14) selectionne automatiquement en __post_init__ selon le diam_nominale et la serie (defaut H13).
```
Diametre nominale;H12;H13;H14
1;1.1;1.2;1.3
2;2.2;2.4;2.6
3;3.2;3.4;3.6
4;4.3;4.5;4.8
4;4.8;5.0;5.3
5;5.3;5.5;5.8
6;6.4;6.6;7.0
7;7.4;7.6;8.0
8;8.4;9.0;10.0
9;9.5;10.0;11.0
10;10.5;11.0;12.0
12;13.0;13.5;14.5
14;15.0;15.5;16.5
16;17.0;17.5;18.5
18;19.0;20.0;21.0
20;21.0;22.0;24.0
22;23.0;24.0;26.0
24;25.0;26.0;28.0
27;28.0;30.0;32.0
30;31.0;33.0;35.0
33;34.0;36.0;38.0
36;37.0;39.0;42.0
39;40.0;42.0;45.0
42;43.0;45.0;48.0
45;46.0;48.0;52.0
48;50.0;52.0;56.0
52;54.0;56.0;62.0
56;58.0;62.0;66.0
60;62.0;66.0;70.0
64;66.0;70.0;74.0
68;70.0;74.0;78.0
72;74.0;78.0;82.0
76;78.0;82.0;86.0
80;82.0;86.0;91.0
85;87.0;91.0;96.0
90;93.0;96.0;101.0
95;98.0;101.0;107.0
```

### assets/Tete_vis.csv
Diametre de tete ISO par diametre nominal et type de tete. Valeur manquante representee par "-" (declenche une saisie manuelle dans l UI si combinee au diametre choisi).
```
Diametre nominale;Hexagonale;CHC cylindrique;CHC tete fraisee;CHC tete bombee;Tete bombee fendue;Tete bombee philips;Tete bombee Pozidriv;Tete bombee Torx interne
1;3.2;1.8;2.0;-;3.2;3.2;-;-
2;4.0;3.8;4.0;-;4.0;4.0;4.0;-
3;5.5;5.5;6.0;5.7;6.0;6.0;6.0;6.0
4;7.0;7.0;8.0;7.6;8.0;8.0;8.0;8.0
5;8.0;8.5;9.5;9.5;10.0;9.0;9.0;9.5
6;10.0;10.0;11.0;10.5;12.0;11.0;11.0;10.5
7;-;-;-;-;-;-;-;-
8;13.0;13.0;15.0;14.0;16.0;14.0;14.0;14.0
9;-;-;-;-;-;-;-;-
10;16.0;16.0;18.5;17.5;20.0;-;20.0;17.5
12;18.0;18.00;22.0;21.0;-;-;-;21.0
14;21.0;21.00;25.0;-;-;-;-;-
16;24.0;24.00;29.0;28.0;-;-;-;-
18;27.0;27.00;-;-;-;-;-;-
20;30.0;30.00;36.0;-;-;-;-;-
22;34.0;33.00;-;-;-;-;-;-
24;36.0;36.00;44.0;-;-;-;-;-
27;41.0;40.00;-;-;-;-;-;-
30;46.0;45.00;-;-;-;-;-;-
33;50.0;50.00;-;-;-;-;-;-
36;55.0;54.00;-;-;-;-;-;-
39;60.0;-;-;-;-;-;-;-
42;65.0;63.00;-;-;-;-;-;-
45;70.0;-;-;-;-;-;-;-
48;75.0;72.00;-;-;-;-;-;-
52;80.0;-;-;-;-;-;-;-
56;85.0;84.00;-;-;-;-;-;-
60;90.0;-;-;-;-;-;-;-
64;95.0;96.00;-;-;-;-;-;-
68;100.0;-;-;-;-;-;-;-
72;105.0;108.00;-;-;-;-;-;-
76;110.0;-;-;-;-;-;-;-
80;115.0;120.00;-;-;-;-;-;-
85;120.0;-;-;-;-;-;-;-
90;130.0;135.00;-;-;-;-;-;-
95;135.0;-;-;-;-;-;-;-
```

### assets/Frottement.csv
Coefficients de frottement suivant materiau vis (Material 1) et materiau oppose (Material 2). Suffixe `min` ou `max` choisi par l option de friction. Colonnes separees pour filets et sous tete, a sec ou lubrifie.
```
Material 1 ;Material 2;Dry_min_filet;Dry_max_filet;Dry_min_tete;Dry_max_tete;Lubricated_min_filet;Lubricated_min_tete;Lubricated_max_filet;Lubricated_max_tete
Acier;Acier;0.14;0.24;0.12;0.18;0.08;0.12;0.06;0.10
Inox;Inox;0.20;0.35;0.20;0.35;0.10;0.20;0.10;0.20
Acier;Inox;0.20;0.30;0.14;0.24;0.10;0.15;0.08;0.16
Inox;Acier;0.20;0.30;0.14;0.24;0.10;0.15;0.08;0.16
Aluminium;Inox;0.30;0.40;0.30;0.40;0.08;0.16;0.08;0.16
Inox;Aluminium;0.30;0.40;0.30;0.40;0.08;0.16;0.08;0.16
Cuivre;Inox;0.20;0.35;0.20;0.35;0.08;0.16;0.08;0.16
Inox;Cuivre;0.20;0.35;0.20;0.35;0.08;0.16;0.08;0.16
Bronze;Inox;0.14;0.24;0.14;0.24;0.08;0.16;0.08;0.16
Inox;Bronze;0.14;0.24;0.14;0.24;0.08;0.16;0.08;0.16
Bronze;Acier;0.12;0.20;0.14;0.24;0.08;0.16;0.08;0.16
Acier;Bronze;0.12;0.20;0.14;0.24;0.08;0.16;0.08;0.16
Bronze;Bronze;0.14;0.24;0.14;0.24;0.08;0.16;0.08;0.16
Acier;Aluminium;0.30;0.40;0.30;0.40;0.08;0.16;0.08;0.16
Aluminium;Acier;0.30;0.40;0.30;0.40;0.08;0.16;0.08;0.16
Aluminium;Aluminium;0.30;0.45;0.30;0.45;0.08;0.16;0.08;0.16
Cuivre;Cuivre;0.14;0.24;0.14;0.24;0.08;0.16;0.08;0.16
Bronze;Cuivre;0.14;0.24;0.14;0.24;0.08;0.16;0.08;0.16
Cuivre;Bronze;0.14;0.24;0.14;0.24;0.08;0.16;0.08;0.16
Aluminium;Cuivre;0.20;0.35;0.20;0.35;0.08;0.16;0.08;0.16
Cuivre;Aluminium;0.20;0.35;0.20;0.35;0.08;0.16;0.08;0.16
Acier;Titane;0.30;0.45;0.35;0.55;0.15;0.25;0.20;0.30
Titane;Acier;0.30;0.45;0.35;0.55;0.15;0.25;0.20;0.30
Aluminium;Titane;0.30;0.50;0.35;0.55;0.15;0.30;0.20;0.35
Titane;Aluminium;0.30;0.50;0.35;0.55;0.15;0.30;0.20;0.35
Bronze;Titane;0.25;0.40;0.30;0.50;0.12;0.22;0.18;0.30
Titane;Bronze;0.25;0.40;0.30;0.50;0.12;0.22;0.18;0.30
Cuivre;Titane;0.30;0.45;0.35;0.55;0.15;0.25;0.20;0.30
Titane;Cuivre;0.30;0.45;0.35;0.55;0.15;0.25;0.20;0.30
Titane;Titane;0.40;0.60;0.45;0.65;0.10;0.25;0.12;0.30
Aluminium;Bronze;0.20;0.35;0.20;0.35;0.08;0.16;0.08;0.16
Bronze;Aluminium;0.20;0.35;0.20;0.35;0.08;0.16;0.08;0.16
Acier;Nylon;0.15;0.30;0.10;0.25;0.08;0.15;0.05;0.12
Nylon;Acier;0.15;0.30;0.10;0.25;0.08;0.15;0.05;0.12
Inox;Nylon;0.20;0.35;0.15;0.30;0.10;0.18;0.06;0.14
Nylon;Inox;0.20;0.35;0.15;0.30;0.10;0.18;0.06;0.14
Aluminium;Nylon;0.25;0.40;0.20;0.35;0.10;0.18;0.06;0.14
Nylon;Aluminium;0.25;0.40;0.20;0.35;0.10;0.18;0.06;0.14
Bronze;Nylon;0.20;0.35;0.15;0.30;0.08;0.15;0.05;0.12
Nylon;Bronze;0.20;0.35;0.15;0.30;0.08;0.15;0.05;0.12
Cuivre;Nylon;0.25;0.40;0.20;0.35;0.10;0.18;0.06;0.14
Nylon;Cuivre;0.25;0.40;0.20;0.35;0.10;0.18;0.06;0.14
Titane;Nylon;0.30;0.45;0.25;0.40;0.12;0.20;0.08;0.16
Nylon;Titane;0.30;0.45;0.25;0.40;0.12;0.20;0.08;0.16
Nylon;Nylon;0.25;0.40;0.25;0.40;0.10;0.18;0.08;0.16
Acier;PTFE;0.03;0.08;0.03;0.08;0.03;0.06;0.03;0.06
PTFE;Acier;0.03;0.08;0.03;0.08;0.03;0.06;0.03;0.06
Inox;PTFE;0.04;0.09;0.04;0.09;0.03;0.06;0.03;0.06
PTFE;Inox;0.04;0.09;0.04;0.09;0.03;0.06;0.03;0.06
Aluminium;PTFE;0.05;0.10;0.05;0.10;0.03;0.06;0.03;0.06
PTFE;Aluminium;0.05;0.10;0.05;0.10;0.03;0.06;0.03;0.06
Bronze;PTFE;0.04;0.09;0.04;0.09;0.03;0.06;0.03;0.06
PTFE;Bronze;0.04;0.09;0.04;0.09;0.03;0.06;0.03;0.06
Cuivre;PTFE;0.05;0.10;0.05;0.10;0.03;0.06;0.03;0.06
PTFE;Cuivre;0.05;0.10;0.05;0.10;0.03;0.06;0.03;0.06
Titane;PTFE;0.06;0.12;0.06;0.12;0.03;0.07;0.03;0.07
PTFE;Titane;0.06;0.12;0.06;0.12;0.03;0.07;0.03;0.07
Nylon;PTFE;0.08;0.15;0.08;0.15;0.04;0.08;0.04;0.08
PTFE;Nylon;0.08;0.15;0.08;0.15;0.04;0.08;0.04;0.08
PTFE;PTFE;0.05;0.10;0.05;0.10;0.03;0.06;0.03;0.06
```

### Images et icones
- `Bolt_logo.png` / `Bolt_logo.ico` : icone de l appli et du raccourci exe.
- `Schema_technique.png` et `construction_image.png` (illustrations fixes, Construction n affiche plus d image dans l onglet).
- `assets/img/*` : images des t�tes et schemas de montage. Mapping principal dans `gui.py` :
  - Vis : `hexagonale` -> Hexagonale.png ; `chc cylindrique` -> CHC Cylindrique.png ; `chc fraisee` -> CHC fraisee.png ; `chc bombee` -> CHC bombee.png ; `bombee fendue` -> bombee fendue.png ; `bombee philips`/`bombee pozidriv` -> Vis_bombee_philips_pozidriv.png ; `bombee torx interne` -> Bombee Torx.png.
  - Montage : `Schema_appui_direct.png` (pas de rondelle) ou `Schema_appui_rondelle.png` (rondelle cochee).

## Noyau metier (src/bolt_app/core.py)
### Constantes et materiaux
- `PACKAGE_DIR`, `PROJECT_ROOT`, `ASSETS_DIR` : reperes relatifs pour acceder aux CSV et images.
- `DISPLAY_MATERIALS` (ordre d affichage) : Acier, Aluminium, Bronze, Cuivre, Inox, Nylon, PTFE, Titane.
- `ALLOWED_MATERIALS` + `MATERIAL_SYNONYMS` : normalisation des saisies (tout est converti en noms francais avec premiere lettre majuscule, fallback Acier si non reconnu sauf cas explicites).
- Fichiers : `PAS_STD_FILE`, `FROTTEMENT_FILE`, `TROU_PASSAGE_FILE`, `TETE_VIS_FILE`. `DIMENSIONNEMENT_MARGIN` = 0.08 (marge 8 % au dessus de Ft cible).

### Dataclass Vis
Champs init : `diam_nominale`, `diam_tete`, `mat_vis`, `serie` (defaut H13), `angle_filet` (60). Champs derives apres init : `pas`, `diam_trou_passage`, `mat_body` (Acier defaut), `mat_sous_tete` (Acier defaut), `is_lubrified`, `is_sous_tete_lubrified`, `mu_filet`, `mu_sous_tete`, `mu_sous_rondelle`, `force_resistance_glissement`, pertes de frottement, contraintes traction/torsion/VM, `last_denominator`.

__post_init__ :
1) Normalise materiau vis et serie.
2) Charge le pas via `Pas-std.csv` (colonne Diametre nominale en mm, tol=1e-6) -> `pas`.
3) Charge le diametre de trou de passage via `Trou_passage.csv` selon `serie` -> `diam_trou_passage`.
4) Valide les dimensions (pas>0, diam_nominale>0, diam_tete>0 et >= diam_nominale, diam_trou_passage>0).

Proprietes derivees :
- `diam_d1 = diam_nominale - 1.0825 * pas`
- `diam_d2 = diam_nominale - 0.6495 * pas`
- `diam_d3 = diam_nominale - 1.22687 * pas`
- `alpha = angle_filet / 2` (deg).

Outils internes : `_normalize_material`, `_normalize_serie`, `_parse_float`, `_compute_denominator = 0.161*pas + mu_filet*diam_d2/1.715 + mu_sous_tete*dh/2`.

### Calcul effort_serrage()
Signature principale : `effort_serrage(couple, mat_body=None, is_lubrified=False, mat_sous_tete=None, is_sous_tete_lubrified=False, friction_mode="max", mu_filet_manual=None, mu_sous_tete_manual=None, has_washer=False, mat_rondelle=None, mat_sous_rondelle=None)`.
Etapes :
1) Valide `couple >= 0`.
2) Normalise le mode de frottement (`max` defaut, ou `min`). Valide que des mu manuels (0..1) sont dans l intervalle.
3) Normalise les materiaux : `mat_body` (defaut Acier), `mat_sous_tete` (defaut mat_body), flags de lubrification filets et sous-tete.
4) Calcule `dh = (diam_tete + diam_trou_passage)/2`.
5) Lit les coefficients de frottement via `_lookup_friction_coefficients` (Material1 = vis, Material2 = corps ou sous-tete). Si mat_sous_tete = mat_body on reutilise les memes coefficients.
6) Choisit `mu_filet`/`mu_sous_tete` :
   - si mu manuels fournis -> utilise ces valeurs,
   - sinon prend `Dry_max/min` ou `Lubricated_max/min` selon mode et cases lubrifiees.
7) Rondelle : par defaut `mu_sous_rondelle = mu_sous_tete`. Si `has_washer` true, lit un couple de friction pour mat_rondelle / mat_sous_rondelle et l applique (lubrifie selon is_sous_tete_lubrified).
8) Denominateur = `_compute_denominator(dh)`. Effort Ft = `couple / denominateur`. Stocke `last_denominator`.
9) Force de resistance au glissement = `(mu_sous_rondelle si rondelle sinon mu_sous_tete) * Ft`.
10) Pertes de frottement :
```
filets_torque = Ft * (mu_filet * diam_d2/1.715)
tete_torque   = Ft * (mu_sous_tete * dh/2)
pertes_filet  = filets_torque / couple * 100
pertes_tete   = tete_torque / couple * 100
pertes_totale = pertes_filet + pertes_tete
```
11) Contraintes :
```
aire_traction = (pi/4) * (diam_nominale - 0.9392*pas)^2
contrainte_traction = Ft / aire_traction
 tan_phi = pas / (pi * diam_d2)
 tan_rho = mu_filet / cos(alpha en rad)
 mth = Ft * (diam_d2/2) * ((tan_phi + tan_rho)/(1 - tan_phi*tan_rho))
 contrainte_torsion = 16*mth / (pi * diam_d3^3)
 contrainte_vm = sqrt(contrainte_traction^2 + 3*contrainte_torsion^2)
```

### Recherche de diametre de tete ISO
- `load_tete_vis_table(path=None)` : lit `Tete_vis.csv` (delimiter ;) -> dict {diam_nominale: {type_tete: diam_tete}} + tuple des types disponibles. Cherche le fichier dans plusieurs emplacements (assets du projet, assets a cote de l exe PyInstaller via `_MEIPASS`, etc.). Mise en cache dans `_TETE_TABLE_CACHE`.
- `lookup_diam_tete(diam_nominale, head_type)` : retourne le diametre de tete ISO ou None si absent.

### Dimensionnement inverse
- Dataclass `DimensionnementResult` : diam_nominale, diam_tete, serie, effort, couple, mat_vis, mat_body, mat_sous_tete, lubrified, head_types (liste de types valides pour ce diametre/etat sec ou lubrifie).
- Fonction `dimensionner(diametres, mat_vis, mat_body, effort_cible, couple_max, serie="H13", mat_sous_tete=None, include_lubrified=False, tete_table=None, manual_diam_tete=None, friction_mode="max", mu_filet_manual=None, mu_sous_tete_manual=None, has_washer=False, mat_rondelle=None, mat_sous_rondelle=None)`.
  - Valide que effort_cible>0, couple_max>0, liste de diametres non vide.
  - Normalise les materiaux (mat_sous_tete defaut = mat_body). Si rondelle cochee, remplit mat_rondelle/mat_sous_rondelle defauts = mat_body.
  - Charge/choisit la table de tete ISO. Si aucun diametre de la plage n a de valeur ISO -> `manual_diam_tete` obligatoire (0<val<120 et > diam max sinon exception). Sinon on utilise les valeurs ISO par diametre et type.
  - Pour chaque diametre unique et pour l etat sec puis lubrifie (si `include_lubrified`) :
     1. Liste des candidats tete = valeurs ISO trouvees pour ce diametre ou valeur saisie si pas d ISO.
     2. Filtre diam_tete > diam_nominale.
     3. Instancie `Vis` (diam_nominale, diam_tete, mat_vis, serie) puis appelle `effort_serrage` avec couple_max, mat_body, mat_sous_tete, friction_mode, mu manuels eventuels, rondelle eventuelle.
     4. Calcule le denominateur (memoise si deja calcule) et derive :
        - couple_min_requis = effort_cible * denom
        - couple_max_permis = min(couple_max, effort_cible*(1+0.08)*denom)
        - couple_recommande = couple_min_requis*(1+0.04) borne a couple_max_permis
        - effort_recommande = couple_recommande / denom
     5. Accepte la solution si effort_recommande >= effort_cible et <= effort_cible*(1+0.08) (tol 1e-6) et si couple_max_permis >= couple_min_requis.
     6. Stocke la solution la plus faible en couple par cle (diametre, etat lubrifie) et accumule les types de tete correspondants.
  - Retourne la liste triee par (diam_nominale, lubrified, couple) avec `head_types` tries alphabetiquement. Serie affichee en sortie est toujours "H12,H13,H14" dans l UI.

## Interface graphique (src/bolt_app/gui.py)
### Chargement des ressources
- `resource_path(*parts)` : si PyInstaller (`_MEIPASS`) utilise le dossier temporaire, sinon remonte de 2 niveaux depuis gui.py. Redefinit les chemins des CSV/icones dans `core` pour pointer vers `assets` embarques.
- `DEFAULT_HEAD_TYPES` + `HEAD_LABEL_MAP/HEAD_REVERSE_MAP` : harmonisent les intitul�s UI vs colonnes CSV (ex: "CHC tete fraisee" -> "CHC fraisee"). `HEAD_IMAGE_FILES` mappe type -> fichier image.
- Constantes UI : fond blanc `APP_BG`, texte `APP_FG`, polices Segoe UI 9/8/bold. `APP_VERSION = "V1.0 Beta"` affichee dans la fenetre et sous les images.
- Helpers : `enable_dark_title_bar` (Windows), `load_diametres` (lit la colonne Diametre nominale du pas), `to_float`, `format_couple` (convertit N.mm/N.m), `make_scrollable` (canvas + scrollbars, ajoute barre horizontale conditionnelle), `build_image_panel`, `add_separator`, `build_friction_block` (bloc de cases Frottement max/min ou saisie manuelle), `build_results_block` (section resultat onglet Calcul).

### Onglet "Calcul"
- Structure : frame scrollable avec colonne gauche (formulaire) et colonne droite (images + mentions ISO/version).
- Bloc Geometrie :
  - Combobox "Diametre nominal (M-)" (liste des diametres du pas, defaut 12).
  - Combobox "Tete de vis" (types issus de `head_types` ou DEFAULT_HEAD_TYPES + option "Autre").
  - Recherche dynamique du diametre de tete ISO via `tete_table`. Si trouve -> affiche "Diametre tete de vis ISO : X mm". Sinon affiche l avertissement rouge "Pas de taille ISO pour ce diametre, saisissez une valeur :" + champ de saisie "Diametre tete de vis (mm)". Selection "Autre" force aussi la saisie manuelle. Validation calculee : diam_tete > 0, <120, > diam_nominale.
- Bloc Materiaux :
  - Combos "Vis" et "Piece taraudee" (valeurs triees `DISPLAY_MATERIALS`, defaut Acier si disponible).
  - Checkbox "Lubrification des filets".
  - Checkbox "Surface d appui (different de piece taraudee)" -> active le combo "Surface d appui" (mat sous tete). Si coche, la checkbox rondelle disparait.
  - Checkbox "Presence d une rondelle" -> affiche combos "Rondelle" et "Surface d appui" pour la rondelle; desactive la case surface d appui principale (mutuellement exclusif avec celle-ci).
- Bloc Images (colonne droite) : titres "Vis" et "Montage" (bold italique). Choix de l image de vis selon la tete selectionnee (fallback CHC cylindrique pour "Autre"). Image reduite ~70 %. Montage : `Schema_appui_rondelle` si rondelle cochee sinon `Schema_appui_direct`. Sous les images : texte "Norme ISO 68-1 - filet a 60" puis "Version V1.0 Beta" (scroll plus bas dans Construction).
- Bloc Frottements : cases "Frottement max." (defaut on) / "Frottement min." / "Saisir les coefficients" (affiche champs filets et sous-tete si coche). Les options max/min se desactivent quand l saisie manuelle est active.
- Bloc Chargement : champ "Couple" (defaut 40), combo "Unites" (N.mm ou N.m, defaut N.m -> converti en N.mm pour les calculs).
- Bloc Actions : boutons "Calculer" et "Reinitialiser".
- Bloc Resultats (cache tant que pas de calcul) : titre "Efforts, Contraintes et Pertes par frottements" apres un separateur pleine largeur, sections numerotees :
  1. Effort de serrage (Pre-charge) -> champ Ft (N, readonly)
  2. Force de resistance au glissement -> champ (N)
  3. Contraintes -> traction/torsion/VM (MPa)
  4. Pertes par frottements -> filets (%), sous tete (%), total (%)
- Logique bouton Calculer :
  1. Parse diametre, tete (ISO ou saisie). Valide diam_tete>diam_nominale et borne [0,120].
  2. Lit materiaux, options surface d appui / rondelle (mutuellement exclusives) et materiaux associes.
  3. Convertit le couple selon l unite, verifie >0.
  4. Lit options de frottement (mode max/min ou valeurs manuelles 0..1).
  5. Instancie `Vis` puis appelle `effort_serrage` avec tous les parametres. Met a jour les champs Ft, glissement, contraintes, pertes (arrondis: Ft et glissement entier, contraintes une decimale, pertes entiere) puis affiche la section Resultats. Les erreurs (valeurs manquantes, hors plage) declenchent un messagebox.
  6. Bouton Reinitialiser masque la section de resultats et vide les champs.

### Onglet "Construction" (dimensionnement inverse)
- Style dedie (polices 10/18, fond blanc). Scrollbar verticale sur tout le formulaire + horizontale sur le tableau si necessaire.
- Bloc Geometrie :
  - "Intervalle de diametre" avec 2 combos (Diametre min., Diametre max.).
  - Si aucun diametre de la plage n a de valeur ISO dans `tete_table`, affiche en rouge : "Pas de taille ISO pour ce diametre, saisissez une valeur de diametre de tete de vis" + champ "Diametre tete de vis (mm)". Valide 0<val<120 et val>diametre max. Sinon champ masque.
- Bloc Materiaux :
  - Combos "Vis" et "Piece taraudee" (defaut Acier).
  - Checkbox "Surface d appui (different de piece taraudee)" -> active combo mat sous tete; si coche, la case rondelle disparait.
  - Checkbox "Lubrification des filets" (pilotera include_lubrified dans le calcul dimensionner).
  - Checkbox "Presence d une rondelle" -> combos mat_rondelle et surface d appui (actifs si coche). Mutuellement exclusive avec Surface d appui (si l une est cochee l autre disparait).
- Bloc Frottements : identique a l onglet Calcul (max/min/saisie).
- Bloc Chargement : "Effort de serrage cible (N)" (defaut 10000), "Couple maximal constructeur" (defaut 40), "Unites" (N.mm/N.m defaut N.m).
- Bloc Actions : boutons Calculer et Reinitialiser.
- Bloc Resultats (colonne droite, masque tant qu aucun calcul) :
  - Titre "Choix de vis possible" + separateur pleine largeur.
  - Tableau Treeview avec colonnes : Diametre (M-), Couple (avec unite choisie), Effort (N), Etat (Sec/Lubrifie), Materiau vis, Materiau assemblage, Materiau sous tete, Serie (affiche "H12,H13,H14"), Tete de vis (liste des types valides pour le diametre/etat). Scrollbar verticale + horizontale.
  - Label d etat pour messages d absence de solution :
    - si lubrification cochee mais aucune solution -> "Pas de solution, essayez une autre configuration";
    - si lubrification non cochee et aucune solution -> "Pas de resultat, reessayer le calcul en lubrifiant votre assemblage".
  - Label bas de page : "Norme ISO 68-1 - filet a 60".
- Logique bouton Calculer :
  1. Lit les diametres min/max, inverse si ordre mauvais, valide qu une liste existe dans Pas-std.
  2. Lit effort cible et couple max (convertit N.m -> N.mm), valide >0.
  3. Gere l etat surface d appui vs rondelle (mutuellement exclusif). Remplit materiaux sous tete/rondelle selon selections.
  4. Gere les options de frottement (mode ou saisie manuelle 0..1).
  5. Si aucune valeur ISO dans l intervalle -> oblige la saisie d un diametre de tete (validation > diametre max et <120).
  6. Appelle `dimensionner` avec diametres retenus, mat vis, mat body, mat sous tete eventuel, effort cible, couple max, include_lubrified selon checkbox, mode de frottement et coefficients manuels eventuels, info rondelle. Les resultats sont ajoutes au tableau (couple formate selon unite) et affiches. Bouton Reinitialiser vide et masque le tableau.

### Demarrage de l appli
- Fonction `main()` : cree la fenetre `Tk`, titre "Bolt V1.0 Beta - Calcul et Dimensionnement de Boulons", fond blanc, taille 1200x850, theme clam. Charge les diametres, table des tetes, icone Bolt_logo. Cree un Notebook avec onglets "Calcul" et "Construction" puis lance `mainloop()`.

## Packaging PyInstaller (build/bolt.spec)
- Entr�e : `src/bolt_app/gui.py` avec pathex `src`.
- Datas embarquees dans `assets/` et `assets/img/` (PNG, ICO, CSV list�s dans le spec).
- Ic�ne exe : `assets/Bolt_logo.ico`. Nom de l exe : "Bolt" (mode fenetre, pas de console, upx True, noarchive True).
- Commande pour reconstruire : `pyinstaller build/bolt.spec` depuis la racine du projet (assure que pyinstaller est installe et que les chemins assets sont valides). La sortie est placee dans `dist/Bolt` (avec copie des assets embarques).

## Execution locale
- Development : `python -m src.bolt_app.gui` ou `python src/bolt_app/gui.py` depuis la racine (Python 3.x avec tkinter dispo). Les chemins assets sont reassignes au demarrage via `resource_path`.
- Binaire : lancer `dist/Bolt/Bolt.exe` genere par PyInstaller.

## Points d attention / hypotheses
- Unites : couple exprime et calcule en N.mm en interne. L UI propose N.mm ou N.m (conversion x1000). Ft est retourne en Newton, diametres en mm.
- Materiaux : si un materiau n est pas reconnu, fallback Acier (sauf lorsque default_to_steel=False, qui declenche une erreur dans la lecture des CSV). Les listes UI affichent les noms francais tri�s.
- Frictions : mode "max" par defaut; mode "min" lit les colonnes `Dry_min_*` ou `Lubricated_min_*`. La saisie manuelle remplace completement les valeurs mu_filet/mu_sous_tete. Le calcul de force de glissement utilise `mu_sous_tete` ou `mu_sous_rondelle` selon la presence d une rondelle.
- Geometrie : la presence d un trou de passage est toujours definie par le CSV (plus de fallback diam_tete/2). Les diametres d1/d2/d3 et surfaces suivent ISO 68-1 (angle 60 degres constant).
- Dimensionnement : marge fixe 8 % au dessus de Ft cible; la serie affichee dans les resultats est "H12,H13,H14" pour couvrir les trois valeurs meme si la serie d entree est H13.
- UI : fond blanc, titre d onglets en bleu (#0c5da5) pour les sections principales, resultats et tableaux avec scrollbars. Images redimensionnees pour occuper moins d espace, texte "Version V1.0 Beta" sous les images.

Ce fichier decrit tous les assets, donnees, algorithmes, validations et comportements UI actuellement impl�mentes. En disposant uniquement de ce contenu, on peut reconstituer le projet (structure de fichiers, CSV, logique metier et interface) et regenerer l exe via PyInstaller.
