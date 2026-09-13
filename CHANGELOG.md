# Changelog

All notable changes made by the **Rope RTX 5080 Redone** fork are documented here.

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
