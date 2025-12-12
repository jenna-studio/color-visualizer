#!/usr/bin/env python3
"""
Color Visualizer - Cross-Platform Edition
=========================================
A cross-platform color visualization tool that works on Windows, macOS, and Linux.
Replaces the AppleScript version with pure Python.

Supports: HEX, RGB, CMYK, HSL, HSB/HSV color formats

Usage:
    python color_visualizer_crossplatform.py              # Interactive mode with GUI
    python color_visualizer_crossplatform.py "#ffb6c1"   # Command-line mode
    python color_visualizer_crossplatform.py --cli       # Force CLI mode (no GUI)
"""

import sys
import os
import re
import colorsys
import platform
import subprocess
import tempfile
from pathlib import Path

# Check for required dependencies
try:
    from PIL import Image, ImageDraw, ImageFont

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog

    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# COLOR CONVERSION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple (0-255)"""
    hex_color = hex_color.lstrip("#")

    # Handle shorthand hex (#ABC -> #AABBCC)
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])

    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")

    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color"""
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return f"#{r:02X}{g:02X}{b:02X}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple:
    """Convert RGB (0-255) to HSL (h: 0-1, s: 0-1, l: 0-1)"""
    r_norm, g_norm, b_norm = r / 255, g / 255, b / 255
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    return (h, s, l)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple:
    """Convert HSL to RGB (0-255 range)"""
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))


def hsb_to_rgb(h: float, s: float, v: float) -> tuple:
    """Convert HSB/HSV to RGB (0-255 range)"""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def cmyk_to_rgb(c: float, m: float, y: float, k: float) -> tuple:
    """Convert CMYK (0-100) to RGB (0-255)"""
    c, m, y, k = c / 100, m / 100, y / 100, k / 100
    r = int(255 * (1 - c) * (1 - k))
    g = int(255 * (1 - m) * (1 - k))
    b = int(255 * (1 - y) * (1 - k))
    return (r, g, b)


# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PARSING
# ═══════════════════════════════════════════════════════════════════════════════


def extract_numbers(text: str) -> list:
    """Extract all numbers from a string"""
    return [float(x) for x in re.findall(r"[\d.]+", text)]


def is_hex_string(text: str) -> bool:
    """Check if string contains only hex characters"""
    return bool(re.match(r"^[0-9A-Fa-f]+$", text))


def parse_color_input(input_text: str) -> tuple:
    """
    Parse color input in various formats and return RGB tuple.

    Supported formats:
    - HEX: #ffb6c1, ffb6c1, #ABC
    - RGB: rgb(255, 182, 193), 255,182,193
    - CMYK: cmyk(0, 29, 24, 0)
    - HSL: hsl(351, 100, 86)
    - HSB/HSV: hsb(351, 29, 100), hsv(351, 29, 100)
    """
    input_text = input_text.strip()
    input_lower = input_text.lower()

    # HEX format with #
    if input_text.startswith("#"):
        return hex_to_rgb(input_text)

    # HEX format without # (6 or 3 characters)
    if len(input_text) in (3, 6) and is_hex_string(input_text):
        return hex_to_rgb(input_text)

    # RGB format
    if input_lower.startswith("rgb"):
        nums = extract_numbers(input_text)
        if len(nums) >= 3:
            r = max(0, min(255, int(nums[0])))
            g = max(0, min(255, int(nums[1])))
            b = max(0, min(255, int(nums[2])))
            return (r, g, b)

    # CMYK format
    if input_lower.startswith("cmyk"):
        nums = extract_numbers(input_text)
        if len(nums) >= 4:
            return cmyk_to_rgb(nums[0], nums[1], nums[2], nums[3])

    # HSL format
    if input_lower.startswith("hsl"):
        nums = extract_numbers(input_text)
        if len(nums) >= 3:
            h = nums[0] / 360
            s = nums[1] / 100
            l = nums[2] / 100
            return hsl_to_rgb(h, s, l)

    # HSB/HSV format
    if input_lower.startswith("hsb") or input_lower.startswith("hsv"):
        nums = extract_numbers(input_text)
        if len(nums) >= 3:
            h = nums[0] / 360
            s = nums[1] / 100
            v = nums[2] / 100
            return hsb_to_rgb(h, s, v)

    # Plain comma-separated RGB
    if "," in input_text:
        nums = extract_numbers(input_text)
        if len(nums) >= 3:
            r = max(0, min(255, int(nums[0])))
            g = max(0, min(255, int(nums[1])))
            b = max(0, min(255, int(nums[2])))
            return (r, g, b)

    raise ValueError(f"Could not parse color: {input_text}")


# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════


def generate_palette_colors(h: float, s: float, l: float) -> dict:
    """Generate color palette recommendations based on color theory"""
    palettes = {}

    # Complementary (opposite on color wheel)
    comp_h = (h + 0.5) % 1.0
    palettes["Complementary"] = [hsl_to_rgb(h, s, l), hsl_to_rgb(comp_h, s, l)]

    # Analogous (adjacent colors)
    palettes["Analogous"] = [
        hsl_to_rgb((h - 0.083) % 1.0, s, l),
        hsl_to_rgb(h, s, l),
        hsl_to_rgb((h + 0.083) % 1.0, s, l),
    ]

    # Triadic (evenly spaced)
    palettes["Triadic"] = [
        hsl_to_rgb(h, s, l),
        hsl_to_rgb((h + 0.333) % 1.0, s, l),
        hsl_to_rgb((h + 0.666) % 1.0, s, l),
    ]

    # Split Complementary
    palettes["Split Complementary"] = [
        hsl_to_rgb(h, s, l),
        hsl_to_rgb((h + 0.417) % 1.0, s, l),
        hsl_to_rgb((h + 0.583) % 1.0, s, l),
    ]

    # Monochromatic (same hue, different lightness)
    palettes["Monochromatic"] = [
        hsl_to_rgb(h, s, max(0, l - 0.2)),
        hsl_to_rgb(h, s, l),
        hsl_to_rgb(h, s, min(1, l + 0.2)),
    ]

    return palettes


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════


def get_system_font():
    """Get appropriate system font based on OS"""
    system = platform.system()

    font_paths = []

    if system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSDisplay.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
        ]
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
        ]

    for path in font_paths:
        if os.path.exists(path):
            return path

    return None


def get_monospace_font():
    """Get appropriate monospace font based on OS"""
    system = platform.system()

    font_paths = []

    if system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/Courier.ttc",
            "/System/Library/Fonts/Monaco.ttf",
            "/System/Library/Fonts/Menlo.ttc",
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/cour.ttf",
            "C:/Windows/Fonts/lucon.ttf",
        ]
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ]

    for path in font_paths:
        if os.path.exists(path):
            return path

    return None


def load_fonts():
    """Load fonts with fallbacks"""
    fonts = {}

    system_font = get_system_font()
    mono_font = get_monospace_font()

    try:
        if system_font:
            fonts["title"] = ImageFont.truetype(system_font, 48)
            fonts["heading"] = ImageFont.truetype(system_font, 32)
            fonts["label"] = ImageFont.truetype(system_font, 18)
            fonts["small"] = ImageFont.truetype(system_font, 14)
        else:
            raise Exception("No system font found")
    except:
        fonts["title"] = ImageFont.load_default()
        fonts["heading"] = ImageFont.load_default()
        fonts["label"] = ImageFont.load_default()
        fonts["small"] = ImageFont.load_default()

    try:
        if mono_font:
            fonts["text"] = ImageFont.truetype(mono_font, 24)
            fonts["mono_small"] = ImageFont.truetype(mono_font, 14)
        else:
            raise Exception("No mono font found")
    except:
        fonts["text"] = ImageFont.load_default()
        fonts["mono_small"] = ImageFont.load_default()

    return fonts


def generate_color_image(hex_color: str, output_path: str):
    """Create a PNG image showing color spectrum - matches ex/generate_color_image.py exactly"""

    if not PIL_AVAILABLE:
        raise ImportError(
            "Pillow library is required. Install with: pip install pillow"
        )

    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)

    # Image dimensions
    width = 1200
    height = 1300

    # Create image
    img = Image.new('RGB', (width, height), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        heading_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        text_font = ImageFont.truetype("/System/Library/Fonts/Courier.ttc", 24)
        label_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        small_font = ImageFont.truetype("/System/Library/Fonts/Courier.ttc", 14)
    except:
        title_font = heading_font = text_font = label_font = small_font = ImageFont.load_default()

    # Title
    title = "Color Spectrum Visualizer"
    draw.text((width//2, 40), title, fill=(51, 51, 51), font=title_font, anchor="mm")

    # Main color swatch
    swatch_size = 250
    swatch_x = 100
    swatch_y = 120
    draw.rounded_rectangle(
        [(swatch_x, swatch_y), (swatch_x + swatch_size, swatch_y + swatch_size)],
        radius=20,
        fill=(r, g, b),
        outline=(255, 255, 255),
        width=4
    )

    # Color information
    info_x = swatch_x + swatch_size + 80
    info_y = swatch_y + 20

    draw.text((info_x, info_y), hex_color, fill=(51, 51, 51), font=heading_font)

    # Color values
    values = [
        ("RGB", f"rgb({r}, {g}, {b})"),
        ("HSL", f"hsl({int(h*360)}°, {int(s*100)}%, {int(l*100)}%)"),
        ("HEX", hex_color),
    ]

    y_offset = info_y + 60
    for label, value in values:
        # Background box
        box_y = y_offset - 5
        draw.rounded_rectangle(
            [(info_x, box_y), (info_x + 450, box_y + 50)],
            radius=8,
            fill=(255, 255, 255),
            outline=(230, 230, 230),
            width=2
        )

        draw.text((info_x + 15, y_offset), label, fill=(136, 136, 136), font=label_font)
        draw.text((info_x + 15, y_offset + 22), value, fill=(51, 51, 51), font=text_font)
        y_offset += 70

    # Spectrum sections
    spectrum_y = 420

    # Hue Spectrum
    draw.text((100, spectrum_y), "Hue Spectrum", fill=(51, 51, 51), font=heading_font)
    spectrum_y += 50
    bar_width = (width - 200) // 24
    bar_height = 80

    for i in range(24):
        hue = i / 24
        rgb = hsl_to_rgb(hue, s, l)
        x = 100 + i * bar_width
        draw.rectangle(
            [(x, spectrum_y), (x + bar_width - 2, spectrum_y + bar_height)],
            fill=rgb
        )

    spectrum_y += bar_height + 40

    # Color Palette Recommendations
    draw.text((100, spectrum_y), "Recommended Color Palettes", fill=(51, 51, 51), font=heading_font)
    spectrum_y += 50

    palettes = generate_palette_colors(h, s, l)
    palette_box_width = 280
    palette_box_height = 100

    palette_names = ['Complementary', 'Analogous', 'Triadic', 'Split Complementary', 'Monochromatic']

    for idx, palette_name in enumerate(palette_names):
        row = idx // 3
        col = idx % 3

        x_pos = 100 + col * (palette_box_width + 60)
        y_pos = spectrum_y + row * (palette_box_height + 90)

        # Draw palette name
        draw.text((x_pos, y_pos), palette_name, fill=(51, 51, 51), font=label_font)

        # Draw color swatches
        colors = palettes[palette_name]
        swatch_width = palette_box_width // len(colors)

        for i, color in enumerate(colors):
            swatch_x = x_pos + i * swatch_width
            draw.rounded_rectangle(
                [(swatch_x, y_pos + 30), (swatch_x + swatch_width - 4, y_pos + 30 + palette_box_height)],
                radius=8,
                fill=color,
                outline=(255, 255, 255),
                width=3
            )

            # Add hex code below each swatch
            color_hex = f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"
            bbox = draw.textbbox((0, 0), color_hex, font=small_font)
            text_width = bbox[2] - bbox[0]
            text_x = swatch_x + (swatch_width - text_width) // 2 - 2

            # Draw text with semi-transparent background for readability
            draw.rectangle(
                [(swatch_x + 2, y_pos + 30 + palette_box_height - 28),
                 (swatch_x + swatch_width - 6, y_pos + 30 + palette_box_height - 6)],
                fill=(0, 0, 0)
            )
            draw.text((text_x, y_pos + 30 + palette_box_height - 25), color_hex,
                     fill=(255, 255, 255), font=small_font)

    spectrum_y += (2 * (palette_box_height + 90)) + 40

    # Saturation Spectrum
    draw.text((100, spectrum_y), "Saturation Spectrum", fill=(51, 51, 51), font=heading_font)
    spectrum_y += 50

    for i in range(11):
        saturation = i / 10
        rgb = hsl_to_rgb(h, saturation, l)
        x = 100 + i * (bar_width * 2)
        draw.rectangle(
            [(x, spectrum_y), (x + bar_width * 2 - 2, spectrum_y + bar_height)],
            fill=rgb
        )

    # Save image
    img.save(output_path, 'PNG')
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# FILE OPENING (CROSS-PLATFORM)
# ═══════════════════════════════════════════════════════════════════════════════


def open_file(filepath: str):
    """Open a file with the default application (cross-platform)"""
    system = platform.system()

    if system == "Darwin":  # macOS
        subprocess.run(["open", filepath])
    elif system == "Windows":
        subprocess.run(["start", filepath], shell=True)
    else:  # Linux and others
        subprocess.run(["xdg-open", filepath])


# ═══════════════════════════════════════════════════════════════════════════════
# GUI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════


def run_gui():
    """Run GUI mode - uses native macOS dialogs via osascript for reliability"""

    # Use native macOS dialog (works reliably in .app bundles)
    if platform.system() == "Darwin":
        dialog_text = (
            "Enter a color value:\\n\\n"
            "Supported formats:\\n"
            "- HEX: #ffb6c1 or ffb6c1\\n"
            "- RGB: rgb(255, 182, 193) or 255,182,193\\n"
            "- CMYK: cmyk(0, 29, 24, 0)\\n"
            "- HSL: hsl(351, 100, 86)\\n"
            "- HSB/HSV: hsb(351, 29, 100)"
        )

        applescript = f'''
        tell application "System Events"
            activate
            set colorInput to text returned of (display dialog "{dialog_text}" default answer "#ffb6c1" buttons {{"Cancel", "Visualize"}} default button "Visualize")
        end tell
        '''

        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                color_input = result.stdout.strip()

                if color_input:
                    try:
                        r, g, b = parse_color_input(color_input)
                        hex_color = rgb_to_hex(r, g, b)

                        # Generate image
                        output_path = os.path.join(tempfile.gettempdir(), "color_spectrum.png")
                        generate_color_image(hex_color, output_path)

                        # Open the image
                        open_file(output_path)

                    except ValueError:
                        subprocess.run(["osascript", "-e",
                                      f'display dialog "Could not parse color: {color_input}" buttons {{"OK"}} default button "OK" with icon stop'])
                    except Exception as e:
                        subprocess.run(["osascript", "-e",
                                      f'display dialog "Error: {str(e)}" buttons {{"OK"}} default button "OK" with icon stop'])
        except:
            pass

    else:
        # Fallback to Tkinter for non-macOS systems
        root = tk.Tk()
        root.withdraw()
        root.lift()
        root.attributes('-topmost', True)
        root.update()

        dialog_text = (
            "Supported formats:\n"
            "• HEX: #ffb6c1 or ffb6c1\n"
            "• RGB: rgb(255, 182, 193) or 255,182,193\n"
            "• CMYK: cmyk(0, 29, 24, 0)\n"
            "• HSL: hsl(351, 100, 86)\n"
            "• HSB/HSV: hsb(351, 29, 100)"
        )

        color_input = simpledialog.askstring(
            "Color Visualizer",
            f"Enter a color value:\n\n{dialog_text}",
            initialvalue="#ffb6c1",
            parent=root
        )

        if color_input:
            try:
                r, g, b = parse_color_input(color_input)
                hex_color = rgb_to_hex(r, g, b)

                output_path = os.path.join(tempfile.gettempdir(), "color_spectrum.png")
                generate_color_image(hex_color, output_path)
                open_file(output_path)

            except ValueError:
                messagebox.showerror("Error", f"Could not parse color: {color_input}", parent=root)
            except Exception as e:
                messagebox.showerror("Error", f"Error generating spectrum: {str(e)}", parent=root)

        root.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI MODE
# ═══════════════════════════════════════════════════════════════════════════════


def cli_mode():
    """Run in command-line interface mode"""
    print("=" * 60)
    print("🎨 Color Visualizer - Cross-Platform Edition")
    print("=" * 60)
    print()
    print("Supported formats:")
    print("  • HEX: #ffb6c1 or ffb6c1")
    print("  • RGB: rgb(255, 182, 193) or 255,182,193")
    print("  • CMYK: cmyk(0, 29, 24, 0)")
    print("  • HSL: hsl(351, 100, 86)")
    print("  • HSB/HSV: hsb(351, 29, 100)")
    print()

    color_input = input("Enter a color value (or 'q' to quit): ").strip()

    if color_input.lower() == "q":
        print("Goodbye!")
        return

    try:
        r, g, b = parse_color_input(color_input)
        hex_color = rgb_to_hex(r, g, b)

        print(f"\n✅ Parsed color: {hex_color}")
        print(f"   RGB: ({r}, {g}, {b})")

        h, s, l = rgb_to_hsl(r, g, b)
        print(f"   HSL: ({int(h*360)}°, {int(s*100)}%, {int(l*100)}%)")

        print("\n⏳ Generating spectrum image...")

        output_path = os.path.join(tempfile.gettempdir(), "color_spectrum.png")
        generate_color_image(hex_color, output_path)

        print(f"✅ Spectrum saved to: {output_path}")
        print("📂 Opening in default viewer...")

        open_file(output_path)

    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Failed to generate spectrum: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    """Main entry point"""

    # Check for Pillow
    if not PIL_AVAILABLE:
        print("❌ Error: Pillow library is required.")
        print("   Install with: pip install pillow")
        sys.exit(1)

    # Command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        # Force CLI mode
        if arg == "--cli":
            cli_mode()
            return

        # Direct color input
        if arg == "--help" or arg == "-h":
            print(__doc__)
            return

        # Assume it's a color input
        try:
            r, g, b = parse_color_input(arg)
            hex_color = rgb_to_hex(r, g, b)

            output_path = (
                sys.argv[2]
                if len(sys.argv) > 2
                else os.path.join(tempfile.gettempdir(), "color_spectrum.png")
            )

            print(f"🎨 Generating spectrum for {hex_color}...")
            generate_color_image(hex_color, output_path)
            print(f"✅ Saved to: {output_path}")

            if len(sys.argv) <= 2:
                open_file(output_path)

        except ValueError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        return

    # GUI mode (default)
    if TK_AVAILABLE:
        run_gui()
    else:
        # Fall back to CLI if Tkinter not available
        print("⚠️  Tkinter not available, using CLI mode...")
        cli_mode()


if __name__ == "__main__":
    main()
