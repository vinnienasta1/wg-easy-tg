from io import BytesIO
import qrcode


def config_to_qr_png_bytes(config_text: str) -> bytes:
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(config_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
