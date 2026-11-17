# AI Skill Shelf: jury score (round 3)
Estimate, not affiliated with Awwwards. Independent critic (new, blind, saw no earlier card), from 4 pages (home, library, skill detail `#skill=awwwards`, 404) on 13 Nov 2026, after commit 1ff3c42.

**The idea, as the critic read it:** a catalogue of AI skills, each one a bold ink-outlined comic card, dealt into a turning 3D fan on the home screen and shown as a colour grid in the library, each opening an install sheet. "The covers read as collectible trading cards, not books."
**Critic overall: 6.35, about 6.4** (0.4×6.5 + 0.3×6 + 0.2×6.5 + 0.1×6.5)
**Jury estimate: about 7.5** (critic + 1.1, measured on two recent Sites of the Day only; not measured on non-winners)
**Band, from the estimate:** Site of the Day range (7.2 and up), low confidence

## Change across the three critics

| | Round 1 (6.6) | Round 2 (6.7) | Round 3 (now) |
|---|---|---|---|
| Design | 7 | 7 | 6.5 |
| Usability | 6 | 6 | 6 |
| Creativity | 7 | 7 | 6.5 |
| Content | 6 | 7 | 6.5 |
| **Overall** | **6.6** | **6.7** | **6.35** |
| Accessibility | n/a | 5 | **7** |
| Desktop CLS (library) | 0.231 | 0.229 | **0** |
| Serious axe (site pages) | n/a | 2 rules (×39, ×6) | **0** |

The visuals did not change between rounds 2 and 3, yet Design, Creativity and Content each lost 0.5. That is the spread between critics, not a regression. The measured fixes landed (Accessibility 5 → 7, CLS 0, axe 0).

## Two findings the critic misread (tool artifacts, checked)
- **"Page scrolls behind the sheet" (skill-detail m-02 to m-06), its fix 1.** The tool moves the window with `scrollTo`, which `overflow:hidden` does not block. With a real wheel at 390 px the sheet scrolls (scrollTop 0 → 375) and the page stays at 0. Round 2 shots show the same frames.
- **"No link could be clicked" on home, its fix 4.** A real click on "Browse skills" opens the library on the live site, also after wheeling the fan. `#front-link` is hidden until Tab on purpose.
Both counted against Usability (6). The critic's numbers stay as scored.

| Criterion | Score | Evidence |
|---|---|---|
| Design (40%) | 6.5 | one memorable fan composition, ten-colour ink system everywhere. Against: pastel blur + glossy candy shapes fight the flat ink cards; purple capsule under the front card (d-04, d-05, k-01); fan slides under the dock (d-02 to d-07); same colour stacked vertically in the library (black over black, d-01); label tops not aligned; "Smooth Animation (60…"; all-caps "PROMPT MOTION DESIGN IDEAS"; card hover haze greys the badge (h-04, h-05); plain sheet; no footer; GitHub 404 |
| Usability (30%) | 6 | home LCP 752 ms, CLS 0, skip link, visible focus, reduced motion static. Against: library phone LCP 3476 ms; tiny phone front card; phone chrome ~32% of the screen (m-01); plus the two artifacts above |
| Creativity (20%) | 6.5 | cards dealt into a hand with scatter-and-fall intro and fan loop; the fan is a Cover Flow pattern; idea stops at home (static grid, generic sheet) |
| Content (10%) | 6.5 | specific sheet copy (Best for, real prompt, per-OS install). Home 20 words, no line saying what it is for; cut-off home descriptions; skip link "Skip to the shelf link" |

| Developer | Score | Evidence |
|---|---|---|
| Semantics/SEO | 6 | one h1, 0 FAIL; no robots.txt/sitemap; GitHub 404. (It says the deep link keeps "All skills" as title: the tool reads the title at load; the sheet sets it after.) |
| Animations/Transitions | 6 | intro and fan loop alive; library → home hard cut and intro replays (d-90); weak hovers: "All" (h-01), active tab 1 px (h-03), × rotation invisible (h-01) |
| Accessibility | 7 | 0 serious axe on all site pages, skip link first, focus visible, reduced motion still; `reduced.hiddenText: 1` on home |
| WPO | 6 | home 752 ms LCP, 21 KB JS; library phone LCP 3476 ms; 635 KB TTF fonts, no woff2 |
| Responsive | 7 | no overflow, no small targets, app layout on phone; phone home ~60% empty; dice not aligned with Easy |
| Markup/Meta-data | 7 | 0 FAIL, OG/favicon/viewport pass |

## Fixes, most score first (critic's list, artifacts removed)
1. [Animations/Usability] Library → home is a hard cut and the intro replays (d-90-a/b/c). Cross-document view transition, and skip the intro when coming from shelf.html.
2. [WPO/Usability] Library phone LCP 3476 ms and 635 KB TTF fonts. Self-host 2 weights as subset woff2, preload the display face, drop the serif and mono from the library.
3. [Responsive/Usability] Phone home: front card ~160 px, ~60% of the screen empty (m-02 to m-06). Front card ~70vw, lifted into the top band, name and one-line description as real text.
4. [Design] Two visual languages on home: give the candy shapes ink outlines and flat fills, or use a flat paper ground with halftone dots; move the capsule under the front card.
5. [Design] Fan slides under the dock: fade or clip at the dock edge, or shift the fan centre.
6. [Design/Animations] Hovers: card sheen down to ~15% so the badge stays white, stronger lift; tile fill on "All"; × scales and fills; fill on inactive install tabs (already added; the active tab only moves 1 px).
7. [Design] Colour rule: check vertical neighbours too (black above black in d-01).
8. [Design] Library cards: fixed two-line label height so tops align; shorten "Smooth Animation (60…"; title-case "Prompt motion design ideas"; align dice with Easy on phone; collapse the title row on scroll.
9. [SEO] robots.txt, sitemap.xml, branded 404.html, meta description per skill.
10. [A11y/Content] Show the one element hidden under reduced motion; skip link "Skip to the skills"; one short line on home saying what it is for.

## Measured
- Mobile LCP: home 752 ms, library 3476 ms (round 2: 1724 ms; nothing load-related changed, so likely network variance on throttled slow 4G [Likely]). CLS 0 desktop and phone on every page.
- Serious axe: 0 on home, library, detail; 4 on GitHub's 404.
- `noHoverChange` 0, `colorOnly` 0, `invisibleFocus` 0 on site pages.
- Audit: 0 FAIL, 20 WARN (fonts, thin home content, no robots/sitemap).

Not scored: anything stills can't show (how motion feels).
