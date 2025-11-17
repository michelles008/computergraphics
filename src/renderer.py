# src/renderer.py

class Scene:
    """Simple container for render state."""
    def __init__(self):
        self.tower_height = 1.0   # how tall the tower is


def init_scene():
    """
    For now, we create and return a Scene object.
    Later we'll add real OpenGL setup here.
    """
    scene = Scene()
    return scene


def apply_visual_state(scene, visual_state):
    if visual_state is None:
        return

    # default to 1.0 if the key isn't there
    scene.tower_height = float(visual_state.get("tower_height", 1.0))


def render_frame(scene):
    """
    For now, we print the tower height.
    Later this will draw the actual cube/tower with OpenGL.
    """
    print(f"[RENDER] tower height = {scene.tower_height:.2f}")


if __name__ == "__main__":
    # quick test
    s = init_scene()
    for h in [1.0, 1.5, 2.0, 3.0]:
        apply_visual_state(s, {"tower_height": h})
        render_frame(s)
