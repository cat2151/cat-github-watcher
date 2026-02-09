"""
ANSI color codes and colorization functions for terminal output
"""

DEFAULT_COLOR_SCHEME = "monokai"

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
