from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort
import os, time

global done


# Fonction de gestion d'erreur de communication
def on_comm_error(error):
    print(error)
    os._exit(1)  # Sortie forcée en cas d'erreur de communication


def obs(node_id):

    global done

    SPEED            = 200   # Vitesse de croisière
    TURN_SPEED       = 150   # Vitesse de virage
    GROUND_THRESHOLD = 300   # Seuil sol : valeur < seuil → noir (absorbant)
                             # Valeur > seuil → blanc (réfléchissant)
                             # Calibrer entre 200 et 400 selon votre surface

    # Arrêt sur bouton central du robot
    if th[node_id]["button.center"]:
        th[node_id]["motor.left.target"]  = 0
        th[node_id]["motor.right.target"] = 0
        done = True  # Arrêter le robot et sortir de la boucle principale
        return

    # Lecture des capteurs de sol [gauche, droite]
    ground = th[node_id]["prox.ground.delta"]
    left_on_black  = ground[0] > GROUND_THRESHOLD
    right_on_black = ground[1] > GROUND_THRESHOLD

    # Affichage des valeurs sol pour calibration (optionnel)
    print(f"Sol G={ground[0]:4d}  D={ground[1]:4d}  "
          f"-> {'NOIR-G' if left_on_black else '     '} "
          f"{'NOIR-D' if right_on_black else '     '}")

    # Suivi de ligne
    if left_on_black and right_on_black:
        # Les deux capteurs sur la ligne : avancer tout droit
        th[node_id]["motor.left.target"]  =  SPEED
        th[node_id]["motor.right.target"] =  SPEED
    elif left_on_black:
        # Ligne détectée à gauche : corriger en tournant à gauche
        th[node_id]["motor.left.target"]  = -TURN_SPEED
        th[node_id]["motor.right.target"] =  TURN_SPEED
    elif right_on_black:
        # Ligne détectée à droite : corriger en tournant à droite
        th[node_id]["motor.left.target"]  =  TURN_SPEED
        th[node_id]["motor.right.target"] = -TURN_SPEED
    else:
        # Aucun capteur ne voit du noir : avancer tout droit
        th[node_id]["motor.left.target"]  =  SPEED
        th[node_id]["motor.right.target"] =  SPEED


# ── Détection du port et connexion au robot ──────────────────────────────────
thymio_serial_ports = ThymioSerialPort.get_ports()  # Recherche des ports série disponibles
serial_port = thymio_serial_ports[0].device         # Sélection du premier port disponible
th = Thymio(use_tcp=False, serial_port=serial_port,
            refreshing_coverage={"prox.ground.delta", "button.center"})  # Connexion au robot
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