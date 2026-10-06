#!/usr/bin/env python3
"""Builds the static Aurora site. Run: python3 build.py"""
import os, html, datetime, json

SITE = os.path.dirname(os.path.abspath(__file__))
AGENT = "Roxanne Alterio"
AGENCY = "Aurora"
BRAND = "The Alterio Team"
MARKWORD = "LTERIO"
PHONE = "0419 382 733"
TEL = "0419382733"
EMAIL = "roxannealterio@auroraproperty.com.au"
FORMSPREE = "https://formspree.io/f/mgavdpgr"
DOMAIN = "thealterioteam.com.au"

MARK = ('<svg viewBox="0 0 121 100" aria-hidden="true">'
        '<path fill="#fff" d="M97.4 99.9L92.4 99.8L91.7 99.2L46.2 24.4L46.3 21.6L59.7 0.1L61.2 0L62 0.9L113.9 86.6L120.9 97.4L120.9 98.8L119.9 99.8L97.4 99.9Z"/>'
        '<path fill="#fff" d="M2 99.9L0.2 99.5L0.1 97.1L3.4 93L5.9 88L38.6 34.4L40.8 31.3L41.9 31.4L47.1 39L47.7 40.6L56.4 54.5L59.9 62.1L60.8 68.2L60.8 73.7L59.6 79.5L56.5 86L54.4 89L50.7 92.9L46 96.1L40.5 98.6L33.9 99.8L2 99.9Z"/></svg>')

IMG_SIZES = {}          # filled by _scan_images() at the bottom of this section
IMG_BLUR = {}           # a tiny blurred copy of each photo, held in the page itself
IMG_WIDTHS = [640, 1280]


def _scan_images():
    """Record every photo's real pixel size, and which smaller copies exist beside it.

    Running build.py after adding a photo picks it up automatically. The small copies
    are made by sizes.py.
    """
    import os
    if not os.path.isdir("images"):
        return
    try:
        from PIL import Image
    except ImportError:
        return
    for f in sorted(os.listdir("images")):
        if not f.endswith(".jpg") or f[:-4].endswith(("640w", "1280w")):
            continue
        try:
            with Image.open(os.path.join("images", f)) as im:
                w, h = im.size
        except Exception:
            continue
        alts = [n for n in IMG_WIDTHS
                if n < w and os.path.exists("images/%s-%dw.jpg" % (f[:-4], n))]
        IMG_SIZES["images/" + f] = (w, h, alts)
        IMG_BLUR["images/" + f] = _blur(os.path.join("images", f))


def _blur(path):
    """A 20 pixel wide copy of the photo, written straight into the page as text.

    It costs well under a kilobyte and shows instantly, so the space a photo will
    fill is never a blank panel while the real file is still arriving.
    """
    import base64, io as _io
    try:
        from PIL import Image
        with Image.open(path) as im:
            im = im.convert("RGB")
            tiny = im.resize((20, max(1, round(20 * im.height / im.width))), Image.LANCZOS)
            buf = _io.BytesIO()
            tiny.save(buf, "JPEG", quality=40)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


def img(src, alt, sizes="100vw", eager=False, cls="", style=""):
    """An <img> that tells the browser the shape up front and lets a phone pick a
    smaller file. Saves roughly a megabyte on the home page over mobile data."""
    w, h, alts = IMG_SIZES.get(src, (0, 0, []))
    bits = ['src="%s"' % src, 'alt="%s"' % html.escape(alt, quote=True)]
    if alts:
        srcset = ", ".join("%s-%dw.jpg %dw" % (src[:-4], n, n) for n in alts)
        bits.append('srcset="%s, %s %dw"' % (srcset, src, w))
        bits.append('sizes="%s"' % sizes)
    if w:
        bits.append('width="%d" height="%d"' % (w, h))
    if cls:
        bits.append('class="%s"' % cls)
    blur = IMG_BLUR.get(src, "")
    if blur:
        style = ("background:#efebe6 url(%s) center/cover no-repeat;" % blur) + style
    if style:
        bits.append('style="%s"' % style)
    bits.append('fetchpriority="high"' if eager else 'loading="lazy" decoding="async"')
    return "<img " + " ".join(bits) + ">"


_scan_images()

NAV =[("index.html", "Home"), ("listings.html", "Listings"),
       ("holland-park-west.html", "Holland Park West"),
       ("journal.html", "Blog"), ("referrals.html", "Referrals")]

def jsonld(page, title, desc):
    agent = {
      "@context": "https://schema.org",
      "@type": "RealEstateAgent",
      "name": AGENT,
      "image": f"https://{DOMAIN}/images/roxanne.jpg",
      "url": f"https://{DOMAIN}/",
      "telephone": "+61" + TEL[1:],
      "email": EMAIL,
      "worksFor": {"@type": "Organization", "name": AGENCY},
      "areaServed": [{"@type": "Place", "name": n} for n in
          ["Holland Park West", "Holland Park"]],
      "address": {"@type": "PostalAddress", "addressLocality": "Holland Park West",
                  "addressRegion": "QLD", "postalCode": "4121", "addressCountry": "AU"},
      "knowsAbout": ["Holland Park West property market", "Residential property sales",
                     "Property appraisals", "Rental appraisals",
                     "Queensland seller disclosure", "Holland Park West property market"]
    }
    blocks = [agent]
    if page != "index.html":
        blocks.append({
          "@context": "https://schema.org", "@type": "BreadcrumbList",
          "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"https://{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": title.split(" | ")[0],
             "item": f"https://{DOMAIN}/{page}"}]})
    return "".join('<script type="application/ld+json">%s</script>' % json.dumps(b, separators=(",", ":"))
                   for b in blocks)

def shell(page, title, desc, body, extra_js="", head_extra="", hero=False, noindex=False):
    nav = "".join(
        '<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == page else '', l)
        for h, l in NAV)
    nav += '<a class="cta" href="appraisal.html"%s>Free appraisal</a>' % (
        ' aria-current="page"' if page == "appraisal.html" else '')
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.className+=" js";
/* Must run here, in the head, before the browser restores the old scroll position.
   Set from the bottom of the page it is already too late: you see the wrong spot,
   then a jump. */
if('scrollRestoration' in history) history.scrollRestoration='manual';</script>
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="https://{DOMAIN}/{page}">
<meta name="robots" content="{'noindex, follow' if noindex else 'index, follow'}">
<meta name="author" content="{html.escape(AGENT)}">
<meta name="geo.region" content="AU-QLD">
<meta name="geo.placename" content="Holland Park West">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="{'article' if page.startswith('journal-') else 'website'}">
<meta property="og:url" content="https://{DOMAIN}/{page}">
<meta property="og:image" content="https://{DOMAIN}/images/og-default.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_AU">
<meta property="og:site_name" content="{html.escape(BRAND)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="https://{DOMAIN}/images/og-default.jpg">
{jsonld(page, title, desc)}{head_extra}
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="images/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="images/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<meta name="theme-color" content="#141413">
<link rel="preload" href="fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/inter-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="style.css">
</head>
<body class="{'hashero' if hero else ''}">
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="navin">
    <a class="wordmark" href="index.html" aria-label="{BRAND} home">The Alterio Team</a>
    <button class="burger" id="burger" aria-expanded="false" aria-controls="nav" aria-label="Menu"><span></span><span></span><span></span></button>
    <nav class="main" id="nav">{nav}</nav>
  </div>
</header>
<div class="horizon"></div>
<main id="main">
{body}
</main>
<footer class="site">
  <div class="wrap">
    <div>
      <a class="fmark" href="index.html" aria-label="{BRAND} home">Alterio</a>
      <p style="color:#c0b9b1;max-width:36ch">{html.escape(AGENT)} sells homes in Holland Park West
      and Holland Park, postcode 4121, and occasionally in Mount Gravatt East, Coorparoo,
      Annerley and Tarragindi.</p>
    </div>
    <div>
      <h2>Get in touch</h2>
      <a href="tel:{TEL}">{html.escape(PHONE)}</a>
      <a href="mailto:{EMAIL}">{html.escape(EMAIL)}</a>
    </div>
    <div>
      <h2>Pages</h2>
      <a href="listings.html">Listings</a>
      <a href="holland-park-west.html">Holland Park West</a>
      <a href="journal.html">Blog</a>
      <a href="appraisal.html">Free appraisal</a>
      <a href="holland-park-west-report.html">Market report</a>
      <a href="reviews.html">Reviews</a>
      <a href="referrals.html">Referrals</a>
      <a href="privacy.html">Privacy</a>
    </div>
    <div class="fine">
      <p>&copy; {datetime.date.today().year} {html.escape(BRAND)}. {html.escape(AGENT)}, {html.escape(AGENCY)}.
      All information is provided as a guide only
      and interested parties should rely on their own enquiries.</p>
      <p>Articles on this site are general information, not legal or financial advice.</p>
      <p>{PRIOR_AGENCY}</p>
    </div>
  </div>
</footer>
<script>
(function(){{
  /* The head already turned scroll restoration off. This only catches a browser that
     ignored it, and it fires before paint so there is nothing to see. */
  if(!location.hash && window.scrollY) window.scrollTo(0,0);

  /* Opened inside a frame (a preview, or an embed on someone else's page) the page
     itself is not what scrolls, so scrollTo above does nothing and you are dropped
     into the middle of the new page. Asking to bring the top of the page into view
     is the one thing that reaches the container holding the frame. */
  var framed = false;
  try {{ framed = window.self !== window.top; }} catch(e) {{ framed = true; }}
  var toTop = function(){{
    if(location.hash) return;
    try {{ document.body.scrollIntoView({{block:'start'}}); }} catch(e) {{}}
  }};
  if(framed) toTop();

  /* Turn smooth scrolling on only once the page has settled, so landing on a section
     from another page is instant and only in-page clicks glide. */
  window.addEventListener('load',function(){{
    if(framed) toTop();
    setTimeout(function(){{ document.documentElement.classList.add('smoothnav'); }},80);
  }});

  var b=document.getElementById('burger'), n=document.getElementById('nav');
  if(b) b.addEventListener('click',function(){{
    var open=n.classList.toggle('open');
    b.classList.toggle('x',open);
    document.documentElement.classList.toggle('navopen',open);
    b.setAttribute('aria-expanded',open);
  }});

  var doc=document.documentElement;
  var onScroll=function(){{
    if(window.scrollY>70) doc.classList.add('scrolled'); else doc.classList.remove('scrolled');
  }};
  window.addEventListener('scroll',onScroll,{{passive:true}});
  onScroll();

  var groupSel='.vrow, .srow, .numbered li, .post, .strip div, .lcard, .pocket';
  var items=[].slice.call(document.querySelectorAll('section > .wrap, .about .shot, .about .abtext, '+groupSel));
  items.forEach(function(el){{
    if(el.classList.contains('wrap') && el.querySelector(groupSel)) el.classList.add('in');
  }});
  var reduce=window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce || !('IntersectionObserver' in window)){{
    items.forEach(function(el){{ el.classList.add('in'); }});
    return;
  }}
  ['.values','.sales','.numbered','.posts','.strip','.cards','.pockets'].forEach(function(cs){{
    [].forEach.call(document.querySelectorAll(cs),function(c){{
      [].forEach.call(c.children,function(ch,i){{
        ch.style.transitionDelay=(Math.min(i,8)*70)+'ms';
      }});
    }});
  }});
  var pending=items.filter(function(el){{ return !el.classList.contains('in'); }});
  var ticking=false;
  var sweep=function(){{
    ticking=false;
    if(!pending.length) return;
    var h=window.innerHeight||document.documentElement.clientHeight;
    pending=pending.filter(function(el){{
      var r=el.getBoundingClientRect();
      if(r.top < h*0.94){{ el.classList.add('in'); return false; }}
      return true;
    }});
  }};
  var queue=function(){{ if(!ticking){{ ticking=true; requestAnimationFrame(sweep); }} }};
  window.addEventListener('scroll',queue,{{passive:true}});
  window.addEventListener('resize',queue,{{passive:true}});
  window.addEventListener('load',queue);
  sweep();
}})();

/* ---- listings.json, written by Aurora HQ ----
   Drop listings.json next to this page and it takes over the listing grids and the
   recent sales list. No file, no change: the cards built into the page stay. ---- */
