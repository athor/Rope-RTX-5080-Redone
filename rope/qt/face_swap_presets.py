"""Conservative rendering presets; scheduling and recognition settings stay untouched."""

_COMMON = {
    "LikenessSlider": 100,
    "EmbExtrapSlider": 0,
    "HighFidelityAlphaSlider": 50,
    "HighFidelityModeTextSel": "Cached",
    "StrengthSwitch": False,
    "StrengthSlider": 100,
    "BorderTopSlider": 10,
    "BorderSidesSlider": 10,
    "BorderBottomSlider": 10,
    "ColorMatchSwitch": True,
    "ColorSwitch": False,
    "ColorRedSlider": 0,
    "ColorGreenSlider": 0,
    "ColorBlueSlider": 0,
    "ColorGammaSlider": 1,
    "ColorContrastSlider": 1,
    "ColorSaturationSlider": 1,
    "DiffSwitch": False,
    "DiffSlider": 4,
    "OccluderSlider": 0,
    "DFLXSegSwitch": False,
    "DFLXSegSizeSlider": 0,
    "DFLXSegBlurSlider": 0,
    "FaceParserSlider": 0,
    "MouthParserSlider": 0,
    "RestorerTypeTextSel": "GFPGAN",
    "RestorerDetTypeTextSel": "Blend",
}

FACE_SWAP_PRESETS = {
    "low": {
        **_COMMON,
        "SwapperTypeTextSel": "128",
        "HighFidelitySwitch": False,
        "BorderBlurSlider": 10,
        "BlendSlider": 5,
        "OccluderSwitch": False,
        "FaceParserSwitch": False,
        "RestorerSwitch": False,
        "RestorerSlider": 25,
    },
    "high": {
        **_COMMON,
        "SwapperTypeTextSel": "256",
        "HighFidelitySwitch": True,
        "BorderBlurSlider": 12,
        "BlendSlider": 8,
        "OccluderSwitch": True,
        "FaceParserSwitch": True,
        # A low restoration blend limits changes to identity and expression.
        "RestorerSwitch": True,
        "RestorerSlider": 25,
    },
}

HIGH_REQUIRED_MODELS = ("occluder.onnx", "faceparser_resnet34.onnx", "GFPGANv1.4.onnx")


def matching_preset(values: dict) -> str | None:
    for name, preset in FACE_SWAP_PRESETS.items():
        if all(values.get(key) == value for key, value in preset.items()):
            return name
    return None
