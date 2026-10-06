# Alterio website

Static site for **thealterioteam.com.au**, branded The Alterio Team. Aurora stays on the brochures and EOI forms produced in HQ.. No build tools needed to publish. Upload the folder, done.

## What's in here

| File | What it is |
|---|---|
| `index.html` | Home page |
| `listings.html` | Listings, with a Current / Sold toggle |
| `holland-park-west.html` | Suburb guide, the page that wins local searches |
| `appraisal.html` | Sales and rental appraisal request form |
| `referrals.html` | Broker, solicitor and inspector referrals form |
| `reviews.html` | Every verified review, word for word. Built automatically from the `REVIEWS` list |
| `offer.html` | Expression of interest form. Buyers put their offer forward here |
| `auction.html` | Auction bidder registration. Identification, bidding capacity, company and trust details |
| `12-kneale-street.html` | The e-brochure for that listing, one self-contained file |
| `journal.html` + `journal-*.html` | Blog index and three articles |
| `style.css` | All styling |
| `images/` | Photos. **This folder must be uploaded too.** |
| `404.html` | Shown when someone follows a broken or mistyped link |
| `favicon.ico`, `images/icon-*.png` | The tab icon and the icon used when the site is saved to a phone home screen |
| `site.webmanifest` | Name, colours and icons used when the site is saved to a home screen |
| `CNAME` | The custom domain. GitHub Pages reads this. |
| `og.py` | Regenerates the 1200x630 image shown when the site is shared |
| `sizes.py` | Makes the smaller copies of each photo that phones download |
| `tiles/` | Ten 1080x1080 social tiles, ready to post |
| `listings.json` | Optional. Written by Aurora HQ, overrides the listings on the site |
| `sitemap.xml`, `robots.txt` | SEO files |
| `build.py`, `tiles.py` | The generators. Edit these, not the HTML. |

## Deploying to GitHub Pages

1. Upload every file and both folders to the repo, keeping the structure exactly as it is.
2. Settings, Pages, Source: Deploy from a branch, branch `main`, folder `/ (root)`.
3. `CNAME` is already in the folder with the domain in it. Leave it there. So is `.nojekyll`,
   an empty file that tells GitHub to serve the pages exactly as they are rather than running
   them through Jekyll. Finder hides files starting with a dot: press **Shift + Command + .**
   to show them before you select everything to upload.
4. At your domain registrar, point the apex A records to GitHub's four IPs
   (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153)
   and add a CNAME for `www` pointing to `roxannealterio.github.io`.
5. Back in Settings, Pages, enter the custom domain and tick Enforce HTTPS once it's available.

**File paths are case sensitive on GitHub.** `Images/Hero.JPG` will not load if the page asks for
`images/hero.jpg`. Keep everything lowercase.

## Changing the site

Edit `build.py` and run `python3 build.py`. It rewrites every HTML page plus the sitemap.
Editing the `.html` files directly works too, but the next build overwrites them.

Edit `tiles.py` and run `python3 tiles.py` to re-render the social tiles.

### Updating listings from Aurora HQ

Easiest route, no code. Open HQ, go to **Website**, tick the properties that should appear, set
each one to Current or Sold, add the price or the status flag, then press **Download listings.json**.
Upload that file to the repository next to index.html and commit.

The listings page and the Recent sales band on the home page both follow `listings.json` when it
exists, photos included. Delete the file and the site falls back to the lists in `build.py` below.

### Short links for texting buyers

`build.py` writes a tidy forwarding link for every current listing:

| Link | Opens |
|---|---|
| `thealterioteam.com.au/offer/12-kneale-street` | the offer form, address filled in |
| `thealterioteam.com.au/register/12-kneale-street` | the auction registration, address filled in |

Use these in texts and emails rather than `offer.html?p=...`. They read better, and because
there is no `?` in them every phone turns them into a tappable link, which is not reliably true
of a query string.

They are regenerated from the `CURRENT` list each build, so adding a listing creates its links
automatically. Upload the `offer/` and `register/` folders along with everything else.

### Auctions

Set a listing's **How it closes** to Auction in HQ and three things change. The listing card shows
**Register to bid** instead of Make an offer, the brochure leads with Register to bid, and the
Website screen gives you a link to copy and text to buyers. There is also an Announce template that
sends the registration link to your whole database.