(function(){{
  var cur=document.getElementById('panel-current'),
      sold=document.getElementById('panel-sold'),
      sales=document.querySelector('.sales');
  if(!cur && !sales) return;
  var E=function(x){{ return String(x==null?'':x).replace(/[&<>"']/g,function(c){{
    return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]; }}); }};
  function shot(p,flag){{
    if(p.img) return '<div class="ph"><img src="'+E(p.img)+'" alt="'+E(p.addr)+'">'+
      '<span class="flag">'+E(flag)+'</span></div>';
    return '<div class="ph noimg"><span class="plate">'+E(String(p.addr||'').split(' ')[0])+
      '</span><span class="flag">'+E(flag)+'</span></div>';
  }}
  function slugify(x){{
    return String(x||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  }}
  function liveCard(p){{
    var tags=(p.specs||[]).map(function(t){{ return '<span>'+E(t)+'</span>'; }}).join('');
    if(p.note) tags+='<span>'+E(p.note)+'</span>';
    var href=p.link||'', isLink=/^https?:/.test(href);
    var openTag=isLink?('<a class="lmain" href="'+E(href)+'" target="_blank" rel="noopener">'):'<div class="lmain">';
    var closeTag=isLink?'</a>':'</div>';
    var acts='';
    var AR='<svg viewBox="0 0 14 10" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M0 5h12M8.4 1.2 12.4 5l-4 3.8"/></svg>';
    if((p.flag||'For sale')!=='Sold'){{
      if(p.brochure) acts+='<a href="'+E(p.brochure)+'">View the brochure'+AR+'</a>';
      if(p.auction){{
        var dd=p.auctiondate?('&d='+encodeURIComponent(p.auctiondate)):'';
        acts+='<a href="auction.html?p='+E(slugify(p.addr))+dd+'">Register to bid'+AR+'</a>';
      }} else if(!p.brochure){{
        acts+='<a href="offer.html?p='+E(slugify(p.addr))+'">Make an offer'+AR+'</a>';
      }}
    }}
    return '<div class="lcard in">'+openTag+shot(p,p.flag||'For sale')+
      '<div class="body"><p class="addr">'+E(p.addr)+
      (p.also?'<span class="also">('+E(p.also)+')</span>':'')+'</p>'+
      '<p class="sb">'+E(p.suburb)+'</p>'+
      (tags?'<div class="tagrow">'+tags+'</div>':'')+'</div>'+closeTag+
      (acts?'<div class="lacts">'+acts+'</div>':'')+'</div>';
  }}
  function soldCard(p){{
    return '<div class="lcard sold in"><div class="lmain">'+shot(p,'Sold')+
      '<div class="body"><p class="addr">'+E(p.addr)+
      (p.also?'<span class="also">('+E(p.also)+')</span>':'')+'</p>'+
      '<p class="sb">'+E(p.suburb)+'</p>'+
      '<div class="tagrow"><span class="pricetag">'+E(p.price||'Sold')+'</span>'+
      (p.sold?'<span class="soldon">'+E(p.sold)+'</span>':'')+'</div></div></div></div>';
  }}
  fetch('listings.json',{{cache:'no-store'}})
    .then(function(r){{ if(!r.ok) throw 0; return r.json(); }})
    .then(function(d){{
      if(!d) return;
      if(cur && d.current) cur.innerHTML=d.current.map(liveCard).join('') ||
        '<p class="empty">Nothing on the market right now.</p>';
      var soldGrid = sold ? sold.querySelector('.cards') : null;
      if(soldGrid && d.sold) soldGrid.innerHTML=d.sold.map(soldCard).join('') ||
        '<p class="empty">Sold results will appear here.</p>';
      if(sales && d.sold) sales.innerHTML=d.sold.map(function(p){{
        return '<div class="srow in"><span class="a">'+E(p.addr)+'</span>'+
          '<span class="s">'+E(p.sold||String(p.suburb||'').replace(' QLD 4121',''))+'</span>'+
          '<span class="p">'+E(p.price||'Sold')+'</span></div>';
      }}).join('');
    }})
    .catch(function(){{}});
}})();
{extra_js}
</script>
</body>
</html>
"""

FORM_JS = """
(function(){
  var form=document.getElementById('f'); if(!form) return;
  var btn=document.getElementById('send'), err=document.getElementById('err');
  var req=JSON.parse(form.dataset.required||'[]');
  function val(id){var e=document.getElementById(id);if(!e)return '';
    if(e.type==='checkbox')return e.checked?e.value:'';return e.value.trim();}
  function picked(name){return [].slice.call(form.querySelectorAll('input[name="'+name+'"]:checked'))
    .map(function(x){return x.value}).join(', ');}
  btn.addEventListener('click',function(){
    err.textContent='';
    var miss=req.filter(function(r){return !val(r[0])});
    if(miss.length){
      miss.forEach(function(m){var e=document.getElementById(m[0]);if(e)e.classList.add('invalid')});
      err.textContent='Please add '+miss.map(function(m){return m[1]}).join(', ')+'.';
      var first=document.getElementById(miss[0][0]); if(first)first.focus();
      return;
    }
    var em=val('email');
    if(em&&!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(em)){
      document.getElementById('email').classList.add('invalid');
      err.textContent='Please check your email address.';document.getElementById('email').focus();return;
    }
    btn.disabled=true;btn.textContent='Sending…';
    var fd=new FormData();
    var tooBig=null;
    [].slice.call(form.querySelectorAll('input[id],select[id],textarea[id]')).forEach(function(e){
      if(e.type==='radio'||e.type==='checkbox')return;
      if(e.type==='file'){
        var f=e.files&&e.files[0];
        if(f){
          if(f.size>10*1024*1024){tooBig=f.name;return;}
          fd.append(e.dataset.label||e.id,f,f.name);
        }
        return;
      }
      if(e.value.trim())fd.append(e.dataset.label||e.id,e.value.trim());
    });
    if(tooBig){
      btn.disabled=false;btn.textContent=form.dataset.send||'Send';
      err.textContent='"'+tooBig+'" is over 10MB. Please send a smaller photo.';
      return;
    }
    (form.dataset.groups?JSON.parse(form.dataset.groups):[]).forEach(function(g){
      var v=picked(g[0]); if(v)fd.append(g[1],v);
    });
    fd.append('_subject',form.dataset.subject+(val('name')?', '+val('name'):''));
    fd.append('_gotcha',val('company'));
    fetch(form.dataset.endpoint,{method:'POST',body:fd,headers:{Accept:'application/json'}})
      .then(function(r){
        return r.json().catch(function(){return {};}).then(function(j){
          if(!r.ok){
            var why=(j&&j.errors&&j.errors.length&&j.errors.map(function(x){return x.message}).join('. '))
                    ||(j&&j.error)||('the form service returned '+r.status);
            throw new Error(why);
          }
          return j;
        });
      })
      .then(function(){
        form.style.display='none';
        document.getElementById('thanks').classList.add('on');
        document.getElementById('thanks').scrollIntoView({block:'center'});})
      .catch(function(e){
        btn.disabled=false;btn.textContent=form.dataset.send||'Send';
        var lines=[];
        [].slice.call(form.querySelectorAll('input[id],select[id],textarea[id]')).forEach(function(el){
          if(el.type==='file'||el.type==='checkbox'||el.type==='radio')return;
          if(el.value&&el.value.trim())lines.push((el.dataset.label||el.id)+': '+el.value.trim());
        });
        var mail='mailto:"""+EMAIL+"""?subject='+encodeURIComponent(form.dataset.subject||'Website enquiry')+
                 '&body='+encodeURIComponent(lines.join('\\n'));
        err.innerHTML='That did not send ('+String(e.message||'no connection')+'). '+
          'Please call <strong><a href="tel:"""+TEL+"""">"""+PHONE+"""</a></strong>, '+
          '<a href="'+mail+'">send it by email instead</a>, or try again in a moment.';
      });
  });
  form.addEventListener('input',function(e){if(e.target.classList)e.target.classList.remove('invalid')});
})();
"""

def field(fid, label, note="", kind="text", options=None, ph=""):
    lab = f'<label class="lbl" for="{fid}">{label}' + (f' <small>{note}</small>' if note else '') + '</label>'
    if kind == "area":
        inp = f'<textarea id="{fid}" placeholder="{html.escape(ph)}"></textarea>'
    elif kind == "select":
        opts = "".join(f"<option>{html.escape(o)}</option>" for o in options)
        inp = f'<select id="{fid}"><option value="">Choose</option>{opts}</select>'
    else:
        inp = f'<input type="{kind}" id="{fid}" placeholder="{html.escape(ph)}">'
    return f'<div class="f">{lab}{inp}</div>'

def checks(name, items):
    return '<div class="choices">' + "".join(
        f'<label class="choice"><input type="checkbox" name="{name}" value="{html.escape(i)}"><span>{html.escape(i)}</span></label>'
        for i in items) + '</div>'

def form_block(subject, required, groups, fields_html, send_label, thanks_html, note=""):
    return f"""
<div class="formcard">
<form id="f" enctype="multipart/form-data" data-endpoint="{FORMSPREE}" data-subject="{html.escape(subject)}"
      data-required='{required}' data-groups='{groups}' data-send="{html.escape(send_label)}">
  <div class="trap" aria-hidden="true"><label>Company <input type="text" id="company" tabindex="-1" autocomplete="off"></label></div>
  {fields_html}
  <button type="button" class="btn dark send" id="send">{html.escape(send_label)}</button>
  <p class="err" id="err" role="alert"></p>
  {f'<p class="formnote">{note}</p>' if note else ''}
