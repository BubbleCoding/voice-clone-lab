#!/usr/bin/env bash
# Install the lab on a Colab runtime without replacing Colab's own torch, torchaudio and numpy.
# Model weights download in the background while pip runs.
# VCL_FULL_INSTALL=1 uses Chatterbox's own pins instead (fallback; needs a runtime restart).
set -euo pipefail
cd "$(dirname "$0")/.."

# V3 multilingual is on GitHub but not yet in the PyPI release (0.1.7 only has V2).
CHATTERBOX="chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox@5de7a54aa4e5e2baadb0182dde554908b48b85c2"

python - <<'PY' > /tmp/vcl_prefetch.log 2>&1 &
from huggingface_hub import snapshot_download
snapshot_download("ResembleAI/chatterbox", allow_patterns=[
    "ve.pt", "t3_mtl23ls_v2.safetensors", "s3gen.pt", "grapheme_mtl_merged_expanded_v1.json",
    "conds.pt", "Cangjie5_TC.json"])
snapshot_download("mo-thecreator/Deepfake-audio-detection",
                  allow_patterns=["config.json", "model.safetensors", "preprocessor_config.json"])
PY
PREFETCH=$!

if [[ "${VCL_FULL_INSTALL:-0}" == "1" ]]; then
  pip install -q "$CHATTERBOX" || pip install -q chatterbox-tts==0.1.7
  pip install -q -r requirements-colab.txt
  echo "Volledige installatie klaar. Kies Runtime → Sessie opnieuw starten en voer de setupcel opnieuw uit."
else
  pip install -q --no-deps "$CHATTERBOX" || pip install -q --no-deps chatterbox-tts==0.1.7
  pip install -q -r requirements-colab.txt
fi

wait "$PREFETCH" || echo "Model prefetch failed; models download on first load instead (see /tmp/vcl_prefetch.log)."
echo "Installatie klaar."
