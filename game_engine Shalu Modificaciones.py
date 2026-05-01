import uuid
from random import randint



# game_engine.py
# -------------------------------------------------
# You must implement ALL game logic in this file.
# You must design:
#   - Game state structure
#   - Board representation
#   - Player representation
#   - Turn control
# -------------------------------------------------

# Each function should return a dictionary including a "message_type" field indicating if the message is a "broadcast" (to be sent to all players)
# or a "unicast" (to be sent only to the requesting player), and the relevant data fields for the client(s) to update their state.


# Pieces colors for two players
COLORS=["red","blue"]
# Game states: waiting for players, defining turn order, in progress, finished
GAME_STATES=["waiting_for_players","defining_turn_order","in_progress","finished"]

SAFE_SQUARE = [0, 7, 12, 17, 24,29, 34, 41, 46, 51, 58, 63]

CIRCULAR_TRACK = 64   # 0–63

FINAL_PATH = 70       # meta final

# Function to generate random dice rolls
def random_dices(): 
       return randint(1, 6),randint(1, 6)

# Only used during turn order definition phase
first_turn={"draw":set(),"rolls" :0,"turn":None}

# You should add more fields to board_state to represent the complete state of the board, such as the position of the pieces, the state of each player, etc. 
# For now, only the players, the current player, the dice value, and the game state are included.
board_state={    
    "players":[],
    "current_player": None,
    "dices_value": (0,0),
    "game_state": GAME_STATES[0], 
    "last_dice": None,
    "extra_turn": False,
    "dice_moves": None
}


# =================================================
# PLAYER MANAGEMENT
# =================================================

# Function called when a player joins the game. It should add the player to the game state and assign them a color. 
# If the maximum number of players is reached, it should not add more players.
# If the game is ready to start after this player joins, it should update the game state accordingly.
# The function returns a message with the updated board state to be broadcasted to all players.

def add_player(player_name,playerID):    

    global board_state
      
    if len(board_state["players"])==2:        
         return {"message_type":"broadcast","board_state": board_state}
    
   
    color=COLORS[len(board_state["players"])]
    
    board_state["players"].append({"id":playerID,"name":player_name,"color":color,"pieces":[-1,-1,-1,-1]})

    if len(board_state["players"])==2:
        board_state["game_state"]=GAME_STATES[1]
        board_state["current_player"]=board_state["players"][0]["id"]        
        return {"message_type":"broadcast","board_state": board_state}
    
    return {"message_type":"broadcast","board_state": board_state}


# This function returns the player_id of the requesting player. 
# It can be used by the client to identify itself and know which pieces belong to it, among other things.

def get_my_id(player_id):
    return {"message_type":"unicast","id": player_id}



def get_players():
    """
    Return current players and their states.
    """

    global board_state

    players_info = []
    for player in board_state["players"]:
        players_info.append({
            "name": player["name"],
            "color": player["color"],
            "pieces": player["pieces"]
        })
    
    return { 
        "message_type":"unicast",
        "players" : players_info,
        "current_player": board_state["current_player"],
        "game_state": board_state["game_state"]

    }


# =================================================
# TURN MANAGEMENT
# =================================================

def get_current_player():
    """
    Return player_id whose turn it is.
    """
    global board_state

    if board_state["current_player"] is None:
        return {
            "message_type": "unicast",
            "error": "Aún no hay turno asignado."
        }

    return {
        "message_type": "unicast",
        "current_player": board_state["current_player"],
        "game_state": board_state["game_state"]
    }



def next_turn():
    """
    Advance turn to next eligible player.
    """
    global board_state
 
    if len(board_state["players"]) != 2:
        return {
            "message_type": "unicast",
            "error": "No hay suficientes jugadores para cambiar turno."
        }
 
    if board_state["game_state"] != GAME_STATES[2]:
        return {
            "message_type": "unicast",
            "error": "El juego no está en progreso."
        }
 
    player1_id = board_state["players"][0]["id"]
    player2_id = board_state["players"][1]["id"]
 
    if board_state["current_player"] == player1_id:
        board_state["current_player"] = player2_id
    else:
        board_state["current_player"] = player1_id
 

    board_state["dice_moves"] = None
 
    return {
        "message_type": "broadcast",
        "current_player": board_state["current_player"]
    }


