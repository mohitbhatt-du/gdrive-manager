"""Brand assets generation script for GDrive Manager.

Generates:
- icon.png (512x512)
- icon-256.png, icon-128.png, icon-64.png, icon-48.png, icon-32.png, icon-16.png
- icon.ico (multi-resolution Windows ICO containing 16, 32, 48, 64, 128, 256)
- logo.png (high-res brand logo)
- github-banner.png (1280x640 with embedded authentic app screenshot)
- social-preview.png (1280x640 optimized for social cards)
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def draw_nexus_icon(size: int = 512) -> Image.Image:
    """Render the high-precision isometric cloud-drive nexus icon."""
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    margin = int(24 * (size / 512) * scale)
    radius = int(108 * (size / 512) * scale)
    rect_box = [margin, margin, canvas_size - margin, canvas_size - margin]

    # Draw rounded squircle base with gradient simulation
    d.rounded_rectangle(
        rect_box,
        radius=radius,
        fill=(15, 23, 42, 255),
        outline=(124, 58, 237, 220),
        width=int(6 * (size / 512) * scale),
    )

    # Inner ambient purple glow
    cx, cy = canvas_size // 2, canvas_size // 2 - int(6 * (size / 512) * scale)
    glow_r = int(140 * (size / 512) * scale)
    glow_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r], fill=(124, 58, 237, 40))
    img.alpha_composite(glow_layer)

    # Isometric Coordinates for 3 facets
    top_y = cy - int(136 * (size / 512) * scale)
    mid_y = cy
    bot_y = cy + int(136 * (size / 512) * scale)
    left_x = cx - int(120 * (size / 512) * scale)
    right_x = cx + int(120 * (size / 512) * scale)

    # 1. Top Facet (Cloud Streaming - Cyan gradient)
    top_pts = [
        (cx, top_y),
        (right_x, cy - int(68 * (size / 512) * scale)),
        (cx, mid_y),
        (left_x, cy - int(68 * (size / 512) * scale)),
    ]
    d.polygon(top_pts, fill=(6, 182, 212, 255))

    # 2. Left Facet (Virtual Drive Letter - Deep Violet)
    left_pts = [
        (left_x, cy - int(68 * (size / 512) * scale)),
        (cx, mid_y),
        (cx, bot_y),
        (left_x, cy + int(68 * (size / 512) * scale)),
    ]
    d.polygon(left_pts, fill=(109, 40, 217, 255))

    # 3. Right Facet (Offline Storage - Vibrant Purple)
    right_pts = [
        (cx, mid_y),
        (right_x, cy - int(68 * (size / 512) * scale)),
        (right_x, cy + int(68 * (size / 512) * scale)),
        (cx, bot_y),
    ]
    d.polygon(right_pts, fill=(168, 85, 247, 255))

    # Facet Division lines for sleek contrast
    line_w = max(2, int(3 * (size / 512) * scale))
    d.line([top_pts[0], top_pts[2]], fill=(255, 255, 255, 120), width=line_w)
    d.line([top_pts[1], top_pts[3]], fill=(255, 255, 255, 120), width=line_w)
    d.line([(cx, mid_y), (cx, bot_y)], fill=(255, 255, 255, 140), width=line_w)

    # Accent indicators on facets
    # LED indicator on Left Drive Facet
    led_x = left_x + int(40 * (size / 512) * scale)
    led_y = cy + int(20 * (size / 512) * scale)
    led_r = int(8 * (size / 512) * scale)
    d.ellipse([led_x - led_r, led_y - led_r, led_x + led_r, led_y + led_r], fill=(16, 185, 129, 255))

    # Central Nexus Hub Node
    hub_r = int(18 * (size / 512) * scale)
    d.ellipse([cx - hub_r, mid_y - hub_r, cx + hub_r, mid_y + hub_r], fill=(255, 255, 255, 255))
    inner_hub_r = int(9 * (size / 512) * scale)
    d.ellipse(
        [cx - inner_hub_r, mid_y - inner_hub_r, cx + inner_hub_r, mid_y + inner_hub_r],
        fill=(124, 58, 237, 255),
    )

    # Downsample with Lanczos for anti-aliasing
    return img.resize((size, size), Image.Resampling.LANCZOS)


def draw_logo(icon_img: Image.Image) -> Image.Image:
    """Render full horizontal brand logo with icon and typography."""
    w, h = 680, 160
    scale = 2
    img = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Resize icon for logo
    ic = icon_img.resize((120 * scale, 120 * scale), Image.Resampling.LANCZOS)
    img.paste(ic, (20 * scale, 20 * scale), ic)

    # Try loading clean font or fallback to default
    try:
        font_title = ImageFont.truetype("segoeui.ttf", 52 * scale)
        font_sub = ImageFont.truetype("segoeuib.ttf", 14 * scale)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Draw Title: GDrive Manager
    d.text((166 * scale, 36 * scale), "GDrive ", fill=(248, 250, 252, 255), font=font_title)
    # Estimate offset for "Manager"
    d.text((346 * scale, 36 * scale), "Manager", fill=(167, 139, 250, 255), font=font_title)

    # Draw Subtitle
    d.text(
        (168 * scale, 102 * scale), "DESKTOP CLOUD SYNC & STREAMING", fill=(148, 163, 184, 255), font=font_sub
    )
    d.ellipse([540 * scale, 107 * scale, 546 * scale, 113 * scale], fill=(6, 182, 212, 255))

    return img.resize((w, h), Image.Resampling.LANCZOS)


def create_marketing_banner(icon_img: Image.Image, screenshot_path: Path) -> Image.Image:
    """Generate 1280x640 GitHub marketing banner embedding the actual application screenshot."""
    w, h = 1280, 640
    banner = Image.new("RGBA", (w, h), (11, 15, 25, 255))  # Deep Dark Navy #0B0F19
    d = ImageDraw.Draw(banner)

    # Ambient radial gradient glows in background
    glow_l = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_l)
    gd.ellipse([-100, -100, 600, 600], fill=(124, 58, 237, 30))
    gd.ellipse([600, 100, 1400, 800], fill=(6, 182, 212, 22))
    banner.alpha_composite(glow_l)

    # Left Column: Branding, Tagline, Feature Highlights
    # Icon (96x96)
    icon_sized = icon_img.resize((88, 88), Image.Resampling.LANCZOS)
    banner.paste(icon_sized, (72, 70), icon_sized)

    try:
        font_hero = ImageFont.truetype("segoeuib.ttf", 46)
        font_tag = ImageFont.truetype("segoeuib.ttf", 26)
        font_feat = ImageFont.truetype("segoeui.ttf", 18)
        font_badge = ImageFont.truetype("segoeuib.ttf", 13)
        font_foot = ImageFont.truetype("segoeui.ttf", 14)
    except Exception:
        font_hero = ImageFont.load_default()
        font_tag = ImageFont.load_default()
        font_feat = ImageFont.load_default()
        font_badge = ImageFont.load_default()
        font_foot = ImageFont.load_default()

    # Product Title
    d.text((176, 76), "GDrive ", fill=(248, 250, 252), font=font_hero)
    d.text((330, 76), "Manager", fill=(167, 139, 250), font=font_hero)
    d.text((178, 130), "Windows Cloud Storage Bridge", fill=(148, 163, 184), font=font_foot)

    # Primary Tagline
    d.text((72, 190), "Your Google Drives.", fill=(241, 245, 249), font=font_tag)
    d.text((72, 224), "One Desktop.", fill=(167, 139, 250), font=font_tag)

    # Feature Summary Badge Pill
    pill_box = [72, 280, 520, 316]
    d.rounded_rectangle(pill_box, radius=18, fill=(21, 30, 46), outline=(37, 51, 74), width=1)
    d.text((92, 290), "Multi-Account • Cloud Streaming • Offline Sync", fill=(6, 182, 212), font=font_badge)

    # Feature Bullet Points
    bullets = [
        "✦ Mount Drives as Letters (G:, H:, I:) via WinFsp",
        "✦ Offline Mirror & Bidirectional Bi-Sync Engine",
        "✦ Windows Credential Manager Token Security",
        "✦ Real-Time Transfer Telemetry & System Tray",
    ]
    by = 345
    for b in bullets:
        d.text((72, by), b, fill=(203, 213, 225), font=font_feat)
        by += 34

    # Footer note
    d.text(
        (72, 540),
        "Engineered for Windows 10 & 11 (x64) • Powered by rclone",
        fill=(100, 116, 139),
        font=font_foot,
    )

    # Right Column: Authentic Application Screenshot in Window Mockup
    if screenshot_path.exists():
        sc_img = Image.open(screenshot_path).convert("RGBA")
        # Target size for screenshot preview in banner
        sc_w, sc_h = 670, 430
        sc_resized = sc_img.resize((sc_w, sc_h), Image.Resampling.LANCZOS)

        # Window Mockup Frame with Dark Navy Title Bar
        mock_x = 550
        mock_y = 100
        title_h = 32
        frame_w = sc_w + 4
        frame_h = sc_h + title_h + 4

        # Shadow beneath mockup window
        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle(
            [mock_x - 10, mock_y - 10, mock_x + frame_w + 10, mock_y + frame_h + 16],
            radius=16,
            fill=(0, 0, 0, 120),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(14))
        banner.alpha_composite(shadow)

        # Window Border & Titlebar
        d = ImageDraw.Draw(banner)
        d.rounded_rectangle(
            [mock_x, mock_y, mock_x + frame_w, mock_y + frame_h],
            radius=10,
            fill=(15, 23, 42),
            outline=(51, 65, 85),
            width=2,
        )
        # Window control dots (mac/win style pill)
        d.ellipse([mock_x + 14, mock_y + 11, mock_x + 24, mock_y + 21], fill=(239, 68, 68))
        d.ellipse([mock_x + 32, mock_y + 11, mock_x + 42, mock_y + 21], fill=(245, 158, 11))
        d.ellipse([mock_x + 50, mock_y + 11, mock_x + 60, mock_y + 21], fill=(16, 185, 129))
        d.text((mock_x + 80, mock_y + 9), "GDrive Manager", fill=(148, 163, 184), font=font_foot)

        # Paste Screenshot into window body
        banner.paste(sc_resized, (mock_x + 2, mock_y + title_h + 2))

    return banner


def create_social_preview(icon_img: Image.Image) -> Image.Image:
    """Generate 1280x640 GitHub social preview card optimized for small embeds."""
    w, h = 1280, 640
    card = Image.new("RGBA", (w, h), (11, 15, 25, 255))
    d = ImageDraw.Draw(card)

    # Ambient radial gradient glows
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w // 2 - 350, h // 2 - 280, w // 2 + 350, h // 2 + 280], fill=(124, 58, 237, 45))
    card.alpha_composite(glow)

    # Large Center Icon (180x180)
    ic = icon_img.resize((180, 180), Image.Resampling.LANCZOS)
    card.paste(ic, (w // 2 - 90, 100), ic)

    try:
        font_title = ImageFont.truetype("segoeuib.ttf", 60)
        font_sub = ImageFont.truetype("segoeui.ttf", 26)
        font_pill = ImageFont.truetype("segoeuib.ttf", 18)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_pill = ImageFont.load_default()

    d = ImageDraw.Draw(card)
    # Title
    t1 = "GDrive "
    t2 = "Manager"
    t1_w = d.textlength(t1, font=font_title)
    tot_w = t1_w + d.textlength(t2, font=font_title)
    start_x = (w - tot_w) // 2
    d.text((start_x, 310), t1, fill=(248, 250, 252), font=font_title)
    d.text((start_x + t1_w, 310), t2, fill=(167, 139, 250), font=font_title)

    # Tagline
    tagline = "Your Google Drives. One Desktop."
    tag_w = d.textlength(tagline, font=font_sub)
    d.text(((w - tag_w) // 2, 390), tagline, fill=(203, 213, 225), font=font_sub)

    # Feature pill
    pill_text = "Multi-Account  •  Virtual Drive Streaming  •  Offline Sync  •  Windows Credential Vault"
    pill_w = d.textlength(pill_text, font=font_pill) + 48
    pill_x = (w - pill_w) // 2
    d.rounded_rectangle(
        [pill_x, 460, pill_x + pill_w, 508], radius=24, fill=(21, 30, 46), outline=(37, 51, 74), width=1
    )
    d.text((pill_x + 24, 474), pill_text, fill=(6, 182, 212), font=font_pill)

    return card


def main():
    base_dir = Path(__file__).resolve().parent.parent
    branding_dir = base_dir / "assets" / "branding"
    icons_dir = base_dir / "assets" / "icons"
    branding_dir.mkdir(parents=True, exist_ok=True)
    icons_dir.mkdir(parents=True, exist_ok=True)

    print("Generating GDrive Manager original brand identity assets...")

    # 1. Master Icon (512x512)
    icon_512 = draw_nexus_icon(512)
    icon_512.save(branding_dir / "icon.png")
    print("[+] Created assets/branding/icon.png (512x512)")

    # 2. Raster sizes
    sizes = [256, 128, 64, 48, 32, 16]
    raster_images = []
    for s in sizes:
        sized_img = draw_nexus_icon(s)
        out_path = branding_dir / f"icon-{s}.png"
        sized_img.save(out_path)
        raster_images.append(sized_img)
        print(f"[+] Created assets/branding/icon-{s}.png ({s}x{s})")

    # 3. Multi-resolution Windows ICO
    # Must save sizes in order: 16, 32, 48, 64, 128, 256
    ico_imgs = [draw_nexus_icon(s) for s in [16, 32, 48, 64, 128, 256]]
    ico_path = branding_dir / "icon.ico"
    ico_imgs[-1].save(str(ico_path), format="ICO", sizes=[(s, s) for s in [16, 32, 48, 64, 128, 256]])
    # Also update assets/icons/app_icon.ico
    app_ico_path = icons_dir / "app_icon.ico"
    ico_imgs[-1].save(str(app_ico_path), format="ICO", sizes=[(s, s) for s in [16, 32, 48, 64, 128, 256]])
    print("[+] Created assets/branding/icon.ico and assets/icons/app_icon.ico (multi-res Windows ICO)")

    # 4. Logo PNG
    logo_img = draw_logo(icon_512)
    logo_img.save(branding_dir / "logo.png")
    print("[+] Created assets/branding/logo.png (680x160)")

    # 5. Marketing Banner
    screenshot_path = branding_dir / "screenshot-dashboard.png"
    banner_img = create_marketing_banner(icon_512, screenshot_path)
    banner_img.save(branding_dir / "github-banner.png")
    print("[+] Created assets/branding/github-banner.png (1280x640)")

    # 6. Social Preview Image
    social_img = create_social_preview(icon_512)
    social_img.save(branding_dir / "social-preview.png")
    print("[+] Created assets/branding/social-preview.png (1280x640)")

    print("[✓] All brand identity assets generated successfully!")


if __name__ == "__main__":
    main()
