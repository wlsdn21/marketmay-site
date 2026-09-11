"""Generate a two-page portrait A4 QR drink menu from /menu's JSON.

Requires reportlab, qrcode, Pillow and NanumGothic Regular/Bold TTF fonts.
Usage: python scripts/create-print-menu.py --font-dir /path/to/fonts --output /path/to/output
"""
import argparse
import json
from pathlib import Path

import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

parser = argparse.ArgumentParser()
parser.add_argument('--font-dir', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
opt = parser.parse_args()
opt.output.mkdir(parents=True, exist_ok=True)
root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'src/data/drinks.json').read_text())
sections = {s['id']: s for s in data['sections']}
pdfmetrics.registerFont(TTFont('KR', str(opt.font_dir / 'NanumGothic-Regular.ttf')))
pdfmetrics.registerFont(TTFont('KR-Bold', str(opt.font_dir / 'NanumGothic-Bold.ttf')))
GREEN, INK, MUTED = '#153f28', '#25362b', '#5b685c'
RULE, PAPER, TINT = '#d9e1d5', '#f9faf5', '#e7eee1'
W, H = A4
M, GAP = 36, 26
CW = (W - 2*M - GAP)/2
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=16, border=4)
qr.add_data(data['url'])
qr.make(fit=True)
matrix = qr.get_matrix()
qr.make_image(fill_color='black', back_color='white').save(opt.output / 'marketmay-menu-qr.png')
c = canvas.Canvas(str(opt.output / 'marketmay-qr-menu-A4-2pages.pdf'), pagesize=A4, pageCompression=1)
c.setTitle('마켓메이 QR 메뉴판 | A4 2장')
c.setAuthor('마켓메이')
c.setSubject('커피와 음료 메뉴 · https://marketmay.com/menu')
printed = []


def rect(x, y, w, h, color):
    c.setFillColor(HexColor(color))
    c.rect(x, H-y-h, w, h, stroke=0, fill=1)


def line(x, y, right, color=RULE, width=.6):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)
    c.line(x, H-y, right, H-y)


def text(x, y, value, size=12, font='KR', color=INK, right=False):
    c.setFillColor(HexColor(color))
    c.setFont(font, size)
    (c.drawRightString if right else c.drawString)(x, H-y, value)


def wrap(value, width, size=10, font='KR'):
    result, current = [], ''
    for char in value:
        if current and pdfmetrics.stringWidth(current+char, font, size) > width:
            result.append(current.rstrip())
            current = char.lstrip()
        else:
            current += char
    if current:
        result.append(current)
    return result


def header(english, korean, number):
    rect(0, 0, W, H, PAPER)
    rect(0, 0, W, 6, GREEN)
    text(M, 59, 'market may', 36, 'Times-Italic', GREEN)
    text(M, 82, '마켓메이', 11, 'KR-Bold', GREEN)
    text(M, 101, '직접 볶아 더 신선한 커피', 10.5, color=MUTED)
    qx, qy, qs = W-M-78, 24, 78
    rect(qx, qy, qs, qs, '#ffffff')
    cell = qs/len(matrix)
    for row, values in enumerate(matrix):
        for col, filled in enumerate(values):
            if filled:
                rect(qx+col*cell, qy+row*cell, cell, cell, '#000000')
    c.linkURL(data['url'], (qx, H-qy-qs, qx+qs, H-qy), relative=0, thickness=0)
    for cap, yy, sz, ft in [('QR로 메뉴 보기', 114, 8.5, 'KR-Bold'), ('marketmay.com/menu', 126, 8, 'Helvetica')]:
        text(qx+(qs-pdfmetrics.stringWidth(cap, ft, sz))/2, yy, cap, sz, ft, GREEN)
    text(M, 139, english, 24, 'Times-Italic', GREEN)
    ex=M+pdfmetrics.stringWidth(english, 'Times-Italic', 24)+14
    text(ex, 137, korean, 10.5, 'KR-Bold', GREEN)
    line(M, 153, W-M, GREEN, 1)
    text(W-M, 169, '가격 단위: 원', 8, color=MUTED, right=True)
    line(M, H-41, W-M, GREEN, .7)
    text(M, H-25, '매일 마셔도 부담 없는 마켓메이의 로스팅', 9, color=MUTED)
    text(W-M, H-25, f'{number:02d} / 02', 9, 'Helvetica', GREEN, right=True)


