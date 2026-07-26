#  Steganography — Hiding an Image Inside Another

A lightweight Python tool that hides one image inside another using pixel-level bit manipulation. The result looks nearly identical to the original — but secretly holds a second image inside it.


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
Since changing the rightmost (least significant) bits has almost no visible effect, we can **replace the least significant bits of a "cover" image with the most significant bits of a "secret" image.** The cover image still looks normal to the eye, but it now secretly contains the second image — recoverable by reversing the process.

<img width="1989" height="648" alt="image" src="https://github.com/user-attachments/assets/2f32db57-4e0f-4bcd-a6e0-12c148222bc1" />


*(Top row: original cover image and secret image. Bottom row: merged output and the extracted secret image.)*

Some image quality is lost in the process, but it doesn't meaningfully affect visual comprehension of either image.

---

##  Installation

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

##  Usage

**Merge two images** (hide `image2` inside `image1`):
```bash
python steganography.py merge --image1=res/image1.jpg --image2=res/image2.jpg --output=res/output.png
```

**Unmerge** (extract the hidden image):
```bash
python steganography.py unmerge --image=res/output.png --output=res/output2.png
```

>  The merge output and unmerge input must be PNG files.

### Using it in your own code

```python
from PIL import Image
from steganography import Steganography

merged_image = Steganography().merge(Image.open(image1), Image.open(image2))
merged_image.save(output)
```

---

##  License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
