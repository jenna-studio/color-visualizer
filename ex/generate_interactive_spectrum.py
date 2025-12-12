#!/usr/bin/env python3
"""
Interactive Color Spectrum Generator
Creates an HTML-based interactive color picker with clickable colors
"""

import sys
import colorsys

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    """Convert RGB to hex color"""
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"

def rgb_to_hsl(r, g, b):
    """Convert RGB (0-255) to HSL (0-1 range)"""
    r, g, b = r/255, g/255, b/255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h, s, l)

def hsl_to_rgb(h, s, l):
    """Convert HSL to RGB (0-255 range)"""
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))

def generate_interactive_html(hex_color, output_path):
    """Create an interactive HTML color picker"""

    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)

    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Interactive Color Spectrum</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 1000px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.2rem;
        }}
        .main-color {{
            display: flex;
            gap: 30px;
            align-items: center;
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 16px;
        }}
        .color-swatch {{
            width: 200px;
            height: 200px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            border: 4px solid white;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .color-swatch:hover {{
            transform: scale(1.05);
        }}
        .color-info {{
            flex: 1;
        }}
        .color-info h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 2rem;
        }}
        .color-values {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}
        .color-value {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .color-value:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .color-value-label {{
            font-size: 0.75rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }}
        .color-value-data {{
            font-family: 'Monaco', monospace;
            font-size: 0.95rem;
            color: #333;
            font-weight: 600;
        }}
        .spectrum-section {{
            margin-bottom: 30px;
        }}
        .spectrum-section h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }}
        .spectrum-container {{
            display: flex;
            gap: 4px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 12px;
        }}
        .spectrum-bar {{
            flex: 1;
            height: 80px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }}
        .spectrum-bar:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            z-index: 10;
        }}
        .spectrum-bar:hover::after {{
            content: attr(data-color);
            position: absolute;
            bottom: -30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8rem;
            white-space: nowrap;
            font-family: monospace;
        }}
        .notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            display: none;
            animation: slideIn 0.3s ease;
            z-index: 1000;
        }}
        @keyframes slideIn {{
            from {{ transform: translateX(400px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s;
            margin-top: 20px;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }}
        .btn:hover {{
            transform: scale(1.05);
        }}
    </style>
</head>
<body>
    <div class="notification" id="notification"></div>
    <div class="container">
        <h1>🎨 Interactive Color Spectrum</h1>

        <div class="main-color">
            <div class="color-swatch" style="background-color: {hex_color};"
                 onclick="copyColor('{hex_color}')"
                 title="Click to copy HEX"></div>
            <div class="color-info">
                <h2 id="mainColorHex">{hex_color}</h2>
                <div class="color-values">
                    <div class="color-value" onclick="copyColor('{hex_color}')">
                        <div class="color-value-label">HEX</div>
                        <div class="color-value-data">{hex_color}</div>
                    </div>
                    <div class="color-value" onclick="copyColor('rgb({r}, {g}, {b})')">
                        <div class="color-value-label">RGB</div>
                        <div class="color-value-data">rgb({r}, {g}, {b})</div>
                    </div>
                    <div class="color-value" onclick="copyColor('hsl({int(h*360)}, {int(s*100)}%, {int(l*100)}%)')">
                        <div class="color-value-label">HSL</div>
                        <div class="color-value-data">hsl({int(h*360)}°, {int(s*100)}%, {int(l*100)}%)</div>
                    </div>
                    <div class="color-value">
                        <div class="color-value-label">CLICK ANY COLOR</div>
                        <div class="color-value-data" style="font-size: 0.8rem;">To pick & visualize</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="spectrum-section">
            <h3>🌈 Hue Spectrum (0° - 360°)</h3>
            <div class="spectrum-container" id="hueSpectrum"></div>
        </div>

        <div class="spectrum-section">
            <h3>💡 Lightness Spectrum (0% - 100%)</h3>
            <div class="spectrum-container" id="lightnessSpectrum"></div>
        </div>

        <div class="spectrum-section">
            <h3>✨ Saturation Spectrum (0% - 100%)</h3>
            <div class="spectrum-container" id="saturationSpectrum"></div>
        </div>
    </div>

    <script>
        const baseColor = {{
            hex: "{hex_color}",
            r: {r},
            g: {g},
            b: {b},
            h: {h},
            s: {s},
            l: {l}
        }};

        function hslToRgb(h, s, l) {{
            let r, g, b;
            if (s === 0) {{
                r = g = b = l;
            }} else {{
                const hue2rgb = (p, q, t) => {{
                    if (t < 0) t += 1;
                    if (t > 1) t -= 1;
                    if (t < 1/6) return p + (q - p) * 6 * t;
                    if (t < 1/2) return q;
                    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                    return p;
                }};
                const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
                const p = 2 * l - q;
                r = hue2rgb(p, q, h + 1/3);
                g = hue2rgb(p, q, h);
                b = hue2rgb(p, q, h - 1/3);
            }}
            return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
        }}

        function rgbToHex(r, g, b) {{
            return '#' + [r, g, b].map(x => {{
                const hex = x.toString(16);
                return hex.length === 1 ? '0' + hex : hex;
            }}).join('').toUpperCase();
        }}

        function generateHueSpectrum() {{
            const container = document.getElementById('hueSpectrum');
            for (let i = 0; i < 36; i++) {{
                const hue = i / 36;
                const [r, g, b] = hslToRgb(hue, baseColor.s, baseColor.l);
                const hex = rgbToHex(r, g, b);
                const bar = document.createElement('div');
                bar.className = 'spectrum-bar';
                bar.style.backgroundColor = hex;
                bar.setAttribute('data-color', hex);
                bar.onclick = () => pickColor(hex);
                container.appendChild(bar);
            }}
        }}

        function generateLightnessSpectrum() {{
            const container = document.getElementById('lightnessSpectrum');
            for (let i = 0; i <= 10; i++) {{
                const lightness = i / 10;
                const [r, g, b] = hslToRgb(baseColor.h, baseColor.s, lightness);
                const hex = rgbToHex(r, g, b);
                const bar = document.createElement('div');
                bar.className = 'spectrum-bar';
                bar.style.backgroundColor = hex;
                bar.setAttribute('data-color', hex);
                bar.onclick = () => pickColor(hex);
                container.appendChild(bar);
            }}
        }}

        function generateSaturationSpectrum() {{
            const container = document.getElementById('saturationSpectrum');
            for (let i = 0; i <= 10; i++) {{
                const saturation = i / 10;
                const [r, g, b] = hslToRgb(baseColor.h, saturation, baseColor.l);
                const hex = rgbToHex(r, g, b);
                const bar = document.createElement('div');
                bar.className = 'spectrum-bar';
                bar.style.backgroundColor = hex;
                bar.setAttribute('data-color', hex);
                bar.onclick = () => pickColor(hex);
                container.appendChild(bar);
            }}
        }}

        function copyColor(colorValue) {{
            navigator.clipboard.writeText(colorValue).then(() => {{
                showNotification('Copied: ' + colorValue);
            }});
        }}

        function pickColor(hex) {{
            showNotification('Picked: ' + hex + ' - Generating new spectrum...');
            // Use AppleScript to re-run the app with the new color
            setTimeout(() => {{
                window.location.href = 'colorvisualizer://pick/' + hex.replace('#', '');
            }}, 500);
        }}

        function showNotification(message) {{
            const notif = document.getElementById('notification');
            notif.textContent = message;
            notif.style.display = 'block';
            setTimeout(() => {{
                notif.style.display = 'none';
            }}, 2000);
        }}

        // Generate all spectrums on load
        generateHueSpectrum();
        generateLightnessSpectrum();
        generateSaturationSpectrum();
    </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Interactive spectrum saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 generate_interactive_spectrum.py <hex_color> <output_path>")
        sys.exit(1)

    hex_color = sys.argv[1]
    output_path = sys.argv[2]

    generate_interactive_html(hex_color, output_path)
