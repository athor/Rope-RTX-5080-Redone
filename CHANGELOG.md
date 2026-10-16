# Changelog

All notable changes made by the **Rope RTX 5080 Redone** fork are documented here.

## 1.0.1 - 2026-10-16

### Media controls and selection

- Replaced Save Image with Delete Image and Delete Video, placed after the volume control.
- Delete Image acts on selected source portraits in Faces; Delete Video acts on the selected video in Videos.
- Require confirmation, with Cancel as the default, and move files to the Windows Recycle Bin. A failed recycle operation never falls back to permanent deletion.
- Release the active video decoder and finish outstanding processing before moving its file. Refuse deletion during recording and keep files when release fails.
- Remove deleted portraits from the list, in-memory embedding cache and affected face assignments; ignore late indexing results for removed portraits.
- Added a neon green selection border that remains visible without focus. Assigned source faces retain a separate inner gold border.

### Audio and launch

- Enable audio by default and initialize both the volume slider and playback gain to 50%.
- Make Rope.bat start from its own directory and use the project's local Python environment, including paths containing spaces.

### Face-swap rendering presets

- Added Auto Low and Auto High immediately after Delete Video, separated by a vertical divider.
- Auto Low uses 128-resolution swapping, automatic color matching and simple borders, without additional restoration or neural masks.
- Auto High uses 256-resolution swapping, cached High Fidelity correction at 50%, automatic color matching, occlusion/background masks and a 25% GFPGAN restoration blend.
- Presets preserve worker count, model-session mode, detection, recognition threshold, recording settings and source-face assignments. High adds processing work and can run more slowly.
- Apply each preset as one complete parameter update, reset cached fidelity corrections, and highlight the matching preset. Manual rendering adjustments clear the highlight when values no longer match.
- Refuse preset changes during recording and check required High models before applying settings. Presets remain editable and can be persisted with Save Params.
- These are conservative rendering presets, not automatic analysis or a guarantee of an optimal result for every video.

### CPU usage

- Replace the Coordinator's continuously running zero-interval telemetry timer with a 50 ms timer, and disable it when no backend is attached.
- Keep video processing, frame delivery and playhead updates independent of telemetry; GPU inference and image quality are unchanged.
- In an isolated Coordinator probe, the old timer consumed approximately one CPU core; the sampled timer reduced that overhead to near zero while receiving all test frames. This is not a full-application power measurement or a claim of higher face-swap FPS.

### Repository and validation

- Exclude local archives, backups, generated validation logs and personal tuning profiles from version control.
- Added regression tests for safe deletion, decoder release/reload, rendering presets, selection borders and telemetry-independent frame delivery.
- Passed all 18 targeted regression tests, the existing parameter-schema/roundtrip smoke tests, Python compilation checks and Git whitespace checks before publication.
- Model files and runtime dependency versions are unchanged from v1.0.0; existing installations can keep their current models and environment.

## 1.0.0 - 2026-09-13

### GPU and runtime compatibility

- Updated the working environment to Python 3.12 with CUDA-enabled PyTorch 2.11 and CUDA 12.8 wheels for RTX 50-series support.
- Kept ONNX Runtime GPU execution available for detection, recognition and swapping.
- Bypassed the native PyNvVideoCodec path on Windows after confirmed process-level `0xc0000094` crashes; PyAV provides the stable fallback while face processing remains on CUDA.

### Source-face workflow

- Restored the Pearl-style side-by-side Videos and Faces layout.
- Added automatic source-face detection and embedding generation.
- Added persistent on-disk caching for source-face thumbnails and embeddings.
- Fixed atomic `.npz` cache writes and added safe cache versioning.
- Replaced tight aligned-face thumbnails with wider square head crops.
- Made face indexing asynchronous to keep the Qt interface responsive.

### Interface

- Prevented the left media panels from collapsing accidentally.
- Added two-line filenames for video and face tiles.
- Reordered the main actions to: Find Faces, Swap Faces, Clear Faces, Enable Audio, Volume, Save Image.
- Added visible button surfaces, click feedback and active styling for Swap Faces and Enable Audio.
- Restyled the Parameters and Settings tabs for the dark interface.
- Restyled sliders with a dark capsule track and metallic rectangular handle.
- Added a subtle illuminated handle marker when a slider differs from its default value.
- Fixed VRAM conversion from MiB to GiB and prevented text clipping.

### Audio

- Added a functional 0–100% playback-volume slider.
- Added dynamic mute, low-volume and high-volume icons.
- Applied gain in the audio callback without altering source media.

### Parameters

- Fixed Load Params so it opens a JSON file picker.
- Added validation and a warning for invalid parameter profiles.

### Validation

- Compiled all changed Python modules.
- Ran headless Qt smoke tests for layout, controls and parameter loading.
- Verified source-face cache reads and writes.
- Decoded the first frame of 32 local videos after the Windows decoder fallback change with zero failures.
