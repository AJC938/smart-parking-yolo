"""Qt stylesheet for the Smart Parking Intelligence dashboard."""

COLOR_BG = "#161a23"
COLOR_PANEL = "#1e2330"
COLOR_PANEL_ALT = "#252b3b"
COLOR_BORDER = "#323a4d"
COLOR_TEXT = "#e6e9f0"
COLOR_TEXT_MUTED = "#8891a7"
COLOR_ACCENT = "#4f8cff"
COLOR_GOOD = "#33c07e"
COLOR_BAD = "#e5484d"
COLOR_WARN = "#e5a340"

STYLESHEET = f"""
QWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}}

#HeaderBar {{
    background-color: {COLOR_PANEL};
    border-bottom: 1px solid {COLOR_BORDER};
}}

#HeaderTitle {{
    font-size: 18px;
    font-weight: 600;
    color: {COLOR_TEXT};
}}

#HeaderSubtitle {{
    color: {COLOR_TEXT_MUTED};
    font-size: 11px;
}}

QFrame[class="Card"] {{
    background-color: {COLOR_PANEL};
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
}}

QLabel[class="CardTitle"] {{
    color: {COLOR_TEXT_MUTED};
    font-size: 11px;
    font-weight: 600;
}}

QLabel[class="StatValue"] {{
    font-size: 26px;
    font-weight: 700;
}}

QLabel[class="StatLabel"] {{
    color: {COLOR_TEXT_MUTED};
    font-size: 11px;
}}

#VideoFrame {{
    background-color: black;
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
"""
