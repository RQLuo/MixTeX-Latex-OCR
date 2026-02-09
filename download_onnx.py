import requests
import sys
from pathlib import Path


def download_hf_file(repo_id, filename, out_path, revision="main", token=None, use_mirror=True):
    base_urls = []
    if use_mirror:
        base_urls.append("https://hf-mirror.com")
    base_urls.append("https://huggingface.co")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_err = None
    for base in base_urls:
        url = f"{base}/{repo_id}/resolve/{revision}/{filename}"
        try:
            with requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get("Content-Length", 0))
                downloaded = 0
                last_percent = -1
                out_path = Path(out_path)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with out_path.open("wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            if total > 0:
                                downloaded += len(chunk)
                                percent = int(downloaded * 100 / total)
                                if percent != last_percent:
                                    last_percent = percent
                                    sys.stdout.write(f"\r{filename}: {percent}%")
                                    sys.stdout.flush()
                if total > 0:
                    sys.stdout.write("\n")
            print(f"Downloaded: {filename} from {base}")
            return
        except Exception as e:
            last_err = e

    raise RuntimeError(f"Download failed: {filename}") from last_err


def download_mixtex_onnx(out_dir="./mixtex_onnx"):
    repo_id = "wzmmmm/mixtex-onnx"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = [
        "added_tokens.json",
        "config.json",
        "decoder_model.onnx",
        "encoder_model.onnx",
        "generation_config.json",
        "merges.txt",
        "preprocessor_config.json",
        "special_tokens_map.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.json",
    ]

    for filename in files:
        download_hf_file(
            repo_id=repo_id,
            filename=filename,
            out_path=out_dir / filename,
            use_mirror=True,
        )

    # Rename to match MixTeX expected filename
    src = out_dir / "decoder_model.onnx"
    dst = out_dir / "decoder_model_merged.onnx"
    if src.exists():
        src.replace(dst)


if __name__ == "__main__":
    download_mixtex_onnx()
