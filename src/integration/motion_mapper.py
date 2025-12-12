_prev_grips = {"left": 1.0, "right": 1.0}


def _clamp01(value):
    return 0.0 if value < 0.0 else 1.0 if value > 1.0 else value


def _smooth_grip(side: str, value: float, inertia: float = 0.7) -> float:
    prev = _prev_grips.get(side, value)
    smoothed = prev * inertia + value * (1.0 - inertia)
    _prev_grips[side] = smoothed
    return smoothed


def body_to_visual(body_state):
    if not body_state:
        return None

    # Extract values safely
    right_y = _clamp01(float(body_state.get("right_hand_y", 0.0)))
    left_y  = _clamp01(float(body_state.get("left_hand_y", 0.0)))
    right_x = _clamp01(float(body_state.get("right_hand_x", 0.5)))
    left_x  = _clamp01(float(body_state.get("left_hand_x", 0.5)))
    x_center = _clamp01(float(body_state.get("x_center", 0.5)))
    right_grip = _smooth_grip("right", _clamp01(float(body_state.get("right_grip", 1.0))))
    left_grip = _smooth_grip("left", _clamp01(float(body_state.get("left_grip", 1.0))))

    # Hand present if lifted “enough”
    right_present = right_y > 0.05
    left_present  = left_y > 0.05
    hand_count = int(right_present) + int(left_present)

    # 👉 Godzilla is active whenever AT LEAST ONE hand is up
    godzilla_active = hand_count >= 1

    clenched_threshold = 0.55
    right_clenched = right_present and right_grip < clenched_threshold
    left_clenched = left_present and left_grip < clenched_threshold
    break_trigger = hand_count == 2 and right_clenched and left_clenched

    grip_debug = {
        "left": round(left_grip, 3),
        "right": round(right_grip, 3),
    }

    # ---------------------------
    # 0 HANDS → NO TOWER
    #    (but we still pass godzilla flag just in case)
    # ---------------------------
    if hand_count == 0:
        result = {
            "active": False,
            "godzilla_active": godzilla_active,
            "break_trigger": False,
            "grip_debug": grip_debug,
        }
        return result

    # ---------------------------
    # ONE HAND MODE
    # ---------------------------
    if hand_count == 1:
        hand_y = right_y if right_present else left_y

        # height grows as hand goes UP
        height_norm = _clamp01(hand_y)
        side_offset = (x_center - 0.5) * 2.0

        result = {
            "active": True,
            "mode": "one_hand",
            "tower_height": height_norm,
            "side_offset": side_offset,
            "tower_width": 0.25,
            "godzilla_active": godzilla_active,
            "grip_debug": grip_debug,
        }
        result["break_trigger"] = False
        return result

    # ---------------------------
    # TWO HAND MODE
    # ---------------------------
    if hand_count == 2:
        avg_height = (right_y + left_y) / 2.0
        height_norm = _clamp01(avg_height)

        dist = abs(right_x - left_x)
        width_norm = _clamp01(dist)

        side_offset = (x_center - 0.5) * 2.0

        result = {
            "active": True,
            "mode": "two_hands",
            "tower_height": height_norm,
            "side_offset": side_offset,
            "tower_width": width_norm,
            "godzilla_active": godzilla_active,
            "grip_debug": grip_debug,
        }
        result["break_trigger"] = break_trigger
        return result
