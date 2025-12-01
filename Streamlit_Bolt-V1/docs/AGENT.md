# Kellerman-Klein
### Outil pour calculer l'effort de serrage selon le type de vis ###

Ce document contient les instructions a suivre pour la creation de l'outil.

L'Outil Kellerman-Klein (du nom de la formule) doit permettre de calculer les efforts de tension dans une vis selon le type de la vis et le couple de serrage donne en input.

# Architecture cible du code #

Dans cette nouvelle version on conserve l'architecture en classe/objet.

Dans le constructeur l'utilisateur renseignera le 'diam_nominale' en mm le 'diam_tete' en mm la longueur de vis 'Longueur_vis' en mm et le materiau de la vis 'mat_vis' qui sera aussi stocke dans une variable de la classe, les differents materiaux de 'mat_vis' acceptables sont 'Steel', 'Gray Cast Iron', 'Bronze', 'Aluminum'. L'utilisateur devra respecter la casse (premiere lettre en majuscule) et si l'utilisateur saisi un autre materiau que ceux la par defaut le materiau 'Steel' sera choisi. Dans l'initiation du constructeur il faudra faire appel aux donnees qui sont les fichiers csv 'Pas-std.csv' et 'Frottement.csv' qui seront detailles dans la section suivante. L'attribut  'angle_filet' doit etre fixe a 60.0 degres. 

# Fichier 'Pas-std.csv' #
Le fichier 'Pas-std.csv' possede deux colonnes la premiere colonne "Diametre nominale" contient les diametres nominales suivant la norme iso et la deuxieme contient les pas de vis. En prenant le parametre 'diam_nominale' issu de des attributs de l'objet on parcours la premiere colonne et on recupere le pas correspondant dans la colonne d'en face et on assigne la valeur a la variable 'Pas'. Si 'diam_nominale' ne correspond a aucune valeur -> renvoyer une exception avec un message d'erreur de choix de diametre nominale. 

# Methode effort_serrage() #
LaLes arguments sont: le couple en N.mm, le diametre de trou de passage en mm qui par defaut sera nul, le materiau de la piece assemblee qui doit etre soit 'Gray Cast Iron', 'Bronze', 'Aluminum' en respectant la casse et si le materiau n'est pas communique ou nul a defaut ca la valeur de 'mat_body' sera a 'Steel'  il va aussi prendre en dernier argument un booleen de si la piece est lubrifiee ou non qui s'appellera 'is_lubrified' si aucune valeur est renseignee a defaut il sera a 'False'. On assigne a un attribut que l'on appelera 'mat_body' de la fonction la valeur du materiau, un autre attribut le boolen (oui/non lubrifiee) et la valeur du diametre de trou de passage qui par defaut sera nulle si non renseigne. Le fichier 'Frottement.csv' doit ensuite etre lu selon les conditions de la section suivante.

# Fichier 'Frottement.csv'
la premiere colonne du fichier est le materiau de la vis 'mat_vis' et la deuxieme colonne le materiau du corps assemblee 'mat_body' si l'on a un croisement des deux valeurs on choisira soit la valeur de la colonne "Dry max" si le boolen vaut "non lubrifiee" ou la derniere colonne "lubrificated max" si le boolen vaut "lubrifiee". Si il n'y a pas de materiau de corps 'mat_body' non renseigne ou nul mettre par defaut 'mat_body' a steel. 

# Calcul #
La methode de calcul doit reste identique a celle deja etablie dans le fichier 'KellermanKlein_dataclass.py' donc avec l'usage d'une methode de classe et la formule reste la meme. Les exceptions aussi doivent rester presente comme par exemple : si pas de diametre de trou de passage -> on considere le diametre de la tete comme Dh.

# Sorties #

Une fonction main doit pouvoir afficher la vis avec ses caracteristiques : diam_d1, diam_d2 mais aussi l'effort de serrage a l'aide de la methode. La sortie attendu est l'effort de serrage en N qui est la valeur que retournera la methode effort_serrage() cet sorti sera simplement un float(.)

# Unites #
Les unites du probleme sont les suivantes:
        C : Couple de serrage en N.mm
        Ft : Tension de la vis en N
        P : Pas de la vis en mm
        f : Coefficient de frottement du filetage
        Dt : Diametre sur flancs en mm (equivalent a D2)
        Dt = diametre nominal - 0,6495 x pas
        µh : Coefficient de frottement sous tete (Sans unite)
        Dh : Diametre moyen sous tete en mm
        Dh = (diametre tete de vis + diametre trou de passage) / 2 ; si pas de diametre trou de passage on prend Dh = diametre sous tete.