# Helper function to check if it's the requesting player's turn
def is_player_turn(player_id):

    return board_state["current_player"] == player_id
   

# =================================================
# DICE LOGIC
# =================================================
# The roll_dice function should handle both the turn order definition phase and the regular game phase.
def roll_dice(player_id, force_values= None):
 
    global board_state
    global first_turn
 
    # Validar que el jugador exista
    player_ids = [p["id"] for p in board_state["players"]]
    if player_id not in player_ids:
        return {
            "message_type": "unicast",
            "error": "Jugador no válido."
        }
 
    # =============================
    # FASE 1: DEFINIR PRIMER TURNO
    # =============================
    if board_state["game_state"] == GAME_STATES[1]:
 
        if not is_player_turn(player_id):
            return {
                "message_type": "unicast",
                "error": "No es tu turno para lanzar."
            }
 
        dice0, dice1 = random_dices() if force_values is None else force_values
        first_turn["rolls"] += 1
 
        # Comparar con el valor anterior
        if dice0 > board_state["dices_value"][0]:
            first_turn["draw"].clear()
            first_turn["draw"].add(player_id)
            first_turn["turn"] = player_id
 
        elif dice0 == board_state["dices_value"][0]:
            first_turn["draw"].add(player_id)
 
        # Guardar dados actuales
        board_state["dices_value"] = (dice0, dice1)
 
        # Cambiar turno temporal para que lance el otro jugador
        if board_state["players"][0]["id"] == player_id:
            board_state["current_player"] = board_state["players"][1]["id"]
        else:
            board_state["current_player"] = board_state["players"][0]["id"]
 
        # Si ambos ya lanzaron
        if first_turn["rolls"] == 2:
 
            # Si no hay empate
            if len(first_turn["draw"]) == 1:
                board_state["current_player"] = first_turn["turn"]
                board_state["game_state"] = GAME_STATES[2]
 
            # Si hay empate → reiniciar proceso
            else:
                first_turn["rolls"] = 0
                first_turn["turn"] = None
                first_turn["draw"] = set()
                board_state["current_player"] = board_state["players"][0]["id"]
 
        return {
            "message_type": "broadcast",
            "dice": board_state["dices_value"],
            "current_player": board_state["current_player"],
            "game_state": board_state["game_state"]
        }
 
    # =============================
    # FASE 2: JUEGO NORMAL
    # =============================
    if board_state["game_state"] == GAME_STATES[2]:
 
        if not is_player_turn(player_id):
            return {
                "message_type": "unicast",
                "error": "No es tu turno."
            }
 
        dice0, dice1 = random_dices() if force_values is None else force_values
 

        player = None
        for p in board_state["players"]:
            if p["id"] == player_id:
                player = p
 
        if player is None:
            return {
                "message_type": "unicast",
                "error": "Jugador no encontrado."
            }
 
        board_state["dices_value"] = (dice0, dice1)
 
        board_state["dice_moves"] = {
            "d1": dice0,
            "d2": dice1,
            "sum": dice0 + dice1,
            "used_d1": False,
            "used_d2": False,
            "used_sum": False
            }
        
        board_state["last_dice"] = dice0 + dice1
 
        # Detectar presada (dobles)  
        is_double = dice0 == dice1
 
        if not can_exit_jail(player_id, is_double):
            next_turn()
            return {
                "message_type": "broadcast",
                "dice": (dice0, dice1),
                "is_double": is_double,
                "current_player": board_state["current_player"]
            }
 
        if is_double is True:
            for p in board_state["players"]:
                if p["id"] == player_id:
                    for i in range(len(p["pieces"])):
                        if p["pieces"][i] == -1:
                            p["pieces"][i] = 0
            
            board_state["extra_turn"] = True
 
        else:
            board_state["extra_turn"] = False


        return {
            "message_type": "broadcast",
            "dice": (dice0, dice1),
            "is_double": is_double,
            "pieces": player["pieces"], 
            "current_player": board_state["current_player"]
        }
 
    return {"message_type": "unicast", "error": "El juego no está en curso."}
   

