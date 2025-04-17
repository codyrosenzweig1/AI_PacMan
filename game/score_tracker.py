# Initialise global score
score = 0

def reset_score():
    """
    Resets the global score to zero at the start of a new episode or game.
    """
    global score
    score = 0

def update_score(event):
    """
    Updates the global score based on an event.
    
    Parameters:
        event (str): The event type. Expected values are:
                     "food", "super_fruit", "ghost_eaten", "collision", "step".
    
    Returns:
        The updated score.
    """
    global score
    if event == "food":
        score += 10
    elif event == "super_fruit":
        score += 50
    elif event == "ghost_eaten":
        score += 200
    elif event == "collision":
        score -= 500
    elif event == "step":
        score -= 1  # Penalize each move to discourage wandering or osilation
    
    return score

def get_score():
    """
    Returns the current score.
    """
    return score