The registration form covers what a Queensland auctioneer has to establish before issuing a bidder
number: who is bidding, their address, identification with a photo of it, and the capacity they are
bidding in. That last part is why the form asks about companies, trusts, co-buyers, powers of
attorney and buyer's agents, and takes an upload of the written authority where someone is bidding
for another person. Bidding on behalf of someone has to be disclosed before bidding starts, so
collecting it beforehand keeps auction day clean.

General information, not legal advice. Check your own obligations against the Property Occupations
Regulation 2014 or with the REIQ.

### Driver licence uploads

The expression of interest form can take a photo of the front and back of a licence. Formspree only
accepts file uploads on its **Personal, Professional and Business** plans. On the free plan the
rest of the form still arrives, but the two photos are dropped. Limits are 25MB per file and ten
files per submission; the form rejects anything over 10MB before sending, to keep it quick on a
phone.

Both fields are optional on purpose. Licence images are sensitive identity information, so asking
every enquirer for them at the expression of interest stage is a risk you do not need to carry.
The form says they can be left until an offer is accepted, and states that they are used only to
prepare a contract, are not passed to the seller and are deleted if the offer does not proceed.
Make sure that is actually true of how you store them.

### Photo sizes

Each photo sits in `images/` at full size, with a 640 and a 1280 pixel copy beside it.
The page offers all three and the browser takes the one that suits the screen, so a phone
downloads about 90KB where it used to download a megabyte. Nothing is lost on a large screen,
which still gets the original.

**After adding or replacing a photo, run `python3 sizes.py` and then `python3 build.py`.**
Skip `sizes.py` and the site still works, it just sends the full file to everyone.

The build also writes a 20 pixel wide blurred copy of each photo into the page itself, under a kilobyte each. It shows instantly, so you never see an empty grey panel where a photo is about to appear.

### Photo quality

Every image is saved at the largest size the file you sent allows, at 92 to 94 quality with no
chroma subsampling. Several of the sold photos came through at 1320px wide, which is sharp on a
normal screen and slightly soft on a high resolution laptop. If you can pull the originals from the
photographer's portal, send them and I will replace those files. The hero and the Kneale Street card
are the two worth having at full size, since they are shown largest.

### Why a form might say it did not send

The forms post to Formspree over AJAX. If something goes wrong the page now shows the reason
Formspree gave, plus a link that opens the same answers in an email instead, so an enquiry is never
lost. Common causes: the form has not been confirmed from that email address yet, the monthly free
quota is used up, the submission included a file on a free plan, or the page was opened as a local
file rather than from the live domain. Send one real test from the published site once the domain
is connected.

### Brochures

Every brochure carries a **Back to the website** link beside the wordmark at the top, and
**See all listings** and **Request an appraisal** at the bottom. These are relative links,
so they work in the repository, in a preview and on the live domain. A brochure is often the
first page a buyer lands on, so it should never be a dead end.

**There is one expression of interest form, and it is `offer.html`.** The brochure used to
carry a second copy inside it, which meant two sets of fields to keep in step and a buyer
who could not tell which one counted. The two buttons under the headline in a brochure now
open `offer.html` with the address already filled in, so every offer arrives in the same
Formspree inbox in the same shape.

HQ builds a brochure as one self-contained HTML file with the photos inside it. On the Website screen press **Download this brochure**, upload the file to the
repository beside index.html, then type that file name into the brochure box. The listing card then
shows a **Brochure** link.

Every current listing also shows **Make an offer**, which opens `offer.html` with the address
already filled in. That form goes to the same Formspree inbox as the others.

### Adding or changing a listing in the code

Open `build.py` and find the two lists near the top of the listings section.

Paste your realestate.com.au links into `REA_12_KNEALE`, `REA_162A` and `REA_53_KNEALE` at the top
of that section. A card with a real link opens the ad in a new tab.

`CURRENT` is what is for sale. Each entry takes an address, a suburb line, a photo path, a link to
the brochure, a list of specs and a short note such as a deadline. Leave `specs` empty and the card
just shows the note.

`SOLD` is the sale results. Each entry takes an address, suburb, price and `sold`, the month it
sold (`"May 2026"`). Keep the list newest first. The home page shows address, month and price;
the listings page shows the photo, suburb, price and month. With no photo the card
shows a panel with the street number in it, which is deliberate so the list still looks finished.
Add `img="images/your-file.jpg"` to any entry and the photograph replaces the panel.

