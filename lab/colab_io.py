"""Browser I/O for Colab: the microphone and the audio players. The only module that uses google.colab."""

import base64
import json
import uuid

_RECORD_JS = r"""
async function vclRecord(maxSeconds, label) {
  const box = document.createElement('div');
  box.style.cssText = 'font-family:sans-serif;padding:12px;border:1px solid #888;border-radius:8px;max-width:520px';
  const status = document.createElement('div');
  status.style.cssText = 'font-size:18px;margin-bottom:8px';
  const start = document.createElement('button');
  start.textContent = 'Start opname';
  const stop = document.createElement('button');
  stop.textContent = 'Stop';
  stop.disabled = true;
  for (const b of [start, stop]) b.style.cssText = 'font-size:16px;padding:6px 16px;margin-right:8px';
  status.textContent = label + ' Klik op Start als je klaar bent.';
  box.append(status, start, stop);
  document.body.appendChild(box);

  await new Promise(resolve => start.onclick = resolve);
  start.disabled = true;
  let stream;
  try {
    // Browser voice processing (noise suppression, AGC) muffles the voice the model copies.
    stream = await navigator.mediaDevices.getUserMedia({audio: {
      echoCancellation: false, noiseSuppression: false, autoGainControl: false, channelCount: 1}});
  } catch (e) {
    status.textContent = 'Geen toegang tot de microfoon: ' + e.message;
    return JSON.stringify({error: 'mic: ' + e.message});
  }
  for (let n = 3; n > 0; n--) {
    status.textContent = 'Opname begint over ' + n + '...';
    await new Promise(r => setTimeout(r, 1000));
  }
  let recorder;
  try {
    recorder = new MediaRecorder(stream, {audioBitsPerSecond: 128000});
  } catch (e) {
    recorder = new MediaRecorder(stream);
  }
  const chunks = [];
  recorder.ondataavailable = e => chunks.push(e.data);
  const done = new Promise(resolve => recorder.onstop = resolve);
  recorder.start();
  stop.disabled = false;
  const t0 = Date.now();
  const timer = setInterval(() => {
    const s = Math.floor((Date.now() - t0) / 1000);
    status.textContent = '\u{1F534} Opname loopt: ' + s + ' / ' + maxSeconds + ' s';
    if (s >= maxSeconds && recorder.state === 'recording') recorder.stop();
  }, 200);
  stop.onclick = () => { if (recorder.state === 'recording') recorder.stop(); };
  await done;
  clearInterval(timer);
  stream.getTracks().forEach(t => t.stop());
  stop.disabled = true;
  status.textContent = 'Opname klaar, bezig met verwerken...';
  const blob = new Blob(chunks, {type: recorder.mimeType});
  const buf = new Uint8Array(await blob.arrayBuffer());
  let bin = '';
  for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
  box.remove();
  return JSON.stringify({mime: recorder.mimeType, data: btoa(bin)});
}
"""


_AUDIO_JS = """
<script>
(async () => {
  const el = document.getElementById(%(id)s);
  try {
    const r = await google.colab.kernel.invokeFunction(%(callback)s, [%(rel)s], {});
    const d = r.data['application/json'];
    if (d.error) throw new Error(d.error);
    const bin = atob(d.data);
    const buf = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    el.src = URL.createObjectURL(new Blob([buf], {type: 'audio/wav'}));
  } catch (e) {
    const msg = document.createElement('span');
    msg.textContent = 'Audio niet beschikbaar (runtime gestopt of gewist).';
    el.replaceWith(msg);
  }
})();
</script>
"""


def in_colab():
    try:
        import google.colab  # noqa: F401
        return True
    except ImportError:
        return False


def record(max_seconds, label):
    """Record from the browser microphone; returns the raw encoded bytes (webm, mp4 or wav)."""
    from google.colab import output
    js = _RECORD_JS + f"vclRecord({int(max_seconds)}, {json.dumps(label)})"
    result = json.loads(output.eval_js(js, timeout_sec=max_seconds + 600))
    if "error" in result:
        raise RuntimeError(result["error"])
    return base64.b64decode(result["data"])


def register_callback(name, func):
    """Let JavaScript in an output call func through google.colab.kernel.invokeFunction."""
    from google.colab import output
    output.register_callback(name, func)


def download(path):
    from google.colab import files
    files.download(str(path))


def delete_runtime():
    from google.colab import runtime
    runtime.unassign()


def kernel_audio_tag(callback, rel):
    """An audio player that asks the kernel callback for its clip when it is displayed."""
    el_id = f"vcl-{uuid.uuid4().hex}"
    js = _AUDIO_JS % {"id": json.dumps(el_id), "callback": json.dumps(callback), "rel": json.dumps(rel)}
    return f'<audio controls id="{el_id}"></audio>{js}'