</form>
<div class="thanks" id="thanks">{thanks_html}</div>
</div>
"""


# ============================ listings ============================
# Edit these two lists and run the build. Photos live in images/.
#
# PASTE YOUR REALESTATE.COM.AU LINKS HERE. Open the listing on realestate.com.au,
# copy what is in the address bar and paste it between the quotes. A card with a
# real link opens the ad in a new tab. Left as "#" the card goes nowhere.
REA_12_KNEALE = "#"
REA_162A      = "#"
REA_53_KNEALE = "#"

CURRENT = [
  dict(addr="12 Kneale Street", suburb="Holland Park West QLD 4121",
       img="images/12-kneale-street.jpg", link=REA_12_KNEALE,
       brochure="12-kneale-street.html",
       specs=["6 bed", "3 bath", "3 car"], note="Offers invited"),
  dict(addr="162A Birdwood Road", suburb="Holland Park West QLD 4121",
       img="images/162a-birdwood-road.jpg", link=REA_162A,
       specs=["5 bed", "2 bath", "6 car", "2,051m²"], note="Contact agent"),
  dict(addr="53 Kneale Street", suburb="Holland Park West QLD 4121",
       also="Two titles, also known as 1 & 3 Cluden Street",
       img="images/53-kneale-street.jpg", link=REA_53_KNEALE, flag="Under contract",
       specs=[], note="Price withheld"),
]

# Sold. Add img="images/your-file.jpg" to any of these and the photo replaces the panel.
# Dates and prices checked against the Domain property profile for each address, and
# 34 Galsworthy also against propertyvalue.com.au. Newest first.
SOLD = [
  dict(addr="29 Albert Street", suburb="Holland Park West QLD 4121",
       price="$1,880,000", sold="May 2026", img="images/29-albert-street.jpg"),
  dict(addr="34 Galsworthy Street", suburb="Holland Park West QLD 4121",
       price="$1,725,000", sold="April 2026", img="images/34-galsworthy-street.jpg"),
  dict(addr="67 Kneale Street", suburb="Holland Park West QLD 4121",
       price="$3,850,000", sold="January 2026", img="images/67-kneale-street.jpg"),
]

# Shown under the sale results and in the footer.
PRIOR_AGENCY = ("Some sales shown were completed by {agent} while working at another agency."
                .format(agent=AGENT))

def plate(p, flag):
    """A photo when there is one, otherwise the street number, so the row still looks finished."""
    if p.get("img"):
        return ('<div class="ph">'
                + img(p["img"], p["addr"], sizes="(max-width:700px) 92vw, (max-width:1100px) 46vw, 30vw")
                + f'<span class="flag">{html.escape(flag)}</span></div>')
    return (f'<div class="ph noimg"><span class="plate">{html.escape(p["addr"].split(" ")[0])}</span>'
            f'<span class="flag">{html.escape(flag)}</span></div>')

ARROW = ('<svg viewBox="0 0 14 10" aria-hidden="true" fill="none" stroke="currentColor" '
         'stroke-width="1.4"><path d="M0 5h12M8.4 1.2 12.4 5l-4 3.8"/></svg>')

def card_acts(p):
    """The brochure has an offer form inside it, so a card never shows both. A property
    under contract or sold takes no offers at all."""
    acts = []
    flag = p.get("flag", "For sale")
    if flag == "Sold":
        return ''
    if flag == "Under contract":
        return ''
    if p.get("brochure"):
        acts.append(f'<a href="{html.escape(p["brochure"])}">View the brochure{ARROW}</a>')
    if p.get("auction"):
        d = ("&d=" + html.escape(p["auctiondate"].replace(" ", "+"))) if p.get("auctiondate") else ""
        acts.append(f'<a href="auction.html?p={html.escape(slugify(p["addr"]))}{d}">Register to bid{ARROW}</a>')
    elif not p.get("brochure"):
        acts.append(f'<a href="offer.html?p={html.escape(slugify(p["addr"]))}">Make an offer{ARROW}</a>')
    return f'<div class="lacts">{"".join(acts)}</div>' if acts else ''

def slugify(x):
    import re as _re
    return _re.sub(r'[^a-z0-9]+', '-', str(x).lower()).strip('-')

def live_card(p):
    tags = "".join("<span>%s</span>" % html.escape(t) for t in p.get("specs", []))
    if p.get("note"):
        tags += '<span>%s</span>' % html.escape(p["note"])
    href = p.get("link") or ""
    # no portal link yet, so the photo is not a dead click
    if href.startswith("http"):
        open_tag = f'<a class="lmain" href="{html.escape(href)}" target="_blank" rel="noopener">'
        close_tag = '</a>'
    else:
        open_tag, close_tag = '<div class="lmain">', '</div>'
    return ('<div class="lcard">'
            + open_tag
            + plate(p, p.get("flag", "For sale")) +
            f'<div class="body"><p class="addr">{html.escape(p["addr"])}'
            + (f'<span class="also">({html.escape(p["also"])})</span>' if p.get("also") else '') +
            '</p>'
            f'<p class="sb">{html.escape(p["suburb"])}</p>'
            + (f'<div class="tagrow">{tags}</div>' if tags else '') +
            '</div>' + close_tag + card_acts(p) + '</div>')

def sold_card(p):
    shot = plate(p, "Sold")
    return (f'<div class="lcard sold">{shot}'
            f'<div class="body"><p class="addr">{html.escape(p["addr"])}</p>'
            f'<p class="sb">{html.escape(p["suburb"])}</p>'
            f'<div class="tagrow"><span class="pricetag">{html.escape(p["price"])}</span>'
            + (f'<span class="soldon">{html.escape(p["sold"])}</span>' if p.get("sold") else '')
            + '</div></div></div>')

CARDS_CURRENT = "".join(live_card(p) for p in CURRENT)
CARDS_SOLD = "".join(sold_card(p) for p in SOLD)
SOLD_ROWS = "".join(
    f'<div class="srow"><span class="a">{html.escape(p["addr"])}</span>'
    f'<span class="s">{html.escape(p.get("sold") or p["suburb"].replace(" QLD 4121",""))}</span>'
    f'<span class="p">{html.escape(p["price"])}</span></div>' for p in SOLD)


# ============================ reviews ============================
#
# Paste real reviews here, word for word, from your agent profile. Each one takes the
# quote, the reviewer's name as they left it, the street or suburb, and the month.
# Leave the list empty and the whole section disappears from the site, so there is
# never an empty panel waiting to be filled.
#
#   dict(quote="They sold our place in eleven days and never once left us guessing.",
#        who="Sarah M", where="Kneale Street, Holland Park West", when="May 2026"),

REVIEWS = [
  # Every verified review from the realestate.com.au profile, word for word. `home=True`
  # marks the three that appear on the home page; the rest live on reviews.html.
  dict(home=True,
       quote="The Alterio team of Roxy and Deane are confident, knowledgeable and extremely "
             "approachable agents. From first meeting to an unconditional contract in a matter of "
             "weeks they could not do enough to ensure that the process was a success, even going "
             "the extra mile to help us source a gardener to help with a last minute project. They "
             "met and exceeded our expectations with a suburb record sale. We highly recommend this "
             "remarkable young team.",
       who="Seller of a unit", where="Coorparoo", when="2025"),
  dict(home=True,
       quote="We purchased a new home subject to the sale of our current home. We had very tight "
             "contract conditions and not much time to get the sale of our home executed. Roxy took "
             "our needs onboard and did a fantastic job selling our home for a great price within "
             "the first 7 days of been on the market. She made a very stressful time seem easy and "
             "we did not have to make any exceptions. She was very well communicated and easily "
             "contactable whether the problem was big or small. I Highly recommend Roxy",
       who="Seller of a house", where="Tarragindi", when="2025"),
  dict(home=True,
       quote="Rox was patient and professional with our selling journey. She sold our property off "
             "market quickly and with the right buyers through the door. If you\u2019re selling in "
             "the South she\u2019s got you covered.",
       who="Seller of a townhouse", where="Moorooka", when="2025"),
  dict(quote="Working with Roxanne has been one of the best decisions I made during the selling "
             "process. From the very beginning, she was professional, clear, and genuinely invested "
             "in helping me get the best possible outcome. She guided me through every step with "
             "patience and confidence, making what could\u2019ve been a stressful experience feel "
             "smooth and well-supported.",
       who="Seller of an apartment", where="Dutton Park", when="2025"),
  dict(quote="Roxanne has been truly great! Made the purchase of my property easy and stress free. "
             "Definitely recommend her!",
       who="Buyer of a house", where="Moorooka", when="2025"),
  dict(quote="Roxanne was amazing. Great with communication, very accomodating, always did "
             "everything she could to find the answers to any question I had, and was positive and "
             "friendly every single time I had interactions with her. Would 100% work with her again.",
       who="Buyer of a unit", where="Annerley", when="2025"),
  dict(quote="It was such a pleasure dealing with Roxy for the recent sale of my unit. She was "
             "great at providing advice about what I needed to spend money on to get the best sale "
             "price (final contract price exceeded my expectations!), supported me with styling "
             "tips and was always available to chat through any questions I had. I\u2019ve already "
             "recommended Roxy and Mitch to a neighbour! So happy I listed with them and "
             "wouldn\u2019t hesitate to recommend them again to family and friends.",
       who="Seller of a unit", where="Greenslopes", when="2024"),
  dict(quote="Roxanne\u2019s standout positive trait is her optimistic demeanor that can be "
             "contagious. She is also well connected to many tradesmen that can renovate my "
             "property cost effectively, quickly and they do a good job. From the start till "
             "finish, she guided me step by step on how to get the highest price for the sale of my "
             "property. I was really pleased with her service and professionalism. I will use her "
             "again when the need to sell property arises.",
       who="Seller of a block of units", where="Indooroopilly", when="2024"),
  dict(quote="Roxy was great to work with throughout our property purchase. She was very helpful "
             "and attentive, and more than happy to make time for us to come through the property "
             "prior to settlement which we were grateful for.",
       who="Buyer of a house", where="Annerley", when="2024"),
  dict(quote="We are the seller in Dutton Park. We pick Roxanne because she was very convincing "
             "and nice to work with on the phone. She was very confident she could achieve record "
             "for the complex which she did. She was a very responsive agent and very organised. We "
             "are really happy with her works and will definately work with her again.",
       who="Seller of a unit", where="Dutton Park", when="2024"),
  dict(quote="Roxy is very kind and help us a lot! She solve most things for us.",
       who="Seller of a unit", where="Upper Mount Gravatt", when="2024"),
]



def review_card(r):
    foot = " · ".join(x for x in (r.get("where"), r.get("when")) if x)
    return (f'<figure class="quote"><blockquote>{html.escape(r["quote"])}</blockquote>'
            f'<figcaption>{html.escape(r["who"])}'
            + (f'<span>{html.escape(foot)}</span>' if foot else '')
            + '</figcaption></figure>')


REVIEWS_BLOCK = ("" if not REVIEWS else f"""
<section class="band">
  <div class="wrap mid">
    <p class="kick">Reviews</p>
    <h2>Sellers and <em>buyers</em>.</h2>
    <div class="quotes">{"".join(review_card(r) for r in REVIEWS if r.get("home"))}</div>
    <p class="formnote" style="margin-top:20px">Verified reviews from Roxanne&#8217;s
    realestate.com.au profile, published word for word.</p>
    <div class="btnrow" style="margin-top:30px">
      <a class="btn" href="appraisal.html">Request an appraisal</a>
      <a class="btn" href="reviews.html">Read all {len(REVIEWS)} reviews</a>
    </div>
  </div>
</section>
""")


# ============================ suburb market report ============================
#
# Figures are CoreLogic, twelve months to June 2026, published by Your Investment
# Property Magazine, except the Brisbane comparison, which is Cotality for July 2026
# via NAB, and the bedroom medians and population, which are Domain. Update the five
# constants below and the whole page follows. Change REPORT_MONTH every time.

REPORT_MONTH = "October 2026"
HPW = dict(median="$1,515,000", growth="10.53%", dom="24", rent="$750",
           yield_="2.6%", sales="91")
HP  = dict(median="$1,579,175", growth="12.80%", dom="27", rent="$790",
           yield_="2.60%", sales="96")
BNE = dict(median="$1,146,078", growth="5.3%", month="1.5%", quarter="4.9%")

REPORT_BODY = f"""
<section class="tight">
  <div class="wrap mid centre">
    <p class="kick">Market report &middot; {REPORT_MONTH}</p>
    <h1>Holland Park <em>West</em>.</h1>
    <p class="lede">What houses are selling for, how long they are taking, and what has
    changed in the past twelve months. Prepared by Roxanne Alterio.</p>
  </div>
</section>

<section style="padding-top:6px">
  <div class="wrap">
    <div class="btnrow" style="justify-content:center;margin:-8px 0 30px">
      <a class="btn" href="holland-park-west-report.pdf" download>Download the PDF</a>
    </div>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="strip">
      <div><b>{HPW["median"]}</b><span>Median house price</span></div>
      <div><b>{HPW["growth"]}</b><span>Growth, 12 months</span></div>
      <div><b>{HPW["dom"]}</b><span>Days on market</span></div>
      <div><b>{HPW["sales"]}</b><span>Houses sold</span></div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap mid">
    <p class="kick">The headline</p>
    <h2>A $1.5 million <em>suburb</em>.</h2>
    <p class="lede" style="max-width:56ch">The median Holland Park West house sold for
    {HPW["median"]} over the twelve months to June, up {HPW["growth"]}. Brisbane has turned since
    then, which is covered further down.</p>
    <p>Next door, Holland Park sits at {HP["median"]}, up {HP["growth"]}. The two suburbs are
    now within about four per cent of each other on price. Holland
    Park West houses are selling faster, at {HPW["dom"]} days against {HP["dom"]}.</p>
  </div>
</section>

<section>
  <div class="wrap mid">
    <p class="kick">What a house makes</p>
    <h2>By the <em>bedroom</em>.</h2>
    <div class="sales" style="margin-top:26px">
      <div class="srow"><span class="a">Two bedrooms</span><span class="s">9 sales</span><span class="p">$1,136,000</span></div>
      <div class="srow"><span class="a">Three bedrooms</span><span class="s">34 sales</span><span class="p">$1,365,000</span></div>
      <div class="srow"><span class="a">Four bedrooms</span><span class="s">14 sales</span><span class="p">$1,770,000</span></div>
      <div class="srow"><span class="a">Five bedrooms</span><span class="s">15 sales</span><span class="p">$2,030,000</span></div>
    </div>
    <p class="formnote" style="margin-top:20px">Medians of the 77 Holland Park West house sales
    between October 2025 and October 2026, built street by street from the public records. The gap
    between three bedrooms and four is $405,000, though that reflects whole houses rather than the
    value of adding a single room.</p>
  </div>
</section>

<section class="band">
  <div class="wrap mid">
    <p class="kick">How fast</p>
    <h2>Twenty four <em>days</em>.</h2>
    <p class="lede" style="max-width:56ch">That is the median time a Holland Park West house
    takes to sell. Holland Park next door takes {HP["dom"]}.</p>
    <p>Twenty four days is a fast market by any measure. A home that is well presented and
    sensibly priced is meeting its buyer inside a month. A home still sitting at six weeks is telling
    you something, and the longer it sits the harder it becomes to recover.</p>
    <p>{HPW["sales"]} houses changed hands over the year, roughly eight a month in a suburb of about
    6,400 people. The pool of comparable sales is therefore small, and two or three results on your
    own street can move the number your home is worth.</p>
  </div>
</section>

<section>
  <div class="wrap mid">
    <p class="kick">Rates and prices</p>
    <h2>The market has <em>cooled off</em>.</h2>
    <p class="lede" style="max-width:56ch">Brisbane house values have now fallen six months in a
    row. They are down {BNE["month"]} in the last month and {BNE["quarter"]} across the quarter,
    and the city sits 5.4% below the peak it reached in May.</p>
    <p>The annual figure still reads {BNE["growth"]}, which is what most reporting quotes. In July
    the same measure read 14.3%. An appraisal from a year ago is now too low, and a number taken from
    the autumn peak is too high.</p>
    <p>Houses here still sell quickly. The asking price simply has to be right.</p>
  </div>
</section>

<section class="band">
  <div class="wrap mid">
    <p class="kick">Who lives here</p>
    <h2>Owners, not <em>investors</em>.</h2>
    <p class="lede" style="max-width:56ch">Just under two thirds of Holland Park West homes are
    lived in by the people who own them, 64.3% at the last census. The median rent is
    {HPW["rent"]} a week, which on a {HPW["median"]} house is a gross yield of about
    {HPW["yield_"]}.</p>
    <p>A yield that low tells you investors are not setting the price in Holland Park West.
    Families are, and they buy on the school catchment, the block, the floor plan and how the home
    shows on the morning of the open. Presentation counts for more here than it does in an investor
    market.</p>
  </div>
</section>