def heading(x, y, english, korean):
    text(x, y+19, english, 19, 'Times-Italic', GREEN)
    text(x, y+37, korean, 10, 'KR-Bold', GREEN)
    line(x, y+46, x+CW, GREEN, .9)
    return y+51


def item(x, y, width, entry, large=False):
    printed.append(entry['id'])
    size, price_size, detail_size = (16, 15, 10.5) if large else (12, 11.5, 9.5)
    font = 'KR-Bold' if entry.get('signature') else 'KR'
    # Smaller type is only used for unusually long names in the two-column page.
    while pdfmetrics.stringWidth(entry['name'], font, size) > width-48:
        size -= .25
    assert size >= 10.5, (entry['name'], size)
    text(x, y+18, entry['name'], size, font, GREEN if entry.get('signature') else INK)
    text(x+width, y+18, f"{entry['price']:,}", price_size, right=True)
    bottom = y+22
    if entry.get('signature'):
        text(x, bottom+12, 'SIGNATURE', 8, 'Helvetica-Bold', GREEN)
        text(x+63, bottom+12, 'HOT ONLY', 8, 'Helvetica', '#945840')
        bottom += 17
    if entry.get('detail'):
        for detail in wrap(entry['detail'], width, detail_size):
            text(x, bottom+11, detail, detail_size, color=MUTED)
            bottom += 13.5
    line(x, bottom+5, x+width)
    return bottom+(12 if large else 11)


header('Coffee', '커피', 1)
y = 181
for entry in sections['coffee']['items']:
    y = item(M, y, W-2*M, entry, large=True)
assert y < 709, y
option_y = y+16
rect(M, option_y, W-2*M, 82, TINT)
text(M+14, option_y+23, '디카페인 원두 변경 무료', 12, 'KR-Bold', GREEN)
text(M+14, option_y+41, '모든 커피 메뉴에 가능합니다.', 10, color=MUTED)
text(M+14, option_y+65, '2샷 추가 +1,000원', 10.5, color=GREEN)
text(M+264, option_y+23, '오트밀크로 우유 변경 +1,000원', 10.5, color=GREEN)
text(M+264, option_y+44, '아메리카노 리필 2,500원', 10.5, 'KR-Bold', GREEN)
text(M+264, option_y+64, '1인 1음료, 커피류 주문 시 가능', 9, color=MUTED)
assert option_y+82 < H-48, option_y
c.showPage()

header('Tea & Drinks', '티 · 음료', 2)
x1, x2 = M, M+CW+GAP
y1 = heading(x1, 183, 'Ade & Fruit Tea', '에이드 · 과일차')
for entry in sections['fruit']['items']:
    y1 = item(x1, y1, CW, entry)
y1 = heading(x1, y1+17, 'Tea', '티')
for entry in sections['tea']['items'][:3]:
    y1 = item(x1, y1, CW, entry)
y1 += 22
rect(x1, y1, CW, 62, TINT)
text(x1+11, y1+19, 'SEASONAL · 시즌 한정', 8.5, 'KR-Bold', GREEN)
seasonal = sections['seasonal']['items'][0]
printed.append(seasonal['id'])
text(x1+11, y1+43, seasonal['name'], 12, 'KR-Bold', GREEN)
text(x1+CW-11, y1+43, f"{seasonal['price']:,}", 11.5, right=True)
y1 += 62

y2 = heading(x2, 183, 'Milk Tea & Drinks', '밀크티 · 라떼 · 음료')
for entry in sections['tea']['items'][3:] + sections['drinks']['items']:
    y2 = item(x2, y2, CW, entry)
assert max(y1, y2) < H-48, (y1,y2)
assert sorted(printed) == sorted(e['id'] for s in data['sections'] for e in s['items'])
c.showPage()
c.save()
print(f'A4 portrait, 2 pages, {len(printed)} entries; QR on each page: {78*25.4/72:.1f} mm; page 2 body ends {max(y1,y2):.1f}')
