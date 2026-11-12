"""System tray integration using pystray for desktop shell minimization."""

import threading
from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from app.utils.logger import get_logger

logger = get_logger("SystemTray")

class SystemTrayManager:
    """Manages the Windows Notification Area (System Tray) icon and context menu."""

    def __init__(
        self,
        on_show_window: Callable[[], None],
        on_mount_all: Callable[[], None],
        on_unmount_all: Callable[[], None],
        on_quit_app: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None
    ):
        self.on_show_window = on_show_window
        self.on_mount_all = on_mount_all
        self.on_unmount_all = on_unmount_all
        self.on_quit_app = on_quit or on_quit_app or (lambda: None)

        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def _create_tray_image(self) -> Image.Image:
        """Create simple tray icon image."""
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Violet brand circle
        draw.ellipse([4, 4, size - 4, size - 4], fill=(124, 58, 237, 255))
        # White drive symbol
        draw.rounded_rectangle([16, 24, size - 16, size - 24], radius=6, outline=(255, 255, 255, 255), width=4)
        draw.ellipse([size - 26, 30, size - 20, 36], fill=(255, 255, 255, 255))
        return img

    def start(self):
        """Start system tray icon in background thread."""
        if self._icon is not None:
            return

        image = self._create_tray_image()
        menu = pystray.Menu(
            item("Open GDrive Manager", lambda icon, item: self.on_show_window(), default=True),
            pystray.Menu.SEPARATOR,
            item("Mount All Drives", lambda icon, item: self.on_mount_all()),
            item("Unmount All Drives", lambda icon, item: self.on_unmount_all()),
            pystray.Menu.SEPARATOR,
            item("Exit Application", lambda icon, item: self.on_quit_app())
        )

        self._icon = pystray.Icon("GDriveManager", image, "GDrive Manager", menu)
        self._thread = threading.Thread(target=self._icon.run, daemon=True, name="TrayThread")
        self._thread.start()
        logger.info("System tray icon started.")

    def stop(self):
        """Stop and remove system tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception as e:
                logger.debug(f"Error stopping tray icon: {e}")
            self._icon = None
            logger.info("System tray icon stopped.")
