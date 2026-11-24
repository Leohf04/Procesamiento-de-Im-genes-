"""Select a bounded BDD100K lane-marking batch for a GitHub-hosted runner."""
import argparse
import json
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--split", choices=("train", "val"), required=True)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=3000)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--files-list", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    if args.offset < 0:
        parser.error("--offset debe ser >= 0")
    if not 1 <= args.limit <= 4000:
        parser.error("--limit debe estar entre 1 y 4000 para respetar el disco del runner")

    frames = json.loads(args.labels.read_text(encoding="utf-8"))
    if not isinstance(frames, list) or not frames:
        raise ValueError("El archivo de anotaciones debe ser una lista JSON no vacía")
    if args.offset >= len(frames):
        raise ValueError(f"offset {args.offset} fuera de rango; el split contiene {len(frames)} frames")

    selected = frames[args.offset:args.offset + args.limit]
    names = []
    for frame in selected:
        name = frame.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("Frame sin nombre válido")
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Ruta de imagen no permitida: {name}")
        names.append(relative.as_posix())
    if len(names) != len(set(names)):
        raise ValueError("El lote contiene nombres de imagen duplicados")

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.files_list.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(selected, ensure_ascii=False), encoding="utf-8")
    args.files_list.write_text("\n".join(names) + "\n", encoding="utf-8")
    manifest = {
        "dataset": "bdd100k_lane_markings",
        "split": args.split,
        "total_frames_in_split": len(frames),
        "offset": args.offset,
        "selected_frames": len(selected),
        "next_offset": args.offset + len(selected),
        "complete": args.offset + len(selected) >= len(frames),
    }
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
