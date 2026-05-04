from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort
import os, time, random

# ── Identifiants des robots (à ajuster selon vos node_ids) ───────────────────
LEADER_ID   = 0
FOLLOWER_ID = 1

# ── Constantes ────────────────────────────────────────────────────────────────
SPEED         = 300
TURN_SPEED    = 200
PROX_ROBOT    = 3000
WAIT_DURATION = 2.0    # Durée d'arrêt du leader (secondes)
MOVE_DURATION = 1.5    # Durée maximale d'un mouvement aléatoire (secondes)

# ── Variable partagée : le suiveur écrit, le leader lit ──────────────────────
follower_prox = 0    # Valeur prox du suiveur, mise à jour à chaque tick

# ── État du leader ────────────────────────────────────────────────────────────
interactions   = 0
is_waiting     = False
wait_until     = 0.0

# ── État explore (partagé par les deux robots) ────────────────────────────────
move_until     = {}   # {node_id: timestamp fin du mouvement courant}
move_action    = {}   # {node_id: 'FORWARD' | 'LEFT' | 'RIGHT'}

done           = False


# ── Gestionnaire d'erreur de communication ────────────────────────────────────
def on_comm_error(error):
    print(error)
    os._exit(1)


# ── Logique EXPLORE commune ───────────────────────────────────────────────────
def explore(th_obj, node_id):
    now = time.time()

    # Tirer un nouveau mouvement si le précédent est terminé
    if now >= move_until.get(node_id, 0):
        move_action[node_id] = random.choice(["FORWARD", "FORWARD", "LEFT", "RIGHT"])
        move_until[node_id]  = now + random.uniform(0.5, MOVE_DURATION)

    action = move_action.get(node_id, "FORWARD")

    if action == "FORWARD":
        th_obj[node_id]["motor.left.target"]  =  SPEED
        th_obj[node_id]["motor.right.target"] =  SPEED
    elif action == "LEFT":
        th_obj[node_id]["motor.left.target"]  = -TURN_SPEED
        th_obj[node_id]["motor.right.target"] =  TURN_SPEED
    elif action == "RIGHT":
        th_obj[node_id]["motor.left.target"]  =  TURN_SPEED
        th_obj[node_id]["motor.right.target"] = -TURN_SPEED


# ── Comportement SUIVEUR ──────────────────────────────────────────────────────
def obs_follower(node_id):

    global done, follower_prox

    if th_follower[node_id]["button.center"]:
        th_follower[node_id]["motor.left.target"]  = 0
        th_follower[node_id]["motor.right.target"] = 0
        done = True
        return

    # Stocker la valeur max des capteurs frontaux du suiveur
    follower_prox = max(th_follower[node_id]["prox.horizontal"])
    print(f"[Suiveur] prox = {follower_prox}")

    explore(th_follower, node_id)


# ── Comportement LEADER ───────────────────────────────────────────────────────
def obs_leader(node_id):
    """
    Explore aléatoirement.
    Lit follower_prox : si > PROX_ROBOT → s'arrête 2 s puis reprend l'exploration.
    """
    global done, interactions, is_waiting, wait_until

    now = time.time()

    if th_leader[node_id]["button.center"]:
        th_leader[node_id]["motor.left.target"]  = 0
        th_leader[node_id]["motor.right.target"] = 0
        done = True
        return

    # Le leader consulte la valeur prox du suiveur
    if follower_prox > PROX_ROBOT and not is_waiting:
        is_waiting    = True
        wait_until    = now + WAIT_DURATION
        interactions += 1


    # État WAIT : immobile
    if is_waiting:
        if now < wait_until:
            th_leader[node_id]["motor.left.target"]  = 0
            th_leader[node_id]["motor.right.target"] = 0
        return

    # État EXPLORE : mouvement aléatoire
    explore(th_leader, node_id)


# ── Connexion — un dongle par robot ───────────────────────────────────────────
thymio_serial_ports = ThymioSerialPort.get_ports()
if len(thymio_serial_ports) < 2:
    os._exit(1)

th_leader = Thymio(use_tcp=False, serial_port=thymio_serial_ports[0].device,
                   refreshing_coverage={"prox.horizontal", "button.center"})
th_leader.on_comm_error = on_comm_error
th_leader.connect()
time.sleep(1)

th_follower = Thymio(use_tcp=False, serial_port=thymio_serial_ports[1].device,
                     refreshing_coverage={"prox.horizontal", "button.center"})
th_follower.on_comm_error = on_comm_error
th_follower.connect()
time.sleep(1)

leader_nid   = th_leader.first_node()
follower_nid = th_follower.first_node()

th_leader.set_variable_observer(leader_nid,     obs_leader)
th_follower.set_variable_observer(follower_nid, obs_follower)


while not done:
    time.sleep(0.1)


th_leader[leader_nid]["motor.left.target"]      = 0
th_leader[leader_nid]["motor.right.target"]     = 0
th_follower[follower_nid]["motor.left.target"]  = 0
th_follower[follower_nid]["motor.right.target"] = 0

th_leader.disconnect()
th_follower.disconnect()
