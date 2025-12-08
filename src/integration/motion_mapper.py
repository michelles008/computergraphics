# src/integration/motion_mapper.py

def body_to_visual(body_state):
    """
    Convert body tracking dict -> visual state dict.

    body_state: dict from get_body_state(), e.g.
        {
            "right_hand_y": 0.0..1.0,
            "left_hand_y":  0.0..1.0,
            "x_center":     0.0..1.0
        }

    Returns visual_state dict for renderer, e.g.:
        {
            "tower_height": ...,
            "side_offset": ...
        }
    """
    if not body_state:
        return None

    # Safe access with defaults in case a key is missing
    #right_y = float(body_state.get("right_hand_y", 0.5))  # 0..1, higher hand = bigger value
    #x_center = float(body_state.get("x_center", 0.5))      # 0..1, center ≈ 0.5
    right_y = float(body_state.get("right_hand_y", 0.0))
    left_y  = float(body_state.get("left_hand_y", 0.0))
    x_center = float(body_state.get("x_center", 0.5))
    # Map right hand height to tower height:
    # hand low (right_y≈0)  -> tall tower
    # hand high (right_y≈1) -> short tower
    #tower_height = 1.0 + (1.0 - right_y) * 3.0  # range ≈ 1.0 .. 4.0
    right_present = right_y > 0.02     
    left_present  = left_y > 0.02

    hand_count = int(right_present) + int(left_present)

    if hand_count == 0:
        return {
            "active": False
        }

    # --- If ONE hand → tower appears but simple behavior only ---
    if hand_count == 1:
        # whichever hand is present controls height
        hand_y = right_y if right_present else left_y

        tower_height = 1.0 + (1.0 - hand_y) * 2.0
        side_offset = (x_center - 0.5) * 2.0

        return {
            "active": True,
            "mode": "one_hand",
            "tower_height": tower_height,
            "side_offset": side_offset,
            "tower_width": 80     # fixed width
        }
    # --- If TWO hands → advanced control (height + width) ---
    if hand_count == 2:
        # height = average hand height
        avg_height = (right_y + left_y) / 2.0

        tower_height = 1.0 + (1.0 - avg_height) * 3.5

        # width based on difference of hands → further apart = wider
        width_factor = abs(right_y - left_y)
        tower_width = 80 + int(width_factor * 200)  # 80 → 280 pixels

        side_offset = (x_center - 0.5) * 2.0

        return {
            "active": True,
            "mode": "two_hands",
            "tower_height": tower_height,
            "side_offset": side_offset,
            "tower_width": tower_width
        }
    # Map horizontal body position to side offset:
    # x_center=0.0 -> -1 (left), 0.5 -> 0, 1.0 -> +1 (right)
    #side_offset = (x_center - 0.5) * 2.0
