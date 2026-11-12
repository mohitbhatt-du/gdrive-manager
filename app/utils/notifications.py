"""Windows desktop notifications helper."""

import subprocess
import threading

from app.utils.logger import get_logger

logger = get_logger("Notifications")


def send_notification(title: str, message: str, level: str = "info"):
    """Send native Windows desktop notification asynchronously."""

    def _worker():
        try:
            # Clean text for PowerShell command
            clean_title = title.replace('"', '`"').replace("'", "’")
            clean_msg = message.replace('"', '`"').replace("'", "’")

            ps_cmd = (
                f'[reflection.assembly]::loadwithpartialname("System.Windows.Forms") | Out-Null; '
                f"$notify = New-Object System.Windows.Forms.NotifyIcon; "
                f"$notify.Icon = [System.Drawing.SystemIcons]::Information; "
                f"$notify.Visible = $True; "
                f'$notify.ShowBalloonTip(3000, "{clean_title}", "{clean_msg}", [System.Windows.Forms.ToolTipIcon]::Info);'
            )

            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            logger.debug(f"Dispatched notification: {title} - {message}")
        except Exception as e:
            logger.debug(f"Failed to dispatch desktop notification: {e}")

    threading.Thread(target=_worker, daemon=True).start()
