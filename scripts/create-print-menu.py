"""Recreate the supplied physical menu as two portrait A4 pages with QR.

The original's spacing, grouping and prices in thousands of won are preserved.
Requires reportlab, qrcode, Pillow, NanumGothic Regular/Bold fonts.
"""
import argparse
import json
from pathlib import Path
from PIL import Image
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

parser = argparse.ArgumentParser()
parser.add_argument('--font-dir', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--logo', type=Path, help='Clean logo image; defaults to docs/assets/marketmay-print-logo.png')
opt = parser.parse_args()
opt.output.mkdir(parents=True, exist_ok=True)
root = Path(__file__).resolve().parents[1]
logo_path = opt.logo or root / 'docs/assets/marketmay-print-logo.png'
data = json.loads((root / 'src/data/drinks.json').read_text())
items = {i['id']: i for s in data['sections'] for i in s['items']}
pdfmetrics.registerFont(TTFont('KR', str(opt.font_dir/'NanumGothic-Regular.ttf')))
pdfmetrics.registerFont(TTFont('KR-Bold', str(opt.font_dir/'NanumGothic-Bold.ttf')))
W,H = A4
INK, GREEN, RED, PAPER = '#202822', '#254536', '#a45457', '#ffffff'
c=canvas.Canvas(str(opt.output/'marketmay-qr-menu-A4-2pages.pdf'), pagesize=A4, pageCompression=1)
c.setTitle('마켓메이 메뉴판 | 원본 구성 · A4 2장')
c.setAuthor('마켓메이')
c.setSubject('기존 메뉴판 재구성 · https://marketmay.com/menu')
qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=16,border=4)
qr.add_data(data['url']); qr.make(fit=True)
matrix=qr.get_matrix()
printed=[]


def text(x,y,value,size=12,font='KR-Bold',color=INK,align='left'):
    c.setFillColor(HexColor(color)); c.setFont(font,size)
    if align=='right': c.drawRightString(x,H-y,value)
    elif align=='center': c.drawCentredString(x,H-y,value)
    else: c.drawString(x,H-y,value)


def line(x,y,x2):
    c.setStrokeColor(HexColor('#656c61')); c.setLineWidth(.65)
    c.line(x,H-y,x2,H-y)


def page():
    c.setFillColor(HexColor(PAPER)); c.rect(0,0,W,H,fill=1,stroke=0)
    # Add only a discreet QR in the original upper margin.
    x,y,size=473,28,74
    c.setFillColor(HexColor('#ffffff')); c.rect(x,H-y-size,size,size,fill=1,stroke=0)
    unit=size/len(matrix); c.setFillColor(HexColor('#000000'))
    for r,row in enumerate(matrix):
        for col,on in enumerate(row):
            if on: c.rect(x+col*unit,H-y-(r+1)*unit,unit,unit,fill=1,stroke=0)
    c.linkURL(data['url'],(x,H-y-size,x+size,H-y),relative=0,thickness=0)
    text(x+size/2,y+size+13,'QR 메뉴판',8.5,align='center')
    text(x+size/2,y+size+25,'marketmay.com/menu',7.5,'Helvetica',align='center')
    text(57,H-24,'가격 단위: 천 원',8,'KR',color='#63685e')


def item(item_id,x,y,width=205,label=None,show_price=True):
    item=items[item_id]; printed.append(item_id)
    name=label or item['name']
    # Names and their choices match the original board's compact typography.
    size=12
    while pdfmetrics.stringWidth(name,'KR-Bold',size)>width-(37 if show_price else 0): size-=.2
    assert size>=10.5,(name,size)
    text(x,y,name,size)
    if show_price: text(x+width,y,f"{item['price']/1000:.1f}",13.2,'KR-Bold',align='right')


def lines(x,y,values,size=10.5,leading=13):
    for n,value in enumerate(values): text(x,y+n*leading,value,size)


def signature(x,y):
    text(x,y,'signature',13,'Helvetica-Oblique',GREEN)
    text(x+67,y,'(only hot)',13,'Helvetica-Oblique',RED)


