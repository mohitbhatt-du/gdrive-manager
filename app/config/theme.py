"""Theme tokens, colors, typography, and styling parameters."""


class Colors:
    # Main Backgrounds
    BG_MAIN = "#0B0F19"  # Deep dark navy canvas
    BG_SIDEBAR = "#0F172A"  # Dark slate navy sidebar
    BG_SIDEBAR_HOVER = "#1E293B"
    BG_SIDEBAR_ACTIVE = "#2E1065"  # Deep violet active indicator tint

    # Surfaces & Cards
    CARD_BG = "#151E2E"  # Elevated card background
    CARD_HOVER = "#1E2B40"  # Smooth card hover state
    CARD_BORDER = "#25334A"  # Subtle card border
    CARD_INNER = "#0F1624"  # Recessed inner panels

    # Accents & Brand
    ACCENT_PRIMARY = "#7C3AED"  # Modern vibrant violet
    ACCENT_HOVER = "#6D28D9"  # Darker violet
    ACCENT_LIGHT = "#A78BFA"  # Soft violet for icons/subtitles
    ACCENT_CYAN = "#06B6D4"  # Highlight cyan

    # Status Indicators
    STATUS_MOUNTED = "#10B981"  # Emerald Green (Mounted & Active)
    STATUS_CONNECTED = "#3B82F6"  # Electric Blue (Connected)
    STATUS_SYNCING = "#8B5CF6"  # Violet (Sync in progress)
    STATUS_WARNING = "#F59E0B"  # Amber (Warning/Paused)
    STATUS_ERROR = "#EF4444"  # Rose Red (Error/Disconnected)
    STATUS_MUTED = "#6B7280"  # Gray (Disabled)

    # Typography
    TEXT_PRIMARY = "#F9FAFB"  # Crisp white-gray
    TEXT_SECONDARY = "#94A3B8"  # Medium cool gray
    TEXT_MUTED = "#64748B"  # Dimmed helper text
    TEXT_INVERTED = "#0F172A"  # Dark text on light buttons

    # Inputs & Controls
    INPUT_BG = "#0D131F"
    INPUT_BORDER = "#2A3850"
    INPUT_FOCUS = "#7C3AED"
    PROGRESS_BG = "#1F293D"
    PROGRESS_FILL = "#8B5CF6"


class Fonts:
    FAMILY = "Segoe UI"
    MONO = "Consolas"

    HERO = (FAMILY, 22, "bold")
    SECTION_HEADER = (FAMILY, 18, "bold")
    CARD_TITLE = (FAMILY, 15, "bold")
    SUBTITLE = (FAMILY, 12)
    BODY = (FAMILY, 12)
    BODY_BOLD = (FAMILY, 12, "bold")
    BUTTON = (FAMILY, 12, "bold")
    BADGE = (FAMILY, 10, "bold")
    CAPTION = (FAMILY, 10)
    CODE = (MONO, 11)


class Dimensions:
    SIDEBAR_WIDTH = 240
    CARD_CORNER_RADIUS = 12
    BUTTON_CORNER_RADIUS = 8
    INPUT_CORNER_RADIUS = 6
    BADGE_CORNER_RADIUS = 6
    WINDOW_MIN_WIDTH = 1080
    WINDOW_MIN_HEIGHT = 720
