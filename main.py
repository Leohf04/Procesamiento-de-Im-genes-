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
    parser = argparse.ArgumentParser(
        description="Detección y segmentación semántica en escenas urbanas"
    )
    parser.add_argument("--source", type=str, default="0", help="Ruta de video o índice de cámara")
    parser.add_argument("--approach", choices=["instance", "hybrid"], default="instance")
    parser.add_argument("--backend", choices=["auto", "torch", "onnx_cv2"], default="auto")
    parser.add_argument("--config", type=str, default="configs/config.yaml")
    parser.add_argument("--save-video", type=str, default=None)
    parser.add_argument("--save-samples", action="store_true")
    parser.add_argument("--scenario", default="clear_day")
    parser.add_argument("--no-gui", action="store_true")
    parser.add_argument("--max-frames", type=int, default=200)
    return parser.parse_args()


def process_video_source(pipeline, source, gui: bool = True, max_frames: int = 200):
    if isinstance(source, str) and source.isdigit():
        source = int(source)

    if isinstance(source, str) and not os.path.exists(source):
        raise FileNotFoundError(f"La fuente '{source}' no existe.")

    return pipeline.process_video_stream(
        source=source, output_video_path=None, max_frames=max_frames
    )


def main():
    args = parse_args()
    config = load_config(args.config)
    set_global_seed(config.get("system", {}).get("seed", 42))
    backend = resolve_backend(args.backend)

    print(f"Backend activo: {backend}")
    if backend == "onnx_cv2":
        print("Modo demo ligero (Android/Termux): HOG peatones + carriles HSV.")

    pipeline = UrbanPerceptionPipeline(
        approach=args.approach,
        config_path=args.config,
        backend=backend,
    )

    source = args.source
    is_video = not (isinstance(source, str) and source.isdigit())

    if is_video and os.path.isfile(source):
        ext = os.path.splitext(source)[1].lower()
        if ext in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
            image = cv2.imread(source)
            if image is None:
                raise RuntimeError(f"No se pudo leer la imagen '{source}'.")

            if args.scenario != "clear_day":
                evaluator = ScenarioEvaluator(pipeline.model, config)
                image = evaluator.apply_scenario(image, args.scenario)
                print(f"Escenario aplicado: {args.scenario}")

            start = time.perf_counter()
            prediction = pipeline.run_frame(image)
            elapsed = time.perf_counter() - start
            output = render_predictions(
                image, prediction, 1.0 / elapsed if elapsed > 0 else 0.0
            )

            if args.save_video:
                cv2.imwrite(args.save_video, output)
                print(f"Resultado guardado en {args.save_video}")

            if args.save_samples:
                output_dir = config.get("evaluation", {}).get(
                    "output_dir", "data/outputs"
                )
                pred_boxes = (
                    np.asarray(prediction["boxes"])
                    if prediction.get("boxes") is not None
                    else np.zeros((0, 4), dtype=np.float32)
                )
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

    stats = process_video_source(
        pipeline, source, gui=False, max_frames=args.max_frames
    )
    print(f"Frames procesados: {stats['frames_written']}")
    print(f"FPS promedio: {stats['fps']:.2f}")


if __name__ == "__main__":
    main()
