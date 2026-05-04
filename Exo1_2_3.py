from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort
import os, time

global done


# Fonction de gestion d'erreur de communication
def on_comm_error(error):
    print(error)
    os._exit(1)  # Sortie forcée en cas d'erreur de communication


def obs(node_id):
    """
    Appelé automatiquement à chaque rafraîchissement des variables Thymio.
    Priorité : bouton central > clavier > évitement > avancer.
    """
    global done
    SPEED = 500  # Vitesse du robot

    # Lire le capteur frontal central (prox.horizontal[2])
    prox_value = th[node_id]["prox.horizontal"][2]

    # Calcul de la distance approximative en cm
    if prox_value != 0:  # On évite la division par zéro
        distance = 14000 / prox_value
    else:
        distance = float('inf')  # Si le capteur ne détecte rien, distance infinie

    # Afficher la distance pour le débogage (optionnel)
    print(f"Distance au capteur central : {distance:.2f} cm")

    # Afficher un avertissement si la distance est inférieure à 10 cm
    if distance < 10:
        print("AVERTISSEMENT : Distance trop courte, danger imminent !")

    # Arrêt sur bouton central du robot
    if th[node_id]["button.center"]:
        th[node_id]["motor.left.target"] = 0
        th[node_id]["motor.right.target"] = 0
        done = True  # Arrêter le robot et sortir de la boucle principale
        return

    prox = th[node_id]["prox.horizontal"]  # Lecture des autres capteurs de proximité

    # Priorité 1 : commande via boutons avant et arrière
    if th[node_id]["button.forward"]:
        th[node_id]["motor.left.target"] = th[node_id]["motor.right.target"] = SPEED
    elif th[node_id]["button.backward"]:
        th[node_id]["motor.left.target"] = th[node_id]["motor.right.target"] = -SPEED

# ── Détection du port et connexion au robot ─────────────────────────────────────────
thymio_serial_ports = ThymioSerialPort.get_ports()  # Recherche des ports série disponibles
serial_port = thymio_serial_ports[0].device  # Sélection du premier port disponible
th = Thymio(use_tcp=False, serial_port=serial_port,
            refreshing_coverage={"prox.horizontal", "button.center", "button.forward", "button.backward"})  # Connexion au robot
th.on_comm_error = on_comm_error  # Assignation du gestionnaire d'erreurs
th.connect()
id = th.first_node()  # Récupération du node_id du premier robot
done = False

# Enregistrement de l'observateur pour surveiller les variables
th.set_variable_observer(id, obs)

# Boucle principale pour attendre que l'arrêt soit effectué
while not done:
    time.sleep(0.1)

th.disconnect()  # Déconnexion du robot


# Fonction pour contrôler les LEDs
def set_leds(th, id, R, G, B):
    src = """
    dc end_toc ; taille table événements
    dc _ev.init, init ; init event handler
    end_toc:
    init: ; exécuté au démarrage
    push.s 0 ; initialiser compteur
    store counter
    push.s """
    src2 = """ store _userdata
    push.s _userdata push.s """
    src3 = """ store _userdata+1
    push.s _userdata+1 push.s """
    src4 = """ store _userdata+2
    push.s _userdata+2 callnat _nf."""
    src5 = """ stop
    counter: equ _userdata+3 """

    # Lancer le code assembleur pour changer la couleur des LEDs
    th.run_asm(id, src + str(B) + src2 + str(G) + src3 + str(R) + src4 + "leds.top" + src5)


# Exemple d'utilisation de la fonction set_leds pour allumer des LEDs
set_leds(th, id, 32, 0, 0)  # LED rouge (R=32, G=0, B=0)
time.sleep(1)  # Attendre 1 seconde
set_leds(th, id, 0, 32, 0)  # LED verte
time.sleep(1)  # Attendre 1 seconde
set_leds(th, id, 0, 0, 0)  # LED éteinte