<section>
  <div class="wrap mid">
    <p class="kick">Recent results</p>
    <h2>Sold by <em>Roxanne</em>.</h2>
    <div class="sales" style="margin-top:26px">{SOLD_ROWS}</div>
    <p class="formnote" style="margin-top:20px">{PRIOR_AGENCY}</p>
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <p class="kick" style="color:rgba(255,255,255,.55)">No cost, no obligation</p>
    <h2>What is your home <em>worth</em>?</h2>
    <p>A median will not tell you. Your street, your block and your floor plan move the number a
    long way in either direction. A written appraisal puts the comparable sales in front of you, so
    you can see exactly how the figure was reached.</p>
    <div class="btnrow" style="justify-content:center">
      <a class="btn solid" href="appraisal.html">Request an appraisal</a>
      <a class="btn" href="tel:{TEL}">Call {PHONE}</a>
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap mid">
    <p class="formnote">Sources. Median house price, twelve month growth, days on market, median
    rent, gross yield and number of sales: CoreLogic, twelve months to June 2026, published by
    <a href="https://www.yourinvestmentpropertymag.com.au/top-suburbs/qld/4121-holland-park-west" target="_blank" rel="noopener" style="color:var(--ink)">Your Investment Property Magazine</a>.
    These are the most recent figures published for this suburb, and the period they cover closed
    before the market turned. Medians by bedroom count: the 77 sales listed in the PDF, built
    street by street from the domain.com.au street profile for every street in the suburb. Owner
    occupier share: ABS, 2021 census. Brisbane house values, annual, quarterly and monthly change:
    Cotality Home Value Index, index date 30 September 2026.
    Figures are a guide only and are not a valuation of any individual property. Prepared
    {REPORT_MONTH} by {AGENT}, {AGENCY}.</p>
  </div>
</section>
"""


REVIEWS_BODY = f"""
<section class="tight pb-tight">
  <div class="wrap mid centre">
    <p class="kick">Reviews</p>
    <h1 style="margin:0">Sellers and <em>buyers</em>.</h1>
  </div>
</section>

<section class="pt-tight">
  <div class="wrap mid">
    <div class="quotes" style="margin-top:0">{"".join(review_card(r) for r in REVIEWS)}</div>
    <p class="formnote" style="margin-top:22px">All {len(REVIEWS)} verified reviews from
    Roxanne&#8217;s realestate.com.au profile, published word for word, newest first. Spelling and
    wording are the reviewers&#8217; own.</p>
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <p class="kick" style="color:rgba(255,255,255,.55)">No cost, no obligation</p>
    <h2>Thinking of <em>selling</em>?</h2>
    <p>Find out what your home is worth, with the sales behind the number and a straight
    answer on timing.</p>
    <div class="btnrow" style="justify-content:center">
      <a class="btn solid" href="appraisal.html">Request an appraisal</a>
      <a class="btn" href="tel:{TEL}">Call {PHONE}</a>
    </div>
  </div>
</section>
"""


# ============================ pages ============================

HEROIMG = img("images/hero.jpg",
              "A renovated weatherboard home in Holland Park West",
              sizes="100vw", eager=True)
ABOUTIMG = img("images/roxanne.jpg", AGENT,
               sizes="(max-width:860px) 100vw, 46vw")
APPRAISALIMG = img("images/roxanne-square.jpg", AGENT, sizes="86px",
                   style="width:86px;height:86px;border-radius:50%;"
                         "object-fit:cover;object-position:50% 14%;flex:none")

HOME_BODY = f"""
<section class="hero">
  <div class="shotbg">{HEROIMG}</div>
  <div class="scrim"></div>
  <div class="inner">
    <h1>Selling Holland Park <em>West</em>.</h1>
    <p>Residential sales across Holland Park West and Holland Park, postcode 4121.</p>
    <div class="btnrow">
      <a class="btn solid" href="appraisal.html">Request an appraisal</a>
      <a class="btn" href="tel:{TEL}">Call {PHONE}</a>
    </div>
  </div>
  <a class="scrolldown" href="#intro"><span>Scroll <em>down</em></span><i></i></a>
</section>

<section id="intro">
  <div class="wrap mid">
    <p class="kick">{AGENT}</p>
    <h2>Specialising in Holland Park <em>West</em>.</h2>
    <p class="lede" style="max-width:56ch">Roxanne Alterio specialises in residential sales across
    Holland Park West and Holland Park. It is one small pocket of Brisbane and she works it closely,
    which is how she knows the streets, the buyers who are looking, and what a home here is
    genuinely worth. Every campaign is built around a single commitment: the strongest result
    possible for the people who own the home.</p>
    <div class="btnrow" style="margin-top:28px">
      <a class="btn" href="appraisal.html">Request an appraisal</a>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap mid">
    <div class="values">
      <div class="vrow"><span class="no">01</span><h3><em>Knowledge</em></h3>
        <p>Roxanne's understanding of Holland Park West has been built street by street, sale by
        sale. She knows what is selling, what it is achieving, and which buyers are ready to move.
        That knowledge underpins every figure she puts in front of you.</p></div>
      <div class="vrow"><span class="no">02</span><h3><em>Communication</em></h3>
        <p>You will hear from Roxanne after every inspection, in writing. What the buyers said,
        what they did not say, and what she believes it means for your result. You are never left
        wondering where your campaign stands.</p></div>
      <div class="vrow"><span class="no">03</span><h3><em>Negotiation</em></h3>
        <p>Every offer is presented to you in full, with its conditions and its finance. Roxanne
        will tell you which one she would sign, and why. Her commitment is to the contract that
        settles, not simply the largest number on the page.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap mid">
    <p class="kick">Recent sales</p>
    <h2>Sold in Holland Park <em>West</em>.</h2>
    <div class="sales" style="margin-top:26px">{{SALES}}</div>
    <p class="formnote" style="margin-top:20px">{{PRIOR}}</p>
    <div class="btnrow" style="margin-top:26px">
      <a class="btn" href="listings.html">See all listings</a>
    </div>
  </div>
</section>
{REVIEWS_BLOCK}
<section class="band bleed" id="about">
  <div class="about">
    <figure class="shot">{ABOUTIMG}</figure>
    <div class="abtext">
      <p class="kick">{AGENT}</p>
      <h2>Guided by Roxanne <em>Alterio</em>.</h2>
      <p>Roxanne runs every campaign herself, from the first appraisal through to settlement. You
      deal with her at the open home, on the phone when an offer arrives, and in the room when it is
      negotiated. There are no juniors and no handovers.</p>
      <p>Selling a home is rarely only a transaction, and Roxanne treats it accordingly. She is
      unhurried with the questions, straight with the answers, and genuinely invested in how it
      turns out for you.</p>
      <p>She also sells in Mount Gravatt East, Coorparoo, Annerley and Tarragindi, though the
      greater part of her work is here.</p>
      <div class="btnrow" style="margin-top:26px">
        <a class="btn" href="appraisal.html">Request an appraisal</a>
      </div>
      <p class="sig"><strong>{AGENT}</strong>{AGENCY} · <a href="tel:{TEL}">{PHONE}</a></p>
    </div>
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <p class="kick" style="color:rgba(255,255,255,.55)">No cost, no obligation</p>
    <h2>Thinking of <em>selling</em>?</h2>
    <p>A written appraisal with the comparable sales behind it, and a considered view on timing.
    No cost, no obligation, and no pressure to list.</p>
    <div class="btnrow" style="justify-content:center">
      <a class="btn solid" href="appraisal.html">Request an appraisal</a>
      <a class="btn" href="tel:{TEL}">Call {PHONE}</a>
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap mid">
    <p class="kick">Blog</p>
    <h2 style="font-size:2rem">What is changing in <em>Queensland</em>.</h2>
    <div class="posts" style="margin-top:22px">{{POSTS}}</div>
    <p style="margin-top:26px"><a class="textlink" href="journal.html">Read the blog</a></p>
  </div>
</section>
"""

LISTINGS_BODY = f"""
<section class="tight">
  <div class="wrap mid centre">
    <p class="kick">Holland Park West 4121</p>
    <h1>Listings</h1>
  </div>
</section>

<section style="padding-top:10px">
  <div class="wrap">

    <div class="toggle" role="tablist" aria-label="Listing status">
      <button role="tab" id="tab-current" aria-controls="panel-current" aria-selected="true">Current <em>listings</em></button>
      <button role="tab" id="tab-sold" aria-controls="panel-sold" aria-selected="false">Sold <em>listings</em></button>
    </div>

    <div class="cards" id="panel-current" role="tabpanel" aria-labelledby="tab-current">
      {{CURRENT}}
    </div>

    <div id="panel-sold" role="tabpanel" aria-labelledby="tab-sold" hidden>
      <div class="cards">{{SOLD}}</div>
      <p class="formnote" style="margin-top:26px;text-align:center">{{PRIOR}}</p>
    </div>
  </div>
</section>

<section class="band" id="offmarket">
  <div class="wrap cols">
    <div>
      <p class="kick">Not advertised</p>
      <h2>Off market, and <em>coming soon</em>.</h2>
      <p>Not every home is advertised the day it comes up. Some are still being prepared, and some
      sell early to a buyer who was already registered and looking for exactly that house.</p>
      <p>Tell Roxanne what you are after and she will be in touch when something fits, usually
      before it reaches the portals. No cost, no obligation, and your details are not passed on.</p>
      <p class="sig" style="border:0;padding:0;margin-top:18px"><strong>{AGENT}</strong>
      <a href="tel:{TEL}">{PHONE}</a></p>
    </div>
    <div>
      {{OFFFORM}}
    </div>
  </div>
</section>
"""

LISTINGS_JS = """
(function(){
  var tabs=[['tab-current','panel-current'],['tab-sold','panel-sold']];
  tabs.forEach(function(t){
    var b=document.getElementById(t[0]); if(!b) return;
    b.addEventListener('click',function(){
      tabs.forEach(function(o){
        var ob=document.getElementById(o[0]), op=document.getElementById(o[1]);
        var on=(o[0]===t[0]);
        if(ob) ob.setAttribute('aria-selected',on);
        if(op) op.hidden=!on;
      });
    });
  });
})();
"""

APPRAISAL_FIELDS = (
    '<div class="f"><span class="lbl">What would you like?</span>' +
    checks("need", ["A sales appraisal", "A rental appraisal", "Both"]) + '</div>' +
    field("name", "Your name", kind="text") +
    '<div class="row">' + field("mobile", "Mobile", kind="tel") + field("email", "Email", kind="email") + '</div>' +
    field("address", "Property address", ph="12 Kneale Street, Holland Park West") +
    '<div class="row">' +
    field("timing", "Timeframe", kind="select",
          options=["In the next 3 months", "3 to 6 months", "6 to 12 months",
                   "Further off, just curious", "Not selling, I just want the number"]) +
    field("type", "Property type", kind="select",
          options=["House", "Townhouse", "Unit or apartment", "Land", "Something else"]) +
    '</div>' +
    '<div class="f"><span class="lbl">What would be useful?</span>' +
    checks("wants", ["A written appraisal", "A market snapshot", "What's worth fixing first",
                     "A chat, no paperwork"]) + '</div>' +
    field("buying", "Are you buying as well?", kind="select",
          options=["Yes, buying and selling", "Selling only", "Buying only", "Not sure yet"]) +
    field("notes", "Anything worth knowing?", note="Optional", kind="area",
          ph="Renovations, tenants, a deadline you're working to…")
)

APPRAISAL_BODY = f"""
<section class="tight">
  <div class="wrap mid centre">
    <p class="kick">No cost, no obligation</p>
    <h1>What is your home <em>worth</em>?</h1>
    <p class="lede" style="max-width:60ch;margin:18px auto 0">An appraisal should leave you better
    informed whether or not you decide to sell. Roxanne prepares every one herself, backs it with
    the sales it rests on, and gives it to you in writing.</p>
  </div>
</section>

<section style="padding-top:14px">
  <div class="wrap cols">
    <div>
      <p class="kick" style="margin-bottom:22px">Why ask Roxanne</p>
      <ul class="ticks">
        <li><strong>The sales behind the figure.</strong> The three homes most comparable to yours that have sold recently, and where yours sits against each of them</li>
        <li><strong>What is happening right now.</strong> What is selling in Holland Park West, what it is achieving, and how long it is taking to get there</li>
        <li><strong>What is worth spending money on.</strong> The repairs and improvements that return more than they cost, and the ones you can safely leave</li>
        <li><strong>When to sell.</strong> The timing that suits your circumstances, including waiting, if waiting will serve you better</li>
      </ul>
      <div class="callout" style="margin-top:26px">
        <p><strong>Already spoken to an agent?</strong> Most owners are given a single number with
        nothing to measure it against. Roxanne is happy to provide a second, at no cost and with no
        obligation to list. If you have already signed an agency agreement, check its terms first,
        as most are exclusive for a set period.</p>
      </div>
      <div style="display:flex;gap:18px;align-items:center;margin-top:34px;background:var(--stone);padding:22px">
        {APPRAISALIMG}
        <p style="margin:0;font-size:.97rem;color:var(--muted)">Roxanne carries out every appraisal herself. She will walk through the home with you and tell you, plainly, what she believes it will sell for.</p>
      </div>
      <div class="callout" style="margin-top:22px">
        <p><strong>Buying as well?</strong> Note it below. Aligning a sale with a purchase is the
        part most people find difficult, and it is far easier to plan from the outset than to
        correct midway. Roxanne will map both sides out with you before anything is listed.</p>
      </div>
    </div>
    <div>
      {form_block(
        subject="Appraisal request",
        required='[["name","your name"],["mobile","your mobile"],["address","the property address"]]',
        groups='[["need","Appraisal type"],["wants","What would be useful"]]',
        fields_html=APPRAISAL_FIELDS,
        send_label="Request my appraisal",
        thanks_html=f'''<h3>Thank you</h3>
          <p>Roxanne will call within one business day to ask a few questions about the property,
          then prepare your appraisal.</p>
          <p>To speak with her sooner, call <strong>{PHONE}</strong>.</p>''',
        note="Your details are used to prepare this appraisal and follow it up, and are not shared with anyone else.")}
    </div>
  </div>
