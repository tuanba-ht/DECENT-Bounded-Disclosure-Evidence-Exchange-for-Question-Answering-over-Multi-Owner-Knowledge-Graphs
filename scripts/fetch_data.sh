#!/usr/bin/env bash
# Download the RoG releases of WebQSP and CWQ from the Hugging Face Hub.
set -u
base=https://huggingface.co/datasets
fetch() {  # repo file outdir
  local url="$base/$1/resolve/main/$2"
  local out="$3/$(basename "$2")"
  mkdir -p "$3"
  echo "[fetch] $2"
  curl -sL -C - --retry 5 --retry-delay 5 -o "$out" "$url" && echo "  done $(du -h "$out" | cut -f1)"
}
for f in data/test-00000-of-00002-9ee8d68f7d951e1f.parquet data/test-00001-of-00002-773a7b8213e159f5.parquet; do
  fetch rmanluo/RoG-webqsp "$f" data/raw/rog_webqsp/data
done
for f in data/test-00000-of-00003-e62a559c5d2b56ca.parquet data/test-00001-of-00003-2fa9a898639e7d1e.parquet data/test-00002-of-00003-c659cd388440c4ae.parquet; do
  fetch rmanluo/RoG-cwq "$f" data/raw/rog_cwq/data
done
echo "[fetch] done"
