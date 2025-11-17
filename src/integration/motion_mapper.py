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
    right_y = float(body_state.get("right_hand_y", 0.5))  # 0..1, higher hand = bigger value
    x_center = float(body_state.get("x_center", 0.5))      # 0..1, center ≈ 0.5

    # Map right hand height to tower height:
    # hand low (right_y≈0)  -> tall tower
    # hand high (right_y≈1) -> short tower
    tower_height = 1.0 + (1.0 - right_y) * 3.0  # range ≈ 1.0 .. 4.0

    # Map horizontal body position to side offset:
    # x_center=0.0 -> -1 (left), 0.5 -> 0, 1.0 -> +1 (right)
    side_offset = (x_center - 0.5) * 2.0

    return {
        "tower_height": tower_height,
        "side_offset": side_offset,
    }
