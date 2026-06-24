from pathlib import Path
import struct
import zlib
import io

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def gerar_png_icone(tamanho: int) -> bytes:
    buf = io.BytesIO()
    raw = b""
    cx = cy = tamanho // 2
    radius = tamanho // 2
    for y in range(tamanho):
        row = b""
        for x in range(tamanho):
            dx, dy = x - cx, y - cy
            dist = (dx * dx + dy * dy) ** 0.5 / radius
            if dist < 0.85:
                r, g, b, a = 121, 85, 72, 255
            elif dist < 0.92:
                r, g, b, a = 255, 255, 255, 255
            else:
                r, g, b, a = 0, 0, 0, 0
            if tamanho >= 32 and dist < 0.85:
                if abs(dx) < tamanho * 0.08 and abs(dy) > 2:
                    r, g, b, a = 255, 255, 255, 200
                if abs(dy) < tamanho * 0.08 and abs(dx) > 2:
                    r, g, b, a = 255, 255, 255, 200
            row += struct.pack("BBBB", r, g, b, a)
        raw += b"\x00" + row

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    buf.write(struct.pack(">B", 137) + b"PNG\r\n\x1a\n")
    buf.write(chunk(b"IHDR", struct.pack(">IIBBBBB", tamanho, tamanho, 8, 6, 0, 0, 0)))
    buf.write(chunk(b"IDAT", zlib.compress(raw)))
    buf.write(chunk(b"IEND", b""))
    return buf.getvalue()


def criar_icone(caminho: str):
    tamanhos = [16, 32, 48, 64, 128, 256]
    pngs = {t: gerar_png_icone(t) for t in tamanhos}
    buf = io.BytesIO()
    buf.write(struct.pack("<HHH", 0, 1, len(pngs)))
    offset = 6 + len(pngs) * 16
    for t in sorted(pngs):
        d = pngs[t]
        buf.write(struct.pack("<BBBBHHII", t if t < 256 else 0, t if t < 256 else 0, 0, 0, 1, 32, len(d), offset))
        offset += len(d)
    for t in sorted(pngs):
        buf.write(pngs[t])
    with open(caminho, "wb") as f:
        f.write(buf.getvalue())
    print(f"  Icone: {caminho}")


def criar_wizard_bmp(caminho: str, largura: int, altura: int, tipo: str = "large"):
    if not HAS_PIL:
        print(f"  AVISO: Pillow nao disponivel, pulando {caminho.name}")
        return

    img = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if tipo == "large":
        cor1 = (93, 64, 55)
        cor2 = (121, 85, 72)
        cor3 = (78, 52, 46)
        for y in range(altura):
            r = int(cor1[0] + (cor2[0] - cor1[0]) * (y / altura) * 0.7)
            g = int(cor1[1] + (cor2[1] - cor1[1]) * (y / altura) * 0.7)
            b = int(cor1[2] + (cor2[2] - cor1[2]) * (y / altura) * 0.7)
            draw.line([(0, y), (largura, y)], fill=(r, g, b, 255))

        cx, cy = largura // 2, altura // 2 - 20
        for r in range(80, 30, -1):
            alpha = int(60 * (1 - r / 80))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, alpha), width=1)

        draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(255, 255, 255, 40))
        draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(121, 85, 72, 255))

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        draw.text((cx, cy), "SF", fill=(255, 255, 255, 255), font=font, anchor="mm")

        try:
            font2 = ImageFont.truetype("arial.ttf", 14)
        except:
            font2 = ImageFont.load_default()
        titulo = "Sistema Campo Fértil"
        draw.text((cx, altura - 60), titulo, fill=(255, 255, 255, 230), font=font2, anchor="mm")
        draw.text((cx, altura - 40), "Gestao Agropecuaria", fill=(255, 255, 255, 150), font=font2, anchor="mm")

    else:
        cor_fundo = (93, 64, 55)
        for y in range(altura):
            fator = 1 - (y / altura) * 0.3
            r = int(cor_fundo[0] * fator)
            g = int(cor_fundo[1] * fator)
            b = int(cor_fundo[2] * fator)
            draw.line([(0, y), (largura, y)], fill=(r, g, b, 255))

        cx, cy = largura // 2, altura // 2
        draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(255, 255, 255, 50))
        draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(121, 85, 72, 255))
        try:
            font = ImageFont.truetype("arial.ttf", 11)
        except:
            font = ImageFont.load_default()
        draw.text((cx, cy), "SF", fill=(255, 255, 255, 255), font=font, anchor="mm")

    img = img.convert("RGB")
    img.save(caminho, "BMP")
    print(f"  Wizard {tipo}: {caminho} ({largura}x{altura})")


def main():
    print("Gerando recursos graficos...")
    pasta = Path(__file__).parent
    criar_icone(str(pasta / "icone.ico"))
    criar_wizard_bmp(str(pasta / "wizard_large.bmp"), 164, 314, "large")
    criar_wizard_bmp(str(pasta / "wizard_small.bmp"), 55, 55, "small")
    print("Recursos graficos gerados com sucesso!")


if __name__ == "__main__":
    main()