page()
left=59
item('americano',left,148)
item('latte-8',left,208,label='카페라떼 8부(기본)')
item('latte-5',left,240,label='카페라떼 5부(작은 잔)')
item('cappuccino',left,272)
line(left,300,left+213)
item('vanilla',left,334)
item('caramel',left,366)
item('cold-brew',left,426)
item('einspanner',left,486)
item('borgia',left,518)
lines(left,539,['(초코맛 비엔나커피)'])
item('mocha',left,578)
item('affogato',left,610)
lines(left,631,['(하겐다즈)'])
line(left,654,left+213)
item('marocchino',left,690)
signature(left,714)
lines(left,742,['벨기에 다크 초콜릿 슬라이스가','가득 올라간 진한 초코맛 카푸치노'])

# A clean generated logo replaces the dark crop from the original photograph.
mark = Image.open(logo_path)
logo_scale = min(106 / mark.width, 48 / mark.height)
logo_width, logo_height = mark.width * logo_scale, mark.height * logo_scale
c.drawImage(ImageReader(mark),548-logo_width,H-451-logo_height,width=logo_width,height=logo_height,mask='auto')
line(377,511,548)
text(538,559,'디카페인',15,align='right')
text(538,604,'모든 커피 메뉴는',12.5,align='right')
text(538,624,'디카페인 원두로',12.5,color=RED,align='right')
text(538,644,'무료 변경 가능합니다',12.5,color=RED,align='right')
text(538,710,'2샷 추가 +1.0',10.5,align='right')
text(538,731,'오트밀크로 우유 변경 +1.0',10.5,align='right')
text(538,771,'아메리카노 리필 +2.5',10.5,align='right')
text(538,791,'(1인 1음료, 커피류 주문 시 가능)',9.5,align='right')
c.showPage()

page()
left,right,width=57,327,212
item('omija-ade',left,148,width)
item('lemon-ade',left,182,width,show_price=False)
item('grapefruit-ade',left,216,width,show_price=False)
item('omija-tea',left,278,width)
item('lemon-tea',left,312,width,show_price=False)
item('grapefruit-tea',left,346,width,show_price=False)
item('peach',left,408,width)
item('ashotchu',left,442,width)
lines(left,463,['(아샷추 제로 +0.5)'])
line(left,505,left+width)
item('herbal',left,536,width)
lines(left,559,['(캐모마일/페퍼민트/','로즈마리/자스민/제주 녹차)'],leading=21)
item('black-tea',left,627,width,label='포트넘앤메이슨 홍차')
lines(left,648,['(실론/피치/쥬빌레)'])
item('earl-grey',left,692,width)
lines(left,712,['시트러스 과육이 살아있는','달콤 시원한 과일 홍차 티'])
item('yogurt',left,759,width)
lines(left,780,['(블루베리/딸기)'])

item('royal-milk-tea',right,148,width)
signature(right,173)
lines(right,204,['로얄 블렌드 홍차를 우유에 천천히','끓이고, 은은한 꿀 향을 더한 밀크티'])
item('iced-milk-tea',right,280,width,show_price=False)
lines(right,301,['블렌딩 홍차를 냉침해 깔끔 달콤한 맛'],size=10)
line(right,343,right+width)
item('chocolate',right,376,width,label='핫초코/아이스초코')
item('matcha',right,410,width)
item('strawberry-matcha',right,444,width)
item('ginger',right,505,width,label='생강차/생강라떼')
lines(right,526,['(직접 만든 생강 진액)'])
item('belgian',right,572,width)
signature(right,598)
lines(right,630,['벨지안 다크초콜릿을 우유에 직접 녹여,','진한 풍미를 그대로 살린 리얼 핫초코'],size=10)
line(right,696,right+width)
text(right+width,731,'시즌 한정 메뉴',14,align='right')
seasonal=items['passion-fruit']; printed.append(seasonal['id'])
text(right+width,773,seasonal['name'],12.5,align='right')
text(right+width,795,f"{seasonal['price']/1000:.1f}",13.2,align='right')
assert sorted(printed)==sorted(items),printed
c.showPage(); c.save()
print(f'A4 portrait: 2 pages; {len(printed)} items; original group prices; QR on both pages: {74*25.4/72:.1f} mm')
