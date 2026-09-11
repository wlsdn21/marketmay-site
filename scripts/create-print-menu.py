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


def page(label):
    c.setFillColor(HexColor(PAPER)); c.rect(0,0,W,H,fill=1,stroke=0)
    # Align the logo and QR to a shared header on both sheets.
    mark = Image.open(logo_path)
    scale = min(144 / mark.width, 60 / mark.height)
    lw, lh = mark.width * scale, mark.height * scale
    c.drawImage(ImageReader(mark),50,H-39-lh,width=lw,height=lh,mask='auto')
    x,y,size=W-50-74,26,74
    c.setFillColor(HexColor('#ffffff')); c.rect(x,H-y-size,size,size,fill=1,stroke=0)
    unit=size/len(matrix); c.setFillColor(HexColor('#000000'))
    for r,row in enumerate(matrix):
        for col,on in enumerate(row):
            if on: c.rect(x+col*unit,H-y-(r+1)*unit,unit,unit,fill=1,stroke=0)
    c.linkURL(data['url'],(x,H-y-size,x+size,H-y),relative=0,thickness=0)
    text(x+size/2,y+size+13,'QR 메뉴판',8.5,align='center')
    text(x+size/2,y+size+25,'marketmay.com/menu',7.5,'Helvetica',align='center')
    text(50,146,label,14.5)
    text(W-50,146,'가격 단위: 천 원',8.5,'KR',color='#63685e',align='right')
    line(50,158,W-50)


def item(item_id,x,y,width=280,label=None,show_price=True):
    item=items[item_id]; printed.append(item_id)
    name=label or item['name']
    # Names and their choices match the original board's compact typography.
    size=13
    while pdfmetrics.stringWidth(name,'KR-Bold',size)>width-(37 if show_price else 0): size-=.2
    assert size>=10.5,(name,size)
    text(x,y,name,size)
    if show_price: text(x+width,y,f"{item['price']/1000:.1f}",13.2,'KR-Bold',align='right')


def lines(x,y,values,size=10.5,leading=15):
    # Descriptions sit below bold menu names in a quieter regular weight.
    for n,value in enumerate(values):
        text(x,y+n*leading,value,size,'KR',color='#586159')


def choices(x,y,values):
    # A small indent and regular gray type distinguish choices from menu names.
    lines(x+6,y,values,size=10.5,leading=16)


def signature(x,y):
    text(x,y,'signature',13,'Helvetica-Oblique',GREEN)
    text(x+67,y,'(only hot)',13,'Helvetica-Oblique',RED)


page('COFFEE')
left=50
item('americano',left,190)
item('latte-8',left,237,label='카페라떼 8부(기본)')
item('latte-5',left,273,label='카페라떼 5부(작은 잔)')
item('cappuccino',left,309)
line(left,331,left+280)
item('vanilla',left,363)
item('caramel',left,401)
item('cold-brew',left,445)
item('einspanner',left,488)
item('borgia',left,526)
lines(left,546,['(초코맛 비엔나커피)'])
item('mocha',left,585)
item('affogato',left,623)
lines(left,643,['(하겐다즈)'])
line(left,664,left+280)
item('marocchino',left,698)
signature(left,721)
lines(left,748,['벨기에 다크 초콜릿 슬라이스가','가득 올라간 진한 초코맛 카푸치노'])

# Center the options beside the coffee list instead of placing them at the bottom.
c.setStrokeColor(HexColor('#d5d9d3'));c.setLineWidth(.5)
c.line(364,H-229,364,H-707)
right,edge,center=395,W-50,(395+W-50)/2
text(center,283,'디카페인',16,align='center')
text(center,309,'무료 변경',13,color=RED,align='center')
text(center,342,'모든 커피 메뉴를',10.5,align='center')
text(center,359,'디카페인 원두로',10.5,align='center')
text(center,376,'변경할 수 있습니다.',10.5,align='center')
line(right,404,edge)
text(right,440,'2샷 추가',11)
text(edge,440,'+1.0',11,align='right')
text(right,480,'오트밀크 변경',11)
text(edge,480,'+1.0',11,align='right')
text(right,499,'우유를 오트밀크로',9.5,'KR')
line(right,527,edge)
text(right,566,'아메리카노 리필',10.5)
text(edge,566,'+2.5',11,align='right')
lines(right,591,['1인 1음료,','커피류 주문 시 가능'],size=10,leading=16)
c.showPage()

page('NON COFFEE')
left,right,width=50,313,232
item('omija-ade',left,185,width)
item('lemon-ade',left,219,width,show_price=False)
item('grapefruit-ade',left,253,width,show_price=False)
item('omija-tea',left,306,width)
item('lemon-tea',left,340,width,show_price=False)
item('grapefruit-tea',left,374,width,show_price=False)
item('peach',left,426,width)
item('ashotchu',left,460,width)
lines(left,480,['아샷추 제로 +0.5'])
line(left,505,left+width)
item('herbal',left,535,width)
choices(left,557,['캐모마일 / 페퍼민트 /','로즈마리 / 자스민 / 제주 녹차'])
item('black-tea',left,613,width,label='포트넘앤메이슨 홍차')
choices(left,634,['실론 / 피치 / 쥬빌레'])
item('earl-grey',left,673,width)
lines(left,694,['시트러스 과육이 살아있는','달콤 시원한 과일 홍차 티'])
item('yogurt',left,749,width)
choices(left,770,['블루베리 / 딸기'])

item('royal-milk-tea',right,185,width)
signature(right,210)
lines(right,241,['로얄 블렌드 홍차를 우유에 천천히','끓이고, 은은한 꿀 향을 더한 밀크티'])
item('iced-milk-tea',right,305,width,show_price=False)
lines(right,326,['블렌딩 홍차를 냉침해 깔끔 달콤한 맛'],size=10)
line(right,354,right+width)
item('chocolate',right,387,width,label='핫초코/아이스초코')
item('matcha',right,421,width)
item('strawberry-matcha',right,455,width)
item('ginger',right,513,width,label='생강차/생강라떼')
lines(right,534,['(직접 만든 생강 진액)'])
item('belgian',right,582,width)
signature(right,608)
lines(right,640,['벨지안 다크초콜릿을 우유에 직접 녹여,','진한 풍미를 그대로 살린 리얼 핫초코'],size=10)
line(right,690,right+width)
text(right+width,726,'시즌 한정 메뉴',12.5,align='right')
seasonal=items['passion-fruit'];printed.append(seasonal['id'])
text(right+width-48,758,seasonal['name'],13,align='right')
text(right+width,758,f"{seasonal['price']/1000:.1f}",13.2,align='right')
assert sorted(printed)==sorted(items),printed
c.showPage();c.save()
print(f'A4 portrait: 2 balanced pages; {len(printed)} items; logo and QR on both pages; QR {74*25.4/72:.1f} mm')
