import argparse
import os
import time

import cv2
import numpy as np

from src.evaluation.error_analysis import save_failure_case
from src.evaluation.trainer import ScenarioEvaluator
from src.pipeline import UrbanPerceptionPipeline
from src.utils.config_utils import load_config, resolve_backend, set_global_seed
from src.utils.visualization import render_predictions


def parse_args():
    parser = argparse.ArgumentParser(description="Detección y segmentación semántica en escenas urbanas")
    parser.add_argument("--source", type=str, default="0", help="Ruta de video o índice de cámara")
    parser.add_argument("--approach", choices=["instance", "hybrid"], default="instance")
    parser.add_argument("--backend", choices=["auto", "torch", "onnx", "onnx_cv2"], default="auto")
    parser.add_argument("--config", type=str, default="configs/config.yaml")
    parser.add_argument("--save-video", type=str, default=None, help="Ruta del video de salida (solo fuentes de video/cámara)")
    parser.add_argument("--save-image", type=str, default=None, help="Ruta para guardar el resultado cuando la fuente es una imagen")
    parser.add_argument("--save-samples", action="store_true")
    parser.add_argument("--scenario", default="clear_day")
    parser.add_argument("--no-gui", action="store_true")
    parser.add_argument("--max-frames", type=int, default=200)
    return parser.parse_args()


def process_video_source(pipeline, source, gui: bool = True, max_frames: int = 200, output_video_path: str | None = None):
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    if isinstance(source, str) and not os.path.exists(source):
        raise FileNotFoundError(f"La fuente '{source}' no existe.")
    return pipeline.process_video_stream(source=source, output_video_path=output_video_path, max_frames=max_frames)


def main():
    args = parse_args()
    config = load_config(args.config)
    set_global_seed(config.get("system", {}).get("seed", 42))
    backend = resolve_backend(args.backend)
    print(f"Backend activo: {backend}")
    if backend == "onnx_cv2":
        print("Backend clásico OpenCV/HOG (modo demo; no es ONNX).")
    elif backend == "onnx":
        print("ONNX Runtime: segmentación semántica; no incluye detección de instancias.")

    pipeline = UrbanPerceptionPipeline(approach=args.approach, config_path=args.config, backend=backend)
    source = args.source
    is_camera = isinstance(source, str) and source.isdigit()
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    is_image = not is_camera and os.path.isfile(source) and os.path.splitext(source)[1].lower() in image_extensions

    if is_image:
        image = cv2.imread(source)
        if image is None:
            raise RuntimeError(f"No se pudo leer la imagen '{source}'.")
        if args.scenario != "clear_day":
            image = ScenarioEvaluator(pipeline.model, config).apply_scenario(image, args.scenario)
        start = time.perf_counter()
        prediction = pipeline.run_frame(image)
        elapsed = time.perf_counter() - start
        output = render_predictions(image, prediction, 1.0 / elapsed if elapsed > 0 else 0.0)
        if args.save_image:
            os.makedirs(os.path.dirname(args.save_image) or ".", exist_ok=True)
            if not cv2.imwrite(args.save_image, output):
                raise RuntimeError(f"No se pudo guardar la imagen '{args.save_image}'.")
            print(f"Imagen guardada en {args.save_image}")
        if args.save_video:
            raise ValueError("--save-video requiere una fuente de video o cámara; usa --save-image para imágenes.")
        if args.save_samples:
            output_dir = config.get("evaluation", {}).get("output_dir", "data/outputs")
            pred_boxes = np.asarray(prediction.get("boxes", []), dtype=np.float32).reshape(-1, 4)
            save_failure_case(
                image,
                np.zeros((0, 4), dtype=np.float32),
                pred_boxes,
                np.asarray(prediction.get("scores", [])),
                os.path.join(output_dir, "failure_case_sample.png"),
            )
        if not args.no_gui:
            cv2.imshow("Urban Perception", output)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return

    stats = process_video_source(pipeline, source, gui=not args.no_gui, max_frames=args.max_frames, output_video_path=args.save_video)
    print(f"Frames procesados: {stats['frames_written']}")
    print(f"FPS promedio (pipeline completo por frame): {stats['fps']:.2f}")


if __name__ == "__main__":
    main()
