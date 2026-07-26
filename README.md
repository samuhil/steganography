# Steganography — Hiding an Image (or Message) Inside Another

A lightweight, browser-based steganography tool that hides a secret image **or** a text message inside a cover image using pixel-level bit manipulation. Everything runs client-side — no uploads, no backend, no data ever leaves your browser.

 **[Try it live](https://samuhil.github.io/steganography/)**

---

##  Features

- **Text in Image** — hide a secret message inside an image, with an optional password/key
- **Image in Image** — hide an entire second image inside a cover image
- 100% client-side — runs entirely in your browser using HTML5 Canvas
- No installation, no dependencies, no server

---

##  What is Steganography?

Steganography is the practice of concealing a file, message, image, or video within another file, message, image, or video.

**Why steganography over cryptography?**
An encrypted message is unbreakable, but it's *visible* as an encrypted message — which can itself draw suspicion (or trouble, in places where encryption is restricted). Steganography instead hides the message in plain sight, so it never looks like there's anything to find. The tradeoff: once someone knows to look, the hidden content is easier to extract than something properly encrypted.

---

##  How It Works

### Digital images & pixels
A digital image is just a grid (matrix) of pixels. Each pixel holds color values — and more pixels means a more detailed, accurate image.

<img width="4991" height="2807" alt="image" src="https://github.com/user-attachments/assets/e9a8fcb4-39f0-4618-ac35-7ca54ca35720" />

### The RGB color model
Each pixel is made of three 8-bit values: **Red, Green, and Blue** (each ranging 0–255). These three channels combine to produce the full range of visible colors.

<img width="650" height="233" alt="image" src="https://github.com/user-attachments/assets/c803421c-af83-4155-85e6-c540a0e2cb59" />

### Most vs. least significant bits
In an 8-bit binary number:
- The **leftmost bit** is the *most significant* — changing it drastically shifts the value.
  `11111111 → 01111111` drops the value from 255 to 127.
- The **rightmost bit** is the *least significant* — changing it barely matters.
  `11111111 → 11111110` only drops the value from 255 to 254 (under a 1% shift).

<img width="610" height="397" alt="image" src="https://github.com/user-attachments/assets/d9034b78-2b9c-4593-b739-1d65275bd1c3" />

### The steganography trick
Since changing the rightmost (least significant) bits has almost no visible effect, this app **replaces the least significant bits of a "cover" image with the most significant bits of a "secret" image** (for image-in-image mode), or flips a single least-significant bit per color channel to encode message bits (for text-in-image mode). The cover image still looks normal to the eye, but it now secretly contains the hidden data — recoverable by reversing the process.

<img width="1989" height="648" alt="image" src="https://github.com/user-attachments/assets/2f32db57-4e0f-4bcd-a6e0-12c148222bc1" />

*(Top row: original cover image and secret image. Bottom row: merged output and the extracted secret image.)*

Some image quality is lost in the process, but it doesn't meaningfully affect visual comprehension of either image.

---

##  Usage

This is a **single self-contained HTML file** — no installation required.

1. Download or clone this repo
2. Open `steganography_app.html` directly in any modern browser (or visit the [live version](#))
3. Toggle between **Encode** / **Decode** mode
4. Choose **Text in Image** or **Image in Image**
5. Upload your carrier image (and secret image or message)
6. Click the action button, then download your result

```bash
git clone https://github.com/samuhil/steganography.git
cd steganography
open steganography_app.html   # or just double-click the file
```

> Merged/encoded images are exported as **PNG**. Don't re-save or re-compress them as JPEG — this destroys the hidden data.

---

## Python Equivalents

If you'd rather do this in Python instead of the browser, here's code matching the exact same encoding logic used in the app.

### Image in Image

```python
from PIL import Image

def encode_image(carrier_path, secret_path, output_path):
    """Hide secret_image inside carrier_image using 4-bit LSB steganography."""
    carrier = Image.open(carrier_path).convert('RGB')
    secret = Image.open(secret_path).convert('RGB')

    if secret.width > carrier.width or secret.height > carrier.height:
        raise ValueError("Secret image must be same size or smaller than carrier.")

    output = Image.new('RGB', carrier.size)
    carrier_px, secret_px, output_px = carrier.load(), secret.load(), output.load()

    for y in range(carrier.height):
        for x in range(carrier.width):
            r1, g1, b1 = carrier_px[x, y]
            r2, g2, b2 = secret_px[x, y] if x < secret.width and y < secret.height else (0, 0, 0)
            output_px[x, y] = (
                (r1 & 0xF0) | (r2 >> 4),
                (g1 & 0xF0) | (g2 >> 4),
                (b1 & 0xF0) | (b2 >> 4),
            )

    output.save(output_path, 'PNG')


def decode_image(merged_path, output_path):
    """Extract the hidden image from a merged image."""
    merged = Image.open(merged_path).convert('RGB')
    output = Image.new('RGB', merged.size)
    merged_px, output_px = merged.load(), output.load()

    for y in range(merged.height):
        for x in range(merged.width):
            r, g, b = merged_px[x, y]
            output_px[x, y] = ((r & 0x0F) << 4, (g & 0x0F) << 4, (b & 0x0F) << 4)

    output.save(output_path, 'PNG')
```

### Text in Image

```python
from PIL import Image

MARKER = '\x00\x00\x00'

def simple_hash(s):
    h = 5381
    for ch in s:
        h = ((h << 5) + h) + ord(ch)
    return h & 0xFFFF

def simple_xor(s, key):
    if not key:
        return s
    return ''.join(chr(ord(s[i]) ^ ord(key[i % len(key)])) for i in range(len(s)))

def str_to_binary(s):
    return ''.join(format(ord(ch), '08b') for ch in s)

def binary_to_str(bits):
    out = ''
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        c = int(byte, 2)
        if c == 0:
            break
        out += chr(c)
    return out

def encode_text(carrier_path, message, output_path, key=None):
    carrier = Image.open(carrier_path).convert('RGB')

    if key:
        h = simple_hash(key)
        message = chr(h & 0xFF) + chr((h >> 8) & 0xFF) + simple_xor(message, key) + MARKER
    else:
        message = message + MARKER

    bin_msg = str_to_binary(message)
    if len(bin_msg) > carrier.width * carrier.height * 3:
        raise ValueError("Message too long for this image.")

    pixels = carrier.load()
    bit_index = 0
    for y in range(carrier.height):
        for x in range(carrier.width):
            channels = list(pixels[x, y])
            for c in range(3):
                if channels[c] % 2 != 0:
                    channels[c] -= 1
                if bit_index < len(bin_msg):
                    channels[c] += int(bin_msg[bit_index])
                    bit_index += 1
            pixels[x, y] = tuple(channels)

    carrier.save(output_path, 'PNG')

def decode_text(encoded_path, key=None):
    img = Image.open(encoded_path).convert('RGB')
    pixels = img.load()

    bits = []
    for y in range(img.height):
        for x in range(img.width):
            for val in pixels[x, y]:
                bits.append('1' if val % 2 != 0 else '0')

    raw = binary_to_str(''.join(bits))

    if key:
        if len(raw) < 2:
            return None
        stored_hash = ord(raw[0]) | (ord(raw[1]) << 8)
        if stored_hash != simple_hash(key):
            return None
        raw = simple_xor(raw[2:], key)

    return raw or None
```

> Note: text encoding assumes Latin-1/ASCII characters, and the XOR "password" is basic obfuscation, not real encryption.

---

##  License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