</section>

<section class="band" id="rental">
  <div class="wrap cols">
    <div>
      <p class="kick">Not selling</p>
      <h2>What would it <em>rent</em> for?</h2>
      <p>Many of the people asking about value are not planning to sell at all. They are weighing
      up whether to keep the property, move out and let it, or work out whether the numbers stack up
      before buying somewhere else.</p>
      <p>A rental appraisal answers that question, and it costs nothing.</p>
      <ul class="ticks" style="margin-top:22px">
        <li><strong>A weekly rent range</strong> based on what comparable properties are actually
            leasing for, rather than what they are advertised at</li>
        <li><strong>How long it should take to lease,</strong> and the times of year that work for
            and against you</li>
        <li><strong>What tenants here look for,</strong> and the small improvements that lift the
            rent by more than they cost</li>
        <li><strong>The holding costs</strong> set alongside the rent, so you can see the real
            position rather than the gross figure</li>
        <li><strong>Sale and rental side by side,</strong> if you would like to compare keeping the
            property against selling it</li>
        <li><strong>Help finding a rental</strong> if you are selling first and need somewhere to
            live while you build or keep looking</li>
      </ul>
      <div class="btnrow" style="margin-top:28px">
        <button type="button" class="btn dark" id="wantrent">Ask for a rental appraisal</button>
      </div>
    </div>
    <div>
      <div class="panel bordered">
        <h3>Already renting it out?</h3>
        <p style="color:var(--muted)">It is worth reviewing the figure every year or two. Rents
        move, and a property that was well priced when the lease began can sit beneath the market
        for a long time without anyone noticing.</p>
        <p style="color:var(--muted);margin-bottom:0">To talk it through, call
        <strong>{PHONE}</strong>.</p>
      </div>
      <div class="panel bordered" style="margin-top:16px">
        <h3>Selling, then renting?</h3>
        <p style="color:var(--muted);margin-bottom:0">Many owners sell before they have somewhere
        to go, whether they are building, still looking, or waiting out the market. Roxanne helps
        her sellers find a rental for that stretch, so you are never forced to choose between a weak
        offer and having nowhere to live at settlement. Tell her what you need and when, and it is
        handled alongside the sale.</p>
      </div>
      <div class="panel bordered" style="margin-top:16px">
        <h3>Buying an investment?</h3>
        <p style="color:var(--muted);margin-bottom:0">Send the address through before you make an
        offer and Roxanne will tell you what it should let for. That figure decides whether the
        purchase works, and it is far better known beforehand than afterwards.</p>
      </div>
    </div>
  </div>
</section>
"""

RENTAL_JS = """
(function(){
  var b=document.getElementById('wantrent'); if(!b) return;
  b.addEventListener('click',function(){
    var boxes=document.querySelectorAll('input[name="need"]');
    [].forEach.call(boxes,function(x){ x.checked = (x.value==='A rental appraisal'); });
    var f=document.getElementById('f');
    if(f){ f.scrollIntoView({behavior:'smooth',block:'start'}); }
    var n=document.getElementById('name'); if(n) setTimeout(function(){n.focus({preventScroll:true})},500);
  });
})();
"""

REFERRAL_FIELDS = (
    '<div class="f"><span class="lbl">Who do you need?</span>' +
    # Wording kept the same as the list above, so nothing wraps onto two lines
    checks("need", ["Mortgage broker", "Solicitor or conveyancer", "Building and pest",
                    "Depreciation schedule", "Removalist", "Trades or styling",
                    "Property manager", "A rental in between",
                    "Not sure yet"]) + '</div>' +
    field("name", "Your name", kind="text") +
    '<div class="row">' + field("mobile", "Mobile", kind="tel") + field("email", "Email", kind="email") + '</div>' +
    field("address", "Which property?", note="Optional", ph="Address, or the suburb you're looking in") +
    field("timing", "How soon?", kind="select",
          options=["This week", "In the next fortnight", "This month", "Just planning ahead"]) +
    field("notes", "Anything useful to pass on?", note="Optional", kind="area",
          ph="First home, self-employed, tight settlement, investment purchase…")
)

REFERRALS_BODY = f"""
<section class="tight">
  <div class="wrap mid centre">
    <p class="kick">People Roxanne works with</p>
    <h1>Brokers, solicitors and <em>inspectors</em>.</h1>
  </div>
</section>

<section style="padding-top:14px">
  <div class="wrap">
    <div class="helpers">
      <div><h2>Mortgage broker</h2><p>Pre-approval before you bid, and a clear figure for what you can actually borrow. Worth doing even if you have already spoken to your own bank.</p></div>
      <div><h2>Solicitor or conveyancer</h2><p>Your contract reviewed before you sign, and the disclosure pack handled properly. Queensland's rules changed in 2025, so this matters more than it once did.</p></div>
      <div><h2>Building and pest</h2><p>Inspectors who turn their reports around quickly and will talk you through what is serious and what is simply normal for the age of the house.</p></div>
      <div><h2>Depreciation schedule</h2><p>If you are buying an investment, a quantity surveyor can prepare one. Whether it is worthwhile depends on the property and your own position, so speak with your accountant.</p></div>
      <div><h2>Removalists and storage</h2><p>People who arrive when they say they will, and who know how to get a fridge down a Queenslander staircase.</p></div>
      <div><h2>Trades and styling</h2><p>Painters, gardeners, carpet, and a stylist who understands what buyers in this pocket respond to.</p></div>
      <div><h2>Somewhere to live in between</h2><p>Selling before you buy, or building? Roxanne helps her sellers find a rental for the gap, so the sale is never rushed by having nowhere to go.</p></div>
    </div>

    <div class="cols">
      <div>
        <p class="kick">How this works</p><h2 style="font-size:2rem;margin-bottom:22px">Roxanne has people she <em>trusts</em>.</h2>
        <p>If you are struggling to find a good broker, solicitor, building inspector or trade,
        Roxanne works with these people regularly and is happy to recommend them.</p>
        <p>Tell her what you need and she will send through a name and a number, and let them know to
        expect your call. There is no obligation to use them, and you are very welcome to use your
        own.</p>
        <p>Looking after people properly does not stop at the contract, and this is part of how
        Roxanne does it.</p>
        <p class="formnote" style="margin-top:14px">Roxanne does not receive a fee or commission
        for any of these introductions. Her details are passed to them only so they know to expect
        your call.</p>
      </div>
      <div>
        {form_block(
          subject="Referral request",
          required='[["name","your name"],["mobile","your mobile"]]',
          groups='[["need","Needs"]]',
          fields_html=REFERRAL_FIELDS,
          send_label="Send my request",
          thanks_html=f'''<h3>Leave it with us</h3>
            <p>Roxanne will send the introduction through, usually the same day.</p>
            <p>If you need it sooner, call <strong>{PHONE}</strong>.</p>''')}
      </div>
    </div>
  </div>
</section>
"""

SUBURB_BODY = f"""
<section class="wordhero">
  <div class="wrap">
    <p class="kick">Suburb guide, postcode 4121</p>
    <h1>Holland Park <em>West</em></h1>
    <div class="btnrow"><a class="btn" href="appraisal.html">What's my home worth</a></div>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="strip">
      <div><b>8.4km</b><span>South east of the CBD</span></div>
      <div><b>2.8km²</b><span>Suburb area</span></div>
      <div><b>6,468</b><span>Residents, 2021 census</span></div>
      <div><b>4121</b><span>Postcode</span></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap cols">
    <div>
      <p class="kick">The market</p><h2>Who buys here, and <em>why</em>.</h2>
      <p>Holland Park West does something unusual for a suburb this close to the city. The blocks
      are generous by inner south standards, much of the housing sits high enough to hold a view, and
      both the motorway and the busway are minutes away.</p>
      <p>The buyers are mainly families moving up from Greenslopes and Coorparoo in search of a
      fourth bedroom and a yard, alongside downsizers who want to stay close to family and schools.
      Both groups know the recent sales well, which is why an overpriced home sits here.</p>
    </div>
    <div>
      <p class="kick">The practical stuff</p><h2 style="font-size:2rem;margin-bottom:24px">Getting around, and <em>getting in</em>.</h2>
      <ul class="ticks">
        <li><strong>Getting in and out.</strong> Holland Park West busway station on the South East
            Busway, with the Pacific Motorway along the western edge</li>
        <li><strong>Schools in the suburb.</strong> Marshall Road State School, Holland Park State High
            School and Nursery Road State Special School</li>
        <li><strong>Neighbours.</strong> Greenslopes, Holland Park, Mount Gravatt East, Tarragindi,
            Nathan and Mount Gravatt</li>
        <li><strong>Green space.</strong> Whites Hill Reserve is a short drive, with bushland tracks,
            sporting fields and lookouts across the city</li>
        <li><strong>Local history.</strong> The Holland Park Hotel, Glindemann Farmhouse, a former tram
            shelter and St Joachim's Catholic Church are all heritage-listed</li>
      </ul>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap mid centre">
    <p class="kick">Living here</p>
    <h2 style="margin-bottom:34px">Why people <em>stay</em>.</h2>
  </div>
  <div class="wrap mid" style="text-align:left">
    <div class="values">
      <div class="vrow"><span class="no">01</span><h3><em>Close in, without the squeeze</em></h3>
        <p>Eight kilometres from the CBD, and yet the blocks remain generous for that distance. You
        get a yard, a driveway you can turn a car around in, and room for the trampoline. Two suburbs
        closer to town, the same money buys a townhouse.</p></div>
      <div class="vrow"><span class="no">02</span><h3><em>Two ways into town</em></h3>
        <p>Holland Park West busway station puts you on the South East Busway with no traffic
        between you and the city, while the Pacific Motorway runs along the western edge for anyone
        who would rather drive.</p></div>
      <div class="vrow"><span class="no">03</span><h3><em>Height, and the view that comes with it</em></h3>
        <p>Much of the suburb sits high, and the right block will catch the city skyline to the
        north west along with a breeze in February.</p></div>
      <div class="vrow"><span class="no">04</span><h3><em>Schools inside the boundary</em></h3>
        <p>Marshall Road State School, Holland Park State High School and Nursery Road State Special
        School all sit inside the suburb boundary, with Griffith University's Nathan campus a short
        drive away.</p></div>
      <div class="vrow"><span class="no">05</span><h3><em>Everything within ten minutes</em></h3>
        <p>Greenslopes Mall and Westfield Garden City for the shopping, Greenslopes Private Hospital
        for the part nobody plans for, and the cafes and restaurants along Logan Road for
        everything else.</p></div>
      <div class="vrow"><span class="no">06</span><h3><em>Green space on the doorstep</em></h3>
        <p>Whites Hill Reserve offers bushland tracks, sporting fields and lookouts across the city,
        and the Mount Gravatt lookout is only minutes away.</p></div>
      <div class="vrow"><span class="no">07</span><h3><em>A suburb that is being rebuilt</em></h3>
        <p>Post war houses on good blocks are steadily being replaced by new homes, which is why the
        street you buy into today will look quite different in ten years. It also means land here has
        a second buyer: the one who wants the block rather than the house.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="kick">Street to street</p><h2>What <em>actually</em> changes the price.</h2>
    <p class="lede">Two houses with the same floorplan can sit $100,000 apart in this suburb. These
    are usually the reasons why.</p>
    <div class="pockets" style="margin-top:28px">
      <div class="pocket"><h3>Elevation</h3>
        <p>Height is the single biggest swing factor here. A block that catches the skyline to the
        north west will sell well above one sitting in a gully two streets away.</p></div>
      <div class="pocket"><h3>Motorway noise</h3>
        <p>The M3 cuts both ways. It is excellent for the commute and audible along the western
        edge, and buyers price that in. Where the house sits relative to the cutting matters far more
        than the distance on a map.</p></div>
      <div class="pocket"><h3>Catchment</h3>
        <p>Families buying for a particular school will pay to be on the right side of the line, and
        they will not consider anything outside it. Always worth confirming before you go to
        market.</p></div>
      <div class="pocket"><h3>Block shape and access</h3>
        <p>Side access, a flat rear yard and a driveway you can turn a car around in are worth more
        in this suburb than an extra bathroom.</p></div>
      <div class="pocket"><h3>What's underneath</h3>
        <p>A great deal of post war stock has been lifted and built in underneath. Whether that work
        was approved and certified makes a real difference now that the disclosure rules have
        tightened.</p></div>
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="panel" style="display:flex;gap:28px;flex-wrap:wrap;align-items:center;justify-content:space-between">
      <div style="max-width:54ch">
        <h3 style="font-size:1.5rem;font-weight:400;letter-spacing:-.015em">Want to know where your street sits?</h3>
        <p style="margin:0;color:var(--muted)">Send the address through and Roxanne will come back
        with the recent sales that genuinely compare, and what yours would achieve today. No cost,
        and no obligation to go any further.</p>
      </div>
      <a class="btn dark" href="appraisal.html">Send the address</a>
    </div>
    <p class="formnote" style="margin-top:24px">Suburb facts from the
      <a href="https://en.wikipedia.org/wiki/Holland_Park_West,_Queensland" target="_blank" rel="noopener" style="color:var(--ink)">Holland Park West suburb entry</a>
      and the 2021 census. Everything else is Roxanne's own read on the area, so speak with her
      about your particular street before relying on it.</p>
  </div>
