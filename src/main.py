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
            result = get_body_state(track_ctx)
            if result is None:
                continue

            body, frame, landmarks = result 

            # 2. Map body -> visual
            visual = body_to_visual(body)
            if visual is None:
                continue

            scene["pose_landmarks"] = landmarks

            visual = body_to_visual(body)
            if visual is None:
                continue

            # 3. add pose landmarks to scene
            scene["pose_landmarks"] = landmarks

            # 4. Apply updates
            apply_visual_state(scene, visual)

            # 5. Render frame (NOW pass landmarks too)
            render_frame(scene, frame, landmarks)

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\n[main] Stopped by user.")
    except Exception as e:
        print(f"[main] Error: {e}")

if __name__ == "__main__":
    main()
