"""
Creates a unique QR code for each name in names.txt
"""

import qrcode

with open("names.txt", encoding="utf-8") as f:
    text = f.read()
members = text.splitlines()

for name in members:
    img = qrcode.make(name)
    # can adjust save location if you'd like
    img.save(f"{name}_QR_Code.png")
