from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort
import os, time

global done

# ── Identifiants des robots (à ajuster selon vos node_ids) ───────────────────
parano_ID   = 0
dirige_ID = 1
cyclique_ID = 2
THRESHOLD = 2000
TURN_SPEED   = 200
SPEED = 300

# Fonction de gestion d'erreur de communication
def on_comm_error(error):
    print(error)
    os._exit(1)  # Sortie forcée en cas d'erreur de communication


def obs_parano(node_id):

    global done

    if th_parano[node_id]["button.center"]:
        th_parano[node_id]["motor.left.target"] = 0
        th_parano[node_id]["motor.right.target"] = 0
        done = True
        return

    prox = th_parano[node_id]["prox.horizontal"]

    if max(prox[:5]) < THRESHOLD:  # Aucun obstacle → tourner à gauche
        th_parano[node_id]["motor.left.target"] = -TURN_SPEED
        th_parano[node_id]["motor.right.target"] = TURN_SPEED


    elif max(prox[:5]) > THRESHOLD:
        gauche = prox[0] + prox[1]
        droite = prox[3] + prox[4]
        if gauche > droite:
            th_parano[node_id]["motor.left.target"] = -TURN_SPEED
            th_parano[node_id]["motor.right.target"] = TURN_SPEED
        else:
            th_parano[node_id]["motor.right.target"] = -TURN_SPEED
            th_parano[node_id]["motor.left.target"] = TURN_SPEED

        th_parano[node_id]["motor.left.target"] = SPEED
        th_parano[node_id]["motor.right.target"] = SPEED

def obs_dirige(node_id):

    global done

    if th_dirige[node_id]["button.center"]:
        th_dirige[node_id]["motor.left.target"] = 0
        th_dirige[node_id]["motor.right.target"] = 0
        done = True
        return

    prox = th_dirige[node_id]["prox.horizontal"]

    if max(prox[:5]) > THRESHOLD:
        gauche = prox[0] + prox[1]
        droite = prox[3] + prox[4]
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


thymio_serial_ports = ThymioSerialPort.get_ports()
serial_port = thymio_serial_ports[0].device
serial_port_2 = thymio_serial_ports[1].device


th_parano = Thymio(use_tcp=False, serial_port=serial_port,
                   refreshing_coverage={"prox.horizontal", "button.center"})
th_dirige = Thymio(use_tcp=False, serial_port=serial_port_2,
                   refreshing_coverage={"prox.horizontal", "button.center"})
th_parano.on_comm_error = on_comm_error
th_dirige.on_comm_error = on_comm_error
th_parano.connect()
th_dirige.connect()
time.sleep(1)

id_parano = th_parano.first_node()
id_dirige = th_dirige.first_node()
th_parano.set_variable_observer(id_parano, obs_parano)
th_dirige.set_variable_observer(id_dirige, obs_dirige)

print("[INFO] Paranoïaque démarré — bouton central pour arrêter.")

while not done:
    time.sleep(0.1)

th_parano.disconnect()
th_dirige.disconnect()
print("[INFO] Déconnecté.")



