# ai/env.py

from game.score_tracker import update_score, get_score
from ai.ghosts        import update_ghosts

# History for backtracking (same as before)
_prev_pos  = None
_prev2_pos = None

def step_environment(graph,
                     new_pacman_pos,
                     ghost_positions,
                     food_positions,
                     super_fruit_pos,
                     ghost_hunter,
                     hunter_timer,
                     HUNTER_DURATION=50):
    """
    One timestep:
     - applies all update_score(...) calls internally
     - returns ( ... , done, reward)
    """

    global _prev_pos, _prev2_pos

    # Remember score before any events
    old_score = get_score()

    done = False

    # 0) back-and-forth penalty
    if _prev2_pos is not None and new_pacman_pos == _prev2_pos:
        update_score("backtrack")

    # shift history
    _prev2_pos = _prev_pos
    _prev_pos  = new_pacman_pos

    # 1) step penalty
    update_score("step")

    # 2) move Pac-Man
    pacman_pos = new_pacman_pos

    # 3) food pellet
    if pacman_pos in food_positions:
        food_positions.remove(pacman_pos)
        update_score("food")

    # 4) super-fruit
    if super_fruit_pos is not None and pacman_pos == super_fruit_pos:
        super_fruit_pos = None
        update_score("super_fruit")
        ghost_hunter = True
        hunter_timer = HUNTER_DURATION

    # 5) hunter countdown
    if ghost_hunter:
        hunter_timer -= 1
        if hunter_timer <= 0:
            ghost_hunter = False

    # 6) move ghosts
    ghost_positions = update_ghosts(graph, pacman_pos, ghost_hunter)

    # 7) collision
    if pacman_pos in ghost_positions:
        if ghost_hunter:
            update_score("ghost_eaten")
        else:
            update_score("collision")
            done = True

    # 8) level-complete
    if not food_positions:
        done = True

    # compute how much score changed this step
    new_score = get_score()
    reward    = new_score - old_score

    return (
        pacman_pos,
        ghost_positions,
        food_positions,
        super_fruit_pos,
        ghost_hunter,
        hunter_timer,
        done,
        reward
    )