def get_last_dice():
    """
    Return last rolled dice value.
    """
    global board_state

    return {
        "message_type": "unicast",
        "dice": board_state["dices_value"]
    }


# =================================================
# PIECE MANAGEMENT
# =================================================

def get_player_pieces(player_id):
    """
    Return all pieces of player and their positions.
    """
    global board_state

    for player in board_state["players"]:
        if player["id"] == player_id:
            return {
                "message_type": "unicast",
                "pieces": player["pieces"]
            }


    return {
        "message_type": "unicast",
        "error": "Jugador no encontrado"
    }



def can_piece_move(player_id, piece_id, dice_value):
    """
    Validate if selected piece can move.

    Must check:
    - Piece in jail
    - Dice allows exit
    - Movement does not exceed home
    - Blockades
    """
    global board_state

    for player in board_state["players"]:
        if player["id"] == player_id:

            pos_actual = player["pieces"][piece_id]

            if pos_actual == -1:
                return False

            if pos_actual + dice_value > FINAL_PATH:
                return False

            return True

    return False


def move_piece(player_id, piece_id, cells_to_move):
    global board_state

    if not is_player_turn(player_id):
        return {"message_type": "unicast", "error": "No es tu turno."}

    moves = board_state.get("dice_moves")
    if moves is None:
        return {"message_type": "unicast", "error": "Debes lanzar los dados primero."}

    idx = int(piece_id)
    cells_to_move = int(cells_to_move)

    if idx < 0 or idx >= 4:
        return {"message_type": "unicast", "error": "Ficha inválida."}

    p_actual = None
    for p in board_state["players"]:
        if p["id"] == player_id:
            p_actual = p

    if p_actual is None:
        return {"message_type": "unicast", "error": "Jugador no encontrado."}


    move_type = None

    if cells_to_move == moves["d1"] and not moves["used_d1"]:
        move_type = "d1"

    elif cells_to_move == moves["d2"] and not moves["used_d2"]:
        move_type = "d2"

    elif cells_to_move == moves["sum"] and not moves["used_sum"]:
        move_type = "sum"

    if move_type is None:
        return {
            "message_type": "unicast",
            "error": f"Movimiento no válido. Opciones: {moves['d1']}, {moves['d2']} o {moves['sum']}"
        }


    if not can_piece_move(player_id, idx, cells_to_move):

        if board_state.get("extra_turn"):
            return {
                "message_type": "broadcast",
                "message": "No puedes mover esta ficha, pero tienes otro intento por par.",
                "current_player": board_state["current_player"]
            }

        board_state["extra_turn"] = False

    # =================================================
    # 8. CONSUMIR EL DADO (CORREGIDO)
    # =================================================
    if move_type == "d1":
        moves["used_d1"] = True
        # Eliminamos: moves["used_sum"] = True 

    elif move_type == "d2":
        moves["used_d2"] = True
        # Eliminamos: moves["used_sum"] = True 

    elif move_type == "sum":
        moves["used_sum"] = True
        moves["used_d1"] = True
        moves["used_d2"] = True

    # =================================================
    # 9. MOVER FICHA
    # =================================================
    p_actual["pieces"][idx] += cells_to_move
    nueva_pos = p_actual["pieces"][idx]

    # =================================================
    # 10. POSICIÓN REAL
    # =================================================
    mi_pos_real = nueva_pos

    if player_id == board_state["players"][1]["id"]:
        mi_pos_real = (nueva_pos + 34) % CIRCULAR_TRACK

    # =================================================
    # 11. CAPTURA
    # =================================================
    if nueva_pos < CIRCULAR_TRACK and not is_safe_square(mi_pos_real):

        rival_id, rival_piece_idx = check_capture(player_id, mi_pos_real)

        if rival_id is not None:
            send_piece_home(rival_id, rival_piece_idx)

    # =================================================
    # 12. VICTORIA
    # =================================================
    if has_player_won(player_id):
        board_state["game_state"] = GAME_STATES[3]

        return {
            "message_type": "broadcast",
            "winner": player_id,
            "board_state": board_state
        }

    # =================================================
    # 13. CONTROL DE FIN DE TURNO (REVISADO)
    # =================================================
    
    # El turno solo termina si se gastaron AMBOS dados o la SUMA
    # Verificamos que d1 Y d2 sean True, o que sum sea True
    turn_finished = moves["used_sum"] or (moves["used_d1"] and moves["used_d2"])

    if turn_finished:
        if board_state.get("extra_turn"):
            # Si hubo dobles, reseteamos dados pero NO pasamos turno
            board_state["dice_moves"] = None
            board_state["extra_turn"] = False
        else:
            # Solo aquí pasamos al siguiente jugador
            next_turn()

    # =================================================
    # 14. RESPUESTA
    # =================================================
    return {
        "message_type": "broadcast",
        "players": board_state["players"],
        "current_player": board_state["current_player"],
        "dice_moves": moves
    }


