#!/usr/bin/env python3
"""
Color Spectrum Image Generator
Creates a PNG image showing color information and spectrum variations
"""

import sys
from PIL import Image, ImageDraw, ImageFont

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hsl(r, g, b):
    """Convert RGB (0-255) to HSL"""
    r, g, b = r/255, g/255, b/255
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2

    if max_c == min_c:
        h = s = 0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)

        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6

    return (h, s, l)

def hsl_to_rgb(h, s, l):
    """Convert HSL to RGB (0-255 range)"""
    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p

    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return (int(r * 255), int(g * 255), int(b * 255))

def generate_palette_colors(h, s, l):
    """Generate color palette recommendations"""
    palettes = {}

    # Complementary (opposite on color wheel)
    comp_h = (h + 0.5) % 1.0
    palettes['Complementary'] = [
        hsl_to_rgb(h, s, l),
        hsl_to_rgb(comp_h, s, l)
    ]

    # Analogous (adjacent colors)
    palettes['Analogous'] = [
        hsl_to_rgb((h - 0.083) % 1.0, s, l),
        hsl_to_rgb(h, s, l),
        hsl_to_rgb((h + 0.083) % 1.0, s, l)
    ]

    # Triadic (evenly spaced)
    palettes['Triadic'] = [
        hsl_to_rgb(h, s, l),
        hsl_to_rgb((h + 0.333) % 1.0, s, l),
        hsl_to_rgb((h + 0.666) % 1.0, s, l)
    ]

    # Split Complementary
    palettes['Split Complementary'] = [
        hsl_to_rgb(h, s, l),
        hsl_to_rgb((h + 0.417) % 1.0, s, l),
        hsl_to_rgb((h + 0.583) % 1.0, s, l)
    ]

    # Monochromatic (same hue, different lightness)
    palettes['Monochromatic'] = [
        hsl_to_rgb(h, s, max(0, l - 0.2)),
        hsl_to_rgb(h, s, l),
        hsl_to_rgb(h, s, min(1, l + 0.2))
    ]

    return palettes

def generate_color_image(hex_color, output_path):
    """Create a PNG image showing color spectrum"""

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
    except:
        title_font = heading_font = text_font = label_font = ImageFont.load_default()

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

    try:
        small_font = ImageFont.truetype("/System/Library/Fonts/Courier.ttc", 14)
    except:
        small_font = ImageFont.load_default()

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
    print(f"Color spectrum image saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 generate_color_image.py <hex_color> <output_path>")
        sys.exit(1)

    hex_color = sys.argv[1]
    output_path = sys.argv[2]

    generate_color_image(hex_color, output_path)