Il n'y a pas besoin d'autres parametres tel que le module d'Young pour ce calcul
Pour les fichiers sont les suivantes: 'Pas-std.csv' - 1er colonne : diametre nominale (pas d'unite). - 2ieme colonne Pas mmm

'Frottement.csv' La premiere colonne 'Material 1' sera la valeur parcouru et comparee avec le materiau de la vis 'mat_vis' la dexuieme colonne 'Material 2' le materiau parcourus par 'mat_body" lorsque les deux s'alignent il faut prendre la valeur de la meme ligne soit en 'Dry max soit en Lubricated max.


# MIS A JOUR V2 #

Desormais le parametre 'diam_trou_passage' ne sera pas saisi dans la methode mais il sera definit en meme temps que le Pas de vis 'Pas' en __post_init__ a l'aide du fichier 'Trou_passage.csv' qui devra aussi etre creer comme objet a l'aide de PATH, tel que ca a ete fait pour les autres csv.
Le fichier csv se presente comme suit: il y a une premiere colonne 'diametre_nominale' et les autres colonnes sont des types de series H12, H13, H14. dans les attributs de la classe vis ainsi que les arguments du constructeurs il faut ajouter un parametre 'serie' qui sera par defaut a H13 si non renseigne. L'utilisateur doit renseigner la serie entre H12, H13 et H14 et lorsque le post init sera fait il faudra que le fichier 'Trou_passage.csv' soit parcourus et que la valeur correspondant aux parametres 'diam_nominale' ainsi que la serie 'serie' puisse permettre de trouver la bonne case dans le fichier 'Trou_passage.csv' et l'assigner a la variable 'diam_trou_passage'. Il faut aussi retirer la condition ligne 66 disant que s'il n'y a pas de trou de passage 'diam_trou_passage' alors dh = 'diam_tete'/2 car desormais 'diam_trou_passage' sera par defaut a la valeur correspondant a 'H13' suivant le 'diam_nominale' du fichier 'Trou_passage.csv' par defaut. Je laisse codex gerer les cas d'exceptions. 

# MIS A JOUR V3 #

*** changements algorithmiques ***
Il faut desormais changer le nom de l'application 'app_gui' qui sera desormais 'Bolt' et utiliser l'image 'Bolt_Logo.png' comme icon de l'application.

Il faudrait en plus ajouter dans la fonction qui calcul de serrage ou dans une autre fonctions supplementaire trois nouvelles variables qui s'appellerons "pertes_frottements_filet", "pertes_frottements_tete" et "pertes_frottements_totale". Voici comment ils seront calcule :

- pertes_frottements_tete = ((effort de serrage * mu_sous_tete * (Dh)/2) / couple ) * 100
- pertes_frottements_filet = ((effort de serrage * ( (0.161 * Pas) + (self.diam_d2 / 1.715))) / couple ) * 100
- pertes_frottements_total = pertes_frottements_filet + pertes_frottements_tete

*** changements de l'interface ***

Dans l'interface de l'utilisateur il faut desormais realisr les changements suivants:

- utiliser l'image 'Bolt_logo' comme icône de l'outil pour son lancement
- renommer l'outil 'Bolt' au lieu de 'app_gui'
- Utiliser l'image 'Schema_technique.png' au centre de l'interface pour illustration
- apres avoir valide le calcul de l'effort de serrage, l'outil doit faire apparaitre en meme temps que le resultat de l'effort de tension et un peu plus bas:
        - la 'perte de couple par frottement sous tete' qui affichera la valeur de 'pertes_frottements_tete' suivi de '%'
        - la 'perte de couple par frottement des filets' qui affichera la valeur de 'pertes_frottements_filet' suivi de '%'
        - la 'perte de couple par frottement totale' qui affichera la valeur de 'pertes_frottements_total' suivi de '%'


# MIS A JOUR V4 #

*** Changements algorithmiques ***
- Il faut retirer le parametre 'Longueur_vis qui ne sera pas utilise.

- Remplacer les "allowed materials" par les materiaux suivants : "Acier", "Bronze", "Cuivre", "Inox", "Aluminium"

- Modifier le calcul des pertes par frottements: la formule de 'pertes_frottements_filets' va evoluer. Desormais elle se calculera de la maniere suivante : 
        pertes_frottements_filet = (((effort de serrage * (self.diam_d2 / 1.715))) / couple ) * 100

*** Changements de l'interface ***

- Sur l'interface de l'outil il faudrait que soit afficher de maniere permanente (en haut ou en bas de l'outil proche de l'image) que les angles de filet sont a 60° car suit la norme ISO 68-1, en ecrivant 'angle filet : 60° ISO 68-1'.

*** Changements architecture dossier ***
Il faudrait recree directement le fichier executable apres avoir fait les mise a jour en gardant les meme instructions pour celui-ci (icone, titre, etc.).

Est il possible de re arranger l'ordre des dossier de maniere a ce qu'on puisse voir directement l'outil "Bolt" en allant dans le dossier et que tous les autres fichiers de code ne soit pas visibles directement ou cache dans d'autres dossier??


# MIS A JOUR V5-1 #

*** Calcul de l'effort de serrage ***
Desormais pour le frottement il faudra lire deux valeurs dans le fichier "Frottement.csv" et donc assigner a la variable 'mu_filet' la valeur 'Dry_max_filet' et a la variable 'mu_sous_tete' la valeur 'Dry_max_tete', en reutilisant la meme methode que plus haut c'est a dire faire une correspondance entre le nom choisis dans la liste deroulante et le Material 1 puis le second avec le Material 2. Si la checkbox 'lubrifie' est cochee sur l'outil choisir a la place la valeur 'Lubricated_max_filet' a la place de 'Dry_max_filet' pour le 'mu_filet' et si la deuxieme case 'lubrifie' est coche (voir le paragraphe *** Affichage dans l'outil ***) assigner la valeur 'Lubricated_max_tete' a 'mu_sous_tete'.

- Dans DISPLAY_MATERIALS et MATERIAL_SYNONYMS ajouter les nouveaux materiaux renseignes dans "Frottement.csv".


*** Affichage dans l'outil ***

- Dans la premiere ligne, remplacer le '(mm)' dans 'Diametre nominale(mm)' par '(M-)'
- Trier l'affichage des Noms de materiaux dans les listes deroulantes par ordre alphabetique
- Mettre en gras l'effort de serrage en sortie et ecrire "Effort de Serrage Ft : " Au lieu de "Ft"
- Ne plus afficher D1 et D2 en sortie 
- Ajouter une check box "Rondelle/Corps avec materiau different", si elle est cochee ajouter une autre liste deroulante nomee "materiau sous-tete" (par defaut cette partie est grisee)
- Ajouter aussi la check box 'lubrifie' qui sera aussi grisee par defaut et en dessous de "materiau sous-tete" et qui se degrisera aussi quand "Materiau du corps sous tete different" est coche.

# Mise en forme #
La mise en forme generale doit se faire en quatres blocs separes par des tirets entre chaque blocs :
- 1 ere bloc "Geometrie", ou on aura les listes deroulantes, cases a remplir suivantes:
        - Diametre nominale (M-)  # qui est une liste deroulante
        - Serie    # qui est une liste deroulante
        - Diametre de tete (mm)  # qui est une valeur a saisir
- 2 ieme bloc "Materiaux" ou on aura les listes deroulantes et boutons suivants
        - Materiau de la vis  # qui est une liste deroulante
        - Materiau de la piece # qui est une liste deroulante
        - Filets lubrifies  # qui est une case a cocher
        - materiau du corps sous tete different # qui est une case a cocher
        - materiau du corps sous tete # qui est une liste deroulante
        - materiau sous tete lubrifie # qui est une case a cocher
- 3 ieme bloc "Chargement" ou on aura la case suivante a remplir
        - Couple 
        - Nm ou Nmm # Qui est une liste deroulante avec l'unite du couple comme faite precedemment 
- 4 ieme bloc les boutons "Calculer" et "Reinitialiser" en dessous.
        Les resultats devront apparaitre en dessous des boutons calculer et reinitialiser.

# Patch #

pour les tirets separants des blocs utiliser des traits continus plutôt que des traits discontinus (une succession de ___)
remplacer le checkbox "Materiau du corps sous tete different" par "Autre materiau bloc sous-tete"
remplacer "Materiau du corps sous tete" par "Materiau bloc sous-tete"
Mettre des espaces entre les boutons/liste deroulantes dans les blocs et augmenter l'espace entre deux blocs.

# Patch 2 #

Mettre le fond en bleu #0A66C2.
Mettre le resultat effort de serrage dans un format permettant un copie colle


# MIS A JOUR V5-1.1 #

***Modification du code***

*** Ajout de nouveaux attributs de la classe ***
On ajoutera un nouvel attribut dans la classe qui s'appellera 'alpha' il sera aussi declarer avec @proprety et on lui assignera la valeur de: self.alpha = angle_filet / 2.

On ajoutera aussi une nouvel @proprety qu'on appellera diam_d3 on lui assignera la valeur suivante:
self.diam_d3 = diam_nominale - (1.22687 * self.pas)

*** Ajout de methodes ***
Pour cette nouvelle mise a jour il faudra ajouter trois nouvelles methodes :

- Une premiere qui s'appellera : calcul_contrainte_traction().
Cette methode prendra en argument l'effort de serrage (il faudra donc soit la creer à l'interieur de la methode en calculant l'effort de serrage soit recuperer la valeur par reference) et aussi le diametre nominal 'diam_nominale' de la vis. 
A l'interieur de la fonction il sera d'abord calcule l'air de traction de la vis At qui s'exprimera de la maniere suivante:
At = (pi/4) * ((diam_nominale - (0.9392 *self.pas)**2))
On calcul ensuite la contrainte F = effort de serrage / At
Cette contrainte doit etre retournee ensuite.

- Une seconde methode qui s'appellera: calcul_contrainte_torsion()
Cette methode prendra en argument l'effort de serrage.
 il faudra calculer la variable couple de filet Mth. Mais dans un premier temps on calcul des variables internes necessaire au calcul des couples il s'agit des variables tan_phi et tan_rho qui s'ecriront de la maniere suivante:
 tan_phi = self.pas / (pi * self.d2)
 tan_rho = mu_filet / cos(alpha)
 ensuite pour le couple au filet:
 Mth = Effort de serrage * (self.diam_d2/2) * ((tan_phi + tan_rho) / (1-(tan_phi * tan_rho)))

 Puis on calcul enfin la contrainte de torsion

 tau_max = 16 * Mth / (pi *(self.diam_d3)^3)

- Une troisieme methode qui s'appellera: contrainte_equivalent_VM()
Cette methode prendra en argument la contrainte de traction trouvee avec la methode 'calcul_contrainte_traction()' que l'on appellera ici 'contrainte_traction' et la contrainte de torsion trouvee avec la methode calcul_contrainte_torsion() que l'on appellera ici 'contrainte_torsion'. On aura donc contraintes_vm = ((contrainte_traction^2) +(3 * contrainte_torsion^2))^(1/2), cette valeur doit etre retournee.

*** Affichage des contraintes dans l'Outil ***
- Ajouter une Section RESULTATS qui apparaitra en dessous des boutons "Calcul" et "Reinitialiser" uniquement apres que le bouton calcul soit appuye. En appuyant sur "Reinitialiser" cette section et son contenu doit disparaître.

- La section doit contenir les informations suivantes:
        - L'effort de Serrage Ft qui sera toujours affiche comme precedemment sans evolution
        - La Contrainte de Traction qui sera appelee "Contrainte de Traction dans les filets (MPa)"; La mise en forme doit etre la meme que pour l'effort de Serrage Ft
        - La Contrainte de Torsion qui sera appelee "Contrainte de Torsion dans les filets (MPa)" ; La mise en forme doit aussi être semblable a celle de L'effort de Serrage Ft 
        - La Contrainte de Von Mises qui sera appelee "Contrainte Equivalente VM (MPa)"; La mise en forme doit être semblable a celle de L'effort de Serrage Ft

# Patch 3 #

Peux-tu ajouter une condition dans la saisi des valeurs dans l'outil de sorte a ce que si l'utilisateur saisi un diametre de tete plus petit que le diametre nominale une erreur apparaisse "diametre de tete plus petit que le diametre nominale saisir une valeur valide".

Peux tu mettre changer le nom de la section "RESULTATS" en "Resultats Pre-chargement et Contraintes", ajouter aussi un tiret "__" separant les boutons du dessus et cette section, puis redefinir la taille globale de tout les textes de maniere a ce que tout puisse tenir dans la fenetre car actuellement on ne peut pas voir la valeur de la contrainte VM car elle depasse.

# Hypothese MIS A JOUR V5-2 #

Dans cette version j'aimerai creer un deuxieme onglet qui s'appelle "Dimensionnement". Cette fois l'outil sera scinde en deux.

Un premier Onglet "Calcul" et un second onglet "Dimensionnement".

*** Interface ***
L'utilisateur un  effort de serrage qu'il souhaite , une plage de diametre nominale souhaitee ainsi qu'un couple maximale qu'il peut se permettre. L'outil devra donner en sorti les differents diametre de vis possible et les materiaux permettant d'atteindre son objectif par exemple tel combinaison effort de serrage / Couple max sera possible que avec tel diametre. L'utilisateur devra choisir les materiaux de la vis et du corps, il pourra optionnellement choisir un materiau sous tete (une case a cocher qui sera decochee par defaut et on ne calculera que les cas sec). Il pourra aussi cocher une case pour preciser si c'est lubrifier ou non (par defaut cette case sera decochee). S'il coche lubrifie les resultats lubrifies apparaitront avec lubrifier entre parenthese et les autres non. Pour les unites du couple on peut faire comme dans le premier onglet et lui laisser le choix entre N.mm et N.m. Les resultats devront etre triees du diametre le plus petit au plus grand. Si les resultats sont uniquement des cas lubrifies pas besoin de message necessaire. En cas d'absence de solution a sec faire apparaitre le message "Pas de resultat, reessayer le calcul en lubrifiant votre assemblage".
En cas d'absence de solution lubrifier le message "Pas de solution, essayez une autre configuration". Attention Ne prendre en consideration ici, dans cet onglet, que la lubrification des filets et pas la lubrification sous tete il ne devrait y avoir donc qu'une seule case ici "lubrification des filets" et pas la case sous tete comme dans la premiere partie. Par contre l'utilisateur devra bien choisir un materiau sous tete de vis (optionnel si une case coche) et un materiau de corps. Si le materiau sous tete de vis n'est pas coche alors il sera le meme que le materiau du corps.

*** partie algorithmique ***
En terme de code il faudrait que tu creer une nouvelle classe vis qui herite de la premiere (si c'est la maniere la plus simple de proceder). Il faudrait garder les meme parametres mais faire le calcul a l'envers. Utiliser un algorithme pouvant trouver toutes les combinaisons possibles de diametre nominal, effort de serrage et couple qui correspondent a la demande de l'utilisateur en input. Et s'il n'y a aucune correspondance possible renvoyer une exception indiquant qu'il n'y a pas de correspondance.
Il faudrait aussi gerer tous les cas d'exception: couple maxi inferieur a effort de serrage ou autre.

Pour le couple a utiliser il n'est pas necessaire d'utiliser le couple maximum de l'utilisateur, l'idee est de trouver le couple se rapprochant au mieux de son effort de serrage sans etre egale a lui (pour des raisons de conservatisme en raison de l'incertitude lie au frottement).

filtrer les combinaisons dont le couple requis ≤ couple max, trier par ecart à Ft cible avec marge de 8 % (marge figee, non affichee). L'effort de serrage qui en decoule doit imperativement etre au dessus de l'effort de serrage demande par l'utilisateur.

# Patch 4 #
*** Partie graphique ***
Peux tu mettre le fond en blanc dans les deux onglets.

Peux tu également ajouter une liste déroulante afin de pouvoir défiler dans l'outil vers le bas car le contenu est plus grand que ce qui est affiché.

# Patch 4.2 #

*** Partie graphique ***

Onglet "Dimensionnement"
- Renommer l'onglet "Construction" au lieu de "Dimensionnement"
- Remplacer les première lignes "Diametre nominal min (M-)" et "Diametre nominale max (M-)" par une première ligne "intervalle de diamètre"
suivis d'un ligne ou il y aura ecrit "Diametre min." et "Diametre max." sur la meme ligne. En dessous des de chacun des titres de diametres il faut ajouter un
e liste deroulante avec le choix des diametre.

-retirer la ligne sur le choix de la Serie. Desormais dans la liste des resultats les differents types de series seront affiches sous une seule colonne apres les materiaux avec des virgules par exemple "Série" et en dessous "H12,H13, H14"

- Remplacer "Couple maximal" par "Couple maximal constructeur"

- Remplacer "Nm ou Nmm" par "Unite"

- au dessus du tableau des resultats apparaissant apres le calcul ecrire "Choix de vis possible"

- remplacer dans cet onglet l'image "Schema_Technique.png" par l'image "construction_image.png" suivant les memes proportions. 

Onglet "Calcul"
- Remplacer la ligne "Materiau de la piece" par "Matériau de la pièce d'assemblage"
- Remplacer "Filets lubrifies" par "Lubrification des filets"
- Remplacer "Autre materiau bloc sous-tete" par "Matériau différent sous tête de vis"

- Remplacer "Materiau bloc sous-tete" par "Matériau sous tête de vis"

- Remplacer "Nm" ou "Nmm" par "Unités"

- Au dessus de "Resultat Pre-cgargement et Contraintes" lorsque celui-ci est apparent ajouter une ligne de separation qui fait toute la ligne.

- Remplacer "Resultat Pre-cgargement et Contraintes" par "Effort de serrage et Contraintes"

*** Commun aux deux parties ***
- Mettre les titres des blocs (Géométrie, Materiaux, Chargement, Actions, intervalle de diamètre) dans une police un peu plus importante que le reste du texte.

- En dessous de l'image remplacer le texte "angle filet: 60° ISO 68-1" par " Norme ISO 68-1 - filets à 60°"

- ajouter une barre de défilement horizontale qu'il sera possible d'utiliser lorsque l'application sera en taille reduite.

*** Partie Calcul ***

Les Series H12, H13, H14 ne sont desormais plus des donnees d'entree et devront etre calculer en meme temps que les autres parametres et proposee en sortie

# Patch 4.3 #

*** Onglet Calcul ***
Desormais il faudra retirer la ligne 'Diametre de tete(mm)' et ajouter à la place une liste déroulante intitulé 'Type de tête'. Cette liste proposera les differents type de tete de vis qui sont sur le fichier 'Tete_vis.csv' , a savoir "Hexagonale", "CHC cylindrique", "CHC tete fraisee", "CHC tete bombee", "Tete bombee fendue", "Tete bombee philips", "Tete bombee Pozidriv", "Tete bombee Torx interne" qui vont des colonnes B a I a laquelle on croisera le diametre nominal colonne A. Desormais le diametre de tete "Diam_tete" sera aussi définit avec le code en faisant correspondre le diametre nominale choisit dans l'interface avec la ligne de 'Type de tête' choisit par l'utilisateur, je te laisse gérer la manière dont ce sera réalisé. Si le croisement des deux valeurs tombe sur une valeur "-" du fichier 'Tete_vis' il faudra qu'apparaisse écrit en rouge et sous la case du 'Type de tête' choisit "Pas valeur ISO pour ce diamètre, veuillez saisir une valeur", puis faire apparaître en dessous une case 'Diamètre de tête (mm)' avec la valeur à saisir, cette valeur sera un float, qui devra etre positif, en dessous de 120 et au dessus du diametre nominal, il faudra envoyer un message d'erreur en cas de valeurs qui ne respecte pas ces critères, ensuite assigner a "Diam_tete". Lorsque l'utilisateur change la valeurs de la liste roulante et qu'il choisi a nouveau un diametre ISO, la texte  Pas valeur ISO pour ce diamètre, veuillez saisir une valeur" ainsi que la case de valeur a saisir disparaissent.L'apparition de cette case doit etre dynamique et ne dois pas attendre qu'on appui sur le bouton "calculer", des lors ou un diametre nominal et un Type de tête choisi ne correspondent a aucune valeur sur le fichier 'Tete_vis.csv' il faudra automatiquement et dynamiquement faire apparaitre le message "Pas valeur ISO pour ce diamètre, veuillez saisir une valeur" puis la valeur à saisir en dessous. Si l'utilisateur choisit de nouveau une valeur ISO cette case ainsi que le message doivent disparaître

*** Onglet Dimension ***

Retirer la ligne "Diametre de tete (mm)".

Desormais le calcul s'effectuera avec tous les types de diametres de tete possible pour la plage de diametre nominale donnee, par exemple pour un M6 on regardera les cas possibles avec les 8 types de diamètres et on retournera tous les types de diametres qui matchent avec la recherche et seront affiches dans la derniere colonne du tableau de resultat de recherche par ordre alphabetique. S'il n'y a pas de diametre correspondant (comme en M7 ou M9) dans toute la plage qu'à saisi l'utilisateur (par exemple M7 en min et M7 en max) ajouter dynamiquement une case demandant a l'utilisateur de saisir la taille du diametre de tete car le diametre nominale est non existant en ISO cette valeur sera un float, qui devra etre positif, en dessous de 120 et au dessus du diametre nominal, il faudra envoyer un message d'erreur en cas de valeurs qui ne respecte pas ces critères, ensuite assigner a "Diam_tete". Tant que la plage contient des valeurs ISO faire les calculs avec les valeurs ISO si elle ne contient aucune valeur ISO dans ce cas faire apparaître la case et demander la saisie.  dans le tableau des résultats il y aura les différents types de diamètres possibles separes par une virgule comme les series.

# Correctifs #

Dans l'onglet Calcul : Remplacer le message "Pas valeur ISO pour ce diametre, veuillez saisir une valeur" par "Pas de taille ISO pour ce diamètre, saisissez une valeur :"  

- Au dessus de "Effort de Serrage et Contraintes" remplacer le trait "_" par un trait faisant la longueur de toute la ligne. 

- revoir l'orthographe de certains titre et liste deroulantes:
        - remplacer "Diametre nominal (M-)" par "Diamètre nominal (M-)"
        - remplacer "Type de tete" par "Tête de vis"
        - remplacer "Tete bombee philips" par "Bombée Philips"
        - remplacer "CHC tete bombee" par "CHC bombée"
        - remplacer "CHC tete fraisee" par "CHC fraisée"
        - remplacer ""Tete bombee Pozidriv"" par "bombée Pozidriv"
        - remplacer ""Tete bombee Torx interne"" par "bombée Torx interne"
        - remplacer "Diametre de tete" par "Diamètre tête de vis" lorsqu'il est apparent
        - remplacer "Geometri" par "Géométrie"
        remplacer "Materiaux" par "Matériaux"

-----------------------

Dans l'onglet "Construction" : 
- Remplacer le message "Pas valeur ISO pour cette plage veuillez saisir un diametre de tete" par "Pas de taille ISO pour ce diamètre, saisissez une valeur de diamètre de tête de vis".

- En dessous de Choix de vis possible et au dessus du tableau des résultats faire en sorte que le trait "_" ait la longueur de toute la ligne afin de marquer une bonne demarquation

- Dans le tableau qui affiche les résultats de vis possible, ajouter une barre de défilement horizontale sur le tableau afin de pouvoir voir les résultats aux extrémités.

# Mise à jour V1.0 Beta #

Dans l'interface, mettre en gras le nom des titres des blocs "Géométrie" , "Matériaux" , "Chargement", Actions". Remplacer "Reinitialiser" par "Réinitialiser". Dans l'onglet "Constructions" remplacer "Unite" par "Unités".

En dessous du bloc "Matériaux" ajouter un bloc "Frottements" avec 3 cases à cocher: "Frottement max." , "Frottement min." et "Saisir les coefficients". Par défaut la case "Frottement max." est selectionnee.

Si la case "Frottement min" est cochée, desormais lorsque le fichier "Frottement" lu il ne faudra plus lire les colonnes "Dry_max_filet", "Dry_max_tete", "Lubricated_max_tete" , "Lubricated_max_filet" mais a la place les colonnes "Dry_min_filet", "Dry_min_tete", "Lubricated_min_tete" , "Lubricated_min_filet" pour recuperer les valeurs de frottement (en gardant la meme methodologie donc en la faisant correspondre avec le diametre nominale saisi).

Si la case "Saisir le coefficient" est coché par l'utilisateur, deux cases devront apparaître dynamiquement juste en dessous. La première sera "Frottement des filets" et la deuxieme "Frottement sous tete".Les deux cases ne devront prendre des valeurs que entre 0 et 1. Lorsque ces valeurs sont saisis elles doivent remplacer les valeurs de 'mu_filet' (pour" Frottement des filets") et 'mu_sous_tete' pour "Frottement_sous_tete". Si l'utilisateur décoche la case "Saisir les coefficients de Frottement" les deux cases doivent disparaitre.

Dans l'onglet "Calcul" dans l'affichage des resultats remplacer "Effort de serrage et Contraintes" par "Efforts, Contraintes et Pertes par frottements". Le "1)Pre-Chargement" devra desormais s'appeller "1) Effort de serrage (Pré-charge)". Remplacer aussi le titre "Effort de Serrage Ft (N):" par seulement "Ft (N)". "2)Contraintes " sera désormais "3) Contraintes". "3) Pertes" sera desormais "4) Pertes par frottements". Ajouter en 2) juste en dessous du resultat du 1) une nouvelle section "2) Force de résistance au glissement"  la valeur sera au meme format que pour les autres resultats et elle sera egale a : ('mu_filet' * Effort de serrage).

Dans l'onglet "Construction" Ajouter egalement le bloc "Frottements" avec 3 cases à cocher: "Frottement max." , "Frottement min." et "Saisir les coefficients". Par défaut la case "Frottement max." est selectionnee et le fonctionnement sera le meme que dans l'onglet calcul.

Pour le titre de l'outil changer "Bolt v5.2 - Effort de serrage" en "Bolt V1.0 Beta - Calcul et Dimensionnement de Boulons"

# ajouts V1.0 Beta #

Desormais "Materiau de la rondelle" ne sera visible que si "Rondelle" est coché et disparaitra s'il est décoché ce changement devra se faire en dynamique. Meme chose pour l'onglet "Construction". En plus de Matériau Rondelle afficher une deuxième case 'matériau sous rondelle' avec une liste déroulante des materiaux definis jusqu'a present, cette case devra aussi disparaitre si 'Rondelle' est decoche.


Ajouter un nouvelle attribut dans la classe principale qui s'appellera 'mu_sous_rondelle' lorsque la case 'Rondelle' sera cochée il faudra ouvrir le fichier 'Frottement.csv' et rechercher le coefficient de frottement adequat. Le 'Matierial 1' sera le matériau de la rondelle et le 'Material 2' le materiau de la pièce sous la tete qui sera choisis par l'utilisateur avec la liste deroulante sous 'materiau sous rondelle'.

Desormais le calcul de la force de resistance au glissement ne sera plus egale a ('mu_filet' * Effort de serrage) mais sera plutot ('mu_sous_tete' * Effort de serrage) si 'Rondelle' n'est pas coche et si 'Rondelle' est coche il vaudra ('mu_sous_rondelle' * Effort de serrage).

# 2ieme ajouts #

Dans la liste deroulante des choix de tete de vis pour l'onglet calcul ajouter un choix "Autre" qui sera en dernier dans la liste. Si cet option est choisit, afficher la case permettant a l'utilisateur de saisir directement la taille de "Diamètre tete de vis (mm)"

Voir pourquoi dans l'outil lorsque l'on choisi les vis 'CHC fraisee', 'CHC bombee', 'CHC bombee fendu', 'Bombee Philips', 'Bombee Pozidriv', 'Bombee Torx interne' , l'outil renvoi "Pas de taille ISO pour ce diametre, saisissez une valuer:" pour toutes les tailles or il y a bien des tailles pour certains diametres dans le fichier 'tete_vis.csv' voir pourquoi ces valeurs ne sont pas lues.

desormais le choix des images affiches sur l'outil sera dynamique et dependera des choix de l'utilisateur ou de ce qu'il cochera.la partie droite presentant les images sera scindee en deux parti: une premiere image au dessus, intitule "Vis" (le titre sera en gras, souligne et au dessus de l'image et centre) et l'image sera soit le fichier 'bombee fendue.png' ou 'Bombee Torx.png' ou 'CHC bombee.png' ou 'CHC Cylindrique.png' ou 'CHC fraisee.png' ou 'Hexagonale.png' ou 'Vis_bombee_philips_pozidriv.png' selon le choix de l'utilisateur qui sera expliqué dans le paragraphe suivant. Puis une seconde image qui sera intitulé "Montage" (le titre sera en gras, souligne et au dessus de l'image et centre)et sera soit le fichier 'Schema_appui_direct.png' soit le fichier 'Schema_appui_rondelle.png' selon le choix de l'utilisateur qui sera expliqué dans le paragraphe suivant.

La première image sera choisi en fonction de la tete de vis qui sera choisis en liste deroulante et changera en dynamique.
Si l'utilisateur choisis la vis 'Hexagonale' alors on l'image affichee sera 'Hexagonale.png'. Si l'utilisateur choisis la vis 'CHC cylindrique' alors on l'image affichee sera 'CHC Cylindrique.png'. Si l'utilisateur choisis la vis 'CHC fraisee' alors on l'image affichee sera 'CHC fraisee.png'. Si l'utilisateur choisis la vis 'CHC bombee' alors on l'image affichee sera 'CHC bombee.png'. Si l'utilisateur choisis la vis 'Bombee fendue' alors on l'image affichee sera 'bombee fendue.png'. Si l'utilisateur choisis la vis 'Bombee Philips' alors on l'image affichee sera 'Vis_bombee_philips_pozidriv.png'. Si l'utilisateur choisis la vis 'Bombee Pozidriv' alors on l'image affichee sera 'Vis_bombee_philips_pozidriv.png'. Si l'utilisateur choisis la vis 'Bombee Torx interne' alors on l'image affichee sera 'Bombee Torx.png'. 

Remplacer "Matériau de la vis" par "Vis". Remplacer "Matériau de la pièce d'assemblage" par "Trou taraudé". Remplacer "Materiau different sous tete de vis" par "Surface d'appui"
Remplacer "Rondelle" par "Présence d'une rondelle"
Remplacer "Materiau de la rondelle" par "Rondelle" remplacer "Materiau sous rondelle" par "Surface d'appui".

# Correctifs 2ieme ajouts #
Peut tu retirer la mention "illustration indisponible" en haut de l'image.

Placer la mention "Norme ISO 68-1 - filet à 60°" en dessous de la premiere image, au dessus de la deuxieme.  
Placer la mention "version v1.0 beta" en dessous de la seconde image.
Retrecir la premiere image (la plus haute) d'environ 30%. 

Il y a un probleme dans le code avec les vis: Bombee Torx interne, Bombee Pozidriv, Bombee Philips, Bombee Fendu, Bombee, CHC fraisee, CHC bombee. meme lorsque l'on choisit un diametre qui existe sur la liste des que l'on appui sur "Calculer" l'outil renvoi "Pas de diamètre ISO pour ce diamètre, saisissez une valeur:" or ce message d'erreur n'est pas suppose apparaitre en appuyant si calcul et il est suppose apparaitre uniquement si on selectionne un diametre qui n'est pas dans les tables de tete_vis.csv. Peux tu resoudre le probleme.

# 2ieme correctif #

Peux tu remplacer le "Trou taraudé" par "Pièce taraudée".

Lorsque "Surface d'appui" est coche faire en sorte que "Presence d'une rondelle" ne soit plus apparent il ne doit pas etre possible de cocher les deux en meme temps. Lorsque Presence d'une rondelle est coche faire en sorte que Surface d'appui ne soit plus apparent. Retirer la case a coche "Materiau sous tete lubrifie" cet option ne sera plus a considerer.

Dans l'onglet "Construction" retirer l'image et faire en sorte que les textes et les options soit centres dans la fenetre de l'outil.