</section>
"""


OFF_FIELDS = (
    field("name", "Your name", kind="text") +
    '<div class="row">' + field("mobile", "Mobile", kind="tel") + field("email", "Email", kind="email") + '</div>' +
    '<div class="f"><span class="lbl">Where are you looking?</span>' +
    checks("areas", ["Holland Park West", "Holland Park", "Mount Gravatt East",
                     "Coorparoo", "Annerley", "Tarragindi"]) + '</div>' +
    '<div class="row">' +
    field("budget", "Budget", kind="select",
          options=["Up to $1m", "$1m to $1.5m", "$1.5m to $2m", "$2m to $3m",
                   "$3m and above", "Depends on the property"]) +
    field("type", "What are you after?", kind="select",
          options=["A house to live in", "A knockdown or development site",
                   "A new build", "An investment", "Not sure yet"]) +
    '</div>' +
    field("notes", "Anything specific?", note="Optional", kind="area",
          ph="Four bedrooms, flat yard, needs to be in the Marshall Road catchment...")
)
OFF_FORM = form_block(
    subject="Off market enquiry",
    required='[["name","your name"],["mobile","your mobile"]]',
    groups='[["areas","Areas"]]',
    fields_html=OFF_FIELDS,
    send_label="Add me to the list",
    thanks_html=f'''<h3>You are on the list</h3>
      <p>Roxanne will call when something comes up that matches. To talk it through
      sooner, call <strong>{PHONE}</strong>.</p>''',
    note="Your details are used to let you know about matching properties and nothing else.")


# ============================ expression of interest ============================

OFFER_FIELDS = (
    field("property", "Which property?", ph="12 Kneale Street, Holland Park West") +
    '<div class="f"><span class="lbl">Who is buying?</span>' +
    checks("buyertype", ["Owner occupier", "Investor", "First home buyer",
                         "Builder or developer", "Trust or company"]) + '</div>' +
    field("name", "Full name of every buyer", note="As it will appear on the contract",
          kind="area", ph="Jane Mary Citizen and John Alan Citizen") +
    '<div class="row">' + field("mobile", "Mobile", kind="tel") + field("email", "Email", kind="email") + '</div>' +
    field("address", "Your current address") +
    '<div class="row">' +
    field("licence", "Driver licence number") +
    field("licencestate", "Licence state", kind="select",
          options=["QLD", "NSW", "VIC", "SA", "WA", "TAS", "NT", "ACT", "Overseas"]) +
    '</div>' +
    '<div class="f"><span class="lbl">Driver licence photo <small>Optional at this stage</small></span>' +
    '<p class="hint" style="margin:-2px 0 12px">Front and back. Only needed to prepare a contract, '
    'so you are welcome to leave it until your offer is accepted. Photos of the card are fine, '
    'JPG, PNG or PDF up to 10MB each.</p>' +
    '<div class="row">' +
      '<div class="f"><label class="lbl lite" for="licfront">Front</label>'
      '<input type="file" id="licfront" accept="image/*,application/pdf"></div>' +
      '<div class="f"><label class="lbl lite" for="licback">Back</label>'
      '<input type="file" id="licback" accept="image/*,application/pdf"></div>' +
    '</div></div>' +

    '<h2 class="fsec" style="margin:34px 0 14px">Your offer</h2>' +
    '<div class="row">' +
    field("price", "Price offered", ph="$1,850,000") +
    field("deposit", "Deposit", ph="$50,000, or 5%") +
    '</div>' +
    '<div class="row">' +
    field("settlement", "Settlement", kind="select",
          options=["30 days", "45 days", "60 days", "90 days", "Flexible, to suit the seller", "Other"]) +
    field("finance", "Finance", kind="select",
          options=["Cash, no finance needed", "Pre-approved", "Subject to finance", "Not yet arranged"]) +
    '</div>' +
    field("lender", "Lender or broker", note="If your offer is subject to finance",
          ph="Bank or broker name, and their contact") +
    '<div class="f"><span class="lbl">Conditions</span>' +
    checks("conditions", ["Building and pest", "Subject to finance", "Subject to my sale",
                          "Due diligence", "None, unconditional"]) + '</div>' +

    '<h2 class="fsec" style="margin:34px 0 14px">Your solicitor</h2>' +
    '<div class="row">' +
    field("solicitor", "Solicitor or conveyancer", note="Optional") +
    field("solicitorcontact", "Their phone or email", note="Optional") +
    '</div>' +
    field("notes", "Anything the seller should know?", note="Optional", kind="area",
          ph="Why you want the home, how quickly you can move, anything that strengthens your offer...")
)

OFFER_BODY = f"""
<section class="tight">
  <div class="wrap mid centre">
    <p class="kick">Expression of interest</p>
    <h1>Put your offer <em>forward</em>.</h1>
  </div>
</section>

<section style="padding-top:8px">
  <div class="wrap narrow">
    {{OFFERFORM}}
    <div class="callout" style="margin-top:26px">
      <p>Not sure what to put? Call <strong>{PHONE}</strong> before you submit.</p>
    </div>
  </div>
</section>
"""

OFFER_JS = """
(function(){
  var q=new URLSearchParams(window.location.search).get('p');
  if(!q) return;
  var f=document.getElementById('property');
  if(f && !f.value){
    f.value=q.split('-').map(function(w){
      if(!w) return w;
      var c=w.charAt(0);
      if(c>='0' && c<='9') return w.toUpperCase();
      return c.toUpperCase()+w.slice(1);
    }).join(' ');
  }
})();
"""


# ============================ auction registration ============================

AUCTION_FIELDS = (
    '<div class="row">' +
    field("property", "Property", ph="12 Kneale Street, Holland Park West") +
    field("auctiondate", "Auction date", ph="Saturday 25 October, 10:00am") +
    '</div>' +

    '<h3 style="margin:30px 0 14px">Who is bidding</h3>' +
    field("name", "Full name of the person bidding", ph="As it appears on your identification") +
    '<div class="row">' + field("mobile", "Mobile", kind="tel") + field("email", "Email", kind="email") + '</div>' +
    field("address", "Residential address", ph="Street, suburb, state, postcode") +
    '<div class="row">' +
    field("idtype", "Identification", kind="select",
          options=["Queensland driver licence", "Interstate driver licence",
                   "Australian passport", "Overseas passport", "Proof of age card", "Other"]) +
    field("idnumber", "Identification number") +
    '</div>' +
    '<div class="f"><span class="lbl">Photo of your identification <small>Front and back</small></span>' +
    '<p class="hint" style="margin:-2px 0 12px">The auctioneer has to be satisfied of your identity '
    'before issuing a bidder number. Sending it now means you are registered before you arrive '
    'rather than queuing on the day.</p>' +
    '<div class="row">' +
      '<div class="f"><label class="lbl lite" for="idfront">Front</label>'
      '<input type="file" id="idfront" accept="image/*,application/pdf"></div>' +
      '<div class="f"><label class="lbl lite" for="idback">Back</label>'
      '<input type="file" id="idback" accept="image/*,application/pdf"></div>' +
    '</div></div>' +

    '<h3 style="margin:30px 0 14px">In what capacity</h3>' +
    '<div class="f"><span class="lbl">I am bidding</span>' +
    checks("capacity", ["In my own name",
                        "With a co-buyer",
                        "For a company",
                        "As trustee of a trust",
                        "For another person",
                        "Under a power of attorney",
                        "As a buyer's agent"]) + '</div>' +
    field("cobuyer", "Any other buyers' full names", note="If the contract will be in more than one name",
          kind="area", ph="Every name that will appear on the contract") +
    '<div class="row">' +
    field("company", "Company or trust name", note="If applicable") +
    field("acn", "ACN or ABN", note="If applicable") +
    '</div>' +
    field("position", "Your position in the company or trust", note="If applicable",
          ph="Director, secretary, authorised officer") +
    field("onbehalf", "If bidding for someone else, their full name and address",
          note="Optional", kind="area",
          ph="Queensland requires this to be disclosed before bidding starts") +
    '<div class="f"><label class="lbl" for="authority">Written authority '
    '<small>If bidding for someone else</small></label>' +
    '<p class="hint" style="margin:-2px 0 12px">A letter of authority or power of attorney. '
    'Without it the auctioneer cannot accept your bid on their behalf.</p>' +
    '<input type="file" id="authority" accept="image/*,application/pdf"></div>' +

    '<h3 style="margin:30px 0 14px">Before the day</h3>' +
    '<div class="f"><span class="lbl">Please confirm</span>' +
    checks("confirm", ["I have the contract and disclosure statement",
                       "I understand an auction contract is unconditional",
                       "I can pay the deposit on the fall of the hammer",
                       "My finance is arranged"]) + '</div>' +
    field("solicitor", "Your solicitor or conveyancer", note="Optional") +
    field("notes", "Anything worth knowing?", note="Optional", kind="area",
          ph="A question about the contract, the deposit, or bidding by phone...")
)

AUCTION_BODY = f"""
<section class="tight">
  <div class="wrap mid centre">
    <p class="kick">Auction</p>
    <h1>Register to <em>bid</em>.</h1>
    <p class="lede">In Queensland only registered bidders can bid, and the auctioneer has to be
    satisfied of your identity before issuing your bidder number. Doing it here means you walk in,
    collect your number and go.</p>
  </div>
</section>

<section style="padding-top:14px">
  <div class="wrap cols">
    <div>
      <p class="kick">How auction day runs</p>
      <h2 style="font-size:2rem;margin-bottom:22px">No surprises on the <em>day</em>.</h2>
      <ul class="ticks">
        <li><strong>Register before you bid.</strong> Only registered bidders can bid. Register here
            and your number is waiting for you</li>
        <li><strong>Bidding for someone else?</strong> It must be disclosed before bidding starts
            and written authority is required. Send it through with this form</li>
        <li><strong>Buying in a company or trust?</strong> The name on the contract has to be right
            on the day. Send the details through now and the contract is prepared correctly</li>
        <li><strong>An auction contract is unconditional.</strong> No finance clause, no building
            and pest clause. Do that work beforehand</li>
        <li><strong>The deposit is payable on the fall of the hammer.</strong> Have it ready to transfer</li>
      </ul>
      <div class="callout" style="margin-top:26px">
        <p>Cannot be there? Phone and proxy bidding can usually be arranged, but must be set up in
        advance. Call <strong>{PHONE}</strong> to organise it.</p>
      </div>
      <p class="formnote" style="margin-top:20px">General information only, not legal advice. Your
      solicitor should review the contract and the disclosure statement before you bid.</p>
    </div>
    <div>
      {{AUCTIONFORM}}
    </div>
  </div>
</section>
"""

AUCTION_JS = """
(function(){
  var q=new URLSearchParams(window.location.search);
  var p=q.get('p'), d=q.get('d');
  var f=document.getElementById('property');
  if(f && p && !f.value){
    f.value=p.split('-').map(function(w){
      if(!w) return w;
      var c=w.charAt(0);
      if(c>='0' && c<='9') return w.toUpperCase();
      return c.toUpperCase()+w.slice(1);
    }).join(' ');
  }
  var a=document.getElementById('auctiondate');
  if(a && d && !a.value) a.value=d.replace(/\+/g,' ');
})();
"""


# ============================ suburb market update ============================

UPDATE_FIELDS = (
    '<div class="row">' + field("name", "First name") + field("email", "Email", kind="email") + '</div>' +
    '<div class="row">' +
    field("street", "Your street", note="Optional", ph="So the update is relevant to you") +
    field("mobile", "Mobile", note="Optional, for anything urgent", kind="tel") + '</div>' +
    '<div class="f"><span class="lbl">Which are you?</span>' +
    checks("who", ["I own in Holland Park West", "I own in Holland Park",
                   "I am looking to buy here", "I am a neighbour, just interested"]) + '</div>'
)

UPDATE_BLOCK = f"""
<section class="band" id="update">
  <div class="wrap cols">
    <div>
      <p class="kick">Every sale, every month</p>
      <h2>The Holland Park West <em>update</em>.</h2>
      <p>Once a month, a single email listing every house that sold in Holland Park West and
      Holland Park, what it achieved and how long it took to get there.</p>
      <p style="margin-bottom:0">Free, and one click to stop at any time.</p>
    </div>
    <div>
      {{UPDATEFORM}}
    </div>
  </div>
