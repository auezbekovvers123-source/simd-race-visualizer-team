"""
CSV, chart PNG, and window screenshot export — Person 6.
"""

from __future__ import annotations

import csv
from tkinter import filedialog, messagebox

from person1.config import OP_KEY_TO_LABEL

OperationKey = str


def export_csv(
    parent,
    *,
    n: int,
    op: OperationKey,
    width: int,
    t_scalar: float,
    t_vector: float,
) -> None:
    """Write one results row to a user-selected CSV file."""
    path = filedialog.asksaveasfilename(
        parent=parent,
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv"), ("All files", "*.*")],
        title="Export results as CSV",
    )
    if not path:
        return
    speed = t_scalar / t_vector if t_vector > 0 else 0.0
    with open(path, "w", newline="", encoding="utf-8") as f:
        wtr = csv.writer(f)
        wtr.writerow(
            ["array_size", "operation", "simd_width_model", "scalar_seconds", "vector_seconds", "speedup"]
        )
        wtr.writerow([n, OP_KEY_TO_LABEL.get(op, op), width, f"{t_scalar:.9f}", f"{t_vector:.9f}", f"{speed:.6f}"])
    messagebox.showinfo("Exported", f"Wrote:\n{path}", parent=parent)


def save_chart_png(parent, figure) -> None:
    """Save the matplotlib figure to PNG."""
    path = filedialog.asksaveasfilename(
        parent=parent,
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("All files", "*.*")],
        title="Save bar chart",
    )
    if not path:
        return
    figure.savefig(path, dpi=160, bbox_inches="tight")
    messagebox.showinfo("Saved", f"Chart saved to:\n{path}", parent=parent)


def save_window_screenshot(parent) -> None:
    """Capture the Tk toplevel via GDI BitBlt → 32-bit BMP (Windows)."""
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
        hwnd = int(parent.winfo_id())

        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", wintypes.LONG),
                ("top", wintypes.LONG),
                ("right", wintypes.LONG),
                ("bottom", wintypes.LONG),
            ]

        rect = RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            raise OSError("GetWindowRect failed")
        ww = int(rect.right - rect.left)
        hh = int(rect.bottom - rect.top)
        if ww <= 0 or hh <= 0:
            raise OSError("Invalid window size")

        hdc_win = user32.GetWindowDC(hwnd)
        if not hdc_win:
            raise OSError("GetWindowDC failed")
        hdc_mem = gdi32.CreateCompatibleDC(hdc_win)
        hbmp = gdi32.CreateCompatibleBitmap(hdc_win, ww, hh)
        if not hdc_mem or not hbmp:
            if hbmp:
                gdi32.DeleteObject(hbmp)
            if hdc_mem:
                gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(hwnd, hdc_win)
            raise OSError("CreateCompatibleDC/Bitmap failed")

        old_obj = gdi32.SelectObject(hdc_mem, hbmp)
        SRCCOPY = 0x00CC0020
        if not gdi32.BitBlt(hdc_mem, 0, 0, ww, hh, hdc_win, 0, 0, SRCCOPY):
            gdi32.SelectObject(hdc_mem, old_obj)
            gdi32.DeleteObject(hbmp)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(hwnd, hdc_win)
            raise OSError("BitBlt failed")

        class BITMAPFILEHEADER(ctypes.Structure):
            _fields_ = [
                ("bfType", wintypes.WORD),
                ("bfSize", wintypes.DWORD),
                ("bfReserved1", wintypes.WORD),
                ("bfReserved2", wintypes.WORD),
                ("bfOffBits", wintypes.DWORD),
            ]

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wintypes.DWORD),
                ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG),
                ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD),
            ]

        bmp_header = BITMAPINFOHEADER()
        bmp_header.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmp_header.biWidth = ww
        bmp_header.biHeight = hh
        bmp_header.biPlanes = 1
        bmp_header.biBitCount = 32
        bmp_header.biCompression = 0
        row_bytes = ((ww * 32 + 31) // 32) * 4
        bmp_header.biSizeImage = row_bytes * hh

        pixels = ctypes.create_string_buffer(row_bytes * hh)
        lines = gdi32.GetDIBits(hdc_mem, hbmp, 0, hh, pixels, ctypes.byref(bmp_header), 0)
        if lines == 0:
            raise OSError("GetDIBits failed")

        file_header = BITMAPFILEHEADER()
        file_header.bfType = 0x4D42
        file_header.bfOffBits = ctypes.sizeof(BITMAPFILEHEADER) + ctypes.sizeof(BITMAPINFOHEADER)
        file_header.bfSize = file_header.bfOffBits + bmp_header.biSizeImage

        path = filedialog.asksaveasfilename(
            parent=parent,
            defaultextension=".bmp",
            filetypes=[("BMP", "*.bmp"), ("All files", "*.*")],
            title="Save window screenshot",
        )
        if not path:
            gdi32.SelectObject(hdc_mem, old_obj)
            gdi32.DeleteObject(hbmp)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(hwnd, hdc_win)
            return

        def struct_bytes(obj: ctypes.Structure) -> bytes:
            return ctypes.string_at(ctypes.byref(obj), ctypes.sizeof(obj))

        with open(path, "wb") as f:
            f.write(struct_bytes(file_header))
            f.write(struct_bytes(bmp_header))
            f.write(pixels)

        gdi32.SelectObject(hdc_mem, old_obj)
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(hwnd, hdc_win)
        messagebox.showinfo("Saved", f"Screenshot saved as BMP:\n{path}", parent=parent)
    except Exception as exc:  # noqa: BLE001
        messagebox.showerror(
            "Screenshot failed",
            f"Could not capture the window.\nReason: {exc}\n\nTip: use Win+Shift+S or Save chart PNG.",
            parent=parent,
        )
