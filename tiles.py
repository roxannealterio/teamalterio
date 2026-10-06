#!/usr/bin/env python3
"""Renders square social tiles (1080x1080) for Aurora."""
import base64, os, json, html

SCRATCH = "/tmp/claude-0/-home-claude/1ce42e05-4ffd-58eb-b495-8d88b6554833/scratchpad"
OUT = "/home/claude/site/tiles"
os.makedirs(OUT, exist_ok=True)

AGENT = "Roxanne Alterio"
PHONE = "0419 382 733"
SITE = "thealterioteam.com.au"
BRAND = "The Alterio Team"

fonts = ""
for w in (300, 400, 500, 600):
    f = f"{SCRATCH}/node_modules/@fontsource/montserrat/files/montserrat-latin-{w}-normal.woff2"
    b64 = base64.b64encode(open(f, "rb").read()).decode()
    fonts += ('@font-face{font-family:"Montserrat";font-weight:%d;font-style:normal;'
              'src:url(data:font/woff2;base64,%s) format("woff2")}' % (w, b64))
for w in (400, 500):
    for st in ("normal", "italic"):
        f = f"{SCRATCH}/node_modules/@fontsource/cormorant-garamond/files/cormorant-garamond-latin-{w}-{st}.woff2"
        b64 = base64.b64encode(open(f, "rb").read()).decode()
        fonts += ('@font-face{font-family:"Cormorant";font-weight:%d;font-style:%s;'
                  'src:url(data:font/woff2;base64,%s) format("woff2")}' % (w, st, b64))

MARK = ''

CSS = fonts + """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1080px;font-family:"Montserrat",sans-serif;overflow:hidden}
.tile{width:1080px;height:1080px;display:flex;flex-direction:column;position:relative;padding:72px}
.dark{background:#000;color:#fff}
.light{background:#fff;color:#0a0a0a}
.mist{background:#f6f4f1;color:#0a0a0a}
.rule{position:absolute;left:0;right:0;top:0;height:10px;background:#0a0a0a}
.mark{color:inherit;font-family:"Cormorant",Georgia,serif;font-weight:400;font-size:40px;
      line-height:1;letter-spacing:.30em;text-transform:uppercase}
.kick{margin-top:auto;font-size:24px;letter-spacing:.24em;text-transform:uppercase;opacity:.55;font-weight:500}
h1{font-family:"Cormorant",Georgia,serif;font-weight:400;font-size:104px;line-height:1.04;
   letter-spacing:-.012em;margin:24px 0 0;max-width:15ch}
h1.sm{font-size:82px}
h1 b{font-weight:400;font-style:italic}
.sub{font-size:32px;line-height:1.46;margin-top:28px;max-width:26ch;opacity:.78;font-weight:300}
.date{display:inline-block;margin-top:34px;background:#0a0a0a;color:#fff;font-weight:500;
      font-size:26px;letter-spacing:.14em;text-transform:uppercase;padding:15px 26px}
.foot{display:flex;justify-content:space-between;align-items:flex-end;margin-top:auto;padding-top:46px;
      font-size:25px;font-weight:500;opacity:.72}
.foot .r{text-align:right;font-weight:400}
.list{margin-top:34px;display:grid;gap:20px}
.list div{font-size:30px;font-weight:400;padding-left:44px;position:relative;line-height:1.35}
.list div::before{content:"";position:absolute;left:0;top:22px;width:22px;height:1px;background:#0a0a0a}
.big{font-family:"Cormorant",Georgia,serif;font-weight:400;font-size:210px;letter-spacing:-.02em;line-height:1;margin-top:18px}
.big small{display:block;font-size:34px;font-weight:400;letter-spacing:0;margin-top:14px;opacity:.75}
.split{display:grid;grid-template-columns:1fr 430px;padding:0}
.split .pad{padding:72px 48px 72px 72px;display:flex;flex-direction:column}
.split .shot{position:relative;overflow:hidden}
.split .shot img{width:100%;height:100%;object-fit:cover;object-position:50% 14%}
.split h1{font-size:80px;max-width:12ch}
.split .sub{font-size:28px;max-width:20ch}
.split .foot{font-size:23px}
.badge{position:absolute;left:0;bottom:0;background:#0a0a0a;color:#fff;font-weight:500;
       font-size:22px;letter-spacing:.16em;text-transform:uppercase;padding:14px 20px}
"""

