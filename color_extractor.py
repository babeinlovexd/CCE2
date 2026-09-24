from PIL import Image
from collections import Counter

def extract_colors():
    img = Image.open('assets/icon.png').convert('RGBA')
    # Resize to speed up and average colors a bit
    img = img.resize((100, 100))
    colors = img.getdata()

    # Filter out transparent pixels and nearly pure black (assuming it's background or just very common line art)
    valid_colors = []
    for r, g, b, a in colors:
        if a > 128 and not (r < 10 and g < 10 and b < 10):
            valid_colors.append((r//16*16, g//16*16, b//16*16))

    counter = Counter(valid_colors)
    # Get top 5 colors
    top_colors = counter.most_common(10)

    for color, count in top_colors:
        hex_color = "#{:02x}{:02x}{:02x}".format(*color)
        print(f"Color: {color} Hex: {hex_color} Count: {count}")

if __name__ == "__main__":
    extract_colors()