# =================================================
# BOARD LOGIC
# =================================================

def get_board():
    """
    Return full board representation.
    """
    global board_state

    board_view = []

    for player in board_state["players"]:
        board_view.append({
            "player": player["name"],
            "color": player["color"],
            "pieces": player["pieces"]
        })

    return {
        "message_type": "unicast",
        "board": board_view,
        "current_player": board_state["current_player"]
    }





def is_safe_square(position):
    """
    Return True if square is safe.
    """
    if position in SAFE_SQUARE:
        return True
    return False


def detect_blockade(position):
    """
    Return True if position contains a blockade.
    """
    pass


# =================================================
# CAPTURE & RULES
# =================================================

def check_capture(player_id, position):
    """
    Determine if a capture occurs.
    """
    for opponent in board_state["players"]:
        if opponent["id"] != player_id:

            for i in range(len(opponent["pieces"])):

                pos_rel = opponent["pieces"][i]

                # Ignorar piezas fuera del tablero
                if pos_rel < 0 or pos_rel >= CIRCULAR_TRACK:
                    continue

                pos_real = pos_rel

                if opponent["id"] == board_state["players"][1]["id"]:
                    pos_real = (pos_rel + 34) % CIRCULAR_TRACK

                if position == pos_real:
                    return opponent["id"], i

    return None, None


def send_piece_home(player_id, piece_id):
    """
    Return a captured piece to jail/start.
    """
    global board_state

    for player in board_state["players"]:
        if player["id"] == player_id:
            player["pieces"][piece_id] = -1
            return True

    return False


def can_exit_jail(player_id, is_double):
    """
    Valida si el jugador puede salir de la cárcel o seguir jugando.
    """
    global board_state

    for player in board_state["players"]:
        if player["id"] == player_id:

            all_in_jail = True
            for piece in player["pieces"]:
                if piece != -1:
                    all_in_jail = False

            if all_in_jail == True:
                if is_double == True:
                    return True 
                else:
                    return False 
            else:
                return True

    return False


# =================================================
# WIN CONDITION
# =================================================

def has_player_won(player_id):
    """
    Return True if all pieces reached home.
    """
    for player in board_state["players"]:
        if player["id"] == player_id:
            # Comparamos si la lista de piezas es exactamente [70, 70, 70, 70]
            if player["pieces"] == [70, 70, 70, 70]:
                return True
    return False


def check_game_finished():
    """
    Determine if game is over.
    """

    global board_state
    for player in board_state["players"]:
        if has_player_won(player["id"]):
            board_state["game_state"] = GAME_STATES[3] 
            return True
    return False


# =================================================
# GAME STATE
# =================================================

def get_game_status():
    """
    Return:
    - waiting_for_players
    - in_progress
    - finished
    """
    global board_state
    return {
        "message_type": "unicast",
        "game_state": board_state["game_state"]
    }


def get_state():
    """
    Return COMPLETE game state.

    You define structure.
    """
    global board_state
    return {
        "message_type": "unicast",
        "board_state": board_state
    }
