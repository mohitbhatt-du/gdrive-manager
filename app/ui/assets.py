"""Icon and image asset generation using Pillow for crisp, modern GUI icons."""

from PIL import Image, ImageDraw
import customtkinter as ctk
from typing import Dict, Tuple

_pil_cache: Dict[str, Image.Image] = {}

def clear_icon_cache():
    """Clear cached PIL images."""
    _pil_cache.clear()

def _create_smooth_canvas(size: int = 48) -> Tuple[Image.Image, ImageDraw.ImageDraw, int]:
    """Create supersampled canvas for sharp antialiased drawing."""
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    return img, draw, scale

def get_gdrive_icon(size: int = 36) -> ctk.CTkImage:
    """Generate the original GDrive Manager geometric cloud nexus icon."""
    key = f"nexus_icon_{size}"
    if key in _pil_cache:
        final_img = _pil_cache[key]
        return ctk.CTkImage(light_image=final_img, dark_image=final_img, size=(size, size))

    img, draw, s = _create_smooth_canvas(size)
    w = size * s

    # Rounded squircle base
    margin = int(w * 0.04)
    radius = int(w * 0.22)
    draw.rounded_rectangle(
        [margin, margin, w - margin, w - margin],
        radius=radius,
        fill=(15, 23, 42, 255),
        outline=(124, 58, 237, 220),
        width=max(2, int(w * 0.03))
    )

    # Isometric Nexus Coordinates
    cx = w // 2
    cy = w // 2 - int(w * 0.02)
    top_y = cy - int(w * 0.28)
    mid_y = cy
    bot_y = cy + int(w * 0.28)
    left_x = cx - int(w * 0.24)
    right_x = cx + int(w * 0.24)

    # 1. Top Facet (Cloud Streaming - Cyan)
    draw.polygon([(cx, top_y), (right_x, cy - int(w * 0.14)), (cx, mid_y), (left_x, cy - int(w * 0.14))], fill=(6, 182, 212, 255))
    # 2. Left Facet (Virtual Drive - Deep Violet)
    draw.polygon([(left_x, cy - int(w * 0.14)), (cx, mid_y), (cx, bot_y), (left_x, cy + int(w * 0.14))], fill=(109, 40, 217, 255))
    # 3. Right Facet (Offline Sync - Vibrant Purple)
    draw.polygon([(cx, mid_y), (right_x, cy - int(w * 0.14)), (right_x, cy + int(w * 0.14)), (cx, bot_y)], fill=(168, 85, 247, 255))

    # Facet contrast line
    lw = max(1, int(w * 0.015))
    draw.line([(cx, mid_y), (cx, bot_y)], fill=(255, 255, 255, 140), width=lw)
    draw.line([(cx, top_y), (cx, mid_y)], fill=(255, 255, 255, 120), width=lw)

    # Center Hub Node
    hub_r = max(2, int(w * 0.04))
    draw.ellipse([cx - hub_r, mid_y - hub_r, cx + hub_r, mid_y + hub_r], fill=(255, 255, 255, 255))

    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    _pil_cache[key] = final_img
    return ctk.CTkImage(light_image=final_img, dark_image=final_img, size=(size, size))

def get_drive_hardware_icon(size: int = 24, color: str = "#8B5CF6") -> ctk.CTkImage:
    """Generate modern Windows Hard Drive / SSD icon."""
    key = f"drive_hw_{size}_{color}"
    if key in _pil_cache:
        final_img = _pil_cache[key]
        return ctk.CTkImage(light_image=final_img, dark_image=final_img, size=(size, size))

    img, draw, s = _create_smooth_canvas(size)
    w = size * s
    rgb = (139, 92, 246, 255) if color == "#8B5CF6" else (243, 244, 246, 255)

    # Drive body (rounded rectangle)
    margin = int(w * 0.15)
    draw.rounded_rectangle(
        [margin, int(w * 0.28), w - margin, int(w * 0.72)],
        radius=int(w * 0.08),
        outline=rgb,
        width=int(w * 0.06)
    )
    # Drive activity LED / disc slot
    draw.ellipse(
        [w - margin - int(w * 0.18), int(w * 0.45), w - margin - int(w * 0.08), int(w * 0.55)],
        fill=rgb
    )
    draw.line(
        [(margin + int(w * 0.1), int(w * 0.5)), (margin + int(w * 0.45), int(w * 0.5))],
        fill=rgb,
        width=int(w * 0.05)
    )

    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    _pil_cache[key] = final_img
    return ctk.CTkImage(light_image=final_img, dark_image=final_img, size=(size, size))

    # Drive body (rounded rectangle)
    margin = int(w * 0.15)
    draw.rounded_rectangle(
        [margin, int(w * 0.28), w - margin, int(w * 0.72)],
        radius=int(w * 0.08),
        outline=rgb,
        width=int(w * 0.06)
    )
    # Drive activity LED / disc slot
    draw.ellipse(
        [w - margin - int(w * 0.18), int(w * 0.45), w - margin - int(w * 0.08), int(w * 0.55)],
        fill=rgb
    )
    draw.line(
        [(margin + int(w * 0.1), int(w * 0.5)), (margin + int(w * 0.45), int(w * 0.5))],
        fill=rgb,
        width=int(w * 0.05)
    )

    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    _pil_cache[key] = final_img
    return ctk.CTkImage(light_image=final_img, dark_image=final_img, size=(size, size))

