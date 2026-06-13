# Documentation des Skills

Ce document liste et décrit en détail tous les outils (skills) implémentés dans le projet.

## Skill `analyse_zone`

Responsable de :
* orchestrer une analyse d'urgence complète d'une adresse ou d'une zone[cite: 5] ;
* récupérer la localisation, les coordonnées GPS, la météo, les risques connus et les équipements sensibles[cite: 5] ;
* produire une synthèse de situation JSON exploitable[cite: 5].

**API utilisée :** Multiples APIs (via l'appel des autres skills locaux)[cite: 5].

---

## Skill `cartographie_zone`

Responsable de :
* générer une carte HTML interactive (Leaflet) d'une zone d'intervention[cite: 7] ;
* afficher le point central et les périmètres de vigilance[cite: 7] ;
* positionner les équipements sensibles proches sur la carte[cite: 7].

**API utilisée :** OpenStreetMap / Folium.

---

## Skill `equipements_sensibles`

Responsable de :
* rechercher les équipements proches[cite: 5] ;
* identifier : hôpitaux, pharmacies, écoles, services de police, casernes de pompiers, cliniques[cite: 5] ;
* nécessiter une latitude, une longitude et un rayon de recherche en mètres[cite: 5].

**API utilisée :** OpenStreetMap / Overpass API[cite: 5].

---

## Skill `etat_epidemiologique`

Responsable de :
* récupérer l'état sanitaire et épidémiologique d'une région géographique ;
* convertir un code INSEE ou un code postal en code régional pour interroger les bases de données de santé ;
* extraire les indicateurs, les taux d'incidence et les alertes pour diverses maladies (grippe, infections respiratoires aiguës, gastro-entérite, etc.).

**API utilisée :** Sentiweb / API Adresse Data Gouv.

---

## Skill `itineraire_evacuation`

Responsable de :
* calculer un itinéraire d'évacuation routier vers un point de repli[cite: 8] ;
* éviter strictement et physiquement une zone de danger circulaire définie (nogos)[cite: 8] ;
* générer une carte HTML affichant le trajet d'évacuation et la menace[cite: 8].

**API utilisée :** BRouter / API Adresse Data Gouv.

---

## Skill `localisation_site`

Responsable de :
* convertir une adresse, un lieu ou une commune en coordonnées GPS (latitude et longitude)[cite: 5] ;
* récupérer la commune et le code postal[cite: 5] ;
* récupérer le code INSEE associé au lieu pour les analyses de risques[cite: 5].

**API utilisée :** API Adresse Data Gouv[cite: 5].

---

## Skill `localisation_utilisateur`

Responsable de :
* estimer la localisation de l'utilisateur à partir de son adresse IP en cas d'absence de saisie manuelle ;
* récupérer les coordonnées GPS (latitude, longitude) de l'utilisateur ;
* enrichir la localisation avec la ville et le code INSEE correspondant pour lancer les autres outils de l'orchestrateur.

**API utilisée :** ipinfo.io / API Adresse Data Gouv.

---

## Skill `meteo_urgence`

Responsable de :
* récupérer la température actuelle[cite: 5] ;
* récupérer la vitesse du vent[cite: 5] ;
* récupérer les précipitations[cite: 5] ;
* récupérer les informations météo utiles à l'analyse pour évaluer les facteurs aggravants[cite: 5].

**API utilisée :** Open-Meteo[cite: 5].

---

## Skill `risques_site`

Responsable de :
* rechercher les risques territoriaux connus sur une zone[cite: 5] ;
* récupérer les informations Géorisques[cite: 5] ;
* analyser une commune à partir de son code INSEE[cite: 5].

**API utilisée :** Géorisques[cite: 5].

---

## Skill `vigilance_meteo`

Responsable de :
* estimer un niveau de vigilance météo en temps réel à partir de coordonnées GPS ;
* évaluer conjointement la température, les rafales de vent, et les précipitations ;
* analyser les facteurs climatiques aggravants pour déduire un score, un niveau de danger et une couleur d'alerte spécifique au lieu de l'intervention.

**API utilisée :** Open-Meteo.