</section>
"""

# ============================ journal ============================

POSTS = [
 dict(slug="journal-smoke-alarms.html",
      date="2 October 2026",
      sort="2026-10-02",
      title="Every Queensland home needs interconnected smoke alarms by 1 January 2027",
      blurb="The deadline applies from 1 January 2027, and it covers the home you live in, not just rentals.",
      body="""
<p>If you own the home you live in, Queensland's smoke alarm rules change on <strong>1 January 2027</strong>.
From that date all owner-occupied private homes, townhouses and units have to meet the same standard that
rental and recently sold properties have had to meet for years.</p>

<h2>What the standard actually is</h2>
<p>Three things have to be true of the alarms in the house:</p>
<ul>
  <li>They are <strong>photoelectric</strong>, the type that reacts to smouldering smoke rather than flame</li>
  <li>They are <strong>interconnected</strong>, so when one sounds, every alarm in the house sounds</li>
  <li>They meet <strong>Australian Standard 3786-2014</strong></li>
</ul>
<p>Interconnection is the part people underestimate. A working alarm in a hallway is no use to someone
asleep at the other end of the house with the door shut. When they are linked, the whole house gets the
same warning at the same time.</p>

<div class="callout">
  <p>Selling or renting out a home? You already have to comply at the point of sale or lease. That rule started in 2022. The 2027 date simply closes the gap for everyone else.</p>
</div>

<h2>What this means if you're selling</h2>
<p>Compliance comes up twice in a sale. It is a question on the paperwork, and it is one of the first
things a building and pest inspector notes. A buyer will not walk away over the alarms, but they
will use them to chip at the price late in the piece.</p>
<p>It is cheap to deal with early. Electricians are quoting a few hundred dollars for a typical house,
and the work takes a morning. Compare that to a buyer asking for a reduction two days before settlement.</p>

<h3>Worth doing now, not in December</h3>
<p>Electricians get busy as the deadline
closes in. If your alarms are the old ionisation type, or they are not linked, get a quote now while
you can still choose when the work happens.</p>

<h2>Quick self-check</h2>
<ul>
  <li>Look at the alarm. Photoelectric units usually say so on the housing</li>
  <li>Check the date stamped on it. Alarms expire about ten years from manufacture</li>
  <li>Press and hold the test button on one. If the others don't sound too, they are not interconnected</li>
  <li>Count the bedrooms. You need an alarm in each bedroom, in hallways connecting bedrooms, and on
      every storey</li>
</ul>
<p>If you're not sure what you're looking at, send me a photo. I've seen a lot of these.</p>
""",
      sources=[("Smoke alarms (Queensland Government)", "https://www.qld.gov.au/emergency/safety/fire/smoke-alarms"),
               ("Smoke alarm reforms (Queensland Fire Department)", "https://www.fire.qld.gov.au/about-us/corporate-knowledge-centre/qfdlegislation/smoke-alarm-reforms")]),

 dict(slug="journal-seller-disclosure.html",
      date="24 September 2026",
      sort="2026-09-24",
      title="Seller disclosure in Queensland: what the Form 2 means for you",
      blurb="Since August 2025 sellers have had to hand over a disclosure statement before a buyer signs. A year in, here's where people still come unstuck.",
      body="""
<p>Queensland's seller disclosure scheme started on <strong>1 August 2025</strong> under the
<em>Property Law Act 2023</em>. The short version: before a buyer signs a contract, the seller has to give
them a completed <strong>Form 2 disclosure statement</strong> along with a set of prescribed certificates.</p>

<h2>What goes in it</h2>
<p>The statement and its attachments cover the things a buyer would reasonably want to know before
committing, including:</p>
<ul>
  <li>Who the seller is and what is being sold</li>
  <li>Title details, encumbrances and any tenancy in place</li>
  <li>Zoning, transport infrastructure notices and heritage listings</li>
  <li>Whether there is a pool, and a pool safety certificate where one applies</li>
  <li>Body corporate information for scheme land</li>
  <li>Prescribed certificates, covering title searches, environmental notices and building compliance documents</li>
</ul>

<h2>The part that matters most</h2>
<p>If the disclosure isn't given before signing, or it's given but materially wrong or incomplete, the
buyer may be able to <strong>terminate the contract at any time up to settlement</strong>. For an
inaccuracy, the buyer has to show the problem was material, that they didn't already know, and that they
wouldn't have signed had they known.</p>

<div class="callout">
  <p>The real risk for a seller is a buyer pulling out weeks later, after you have already bought
  somewhere else.</p>
</div>

<h2>Where people still get caught</h2>
<h3>Leaving it until there's an offer</h3>
<p>The searches take time to come back. If a buyer is ready to sign on a Sunday and the pack isn't
ready, you're choosing between losing momentum and signing something that can unravel. Order it before
you go to market, not after.</p>

<h3>Assuming it's the agent's job</h3>
<p>The obligation sits with the seller. In practice your solicitor or conveyancer prepares it, and a good
agent makes sure it exists and is in the buyer's hands before anyone signs anything. If nobody has
mentioned a Form 2 to you, ask.</p>

<h3>Letting it go stale</h3>
<p>Certificates have currency. A pack prepared months ago for a campaign that stalled may need refreshing
before it's handed to a new buyer. Check with your solicitor rather than assuming.</p>

<h2>What I do about it</h2>
<p>For every listing I take, the disclosure pack is organised before we launch, and a copy sits with the
brochure so a serious buyer can have it in front of their solicitor the same day. That saves about
a week of back and forth, and gives the buyer nothing to renegotiate on.</p>
""",
      sources=[("Seller disclosure scheme (Queensland Government)", "https://www.qld.gov.au/law/housing-and-neighbours/buying-and-selling-a-property/seller-disclosure-scheme"),
               ("Seller disclosure statement, Form 2 (Queensland Government Publications)", "https://www.publications.qld.gov.au/dataset/property-law-act-2023-forms")]),

 dict(slug="journal-duty-changes.html",
      date="12 September 2026",
      sort="2026-09-12",
      title="Transfer duty concessions now depend on your residency status",
      blurb="From 1 August 2026 the home and first home concessions are limited to citizens and permanent residents. If you're on a temporary visa, the sums changed.",
      body="""
<p>From <strong>1 August 2026</strong>, Queensland's transfer duty home concessions are restricted by
residency status. The concession now applies only where the buyer is:</p>
<ul>
  <li>an Australian citizen, or</li>
  <li>a permanent resident, or</li>
  <li>a self-funded foreign retiree on a legacy subclass 405 or 410 visa</li>
</ul>
<p>It applies to contracts signed on or after that date, and it covers the home concession, the first
home concession and the first home vacant land concession.</p>

<h2>What changes for a temporary visa holder</h2>
<p>Two things happen at once. The concessional rate is gone, so duty is
calculated at the standard rates. On top of that, additional foreign acquirer duty of 8% applies.</p>

<div class="callout">
  <p>On a $1.25 million home, that's the difference between a concessional calculation and full duty
  <em>plus</em> an 8% surcharge. That can change which suburb you can afford, so work it out before you
  fall in love with a house.</p>
</div>

<h2>If you're buying</h2>
<p>Work out your duty position before you start inspecting, not after you've made an offer. A broker and
a solicitor can tell you in an afternoon where you actually sit, and whether the date you sign matters.
If your permanent residency is close to being granted, timing could be worth real money.</p>

<h2>If you're selling</h2>
<p>In suburbs with a lot of temporary residents this changes who can bid. There are not fewer
buyers, but the ones affected have less to spend and will push harder on price and conditions. Knowing which of your buyers this touches is useful
when you're weighing up offers.</p>

<p>The Queensland Revenue Office publishes the detail and a duty calculator, and your solicitor can
confirm your position. Don't take a number from a portal's estimator as gospel.</p>
""",
      sources=[("Home concession changes from August 2026 (Queensland Revenue Office)", "https://qro.qld.gov.au/event/changes-to-home-concessions/"),
               ("Transfer duty concessions and exemptions (Queensland Government)", "https://www.qld.gov.au/housing/buying-owning-home/home-buyers-financial-help/transfer-duty")]),
]

def post_card(p, compact=False, level=3):
    """level keeps the headings in order: h2 straight under the page title on the blog
    index, h3 on the home page where they sit under a section heading."""
    body = f'<h{level}>{html.escape(p["title"])}</h{level}>'
    if not compact:
        body += f'<p>{html.escape(p["blurb"])}</p>'
    return (f'<a class="post" href="{p["slug"]}">'
            f'<span class="date">{p["date"]}</span>'
            f'<span>{body}</span></a>')

def article_schema(p):
    body_text = html.unescape(__import__("re").sub(r"<[^>]+>", " ", p["body"]))
    return '<script type="application/ld+json">' + json.dumps({
      "@context": "https://schema.org", "@type": "Article",
      "headline": p["title"], "description": p["blurb"],
      "datePublished": p["sort"], "dateModified": p["sort"],
      "author": {"@type": "Person", "name": AGENT},
      "publisher": {"@type": "Organization", "name": BRAND,
                    "logo": {"@type": "ImageObject", "url": f"https://{DOMAIN}/images/og-default.jpg"}},
      "mainEntityOfPage": {"@type": "WebPage", "@id": f"https://{DOMAIN}/" + p["slug"]},
      "image": f"https://{DOMAIN}/images/og-default.jpg",
      "articleSection": "Queensland property",
      "wordCount": len(body_text.split())
    }, separators=(",", ":")) + '</script>'

def post_page(p):
    srcs = "".join(f'<p style="margin:0 0 4px"><a href="{u}" target="_blank" rel="noopener">{html.escape(t)}</a></p>'
                   for t, u in p["sources"])
    body = f"""
<section class="tight">
  <div class="wrap narrow">
    <p class="kick"><a href="journal.html" style="color:var(--muted);text-decoration:none">Blog</a></p>
    <h1 style="font-size:clamp(1.9rem,5.2vw,3rem)">{html.escape(p["title"])}</h1>
    <p class="meta">{p["date"]} · {AGENT}</p>
  </div>
</section>
<section style="padding-top:0">
  <div class="wrap narrow">
    <article class="read">
      {p["body"]}
      <div class="sources">
        <p style="margin:0 0 8px"><strong>Where this comes from</strong></p>
        {srcs}
        <p style="margin-top:14px">General information only, current at the date above. It isn't legal or
        financial advice. Check your own position with your solicitor or accountant.</p>
      </div>
    </article>
    <div class="panel" style="margin-top:44px">
      <h3>Questions about your own place?</h3>
      <p style="color:var(--muted)">Call {AGENT} on <strong>{PHONE}</strong>, or
      <a href="appraisal.html" style="color:var(--ink)">request an appraisal</a>.</p>
      <p style="color:var(--muted);margin-bottom:0">You can also
      <a href="holland-park-west.html#update" style="color:var(--ink)">get every Holland Park West sale once a month</a>,
      so you can see what your own place is doing.</p>
    </div>
  </div>
</section>
"""
    return shell(p["slug"], f'{p["title"]} | {BRAND}', p["blurb"], body, head_extra=article_schema(p))

JOURNAL_BODY = """
<section class="tight">
  <div class="wrap mid centre">
    <p class="kick">Blog</p>
    <h1>What's changed, and what it <em>means</em>.</h1>
  </div>
</section>
<section style="padding-top:0">
  <div class="wrap narrow">
    <div class="posts">{POSTS}</div>
  </div>
</section>
"""

# ============================ write ============================

cards_all = "".join(post_card(p, level=2) for p in sorted(POSTS, key=lambda x: x["sort"], reverse=True))
cards_home = "".join(post_card(p, compact=True) for p in sorted(POSTS, key=lambda x: x["sort"], reverse=True)[:3])

PRIVACY_BODY = f"""
<section class="tight">
  <div class="wrap mid centre">
    <p class="kick">Privacy</p>
    <h1>What happens to your <em>details</em>.</h1>
  </div>
</section>

