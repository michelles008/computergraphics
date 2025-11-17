# src/main.py
#
# Connects:
#   tracking.scene      -> get_body_state()
#   integration.mapping -> body_to_visual()
#   renderer            -> apply_visual_state() + render_frame()

from tracking.scene import init_tracking, get_body_state
from integration.motion_mapper import body_to_visual
from renderer import init_scene, apply_visual_state, render_frame
import time

def main():
    # Start tracking + graphics
    track_ctx = init_tracking(preview=False)  
    scene = init_scene()                   

    print("[main] Starting loop. Ctrl+C to quit.")

    try:
        while True:
            # 1. Read body state from camera
            body = get_body_state(track_ctx)
            if body is None:
                # No pose detected this frame; skip but keep loop alive
                continue

            # 2. Map body -> visual
            visual = body_to_visual(body)
            if visual is None:
                continue

            # 3. Apply visual state to scene
            apply_visual_state(scene, visual)

            # 4. Draw one frame
            render_frame(scene)

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\n[main] Stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"[main] Error: {e}")


if __name__ == "__main__":
    main()
