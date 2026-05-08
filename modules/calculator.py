"""
modules/calculator.py — Core calculation logic for Microscope Specimen Size Calculator
"""

# Microscope types with their magnification factors
MICROSCOPE_TYPES = {
    "Light Microscope": 40,
    "Electron Microscope": 1000,
    "Stereo Microscope": 20,
    "Digital Microscope": 200,
}

# Unit conversion factors to millimetres (base unit)
UNIT_TO_MM = {
    "nm":  1e-6,
    "µm":  1e-3,
    "mm":  1.0,
    "cm":  10.0,
    "m":   1000.0,
}

MM_TO_UNIT = {k: 1 / v for k, v in UNIT_TO_MM.items()}

UNIT_LABELS = list(UNIT_TO_MM.keys())


def calculate_real_size(
    measured_size: float,
    microscope_type: str,
    input_unit: str,
    output_unit: str,
) -> dict:
    """
    Calculate the real-life specimen size.

    Returns a dict with all intermediate values and the final result.
    """
    magnification = MICROSCOPE_TYPES[microscope_type]

    # Convert measured size to mm
    measured_in_mm = measured_size * UNIT_TO_MM[input_unit]

    # Apply formula
    real_size_mm = measured_in_mm / magnification

    # Convert to desired output unit
    real_size_output = real_size_mm * MM_TO_UNIT[output_unit]

    return {
        "microscope_type": microscope_type,
        "magnification": magnification,
        "measured_size": measured_size,
        "input_unit": input_unit,
        "measured_size_mm": measured_in_mm,
        "real_size_mm": real_size_mm,
        "real_size": real_size_output,
        "output_unit": output_unit,
    }


def format_scientific(value: float) -> str:
    """Return a human-friendly scientific notation string."""
    if value == 0:
        return "0"
    if 1e-4 <= abs(value) < 1e6:
        return f"{value:.6g}"
    return f"{value:.4e}"


def build_explanation(result: dict) -> list[str]:
    """Build a step-by-step explanation list."""
    steps = [
        f"**Step 1** — Identify the magnification factor for a *{result['microscope_type']}*: "
        f"**{result['magnification']}×**",

        f"**Step 2** — Convert the measured size to millimetres:  \n"
        f"`{format_scientific(result['measured_size'])} {result['input_unit']}` × "
        f"`{UNIT_TO_MM[result['input_unit']]}` = "
        f"`{format_scientific(result['measured_size_mm'])} mm`",

        f"**Step 3** — Apply the core formula:  \n"
        f"Real Size = Measured Size ÷ Magnification  \n"
        f"`{format_scientific(result['measured_size_mm'])} mm` ÷ "
        f"`{result['magnification']}` = "
        f"`{format_scientific(result['real_size_mm'])} mm`",

        f"**Step 4** — Convert result to the chosen output unit ({result['output_unit']}):  \n"
        f"`{format_scientific(result['real_size_mm'])} mm` × "
        f"`{MM_TO_UNIT[result['output_unit']]}` = "
        f"**`{format_scientific(result['real_size'])} {result['output_unit']}`**",
    ]
    return steps
