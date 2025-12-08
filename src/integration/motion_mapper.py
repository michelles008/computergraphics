# src/integration/motion_mapper.py

def body_to_visual(body_state):
    if not body_state:
        return None

    right_y = float(body_state.get("right_hand_y", 0.0))
    left_y  = float(body_state.get("left_hand_y", 0.0))
    right_x = float(body_state.get("right_hand_x", 0.5))
    left_x  = float(body_state.get("left_hand_x", 0.5))
    x_center = float(body_state.get("x_center", 0.5))

    right_present = right_y > 0.05
    left_present  = left_y > 0.05

    hand_count = int(right_present) + int(left_present)

    if hand_count == 0:
        return {"active": False}

    if hand_count == 1:
        hand_y = right_y if right_present else left_y

        tower_height = 1.0 + hand_y * 2.0

        side_offset = (x_center - 0.5) * 2.0

        return {
            "active": True,
            "mode": "one_hand",
            "tower_height": tower_height,
            "side_offset": side_offset,
            "tower_width": 80     
        }

 
    if hand_count == 2:

        avg_height = (right_y + left_y) / 2.0
        tower_height = 1.0 + avg_height * 3.5

        dist = abs(right_x - left_x)
        tower_width = 80 + int(dist * 300)

        side_offset = (x_center - 0.5) * 2.0

        return {
            "active": True,
            "mode": "two_hands",
            "tower_height": tower_height,
            "side_offset": side_offset,
            "tower_width": tower_width
        }