def get_symbol_icon(name: str, size: int = 20, color: str = "#F9FAFB") -> ctk.CTkImage:
    """Generate clean minimal UI vector icons (plus, sync, folder, cloud, gear, play, stop, check, alert)."""
    key = f"symbol_{name}_{size}_{color}"
    if key in _pil_cache:
        final_img = _pil_cache[key]
        return ctk.CTkImage(light_image=final_img, dark_image=final_img, size=(size, size))

    img, draw, s = _create_smooth_canvas(size)
    w = size * s
    # Convert hex color to RGBA
    h = color.lstrip("#")
    if len(h) == 6:
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    else:
        rgb = (255, 255, 255, 255)

    lw = max(2, int(w * 0.08))

    if name == "plus":
        mid = w // 2
        pad = int(w * 0.22)
        draw.line([(mid, pad), (mid, w - pad)], fill=rgb, width=lw)
        draw.line([(pad, mid), (w - pad, mid)], fill=rgb, width=lw)

    elif name == "sync":
        margin = int(w * 0.2)
        draw.arc([margin, margin, w - margin, w - margin], start=30, end=300, fill=rgb, width=lw)
        # Arrowhead
        ax, ay = int(w * 0.8), int(w * 0.45)
        draw.polygon([(ax, ay - int(w * 0.12)), (ax, ay + int(w * 0.12)), (ax - int(w * 0.12), ay)], fill=rgb)

    elif name == "cloud":
        # Cloud outline
        draw.ellipse([int(w * 0.3), int(w * 0.25), int(w * 0.7), int(w * 0.65)], fill=rgb)
        draw.ellipse([int(w * 0.18), int(w * 0.42), int(w * 0.5), int(w * 0.75)], fill=rgb)
        draw.ellipse([int(w * 0.5), int(w * 0.42), int(w * 0.82), int(w * 0.75)], fill=rgb)
        draw.rectangle([int(w * 0.34), int(w * 0.55), int(w * 0.66), int(w * 0.75)], fill=rgb)

    elif name == "folder":
        # Folder tab + body
        draw.polygon([
            (int(w * 0.15), int(w * 0.3)),
            (int(w * 0.45), int(w * 0.3)),
            (int(w * 0.55), int(w * 0.42)),
            (int(w * 0.85), int(w * 0.42)),
            (int(w * 0.85), int(w * 0.75)),
            (int(w * 0.15), int(w * 0.75))
        ], fill=rgb)

    elif name == "gear":
        # Settings cog
        mid = w // 2
        r_out = int(w * 0.34)
        r_in = int(w * 0.16)
        draw.ellipse([mid - r_out, mid - r_out, mid + r_out, mid + r_out], outline=rgb, width=lw)
        draw.ellipse([mid - r_in, mid - r_in, mid + r_in, mid + r_in], fill=rgb)
        for ang in [0, 45, 90, 135]:
            draw.line([(mid - r_out - int(w*0.06), mid), (mid + r_out + int(w*0.06), mid)], fill=rgb, width=lw)

    elif name == "play":
        # Mount / Start triangle
        draw.polygon([
            (int(w * 0.3), int(w * 0.2)),
            (int(w * 0.78), int(w * 0.5)),
            (int(w * 0.3), int(w * 0.8))
        ], fill=rgb)

    elif name == "stop":
        # Unmount / Stop square
        pad = int(w * 0.28)
        draw.rounded_rectangle([pad, pad, w - pad, w - pad], radius=int(w * 0.06), fill=rgb)

    elif name == "check":
        # Checkmark
        p1 = (int(w * 0.22), int(w * 0.52))
        p2 = (int(w * 0.42), int(w * 0.72))
        p3 = (int(w * 0.78), int(w * 0.32))
        draw.line([p1, p2, p3], fill=rgb, width=lw, joint="curve")

    elif name == "close":
        pad = int(w * 0.28)
        draw.line([(pad, pad), (w - pad, w - pad)], fill=rgb, width=lw)
        draw.line([(w - pad, pad), (pad, w - pad)], fill=rgb, width=lw)

    elif name == "info":
        mid = w // 2
        r = int(w * 0.38)
        draw.ellipse([mid - r, mid - r, mid + r, mid + r], outline=rgb, width=lw)
        draw.ellipse([mid - int(w * 0.04), int(w * 0.28), mid + int(w * 0.04), int(w * 0.36)], fill=rgb)
        draw.line([(mid, int(w * 0.44)), (mid, int(w * 0.7))], fill=rgb, width=lw)

    elif name == "open":
        # Arrow pointing out / open drive in explorer
        draw.rectangle([int(w * 0.2), int(w * 0.35), int(w * 0.65), int(w * 0.8)], outline=rgb, width=lw)
        draw.line([(int(w * 0.5), int(w * 0.5)), (int(w * 0.8), int(w * 0.2))], fill=rgb, width=lw)
        draw.line([(int(w * 0.6), int(w * 0.2)), (int(w * 0.8), int(w * 0.2)), (int(w * 0.8), int(w * 0.4))], fill=rgb, width=lw)

    else:
        # Generic dot
        mid = w // 2
        r = int(w * 0.2)
        draw.ellipse([mid - r, mid - r, mid + r, mid + r], fill=rgb)

    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    _pil_cache[key] = final_img
    return ctk.CTkImage(light_image=final_img, dark_image=final_img, size=(size, size))
