
# Thymio Multi-Personality Project

Ce projet met en œuvre trois robots **Thymio II** fonctionnant simultanément, chacun possédant une "personnalité" distincte codée en Python. Les robots interagissent avec leur environnement en utilisant leurs capteurs de proximité pour adopter des comportements sociaux ou réactifs spécifiques.

## Méthode Multi-Robot : La gestion simultanée

L'originalité de ce projet réside dans la gestion de plusieurs robots sur un seul script Python. Voici comment cela fonctionne :

1.  **Instanciation par port série :** Au lieu d'une connexion globale, nous créons trois objets `Thymio` distincts. Chaque objet est lié à un dongle USB spécifique détecté dans la liste `ThymioSerialPort.get_ports()`.
2.  **Observateurs de variables (`Variable Observers`) :** Pour éviter que le script ne reste "bloqué" sur un robot pendant que les autres attendent, nous utilisons des fonctions *callback*. Dès que les capteurs d'un robot changent, sa fonction dédiée (`obs_parano`, `obs_dirige`, etc.) est appelée de manière asynchrone.
3.  **Filtrage des données :** Chaque instance ne rafraîchit que les variables nécessaires (`prox.horizontal` et `button.center`) pour optimiser la bande passante de la communication sans fil.

---

## Les Personnalités

Chaque robot possède une logique de décision unique basée sur les relevés des 5 capteurs de proximité avant.

### 1. Le Paranoïaque (`obs_parano`)
*   **Logique :** Il a "peur" du vide. S'il ne détecte rien, il tourne sur lui-même frénétiquement pour scanner son environnement.
*   **Réaction :** Dès qu'un obstacle entre dans son champ de vision (`THRESHOLD > 2000`), il charge droit devant lui.

### 2. Le Dirigeant (`obs_dirige`)
*   **Logique :** Il est le guide. Il reste immobile tant qu'il n'y a pas d'interaction.
*   **Réaction :** Lorsqu'un obstacle (ou un autre robot) s'approche, il effectue un évitement intelligent : il calcule si l'obstacle est plus proche à gauche ou à droite et pivote dans la direction opposée avant d'avancer légèrement.

### 3. Le Cyclique (`obs_cyclique`)
*   **Logique :** Un comportement répétitif et prévisible (déterministe).
*   **Réaction :** Dès qu'il détecte un obstacle, il déclenche une routine immuable de 4 étapes :
    1. Avance pendant 1s.
    2. Pivote à gauche pendant 1s.
    3. Pivote à droite pendant 1s.
    4. Recule pendant 1s.


## Exercices réalisés dans ce projet

Pour compléter ton projet Git, voici une section supplémentaire à ajouter à ton **README.md**. Elle détaille les exercices fondamentaux que tu as réalisés : la **mesure de distance physique**, la **gestion des priorités** et le **pilotage des LEDs via l'assembleur**.

---

## Exercices de Base & Apprentissages

Avant de passer au système multi-robot, plusieurs concepts clés ont été maîtrisés à travers des exercices spécifiques :

### 1. Conversion des Capteurs en Distance Réelle
Les capteurs `prox.horizontal` du Thymio renvoient des valeurs brutes. Un des exercices a consisté à convertir ces valeurs en **centimètres** pour obtenir une mesure physique exploitable.
*   **Formule utilisée :** $distance = \frac{14000}{prox\_value}$
*   **Logique :** Plus la valeur du capteur est élevée, plus l'objet est proche. Cette formule permet de déclencher des alertes de sécurité (ex: avertissement sous les 10 cm).

### 2. Gestion des Priorités de Contrôle
Pour éviter que le robot ne reçoive des ordres contradictoires, nous avons implémenté une hiérarchie de commandes dans la fonction `obs()` :
1.  **Sécurité Totale :** Le bouton **Central** coupe les moteurs et arrête le script immédiatement.
2.  **Commandes Manuelles :** Les boutons **Avant** et **Arrière** ont la priorité sur les comportements automatiques.
3.  **Comportement Automatique :** Si aucun bouton n'est pressé, le robot suit sa logique de personnalité.

### 3. Contrôle Avancé des LEDs (Assembleur ASEBA)
Pour changer la couleur des LEDs du dessus (RGB), nous avons utilisé une méthode avancée en injectant du code **Assembleur** directement dans le processeur du Thymio via la fonction `run_asm`.
*   Cela permet de créer des signaux visuels personnalisés (ex: Rouge pour le Paranoïaque, Vert pour le Dirigé).
*   **Fonction dédiée :** `set_leds(th, id, R, G, B)` où les valeurs vont de 0 à 32.

---

### Note technique
*Le script attend exactement 3 robots. Si vous souhaitez en utiliser moins ou plus, modifiez la vérification de longueur de `thymio_serial_ports` au début du fichier.*