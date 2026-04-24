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

EXIT_SQUARE =  {COLORS[0]: 0, COLORS[1]: 34}

IN_SQUARE= {COLORS[0]: 63, COLORS[1]: 29}

BOARD_SQUARE = 67

HOME_SQUARES = {COLORS[0]: [64, 65, 66, 67], COLORS[1]: [30, 31, 32, 33]}

WIN_SQUARES = {COLORS[0]: 67, COLORS[1]: 33}


# Function to generate random dice rolls
def random_dices(): 
       return randint(1, 6),randint(1, 6)

# Only used during turn order definition phase
first_turn={"draw":set(),"rolls" :0,"dice_value":0,"turn":None}

# You should add more fields to board_state to represent the complete state of the board, such as the position of the pieces, the state of each player, etc. 
# For now, only the players, the current player, the dice value, and the game state are included.
board_state={    
    "players":[],
    "current_player": None,
    "dices_value": (0,0),
    "game_state": GAME_STATES[0], 
    "last_dice": None,
    "dice_value": None
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

    return {
        "message_type": "broadcast",
        "current_player": board_state["current_player"]
    }


# Helper function to check if it's the requesting player's turn
def is_player_turn(player_id):

    global board_state

    if board_state["current_player"]==player_id:
        return True
    return False
   




# =================================================
# DICE LOGIC
# =================================================
# The roll_dice function should handle both the turn order definition phase and the regular game phase.
def roll_dice(player_id):

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

        dice0, dice1 = random_dices()
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

        dice0, dice1 = random_dices()
        board_state["dices_value"] = (dice0, dice1)

        # Detectar presada (dobles)  FALTA VALIDACIÓN ---------------
        is_double = dice0 == dice1

        if is_double is True:
            board_state["current_player"] = player_id  
            
            if board_state["players"][0]["id"] == player_id:
                board_state["players"][0]["pieces"] = [0, 0, 0, 0]
            else:
                board_state["players"][1]["pieces"] = [0, 0, 0, 0]

        
        else:
            # Cambiar turno al otro jugador
            if board_state["players"][0]["id"] == player_id:
                board_state["current_player"] = board_state["players"][1]["id"]
            else:
                board_state["current_player"] = board_state["players"][0]["id"]


        return {
            "message_type": "broadcast",
            "dice": (dice0, dice1),
            "is_double": is_double,
            "current_player": board_state["current_player"]
        }

    # =============================
    # OTROS ESTADOS
    # =============================
    return {
        "message_type": "unicast",
        "error": "El juego no está listo para lanzar dados."
    }
   


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
    pass


def move_piece(player_id, piece_id, cells_to_move):
    """
    Perform movement.
    """
    global board_state

    # Validar turno
    if board_state["current_player"] != player_id:
        return {
            "message_type": "unicast",
            "error": "No es tu turno."
        }

    # Validar dado lanzado
    dice = board_state["last_dice"]
    if dice is None:
        return {
            "message_type": "unicast",
            "error": "Debes lanzar el dado primero."
        }

    # Buscar jugador
    player = None
    for p in board_state["players"]:
        if p["id"] == player_id:
            player = p
            break

    if player is None:
        return {
            "message_type": "unicast",
            "error": "Jugador no encontrado."
        }

    # Buscar ficha
    piece = None
    for pc in player["pieces"]:
        if pc["piece_id"] == piece_id:
            piece = pc
            break

    if piece is None:
        return {
            "message_type": "unicast",
            "error": "Ficha no encontrada."
        }

    # Movimiento simple
    piece["position"] += dice

    # Reiniciar dado
    board_state["last_dice"] = None

    # Cambiar turno
    next_turn()

    return {
        "message_type": "broadcast",
        "player_id": player_id,
        "piece_id": piece_id,
        "new_position": piece["position"],
        "current_player": board_state["current_player"]
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
    pass


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
    pass


def send_piece_home(player_id, piece_id):
    """
    Return a captured piece to jail/start.
    """
    pass


def can_exit_jail(player_id, dice_value):
    """
    Validate if player can leave jail.
    """
    pass


# =================================================
# WIN CONDITION
# =================================================

def has_player_won(player_id):
    """
    Return True if all pieces reached home.
    """
    pass


def check_game_finished():
    """
    Determine if game is over.
    """
    pass


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
    pass


def get_state():
    """
    Return COMPLETE game state.

    You define structure.
    """
    pass