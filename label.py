import os
import re
from io import BytesIO

import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont


def print_label(text, wifi, count):
    if count == 0:
        return
    if text:
        img = create_image_uisp(text)
        print_image(img, count)
    if wifi:
        img = create_image_fri(wifi)
        print_image(img, count)


def create_image_uisp(text):
    length = 3
    font_size = 64
    width = 696
    img = Image.new('RGB', (width, int(length * font_size)), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('arial-bold.ttf', font_size)
    for i, line in enumerate(text.splitlines()):
        draw.text((0, i * font_size), line, font=font, fill=(0, 0, 0))
    return img


def create_image_fri(wifi):
    escape_re = re.compile(r'(?<!\\)([\\;,:"])')
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=7,
        border=4,
    )
    s = "WIFI:S:" + escape_re.sub(r'\\\1', wifi["ssid"]) + ";T:WPA;P:" + escape_re.sub(r'\\\1', wifi["psk"]) + ";"
    qr.add_data(s)
    qr.make(fit=True)
    qr = qr.make_image(fill_color="black", back_color="white")
    length = 3.25
    font_size = 64
    width = 696
    img = Image.new('RGB', (width, int(length * font_size) + qr.size[1]), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('arial-bold.ttf', font_size)
    smallfont = ImageFont.truetype('arial-bold.ttf', font_size // 2)
    wifiname_size = draw.textlength("Wi-Fi Name", font=smallfont)
    wifipassword_size = draw.textlength("Wi-Fi Password", font=smallfont)
    draw.text(((width - wifiname_size)/2, 0 * font_size), "Wi-Fi Name", font=smallfont, fill=(0, 0, 0))
    draw.text(((width - wifipassword_size)/2, 1.75 * font_size), "Wi-Fi Password", font=smallfont, fill=(0, 0, 0))
    wifissid_size = draw.textlength(wifi["ssid"], font=font)
    wifipsk_size = draw.textlength(wifi["psk"], font=font)
    draw.text(((width - wifissid_size)/2, 0.6 * font_size), wifi["ssid"], font=font, fill=(0, 0, 0))
    draw.text(((width - wifipsk_size)/2, 2.35 * font_size), wifi["psk"], font=font, fill=(0, 0, 0))
    img.paste(qr, (int((width - qr.size[0])/2), int(length * font_size)))
    return img


def print_image(img, count):
    with BytesIO() as output:
        img.save(output, 'PNG')
        data = output.getvalue()
        try:
            res = requests.post(os.environ["PRINTER_URL"] + "/print", data=data, headers={"Count": str(count)})
            if res.status_code < 300:
                return
        except Exception as e:
            print("Failed to print")
            print(res.status_code, res.content)
            raise Exception(f"Failed to print: {res.status_code} {res.content}")
