from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort
import os, time

global done

# ── Identifiants des robots ───────────────────────────────────────────────────
parano_ID   = 0  # Robot paranoïaque
dirige_ID   = 1  # Robot dirigeant
cyclique_ID = 2  # Robot cyclique

# ── Constantes ────────────────────────────────────────────────────────────────
THRESHOLD  = 2000  # Seuil pour détecter un obstacle
TURN_SPEED = 200   # Vitesse de rotation
SPEED      = 300   # Vitesse de déplacement

done = False  # Variable pour arrêter les robots

# ── Gestionnaire d'erreur de communication ────────────────────────────────────
def on_comm_error(error):
    """Gère les erreurs de communication"""
    print(error)
    os._exit(1)

# ── Observateur pour le robot paranoïaque ─────────────────────────────────────
def obs_parano(node_id):
    """Comportement du robot paranoïaque"""
    global done

    if th_parano[node_id]["button.center"]:  # Si le bouton central est appuyé
        th_parano[node_id]["motor.left.target"] = 0
        th_parano[node_id]["motor.right.target"] = 0
        done = True
        return

    if th_parano[node_id]["button.forward"]:
        port = thymio_serial_ports[0].device
        print(f"[IDENTIFICATION] Perso: PARANOÏAQUE | Port: {port}")
        time.sleep(0.5)

    prox = th_parano[node_id]["prox.horizontal"]

    if max(prox[:5]) < THRESHOLD:  # Aucun obstacle → tourner à gauche
        th_parano[node_id]["motor.left.target"] = -TURN_SPEED
        th_parano[node_id]["motor.right.target"] = TURN_SPEED
    elif max(prox[:5]) > THRESHOLD:  # Obstacle détecté
        gauche = prox[0] + prox[1]
        droite = prox[3] + prox[4]
        # Tourner en fonction de la proximité des obstacles
        if gauche > droite:
            th_parano[node_id]["motor.left.target"] = -TURN_SPEED
            th_parano[node_id]["motor.right.target"] = TURN_SPEED
        else:
            th_parano[node_id]["motor.right.target"] = -TURN_SPEED
            th_parano[node_id]["motor.left.target"] = TURN_SPEED

        th_parano[node_id]["motor.left.target"] = SPEED
        th_parano[node_id]["motor.right.target"] = SPEED

# ── Observateur pour le robot dirigeant ───────────────────────────────────────
def obs_dirige(node_id):
    """Comportement du robot dirigeant"""
    global done

    if th_dirige[node_id]["button.center"]:  # Si le bouton central est appuyé
        th_dirige[node_id]["motor.left.target"] = 0
        th_dirige[node_id]["motor.right.target"] = 0
        done = True
        return
    if th_dirige[node_id]["button.forward"]:
        port = thymio_serial_ports[1].device
        print(f"[IDENTIFICATION] Perso: DIRIGEANT | Port: {port}")
        time.sleep(0.5)

    prox = th_dirige[node_id]["prox.horizontal"]

    if max(prox[:5]) > THRESHOLD:  # Obstacle détecté
        gauche = prox[0] + prox[1]
        droite = prox[3] + prox[4]
        # Tourner en fonction de la proximité des obstacles
        if gauche > droite:
            th_dirige[node_id]["motor.left.target"] = -TURN_SPEED
            th_dirige[node_id]["motor.right.target"] = TURN_SPEED
            th_dirige[node_id]["motor.left.target"] = 150
            th_dirige[node_id]["motor.right.target"] = 150
        else:
            th_dirige[node_id]["motor.left.target"] = TURN_SPEED
            th_dirige[node_id]["motor.right.target"] = -TURN_SPEED
            th_dirige[node_id]["motor.left.target"] = 150
            th_dirige[node_id]["motor.right.target"] = 150
    else:
        th_dirige[node_id]["motor.left.target"] = 0
        th_dirige[node_id]["motor.right.target"] = 0

