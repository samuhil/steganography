from PIL import Image

def encode_image(carrier_path, secret_path, output_path):
    """Hide secret_image inside carrier_image using 4-bit LSB steganography."""
    carrier = Image.open(carrier_path).convert('RGB')
    secret = Image.open(secret_path).convert('RGB')

    if secret.width > carrier.width or secret.height > carrier.height:
        raise ValueError("Secret image must be same size or smaller than carrier.")

    output = Image.new('RGB', carrier.size)
    carrier_px = carrier.load()
    secret_px = secret.load()
    output_px = output.load()

    for y in range(carrier.height):
        for x in range(carrier.width):
            r1, g1, b1 = carrier_px[x, y]

            if x < secret.width and y < secret.height:
                r2, g2, b2 = secret_px[x, y]
            else:
                r2, g2, b2 = 0, 0, 0  # pad with black if secret is smaller

            # keep top 4 bits of carrier, embed top 4 bits of secret in bottom 4 bits
            r = (r1 & 0xF0) | (r2 >> 4)
            g = (g1 & 0xF0) | (g2 >> 4)
            b = (b1 & 0xF0) | (b2 >> 4)

            output_px[x, y] = (r, g, b)

    output.save(output_path, 'PNG')
    print(f"Saved merged image to {output_path}")


def decode_image(merged_path, output_path):
    """Extract the hidden image from a merged image."""
    merged = Image.open(merged_path).convert('RGB')
    output = Image.new('RGB', merged.size)

    merged_px = merged.load()
    output_px = output.load()

    for y in range(merged.height):
        for x in range(merged.width):
            r, g, b = merged_px[x, y]

            # take bottom 4 bits (the hidden data) and shift back to top 4 bits
            r_out = (r & 0x0F) << 4
            g_out = (g & 0x0F) << 4
            b_out = (b & 0x0F) << 4

            output_px[x, y] = (r_out, g_out, b_out)

    output.save(output_path, 'PNG')
    print(f"Saved extracted image to {output_path}")


# Example usage:
if __name__ == '__main__':
    encode_image('carrier.jpg', 'secret.jpg', 'merged.png')
    decode_image('merged.png', 'extracted.png')
