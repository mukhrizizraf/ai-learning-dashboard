# AI Skill Shelf: jury score
Estimate, not affiliated with Awwwards. Independent critic (new, blind, never saw the 13 Nov card), from 4 pages (home, library, skill detail `#skill=awwwards`, 404) on 13 Nov 2026.

**The idea, as the critic read it:** a catalog of AI-assistant skills, each one a bright comic-style collectible card, fanned in 3D on the home screen and in a filterable grid in the library, each opening an install sheet. "Nothing on screen reads as a shelf or a book."
**Critic overall: 6.7** (0.4×7 + 0.3×6 + 0.2×7 + 0.1×7, on the critic's strict scale)
**Jury estimate: about 7.8** (critic + 1.1, measured on two recent Sites of the Day only; the gap on non-winners is not measured)
**Band, from the estimate:** Site of the Day range (7.2 and up), with low confidence

## Change since 13 Nov (critic 6.6)

| | 13 Nov | Now | Change |
|---|---|---|---|
| Design | 7 | 7 | 0 |
| Usability | 6 | 6 | 0 |
| Creativity | 7 | 7 | 0 |
| Content | 6 | 7 | +1 |
| **Overall** | **6.6** | **6.7** | **+0.1** |
| Audit | 0 FAIL, 20 WARN | 0 FAIL, 20 WARN | same |

| Criterion | Score | Evidence |
|---|---|---|
| Design (40%) | 7 | home d-01/d-02: strong fan, ten clearly different colours, one ink-outline system. Against: pastel candy blobs fight the hard comic ink; purple pill touches the front card and "Browse skills" (d-04, d-07, k-01); 12 px condensed italic serif on home cards; plain white detail sheet; no library footer; GitHub's default 404 |
| Usability (30%) | 6 | mobile LCP 956/1724/2328 ms, mobile CLS 0, clear rail and tab bar. Against: desktop CLS 0.229 on library and detail; home `--nav` click test failed (front link covered); detail × scrolls away (skill-detail d-04); install tabs wrap, "Claude app" alone (m-01); content shows through phone chrome (library m-03, m-06); tiny front card on phone home (m-03) |
| Creativity (20%) | 7 | collectible-card idea with fall/crawl/fan motion fits; carried only part way (flat library, generic sheet); "shelf" never shows |
| Content (10%) | 7 | detail sheet is real and specific (purpose, Best for, example prompt, real commands, source). Home has 20 words and no line saying what it is for; "PROMPT MOTION DESIGN IDEAS" all caps, "Smooth Animation (60…" cut off (library d-03) |

| Developer | Score | Evidence |
|---|---|---|
| Semantics/SEO | 6 | one h1, unique titles; no robots.txt/sitemap; `#skill=` keeps title "All skills"; no branded 404 |
| Animations/Transitions | 6 | 3D intro and idle loop, card tilt/sheen, dice spin, CTA lift. Hard cut to empty home on back (d-90-a), intro replays; pageerror "Transition was aborted because of invalid state"; `noHoverChange` "Ask Claude Code"; "Copy" colour-only |
| Accessibility | 5 | skip link first, visible focus rings, reduced motion stops. `label-content-name-mismatch` ×39 (serious); detail `color-contrast` ×6 (#8a8692 = 3.55:1); `invisibleFocus` unlabelled input; home `reduced.hiddenText: 1` |
| WPO | 7 | JS 21 KB gz, ~683 KB page, no loader, LCP under 2.5 s on phone. 635 KB TTF fonts (not woff2); desktop CLS 0.229 |
| Responsive | 7 | no overflow, no small targets on own pages, app-like phone library. Tiny phone front card, wrapping tabs, see-through chrome, dice not aligned with "Easy" (library m-01) |
| Markup/Meta-data | 7 | 0 FAIL, OG/favicon/viewport fine; 39 name mismatches |

## Fixes, most score first
1. [Usability/WPO] Desktop CLS 0.229 on library and detail (`desktop.vitals.cls`; phone is 0). Rows move ~12 px between d-00 and d-01. The 13 Nov fix (0.231 → 0.003) does not hold at 1440 px. Find the shift (entrance animation or font swap) and remove it.
2. [Usability] Home `--nav` test could not click through to shelf.html; `hover.covered` lists "Open Canvas Design". Something sits over the anchors. Check with a real click, then give overlays `pointer-events:none` and the links a higher z-index.
3. [Animations] Home ← library is a hard cut to an empty screen and the intro replays (d-90-a). Add a cross-document view transition and skip the intro when coming from the library. Fix the "Transition was aborted" error.
4. [A11y/Usability] Detail sheet: darken #8a8692 text to ≥4.5:1; give "Copy" and inactive install tabs a real hover; make the header with × sticky; 2×2 grid for install tabs at 390 px.
5. [A11y] `label-content-name-mismatch` ×39: the card's aria-label must contain the visible text exactly. The name and meta spans have no space between them, so the visible text reads "BuilderNew · Medium". Add a space or drop the aria-label and use `aria-describedby` for the description. Label the hidden input.
6. [Design/SEO] Branded 404.html in the card style, with `lang`.
7. [Responsive] Phone home: front card ~160 px wide with ~225 px dead band (m-03). Scale it to ~60% of the width; description ≥13 px.
8. [Usability] Opaque phone shelf strip and tab bar (library m-03, m-06).
9. [Design] Keep candy shapes away from the fan and CTA (d-04, d-07).
10. [Design] Replace the 12 px condensed italic serif on home cards with the grotesk, or hide it on side cards.
11. [Creativity] Make the covers read as books: spine or page-edge strip, a shelf line under each library row.
12. [SEO/WPO] robots.txt, sitemap.xml, `document.title` = skill name when a sheet opens, subset woff2 fonts.
13. [Design/Content] Library footer; title-case "Prompt motion design ideas"; shorten "Smooth Animation (60…".
14. [Design] Phone top bar: align the dice with the "Easy" pill on one 16 px gutter.

## Measured
- Mobile LCP: home 956 ms, library 1724 ms, detail 2328 ms. Mobile CLS 0 everywhere. Desktop CLS: library and detail 0.229.
- FPS (headless, a floor): home 47 desktop / 45 phone; library 50 / 60.
- No loader. No overflow. Small targets: 0 on the site's pages (3 on GitHub's 404).
- Serious axe: library 1 rule (×39), detail color-contrast ×6, 404 4 rules (GitHub page).
- `noHoverChange`: "Ask Claude Code" (detail). `colorOnly`: "Copy" (detail), 2 on 404.
- Idle motion: home yes, library no (by design).
- Audit: 0 FAIL, 20 WARN (all TTF fonts and font weight, plus thin home content, no robots/sitemap).

Not scored: anything stills can't show (how motion feels).