def photo_tile(theme, kick, title, sub, badge="", img="roxanne-square.jpg"):
    data = base64.b64encode(open("/home/claude/site/images/" + img, "rb").read()).decode()
    pad = (f'<div class="pad"><div class="mark">Alterio</div>'
           f'<p class="kick">{html.escape(kick)}</p><h1>{title}</h1>'
           f'<p class="sub">{html.escape(sub)}</p>'
           f'<div class="foot"><span>{html.escape(AGENT)}</span>'
           f'<span class="r">{html.escape(PHONE)}<br>{html.escape(SITE)}</span></div></div>')
    shot = (f'<div class="shot"><img src="data:image/jpeg;base64,{data}" alt="">'
            + (f'<span class="badge">{html.escape(badge)}</span>' if badge else '') + '</div>')
    return f'<div class="tile split {theme}"><div class="rule"></div>{pad}{shot}</div>'

def tile(theme, kick, title, sub="", date="", items=None, big=None, title_class=""):
    body = f'<div class="mark">Alterio</div>'
    body += f'<p class="kick">{html.escape(kick)}</p>'
    if big:
        body += f'<p class="big">{big[0]}<small>{html.escape(big[1])}</small></p>'
    body += f'<h1 class="{title_class}">{title}</h1>'
    if sub:
        body += f'<p class="sub">{html.escape(sub)}</p>'
    if date:
        body += f'<p><span class="date">{html.escape(date)}</span></p>'
    if items:
        body += '<div class="list">' + "".join(f"<div>{html.escape(i)}</div>" for i in items) + '</div>'
    body += (f'<div class="foot"><span>{html.escape(AGENT)}</span>'
             f'<span class="r">{html.escape(PHONE)}<br>{html.escape(SITE)}</span></div>')
    return f'<div class="tile {theme}"><div class="rule"></div>{body}</div>'

TILES = [
 ("01-smoke-alarms", tile("light", "Queensland deadline",
    "Every home needs <b>interconnected</b> smoke alarms.",
    "Photoelectric, interconnected, to AS 3786-2014. Owner-occupied homes included.",
    date="From 1 January 2027")),

 ("02-smoke-alarms-check", tile("light", "Quick check",
    "Is your alarm setup <b>actually</b> compliant?",
    items=["Photoelectric, not ionisation",
           "Linked, so press one and they all sound",
           "Under ten years old",
           "In every bedroom and on every storey"])),

 ("03-seller-disclosure", tile("light", "Selling in Queensland",
    "The <b>Form 2</b> has to be in their hands before they sign.",
    "Miss it, or get it materially wrong, and a buyer may be able to walk away right up to settlement.",
    date="In force since 1 August 2025")),

 ("04-disclosure-tip", tile("light", "Seller tip",
    "Order the disclosure pack <b>before</b> you launch.",
    "Searches take time. The worst moment to discover that is on a Sunday with an offer in front of you.")),

 ("05-duty-change", tile("light", "Transfer duty",
    "Home concessions now depend on <b>residency status</b>.",
    "Citizens, permanent residents and legacy 405/410 retirees. Other temporary visas pay full duty, plus 8% AFAD.",
    date="Contracts from 1 August 2026")),

 ("06-appraisal", tile("light", "No cost, no obligation",
    "What's your home <b>actually</b> worth?",
    items=["A written appraisal with the comparable sales",
           "A suburb snapshot of what's selling, and how fast",
           "What's worth fixing, and what isn't",
           "An honest read on timing"])),

 ("07-open-home", tile("light", "This Saturday",
    "<b>Open home</b>",
    "Add the address and time, then post it. Edit the text in tiles.py and run it again.",
    date="10:00am to 10:30am")),

 ("09-local-expert", photo_tile("light", "Holland Park West 4121",
    "I know this pocket <b>street by street</b>.",
    "Elevation, catchments and motorway noise. The things that move your price.",
    badge="Your local agent")),

 ("10-appraisal-photo", photo_tile("light", "No cost, no obligation",
    "What's your home <b>actually</b> worth?",
    "A written appraisal with the comparable sales behind it, and an honest read on timing.",
    badge="Ask me")),

 ("08-just-listed", tile("light", "Just listed",
    "New to market in <b>Holland Park West</b>.",
    "Swap this line for the headline of your listing, then run the file again to re-render.")),
]

def render():
    from playwright.sync_api import sync_playwright
    head = "<!DOCTYPE html><html><head><meta charset='utf-8'><style>" + CSS + "</style></head><body>"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1)
        for name, markup in TILES:
            path = os.path.join(SCRATCH, "_tile.html")
            open(path, "w").write(head + markup + "</body></html>")
            pg.goto("file://" + path)
            pg.wait_for_timeout(260)
            pg.screenshot(path=os.path.join(OUT, name + ".png"))
        b.close()
    print("rendered %d tiles into %s" % (len(TILES), OUT))

if __name__ == "__main__":
    render()
