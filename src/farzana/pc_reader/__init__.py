"""Read-only PC essentials → vault (calendar/mail/files). No write actions."""

from farzana.pc_reader.watch import process_file, scan_folder, watch_loop

__all__ = ["process_file", "scan_folder", "watch_loop"]
