#!/usr/bin/env python3
"""
Color Spectrum Generator using Pillow
Generates a visual color spectrum image showing:
- Main color swatch
- Hue spectrum
- Lightness spectrum
- Saturation spectrum
"""

import sys
from PIL import Image, ImageDraw, ImageFont
import colorsys

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    """Convert RGB to hex color"""
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"

def hsl_to_rgb(h, s, l):
    """Convert HSL to RGB (0-255 range)"""
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))

def rgb_to_hsl(r, g, b):
    """Convert RGB (0-255) to HSL (0-1 range)"""
    r, g, b = r/255, g/255, b/255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h, s, l)

def get_text_color(bg_r, bg_g, bg_b):
    """Determine if text should be black or white based on background"""
    luminance = (0.299 * bg_r + 0.587 * bg_g + 0.114 * bg_b) / 255
    return (0, 0, 0) if luminance > 0.5 else (255, 255, 255)

def create_spectrum_image(hex_color, output_path):
    """Create a visual spectrum image"""

    # Parse input color
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)

    # Image dimensions
    width = 1000
    height = 900
    margin = 40

    # Create image
    img = Image.new('RGB', (width, height), (250, 250, 250))
    draw = ImageDraw.Draw(img)

    # Try to load a font
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        regular_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    y = margin

    # Title
    draw.text((width // 2, y), "COLOR SPECTRUM VISUALIZER", fill=(51, 51, 51),
              font=title_font, anchor="mt")
    y += 60

    # Main color swatch
    swatch_size = 200
    swatch_x = (width - swatch_size) // 2
    draw.rectangle([swatch_x, y, swatch_x + swatch_size, y + swatch_size],
                   fill=(r, g, b), outline=(100, 100, 100), width=3)

    # Color info next to swatch
    info_x = swatch_x + swatch_size + 30
    info_y = y + 20
    text_color = (51, 51, 51)

    draw.text((info_x, info_y), hex_color, fill=text_color, font=header_font)
    info_y += 40
    draw.text((info_x, info_y), f"RGB: ({r}, {g}, {b})", fill=text_color, font=regular_font)
    info_y += 30
    draw.text((info_x, info_y), f"HSL: ({int(h*360)}°, {int(s*100)}%, {int(l*100)}%)",
              fill=text_color, font=regular_font)

    y += swatch_size + 50

    # Hue Spectrum
    draw.text((margin, y), "🌈 HUE SPECTRUM (0° - 360°)", fill=(51, 51, 51), font=header_font)
    y += 40

    bar_width = (width - 2 * margin) // 36
    bar_height = 80
    x = margin

    for i in range(36):
        hue = i / 36
        color = hsl_to_rgb(hue, s, l)
        draw.rectangle([x, y, x + bar_width - 2, y + bar_height], fill=color)

        # Show degree labels for every 60 degrees
        if i % 6 == 0:
            degree = int(hue * 360)
            draw.text((x + bar_width // 2, y + bar_height + 5), f"{degree}°",
                     fill=(51, 51, 51), font=small_font, anchor="mt")

        x += bar_width

    y += bar_height + 35

    # Lightness Spectrum
    draw.text((margin, y), "💡 LIGHTNESS SPECTRUM (0% - 100%)", fill=(51, 51, 51), font=header_font)
    y += 40

    bar_count = 11
    bar_width = (width - 2 * margin) // bar_count
    x = margin

    for i in range(bar_count):
        light = i / (bar_count - 1)
        color = hsl_to_rgb(h, s, light)
        draw.rectangle([x, y, x + bar_width - 2, y + bar_height], fill=color)

        # Labels
        pct = int(light * 100)
        text_col = get_text_color(*color)
        draw.text((x + bar_width // 2, y + bar_height // 2), f"{pct}%",
                 fill=text_col, font=small_font, anchor="mm")

        x += bar_width

    y += bar_height + 30

    # Saturation Spectrum
    draw.text((margin, y), "✨ SATURATION SPECTRUM (0% - 100%)", fill=(51, 51, 51), font=header_font)
    y += 40

    x = margin

    for i in range(bar_count):
        sat = i / (bar_count - 1)
        color = hsl_to_rgb(h, sat, l)
        draw.rectangle([x, y, x + bar_width - 2, y + bar_height], fill=color)

        # Labels
        pct = int(sat * 100)
        text_col = get_text_color(*color)
        draw.text((x + bar_width // 2, y + bar_height // 2), f"{pct}%",
                 fill=text_col, font=small_font, anchor="mm")

        x += bar_width

    # Save image
    img.save(output_path, 'PNG')
    print(f"Spectrum image saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 generate_color_spectrum.py <hex_color> <output_path>")
        sys.exit(1)

    hex_color = sys.argv[1]
    output_path = sys.argv[2]

    create_spectrum_image(hex_color, output_path)
