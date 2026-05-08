import base64
from pathlib import Path

_LOGO_B64 = None


def get_logo_base64() -> str:
    global _LOGO_B64
    if _LOGO_B64 is None:
        logo_path = Path(__file__).resolve().parents[2] / "Lab2Launchlogo.png"
        with open(logo_path, "rb") as f:
            _LOGO_B64 = base64.b64encode(f.read()).decode()
    return _LOGO_B64


def logo_img_tag(height: int = 80) -> str:
    b64 = get_logo_base64()
    return f'<img src="data:image/jpeg;base64,{b64}" style="height:{height}px; width:auto;" alt="Lab2Launch">'


def logo_header_html(height: int = 90) -> str:
    b64 = get_logo_base64()
    return f"""
    <div style="display:flex; align-items:center; justify-content:center; gap:1rem; margin-bottom:1.5rem;">
        <img src="data:image/jpeg;base64,{b64}" style="height:{height}px; width:auto;" alt="Lab2Launch">
    </div>
    """


def background_css() -> str:
    b64 = get_logo_base64()
    return f"""
    <style>
    body::before {{
        content: '';
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 480px;
        height: 480px;
        background-image: url('data:image/jpeg;base64,{b64}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.04;
        z-index: 0;
        pointer-events: none;
    }}
    </style>
    """
