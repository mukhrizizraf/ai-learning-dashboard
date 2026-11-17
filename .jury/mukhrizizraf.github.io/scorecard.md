# AI Skill Shelf: jury score (round 4)
Estimate, not affiliated with Awwwards. Independent critic (new, blind, saw no earlier card), from 4 pages (home, library, skill detail `#skill=awwwards`, 404) on 13 Nov 2026, after commits 9a2d420 (looks C B A) and 9c1aab3 (skill artwork).

**The idea, as the critic read it:** a bright, app-like library of AI-assistant skills where every skill is a cartoon hardback book: flip a 3D fan of books on the home screen, pick from shelves in the library, open a sheet with a prompt to copy and install steps.
**Critic overall: 6.85, about 6.9** (0.4×7 + 0.3×6.5 + 0.2×7 + 0.1×7)
**Jury estimate: about 8.0** (critic + 1.1, measured on two recent Sites of the Day only; not measured on non-winners)
**Band, from the estimate:** Site of the Day range (7.2 and up), low confidence

| Criterion | Score | Round 3 | Evidence |
|---|---|---|---|
| Design (40%) | 7 | 6.5 | One system: ink outlines, ten cover colours, spine band, clay icons in white badges, shelf boards; grid and label tops line up (library d-01, d-04, d-06); memorable fan (home d-02, d-07). Against: condensed serif fallback on 3D cover descriptions, soft on phones (home m-02, m-04); cut names "Awwwards Website…", "Smooth Animation (6…", "Updates & Announceme…" (library d-01, d-02, d-04); plain white detail sheet, 60 px thumbnail (skill-detail d-01); pastel blur blobs on first paint (home d-00, library d-90-a/b); GitHub 404 |
| Usability (30%) | 6.5 | 6 | Rail, tab bar, category strip, search/Easy/dice always visible (library d-01, m-01); smallTargets 0; 2×2 install choices (skill-detail m-01); reduced motion snaps. Against: home mobile LCP 5756 ms on `p#front-what`; falling books cover the name and push into Browse skills (home m-01); home FPS 37–38; focus leaves the page after "Share skill" (skill-detail keyboard.stops) |
| Creativity (20%) | 7 | 6.5 | Falling books settle into a looping fan, library is shelves of hardbacks: one idea across home and library (library d-90-c, home d-02 to d-07). Against: sheet drops the idea; clay icons look like a common icon pack |
| Content (10%) | 7 | 6.5 | Concrete cover lines, real sample prompt, real install commands, source credit (skill-detail d-01, m-01). Against: home 20 words, nothing says what a skill is |

| Developer | Score | Round 3 | Evidence |
|---|---|---|---|
| Semantics/SEO | 5.5 | 6 | One h1 per page. No robots.txt/sitemap, GitHub 404, thin home. (Its "deep link keeps title All skills" is a tool artifact: the report reads the title at load; `shelf.js:232` sets it when the sheet opens.) |
| Animations/Transitions | 6.5 | 6 | noHoverChange 0, colorOnly 0; book tilt, Browse lift, dock icons, close rotate, Copy fill. Against: logo hover changes nothing (home h-01); Home/Guide grey pill only (library h-02, h-07); library → home hard cut; pageerror "Transition was aborted because of invalid state" |
| Accessibility | 6.5 | 7 | axe serious 0, skip link first, visible focus, reduced motion still. Against: audit FAIL button with no accessible name (home, new); reduced.hiddenText 1; no focus trap in the sheet |
| WPO | 5.5 | 6 | CLS 0, JS 175 KB gz, heaviest page ~839 KB. Against: throttled mobile LCP 5756 ms home (round 3: 752 ms), 3208 ms library, 2528 ms detail; settledMs null. (Its "8 TTF fonts, 635 KB" is likely a tool artifact: Google Fonts sends woff2 to a real Chrome; the audit fetches without a browser user agent.) |
| Responsive | 7 | 7 | overflowX false, smallTargets 0, composed 2-column phone shelf. Against: intro collision (home m-01); dice button ~40 px short of Easy's right edge (library m-01); empty band under the phone top bar (home m-02) |
| Markup/Meta-data | 7 | 7 | OG, favicon, viewport pass; the one FAIL is the unnamed button |

## Fixes, most score first
1. [Usability, WPO] home m-01, mobile LCP 5756 ms on `p#front-what`: the phone name/description block paints only after the WebGL intro, and falling books cover it. Paint `#front-info` text at once in HTML, and keep the books above it while they land. (Round 3 home LCP was 752 ms: this is a regression from the C B A phone home.)
2. [Design, Creativity, SEO] skill-detail d-01, m-01: carry the book into the sheet: header band in the cover colour with the spine band, cover art at 160 px or more instead of the 60 px thumbnail.
3. [Animations] library d-90-a/b: drop the pastel blob first paint so it matches the settled #f5f5f7; catch the aborted view transition on plain `shelf.html` loads (`shelf.js:149`, only `?cat=` loads catch it today); add shared elements (logo, Browse skills) to the cross-document transition.
4. [Design] home d-02, m-02, m-04: 3D cover descriptions draw in a serif fallback: draw canvas text after `document.fonts.ready` with the site sans at 2× texture resolution, or leave the description off the cover on phones (the HTML already shows it).
5. [Design, Content] library d-01, d-02, d-04: allow 3 lines in `.row-name` on desktop or shorten the names; "PROMPT MOTION DESIGN IDEAS" in title case (m-03).
6. [Accessibility, Markup] audit FAIL: `#front-name` (`index.html:57`) is an empty button in the HTML; give it an `aria-label` or default text. Check `reduced.hiddenText: 1`.
7. [SEO] branded 404.html, robots.txt, sitemap.xml.
8. [Animations] home h-01 logo and library h-02/h-07 rail items: same lift and ink shadow as Browse skills.
9. [Accessibility] skill-detail keyboard.stops: trap focus in the sheet, return it to the card on close.
10. [Responsive] library m-01 dice to the right gutter; home m-02 trim the empty band under the bar.
11. [Content] one short line on the home saying what a skill is.

## Measured
- Mobile LCP (4× CPU, slow 4G): home 5756 ms, library 3208 ms, detail 2528 ms, 404 664 ms. CLS 0 everywhere.
- FPS (software GPU, a floor): home 37 desktop / 38 phone, library 50 / 57.
- axe serious: 0 on site pages (4 on GitHub's 404). Overflow none. smallTargets 0 on site pages. noHoverChange 0, colorOnly 0 on site pages.
- Idle motion: home yes (fan auto-advances), library no.
- Console: 1 pageerror on library (aborted view transition).
- Audit: 1 FAIL (unnamed button, home), 20 WARN.

Not scored: anything stills can't show (how motion feels, sound).
Critic spread between runs is about ±0.5 per category, so the +0.5 overall is at the edge of noise; this time the visuals changed, so part of it is likely real.
