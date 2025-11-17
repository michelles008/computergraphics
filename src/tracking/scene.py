# src/tracking/scene.py

def init_tracking():
    """
    Set up webcam + MediaPipe/OpenCV.
    For now, return a dummy context object (e.g., a dict or None).
    """
    # TODO: Replace with actual webcam + pose setup later
    ctx = {"dummy": True}
    return ctx


def get_body_state(ctx):
    """
    Simulated body tracking output for now.

    Returns a dict like:
    {
        "right_hand_y": 0.0–1.0,
        "left_hand_y": 0.0–1.0,
        "x_center": 0.0–1.0
    }
    or None if no body detected.
    """
    # TODO: Replace with real MediaPipe tracking later
    import random
    return {
        "right_hand_y": random.random(),
        "left_hand_y": random.random(),
        "x_center": random.random(),
    }


if __name__ == "__main__":
    ctx = init_tracking()
    while True:
        state = get_body_state(ctx)
        print(state)