<section style="padding-top:6px">
  <div class="wrap mid">
    <article class="read">
      <h2>What is collected</h2>
      <p>Only what a form asks for. An appraisal request takes your name, mobile, email and the
      property address. An expression of interest or an auction registration also takes the details
      a contract or a bidder record needs, which can include identification. A referral request
      takes your name and number and what you are looking for.</p>
      <p>Nothing is collected by visiting the site. There is no advertising tracker, no analytics
      script and no cookie set by this site.</p>

      <h2>What it is used for</h2>
      <p>To do the thing you asked for, and to follow it up. An appraisal request is used to
      prepare the appraisal and to talk it through with you. An offer is used to prepare a contract
      and to verify who is making it. A buyer registration is used to let you know when something
      fits.</p>

      <h2>Who it goes to</h2>
      <p>Roxanne, and Aurora Property as the licensed agency. Beyond that:</p>
      <ul>
        <li>An offer is passed to the seller, because that is the point of making one. Identification
        is not.</li>
        <li>A referral request is passed to the one professional you asked for, so they know to
        expect your call. Roxanne does not receive a fee or commission for the introduction.</li>
        <li>Form submissions travel through a third party form service, which stores them while
        they are delivered.</li>
      </ul>
      <p>Your details are not sold, and they are not passed to anyone else for their own marketing.</p>

      <h2>How long it is kept</h2>
      <p>An agency is required by law to keep transaction records for a period after a sale, so
      anything connected to an offer, a contract or a bidder registration is kept for as long as
      that requires. An enquiry that goes nowhere is kept while it is still useful and then
      removed on request.</p>

      <h2>Marketing</h2>
      <p>If you are sent a market update or a newsletter, every one carries an unsubscribe link and
      it is actioned. Asking Roxanne directly works just as well.</p>

      <h2>Seeing it, correcting it, or having it removed</h2>
      <p>Ask. Call {PHONE} or email <a href="mailto:{EMAIL}">{html.escape(EMAIL)}</a> and say what
      you want done. If something is wrong it gets corrected. If you want your details off the list
      they come off.</p>

      <h2>If you are not happy with the answer</h2>
      <p>Raise it with Roxanne first. If that does not resolve it, the Office of the Australian
      Information Commissioner takes privacy complaints, at
      <a href="https://www.oaic.gov.au" target="_blank" rel="noopener">oaic.gov.au</a>.</p>

      <p class="formnote" style="margin-top:34px">This page describes how {AGENT} handles personal
      information collected through this website. Aurora Property may hold its own privacy policy
      covering the agency more broadly, and where the two differ the agency&#8217;s policy applies to
      agency records. Last updated {REPORT_MONTH}.</p>
    </article>
  </div>
</section>
"""


pages = {
  "index.html": shell("index.html", f"Holland Park West Real Estate Agent | {AGENT}, {BRAND}",
      "Roxanne Alterio sells homes in Holland Park West and Holland Park 4121. Recent sales, free written appraisals and a campaign built around your timeline.",
      HOME_BODY.replace("{POSTS}", cards_home).replace("{SALES}", SOLD_ROWS)
                .replace("{PRIOR}", html.escape(PRIOR_AGENCY)), hero=True),
  "listings.html": shell("listings.html", f"Houses for Sale in Holland Park West 4121 | {BRAND}",
      "Houses for sale and recently sold in Holland Park West and Holland Park, with full brochures, inspection times and online offers.",
      LISTINGS_BODY.replace("{CURRENT}", CARDS_CURRENT).replace("{SOLD}", CARDS_SOLD)
                   .replace("{OFFFORM}", OFF_FORM).replace("{PRIOR}", html.escape(PRIOR_AGENCY)),
      LISTINGS_JS + FORM_JS),
  "appraisal.html": shell("appraisal.html", f"Free Property Appraisal, Holland Park West 4121 | {BRAND}",
      "A free written appraisal for your Holland Park West or Holland Park home, built on the comparable sales in your own streets. Sales and rental.",
      APPRAISAL_BODY, FORM_JS + RENTAL_JS),
  "referrals.html": shell("referrals.html", f"Mortgage Broker and Solicitor Referrals, Holland Park West | {BRAND}",
      "Mortgage brokers, solicitors, building and pest inspectors and trades. Introductions to people worth using.",
      REFERRALS_BODY, FORM_JS),
  "holland-park-west.html": shell("holland-park-west.html", f"Holland Park West Suburb Guide and Market, 4121 | {AGENT}",
      "Thinking of selling in Holland Park West 4121? What the suburb is like to live in, what moves price street to street, and a free appraisal.",
      SUBURB_BODY + UPDATE_BLOCK.replace("{UPDATEFORM}", form_block(
        subject="Market update signup",
        required='[["name","your first name"],["email","your email"]]',
        groups='[["who","Who they are"]]',
        fields_html=UPDATE_FIELDS,
        send_label="Send me the update",
        thanks_html=f'''<h3>You are on the list</h3>
          <p>To find out what your own home is
          worth before then, call <strong>{PHONE}</strong> or
          <a href="appraisal.html">request an appraisal</a>.</p>''',
        note="One email a month. Your address is used for this and nothing else, and every email has an unsubscribe link."),
      ), FORM_JS, hero=True),
  "offer.html": shell("offer.html", f"Expression of Interest | {BRAND}",
      "Put your offer forward online for a property listed with Roxanne Alterio.",
      OFFER_BODY.replace("{OFFERFORM}", form_block(
        subject="Expression of interest",
        required='[["property","the property"],["name","the buyer names"],["mobile","your mobile"],["email","your email"],["price","your offer"]]',
        groups='[["buyertype","Buyer type"],["conditions","Conditions"]]',
        fields_html=OFFER_FIELDS,
        send_label="Submit my expression of interest",
        thanks_html=f'''<h3>Received, thank you</h3>
          <p>Roxanne will call to confirm she has it and talk through the next step, usually within
          a couple of hours.</p>
          <p>If you need her sooner, call <strong>{PHONE}</strong>.</p>''',
        note="This is an expression of interest, not a contract. Nothing is binding on you or the seller until a contract is signed by both parties. Licence details are used only to prepare a contract and to verify who is making the offer, and are not passed to the seller. They are kept only as long as the law requires an agency to keep them.")),
      FORM_JS + OFFER_JS),
  "auction.html": shell("auction.html", f"Auction Bidder Registration | {BRAND}",
      "Register to bid at a Holland Park West auction. Identification, bidding capacity and company or trust details, submitted before auction day.",
      AUCTION_BODY.replace("{AUCTIONFORM}", form_block(
        subject="Auction bidder registration",
        required='[["property","the property"],["name","your full name"],["mobile","your mobile"],["email","your email"],["address","your residential address"]]',
        groups='[["capacity","Bidding capacity"],["confirm","Confirmed"]]',
        fields_html=AUCTION_FIELDS,
        send_label="Register to bid",
        thanks_html=f'''<h3>Registration received</h3>
          <p>Roxanne will check it over and call to confirm, and the bidder number will be ready
          on arrival. If anything is missing you will hear well before auction day.</p>
          <p>Any questions in the meantime, call <strong>{PHONE}</strong>.</p>''',
        note="Registering is not a commitment to bid. Identification is used only to verify who is bidding, as the auctioneer is required to do, and is not passed to the seller.")),
      FORM_JS + AUCTION_JS),
  "holland-park-west-report.html": shell("holland-park-west-report.html",
      f"Holland Park West Market Report, {REPORT_MONTH} | {BRAND}",
      f"What houses are selling for in Holland Park West 4121, how long they take and what has changed in the past twelve months. Median {HPW['median']}, up {HPW['growth']}.",
      REPORT_BODY),

  "reviews.html": shell("reviews.html", f"Reviews | Roxanne Alterio, {BRAND}",
      f"Every verified review of Roxanne Alterio from realestate.com.au, word for word. Sellers and buyers across Brisbane's inner south.",
      REVIEWS_BODY) if REVIEWS else None,

  "journal.html": shell("journal.html", f"Queensland Property Rule Changes Explained | {BRAND}",
      "Seller disclosure, smoke alarm deadlines and transfer duty changes, explained in plain words by a Holland Park West agent.",
      JOURNAL_BODY.replace("{POSTS}", cards_all)),

  # GitHub Pages serves this for any address that does not exist. Without it a
  # mistyped link shows GitHub's own error page with none of the branding on it.
  "privacy.html": shell("privacy.html", f"Privacy | {BRAND}",
      "What happens to the details you send through this site, who sees them and how to have them removed.",
      PRIVACY_BODY),

  "404.html": shell("404.html", f"Page not found | {BRAND}",
      "That page is not here. Browse the Holland Park West listings or request an appraisal.",
      f"""
<section class="tight">
  <div class="wrap mid centre" style="padding-top:40px">
    <p class="kick">404</p>
    <h1>This page has <em>moved on</em>.</h1>
    <p class="lede">The address you followed does not exist, or the listing it pointed to has
    since sold.</p>
    <div class="btnrow" style="justify-content:center;margin-top:30px">
      <a class="btn solid" href="listings.html">See the listings</a>
      <a class="btn" href="appraisal.html">Request an appraisal</a>
    </div>
    <p style="margin-top:34px;color:var(--muted)">Or call Roxanne on
      <a href="tel:{TEL}" style="color:var(--ink)">{PHONE}</a>.</p>
  </div>
</section>
""", noindex=True),
}
pages = {k: v for k, v in pages.items() if v is not None}

for p in POSTS:
    pages[p["slug"]] = post_page(p)

for name, content in pages.items():
    open(os.path.join(SITE, name), "w").write(content)


# ---- tidy links to text to buyers --------------------------------------------
# thealterioteam.com.au/offer/12-kneale-street  instead of  offer.html?p=12-kneale-street
# Shorter to read, and with no "?" in it every phone turns it into a tappable link,
# which is not true of a query string. Each one is a stub that forwards to the real
# form with the address already filled in.

def short_link(folder, slug, target, label):
    d = os.path.join(SITE, folder, slug)
    os.makedirs(d, exist_ok=True)
    url = "../../%s?p=%s" % (target, slug)
    open(os.path.join(d, "index.html"), "w").write(f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(label)} | {BRAND}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="https://{DOMAIN}/{target}?p={slug}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace("{url}");</script>
<style>body{{margin:0;display:grid;place-items:center;min-height:100vh;
background:#fff;color:#0b0b0b;font:400 16px/1.6 system-ui,sans-serif;text-align:center;padding:24px}}
a{{color:inherit}}</style>
</head>
<body><p>Opening the form&hellip;<br><a href="{url}">Continue</a></p></body>
</html>
""")
    return "%s/%s/%s" % (DOMAIN, folder, slug)


# A tidy link for the market report: thealterioteam.com.au/report
os.makedirs(os.path.join(SITE, "report"), exist_ok=True)
open(os.path.join(SITE, "report", "index.html"), "w").write(f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Holland Park West Market Report | {BRAND}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="https://{DOMAIN}/holland-park-west-report.html">
<meta http-equiv="refresh" content="0; url=../holland-park-west-report.html">
<script>location.replace("../holland-park-west-report.html");</script>
<style>body{{margin:0;display:grid;place-items:center;min-height:100vh;background:#fff;
color:#0b0b0b;font:400 16px/1.6 system-ui,sans-serif;text-align:center;padding:24px}}
a{{color:inherit}}</style>
</head>
<body><p>Opening the report&hellip;<br><a href="../holland-park-west-report.html">Continue</a></p></body>
</html>
""")

SHORT_LINKS = [("Holland Park West market report", DOMAIN + "/report")]
for p in CURRENT:
    s = slugify(p["addr"])
    SHORT_LINKS.append(("Make an offer on " + p["addr"],
                        short_link("offer", s, "offer.html", "Make an offer on " + p["addr"])))
    SHORT_LINKS.append(("Register to bid on " + p["addr"],
                        short_link("register", s, "auction.html", "Register to bid on " + p["addr"])))

today = datetime.date.today().isoformat()
priority = {"index.html": "1.0", "appraisal.html": "0.9", "holland-park-west.html": "0.9",
            "holland-park-west-report.html": "0.9",
            "listings.html": "0.8", "offer.html": "0.7", "auction.html": "0.7",
            "journal.html": "0.7",
            "referrals.html": "0.6"}
# brochures are dropped into the folder rather than generated, but they are real
# pages a buyer can land on, so they belong in the sitemap too
extra = sorted(f for f in os.listdir(SITE)
               if f.endswith(".html") and f not in pages)
for n in extra:
    priority[n] = "0.8"

# never offered to Google
NO_SITEMAP = {"404.html"}

urls = "".join(
    f"<url><loc>https://{DOMAIN}/{n}</loc><lastmod>{today}</lastmod>"
    f"<changefreq>{'weekly' if n in ('index.html','listings.html') else 'monthly'}</changefreq>"
    f"<priority>{priority.get(n, '0.5')}</priority></url>"
    for n in sorted(set(list(pages) + extra) - NO_SITEMAP))
open(os.path.join(SITE, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n')
open(os.path.join(SITE, "robots.txt"), "w").write(
    "User-agent: *\nAllow: /\n\nSitemap: https://%s/sitemap.xml\n" % DOMAIN)
open(os.path.join(SITE, "site.webmanifest"), "w").write(json.dumps({
    "name": "%s, %s" % (AGENT, BRAND),
    "short_name": "Alterio",
    "description": "Residential sales in Holland Park West and Holland Park.",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#faf9f5",
    "theme_color": "#141413",
    "icons": [
        {"src": "images/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "images/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "images/icon-512.png", "sizes": "512x512", "type": "image/png",
         "purpose": "maskable"},
    ],
}, indent=2) + "\n")
print("wrote sitemap.xml, robots.txt and site.webmanifest")
print("built %d pages: %s" % (len(pages), ", ".join(sorted(pages))))
print("short links:")
for label, url in SHORT_LINKS:
    print("  %-40s %s" % (label, url))