# ── Observateur pour le robot cyclique ───────────────────────────────────────
def obs_cyclique(node_id):
    """Comportement du robot cyclique"""
    global done

    if th_cyclique[node_id]["button.center"]:  # Si le bouton central est appuyé
        th_cyclique[node_id]["motor.left.target"]  = 0
        th_cyclique[node_id]["motor.right.target"] = 0
        done = True
        return
    if th_cyclique[node_id]["button.forward"]:
        port = thymio_serial_ports[2].device
        print(f"[IDENTIFICATION] Perso: CYCLIQUE | Port: {port}")
        time.sleep(0.5)

    prox = th_cyclique[node_id]["prox.horizontal"]

    if max(prox[:5]) > THRESHOLD:  # Obstacle détecté
        # Étape 1 : Avancer
        th_cyclique[node_id]["motor.left.target"]  = SPEED
        th_cyclique[node_id]["motor.right.target"] = SPEED
        time.sleep(1)

        # Étape 2 : Tourner à gauche
        th_cyclique[node_id]["motor.left.target"]  = -TURN_SPEED
        th_cyclique[node_id]["motor.right.target"] = TURN_SPEED
        time.sleep(1)

        # Étape 3 : Tourner à droite
        th_cyclique[node_id]["motor.left.target"]  = TURN_SPEED
        th_cyclique[node_id]["motor.right.target"] = -TURN_SPEED
        time.sleep(1)

        # Étape 4 : Reculer
        th_cyclique[node_id]["motor.left.target"]  = -SPEED
        th_cyclique[node_id]["motor.right.target"] = -SPEED
        time.sleep(1)

        # Fin du cycle → arrêt
        th_cyclique[node_id]["motor.left.target"]  = 0
        th_cyclique[node_id]["motor.right.target"] = 0
    else:
        th_cyclique[node_id]["motor.left.target"]  = 0
        th_cyclique[node_id]["motor.right.target"] = 0


# ── Connexion — un dongle par robot ───────────────────────────────────────────
thymio_serial_ports = ThymioSerialPort.get_ports()  # Récupérer les ports série
if len(thymio_serial_ports) < 3:  # Vérifier qu'il y a au moins 3 dongles
    print(f"[ERREUR] 3 dongles attendus, {len(thymio_serial_ports)} détecté(s).")
    os._exit(1)

# Connexion des robots via les ports série
th_parano   = Thymio(use_tcp=False, serial_port=thymio_serial_ports[0].device,
                     refreshing_coverage={"prox.horizontal", "button.center", "button.forward"})
th_dirige   = Thymio(use_tcp=False, serial_port=thymio_serial_ports[1].device,
                     refreshing_coverage={"prox.horizontal", "button.center", "button.forward"})
th_cyclique = Thymio(use_tcp=False, serial_port=thymio_serial_ports[2].device,
                     refreshing_coverage={"prox.horizontal", "button.center", "button.forward"})

# Gestion des erreurs de communication
th_parano.on_comm_error   = on_comm_error
th_dirige.on_comm_error   = on_comm_error
th_cyclique.on_comm_error = on_comm_error

# Connexion des robots
th_parano.connect()
th_dirige.connect()
th_cyclique.connect()
time.sleep(1)

# Récupérer l'ID des nœuds des robots
id_parano   = th_parano.first_node()
id_dirige   = th_dirige.first_node()
id_cyclique = th_cyclique.first_node()

# Définir les observateurs de variables pour chaque robot
th_parano.set_variable_observer(id_parano,     obs_parano)
th_dirige.set_variable_observer(id_dirige,     obs_dirige)
th_cyclique.set_variable_observer(id_cyclique, obs_cyclique)

print("[INFO] 3 robots démarrés — bouton central pour arrêter.")

# Boucle d'attente jusqu'à ce que l'utilisateur appuie sur le bouton central
while not done:
    time.sleep(0.1)

# Déconnexion des robots
th_parano.disconnect()
th_dirige.disconnect()
th_cyclique.disconnect()

print("[INFO] Déconnecté.")