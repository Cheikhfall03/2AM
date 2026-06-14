"""Boucle principale: caméra → YOLO → distance → annonce vocale.

Utilisation:
    python main.py                # mode webcam temps réel
    python main.py --source img.jpg
    python main.py --no-display   # désactive la fenêtre OpenCV (mode embarqué)
"""

import argparse
import sys
import time

import cv2

from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    ALERT_DISTANCE_M,
    FR_LABELS,
)
from detector import ObstacleDetector
from distance import estimate_distance, horizontal_position
from narrator import Narrator, describe


def draw_overlay(frame, det, distance_m, position):
    label_fr = FR_LABELS.get(det.label, det.label)
    color = (0, 0, 255) if (distance_m and distance_m < 1.5) else (0, 200, 0)
    cv2.rectangle(frame, (det.x1, det.y1), (det.x2, det.y2), color, 2)
    txt = f"{label_fr} {position}"
    if distance_m is not None:
        txt += f" {distance_m:.1f}m"
    cv2.putText(
        frame, txt, (det.x1, max(20, det.y1 - 8)),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
    )


def pick_priority(detections, frame_w):
    """Sélectionne l'obstacle le plus pertinent: le plus proche dans la zone alerte."""
    best = None
    best_dist = float("inf")
    for det in detections:
        d = estimate_distance(det.label, det.height)
        if d is None or d > ALERT_DISTANCE_M:
            continue
        if d < best_dist:
            best = (det, d, horizontal_position(det.cx, frame_w))
            best_dist = d
    return best


def run(source, display: bool):
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if not cap.isOpened():
        print(f"Impossible d'ouvrir la source: {source}", file=sys.stderr)
        return 1

    detector = ObstacleDetector()
    narrator = Narrator()
    print("Prototype lancé. Ctrl+C pour quitter.")

    frame_count = 0
    t0 = time.monotonic()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            detections = detector.detect(frame)
            chosen = pick_priority(detections, frame.shape[1])

            if chosen:
                det, dist, pos = chosen
                phrase = describe(det.label, dist, pos)
                narrator.announce(det.label, phrase)

            if display:
                for det in detections:
                    d = estimate_distance(det.label, det.height)
                    pos = horizontal_position(det.cx, frame.shape[1])
                    draw_overlay(frame, det, d, pos)
                cv2.imshow("Detection d'obstacles - prototype", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            frame_count += 1
            if frame_count % 30 == 0:
                fps = frame_count / (time.monotonic() - t0)
                print(f"FPS moyen: {fps:.1f} | détections: {len(detections)}")
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        if display:
            cv2.destroyAllWindows()
        narrator.shutdown()
    return 0


def main():
    parser = argparse.ArgumentParser(description="Prototype détection d'obstacles")
    parser.add_argument(
        "--source", default=None,
        help="Chemin vidéo/image, ou index caméra (def: caméra config.py)",
    )
    parser.add_argument(
        "--no-display", action="store_true",
        help="Désactive l'affichage OpenCV (mode embarqué/headless)",
    )
    args = parser.parse_args()

    if args.source is None:
        source = CAMERA_INDEX
    elif args.source.isdigit():
        source = int(args.source)
    else:
        source = args.source

    sys.exit(run(source, display=not args.no_display))


if __name__ == "__main__":
    main()