The sold list also feeds the Recent sales band on the home page, so you only enter a result once.

### Swapping a photo

Drop the new file into `images/` using the same filename, or change the filename in `build.py`.

- `hero.jpg` is the home page hero. Landscape, 2400px wide or more is ideal.
- `suburb.jpg` is the Holland Park West banner. Wide crop.
- `roxanne-square.jpg` is the portrait in the About block and on the appraisal page.
- `og-default.jpg` is the 1200x630 image that shows when a link is shared. Keep those dimensions.

### Adding seller reviews

Open `build.py` and find the `REVIEWS` list. Each entry takes the quote word for word, the
reviewer's name as they left it, the street or suburb, and the month:

```python
REVIEWS = [
  dict(quote="Sold in eleven days and we were never left guessing.",
       who="Sarah M", where="Kneale Street, Holland Park West", when="May 2026"),
]
```

Add `home=True` to the two or three that should show on the home page. Every review in the list
appears on `reviews.html`, which is generated automatically and linked from the home page and the
footer. Leave the list empty and both the home page section and the whole reviews page disappear.

Quote them exactly as written. Do not tidy the grammar, do not merge two reviews into one, and
do not add a review that was not left. Check your agency and the platform you took them from are
happy for them to be republished.

### Writing a new article

Add a new `dict(...)` to the `POSTS` list in `build.py` with a `slug`, `date`, `sort` (YYYY-MM-DD),
`title`, `blurb`, `body` and `sources`. Run the build. It appears on the journal page, the home page,
the sitemap, and gets its own Article schema automatically.

## Positioning

The site is deliberately pointed at **Holland Park West and Holland Park 4121** and nothing wider.
Every page title, meta description and the structured data Google reads name those two suburbs.
Mount Gravatt East, Coorparoo, Annerley and Tarragindi appear once, low on the home page and in the footer,
so nobody thinks a listing there would be turned away.

Widen it when the sold list can back it up. The place to change it is the hero in `HOME_BODY`,
the titles and descriptions in the `pages` dictionary, and `areaServed` in `jsonld()`.

### The monthly update is the growth engine

`holland-park-west.html#update` collects people who want every Holland Park West sale once a month.
That list is the thing that wins a suburb, because it puts you in front of owners years before they
sell. Signups arrive in Formspree. Export them, then import them into HQ under **Database** so you
can text or email them when something lists or sells.

It only works if you actually send it. Once a month, every sale, what it made, how long it took,
two sentences of what it means. If you cannot commit to that, take the section down rather than
collect addresses you never use.

## Design notes

- Display type is **Cormorant Garamond**, with the emphasis word in each headline set in italic
  using `<em>`. Labels, buttons and navigation are **Montserrat**.
- The wordmark is the word ALTERIO set in Cormorant with wide letterspacing. It deliberately does
  not reuse the Aurora triangle.
- The site is locked to light. It stays white even if the phone or laptop is in dark mode.
- Palette is black, white and a warm stone band (`--stone`). No blue anywhere.
- Section rhythm alternates white, stone band, white, black call to action.
- The home page and the suburb page open on a dark hero, so their header starts transparent and
  fades to black once you scroll past 70px. That is the `hero=True` flag on `shell()` in `build.py`,
  which adds `class="hashero"` to the body. Only use it on a page whose top is dark, otherwise the
  white navigation sits on white.
- The tokens live at the top of `style.css` if you ever want to shift the neutrals.

## SEO

- Every page has a unique title, description, canonical link, Open Graph and Twitter card.
- `RealEstateAgent` structured data on every page, `BreadcrumbList` on inner pages,
  `Article` on each journal post.
- Submit `https://thealterioteam.com.au/sitemap.xml` in Google Search Console once the domain is live.
- Claim your Google Business Profile with the same name, phone and suburb. That plus the
  Holland Park West page is what moves you up for local searches.

## Still to do

- The three sale prices and dates were checked against each address's Domain property profile,
  and 34 Galsworthy also against propertyvalue.com.au. **34 Galsworthy is recorded at
  $1,725,000 on 24 April 2026, not $1,750,000.** The site shows the recorded figure. If you
  know the contract price was different, say so and it will be changed back.
- Paste the realestate.com.au links so the cards open the ads.
- Add a photo for 53 Kneale Street.
- Add photos to the sold entries when you have them.
