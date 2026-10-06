#!/usr/bin/env python3
"""Renders images/og-default.jpg, the 1200x630 card shown when the site is shared."""
import base64, os, html

SCRATCH = "/tmp/claude-0/-home-claude/1ce42e05-4ffd-58eb-b495-8d88b6554833/scratchpad"
SITEDIR = os.path.dirname(os.path.abspath(__file__))
AGENT, PHONE, SITE = "Roxanne Alterio", "0419 382 733", "thealterioteam.com.au"

fonts = ""
for w in (400, 500, 600):
    f = f"{SCRATCH}/node_modules/@fontsource/montserrat/files/montserrat-latin-{w}-normal.woff2"
    fonts += ('@font-face{font-family:"Montserrat";font-weight:%d;font-style:normal;'
              'src:url(data:font/woff2;base64,%s) format("woff2")}'
              % (w, base64.b64encode(open(f, "rb").read()).decode()))
for w in (400,):
    for st in ("normal", "italic"):
        f = (f"{SCRATCH}/node_modules/@fontsource/cormorant-garamond/files/"
             f"cormorant-garamond-latin-{w}-{st}.woff2")
        fonts += ('@font-face{font-family:"Cormorant";font-weight:%d;font-style:%s;'
                  'src:url(data:font/woff2;base64,%s) format("woff2")}'
                  % (w, st, base64.b64encode(open(f, "rb").read()).decode()))

portrait = base64.b64encode(open(os.path.join(SITEDIR, "images/roxanne-square.jpg"), "rb").read()).decode()

CSS = fonts + """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1200px;height:630px;overflow:hidden;font-family:"Montserrat",sans-serif;background:#fff}
.card{width:1200px;height:630px;display:grid;grid-template-columns:1fr 430px;background:#fff}
.pad{padding:58px 48px 48px 62px;display:flex;flex-direction:column;color:#0a0a0a}
.mark{font-family:"Cormorant",Georgia,serif;font-weight:400;font-size:30px;line-height:1;
      letter-spacing:.30em;text-transform:uppercase}
.kick{margin-top:46px;font-size:16px;letter-spacing:.24em;text-transform:uppercase;color:#6c6760;font-weight:500}
h1{font-family:"Cormorant",Georgia,serif;font-weight:400;font-size:78px;line-height:1.06;
   letter-spacing:-.01em;margin-top:20px;max-width:13ch}
h1 em{font-style:italic}
.sub{margin-top:22px;font-size:21px;line-height:1.5;color:#6c6760;max-width:30ch;font-weight:400}
.foot{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;
      border-top:1px solid #e2ddd6;padding-top:22px;font-size:17px;font-weight:500}
.foot .r{text-align:right;font-weight:400;color:#6c6760}
.shot{overflow:hidden}
.shot img{width:100%;height:100%;object-fit:cover;object-position:50% 14%}
"""

BODY = f"""<div class="card">
 <div class="pad">
  <div class="mark">Alterio</div>
  <p class="kick">Holland Park West 4121</p>
  <h1>Selling Holland Park <em>West</em>.</h1>
  <p class="sub">One suburb, done properly. Recent sales, free appraisals and honest advice.</p>
  <div class="foot"><span>{html.escape(AGENT)}</span>
    <span class="r">{PHONE}<br>{SITE}</span></div>
 </div>
 <div class="shot"><img src="data:image/jpeg;base64,{portrait}" alt=""></div>
</div>"""

def render():
    from playwright.sync_api import sync_playwright
    path = os.path.join(SCRATCH, "_og.html")
    open(path, "w").write("<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
                          + CSS + "</style></head><body>" + BODY + "</body></html>")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        pg.goto("file://" + path); pg.wait_for_timeout(500)
        pg.screenshot(path=os.path.join(SCRATCH, "_og.png"))
        b.close()
    from PIL import Image
    Image.open(os.path.join(SCRATCH, "_og.png")).convert("RGB").save(
        os.path.join(SITEDIR, "images/og-default.jpg"), quality=90)
    print("wrote images/og-default.jpg")

if __name__ == "__main__":
    render()
