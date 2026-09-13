<img width="3840" height="2099" alt="red" src="https://github.com/user-attachments/assets/d591199f-9773-4930-934f-ef28f66a6596" />
# Rope RTX 5080 Redone

Windows-focused fork of [Hillobar/Rope](https://github.com/Hillobar/Rope), based on the `Rope-Bronze` branch.

This fork improves RTX 50-series compatibility, restores the practical Pearl-style media layout, adds persistent face-thumbnail caching, modernizes the controls and fixes several Windows stability and usability issues.

## Main changes

- Pearl-style side-by-side **Videos** and **Faces** columns.
- Automatic source-face detection, wider head crops and persistent thumbnail/embedding cache.
- Safer Windows video playback after native `PyNvVideoCodec` crashes.
- Functional audio volume control.
- Clear active states for **Swap Faces** and **Enable Audio**.
- Improved action buttons, tabs, labels, VRAM display and sliders.
- Working JSON file picker for **Load Params**.
- RTX 50-series compatible Python/PyTorch/CUDA dependency stack.

See [CHANGELOG.md](CHANGELOG.md) for details.

## Simple Windows installation

### 1. Requirements

- Windows 10 or 11
- NVIDIA graphics driver installed and up to date
- [Git for Windows](https://git-scm.com/download/win)
- [Python 3.12 (64-bit)](https://www.python.org/downloads/)

During Python installation, enable **Add Python to PATH**.

### 2. Download this fork

Open Command Prompt and run:

```bat
cd /d C:\ai
git clone https://github.com/athor/Rope-RTX-5080-Redone.git "Rope RTX 5080 Redone"
cd /d "C:\ai\Rope RTX 5080 Redone"
```

You may replace `C:\ai` with another folder.

### 3. Create the Python environment

```bat
py -3.12 -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.lock.txt
```

The dependency lock installs the CUDA-enabled PyTorch build required by this branch. A separate CUDA Toolkit installation is normally unnecessary; the NVIDIA driver is still required.

### 4. Install the models

1. Download `models.zip` from this fork's [latest release](https://github.com/athor/Rope-RTX-5080-Redone/releases/latest).
2. Extract it.
3. Put the model files inside:

```text
C:\ai\Rope RTX 5080 Redone\models
```

The folder must directly contain files such as `det_10g.onnx`, `w600k_r50.onnx` and `inswapper_128.fp16.onnx`, not another nested `models` folder.

You can also keep the models elsewhere and select that directory under **Settings → Models Folder**.

### 5. Start Rope

Double-click `Rope.bat`, or run:

```bat
call venv\Scripts\activate.bat
python Rope.py
```

The first face-folder load builds a local cache and can take a little while. Later launches reuse it and are much faster.

## Basic workflow

1. Pick a target video or image in the **Videos** column.
2. Pick the source portraits in the **Faces** column.
3. Click **Find Faces**.
4. Select a detected target face and assign the desired source face.
5. Enable **Swap Faces** and press Play.

## Troubleshooting

### `No module named torch`

Activate the environment and install its dependencies:

```bat
call venv\Scripts\activate.bat
pip install -r requirements.lock.txt
```

### `venv\Scripts\activate.bat` is not recognized

Run the commands from the repository folder, or recreate the environment:

```bat
py -3.12 -m venv venv
```

### Models are missing

Extract the official model archive into `models`, or choose its location under **Settings → Models Folder**.

### First face scan is slow

This is expected while the detector and source-face cache initialize. Subsequent scans and launches should be considerably faster.

## Credits

- Original project: [Hillobar/Rope](https://github.com/Hillobar/Rope)
- This fork keeps the original project history and remains based on Rope-Bronze.

## Disclaimer and responsible use

Use this software only with the necessary rights and consent. Do not create deceptive, defamatory, harmful or non-consensual content. Users are solely responsible for complying with privacy, intellectual-property and other applicable laws. This software is provided without warranty, and its authors or contributors cannot be held responsible for misuse or resulting consequences.
