def _clamp01(value):
    return 0.0 if value < 0.0 else 1.0 if value > 1.0 else value


def body_to_visual(body_state):
    if not body_state:
        return None

    # Extract values safely
    right_y = _clamp01(float(body_state.get("right_hand_y", 0.0)))
    left_y  = _clamp01(float(body_state.get("left_hand_y", 0.0)))
    right_x = _clamp01(float(body_state.get("right_hand_x", 0.5)))
    left_x  = _clamp01(float(body_state.get("left_hand_x", 0.5)))
    x_center = _clamp01(float(body_state.get("x_center", 0.5)))

    # Hand present if lifted “enough”
    right_present = right_y > 0.05
    left_present  = left_y > 0.05
    hand_count = int(right_present) + int(left_present)

    # 👉 Godzilla is active whenever AT LEAST ONE hand is up
    godzilla_active = hand_count >= 1

    # ---------------------------
    # 0 HANDS → NO TOWER
    #    (but we still pass godzilla flag just in case)
    # ---------------------------
    if hand_count == 0:
        return {
            "active": False,
            "godzilla_active": godzilla_active
        }

    # ---------------------------
    # ONE HAND MODE
    # ---------------------------
    if hand_count == 1:
        hand_y = right_y if right_present else left_y

        # height grows as hand goes UP
        height_norm = _clamp01(hand_y)
        side_offset = (x_center - 0.5) * 2.0

        return {
            "active": True,
            "mode": "one_hand",
            "tower_height": height_norm,
            "side_offset": side_offset,
            # keep a thin, constant width when only one hand is visible
            "tower_width": 0.25,
            "godzilla_active": godzilla_active
        }

    # ---------------------------
    # TWO HAND MODE
    # ---------------------------
    if hand_count == 2:
        avg_height = (right_y + left_y) / 2.0
        height_norm = _clamp01(avg_height)

        dist = abs(right_x - left_x)
        width_norm = _clamp01(dist)

        side_offset = (x_center - 0.5) * 2.0

        return {
            "active": True,
            "mode": "two_hands",
            "tower_height": height_norm,
            "side_offset": side_offset,
            "tower_width": width_norm,
            "godzilla_active": godzilla_active
        }
