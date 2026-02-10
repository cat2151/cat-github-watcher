"""
ANSI color codes and colorization functions for terminal output
"""

import re

DEFAULT_COLOR_SCHEME = "monokai"
SUPPORTED_COLOR_KEYS = ("phase1", "phase2", "phase3", "llm", "url")

_COLOR_SCHEMES = {
    # Monokai-inspired palette
    "monokai": {
        "phase1": "\033[38;2;230;219;116m",  # yellow
        "phase2": "\033[38;2;102;217;239m",  # cyan/blue
        "phase3": "\033[38;2;166;226;46m",  # green
        "llm": "\033[38;2;249;38;114m",  # pink
        "url": "\033[38;2;121;193;255m",  # soft blue
    },
    # Legacy palette (pre-Monokai)
    "classic": {
        "phase1": "\033[93m",
        "phase2": "\033[96m",
        "phase3": "\033[92m",
        "llm": "\033[95m",
        "url": "\033[94m",
    },
}


def _hex_to_ansi(color_hex: str, color_name: str) -> str:
    match = re.fullmatch(r"#?([0-9a-fA-F]{6})", color_hex.strip())
    if not match:
        raise ValueError(
            f"Invalid color code for '{color_name}': '{color_hex}'. "
            "Use 6-digit hex like #RRGGBB or an ANSI escape code."
        )

    hex_value = match.group(1)
    red = int(hex_value[0:2], 16)
    green = int(hex_value[2:4], 16)
    blue = int(hex_value[4:6], 16)
    return f"\033[38;2;{red};{green};{blue}m"


def normalize_color_code(color_code: str, color_name: str) -> str:
    if not isinstance(color_code, str):
        raise ValueError(
            f"Color '{color_name}' must be a string (hex like #RRGGBB or ANSI code), "
            f"got {type(color_code).__name__}: {color_code}"
        )

    if "\x1b[" in color_code or "\033[" in color_code:
        return color_code
    return _hex_to_ansi(color_code, color_name)


def apply_custom_colors(custom_palette: dict[str, str]) -> dict[str, str]:
    """Override the active palette with custom color codes."""
    if not isinstance(custom_palette, dict):
        raise ValueError("Custom colors must be provided as a table/dictionary.")

    normalized_palette: dict[str, str] = {}
    for key in SUPPORTED_COLOR_KEYS:
        if key not in custom_palette:
            continue
        normalized_palette[key] = normalize_color_code(custom_palette[key], key)

    if not normalized_palette:
        return {}

    Colors.YELLOW = normalized_palette.get("phase1", Colors.YELLOW)
    Colors.CYAN = normalized_palette.get("phase2", Colors.CYAN)
    Colors.GREEN = normalized_palette.get("phase3", Colors.GREEN)
    Colors.MAGENTA = normalized_palette.get("llm", Colors.MAGENTA)
    Colors.BLUE = normalized_palette.get("url", Colors.BLUE)
    return normalized_palette


class Colors:
    """ANSI color codes for terminal output"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = _COLOR_SCHEMES[DEFAULT_COLOR_SCHEME]["phase3"]
    YELLOW = _COLOR_SCHEMES[DEFAULT_COLOR_SCHEME]["phase1"]
    CYAN = _COLOR_SCHEMES[DEFAULT_COLOR_SCHEME]["phase2"]
    MAGENTA = _COLOR_SCHEMES[DEFAULT_COLOR_SCHEME]["llm"]
    RED = "\033[91m"
    BLUE = _COLOR_SCHEMES[DEFAULT_COLOR_SCHEME]["url"]


def colorize_phase(phase: str, llm_progress: str | None = None) -> str:
    """Add color to phase string

    Args:
        phase: Phase string (phase1, phase2, phase3, or LLM working)
        llm_progress: Progress label to prepend for LLM working (optional)

    Returns:
        Colorized phase string with ANSI codes
    """
    if phase == "phase1":
        return f"{Colors.BOLD}{Colors.YELLOW}[{phase}]{Colors.RESET}"
    elif phase == "phase2":
        return f"{Colors.BOLD}{Colors.CYAN}[{phase}]{Colors.RESET}"
    elif phase == "phase3":
        return f"{Colors.BOLD}{Colors.GREEN}[{phase}]{Colors.RESET}"
    else:  # LLM working
        label = phase
        if llm_progress:
            label = f"{llm_progress}, {phase}"
        return f"{Colors.BOLD}{Colors.MAGENTA}[{label}]{Colors.RESET}"


def colorize_url(url: str) -> str:
    """Add color to URLs to improve visibility/clickability in terminals."""
    if not url:
        return url
    return f"{Colors.BLUE}{url}{Colors.RESET}"


def set_color_scheme(color_scheme: str) -> str:
    """Apply the configured color scheme to the Colors palette."""
    normalized = (color_scheme or "").strip().lower()
    palette = _COLOR_SCHEMES.get(normalized)

    if not palette:
        normalized = DEFAULT_COLOR_SCHEME
        palette = _COLOR_SCHEMES[DEFAULT_COLOR_SCHEME]

    Colors.YELLOW = palette["phase1"]
    Colors.CYAN = palette["phase2"]
    Colors.GREEN = palette["phase3"]
    Colors.MAGENTA = palette["llm"]
    Colors.BLUE = palette["url"]
    return normalized


def get_supported_color_schemes() -> list[str]:
    """Return a list of supported color scheme names."""
    return sorted(_COLOR_SCHEMES.keys())


# Initialize palette with default scheme
set_color_scheme(DEFAULT_COLOR_SCHEME)
