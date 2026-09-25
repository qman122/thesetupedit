# Site audit: The Setup Edit (before the September 2026 upgrade)

Audited `docs/` as built by `build.py` (commit 6b030d2), at 1440px and 390px.
The bones were good: an editorial layout, real photography, honest copy, fast static pages.
What held it back is below.

## Looks generic or AI-made
- Tracked-out ALL-CAPS micro labels everywhere: above every section, on every product row, and in the nav, meta strings and buttons. That is the most common template tell.
- Magazine props with no job: "Autumn 2026 Edition", "No. 01" to "No. 04", "In this edition", "On the cover".
- Setup items numbered 01 to 08 even though a shopping list is not a sequence.
- An arrow appended to every link and button, meta strings joined with middle dots, and a drop cap on every guide.
- The shop used drawn "covers" (CSS boxes and lines) instead of real imagery.
- Four home-page setups in a row used the same image-and-text zigzag.
- Inter Tight as the UI face, the default sans on most generated sites.

## Conversion leaks
- "View on Amazon" was a small uppercase underlined text link. It did not look like a button and was easy to skip on mobile.
- There was no "start here" guidance. Every item carried the same weight, so there was no obvious first click.
- The free Cable Checklist (the lead magnet) appeared only once, inside a dark band near the bottom of the home page. Setup and guide pages, where Pinterest traffic lands, never mentioned it.
- There was no persistent call to action, so on long guides the reader had to scroll back to act.
- Guides had no summary of the products they recommend, so skimmers had to read the whole article to find the picks.
- The paid products (Clean Desk Guide, Wallpaper Pack) appeared only on the home page, with thin descriptions.
- Related content existed but was thin: no "more setups" on setup pages and no "keep reading" on guides.

## Mobile (390px)
- The guide table of contents was hidden completely on phones.
- Tap targets for the text-link CTAs were about 30px tall.
- The About link was dropped from the mobile nav.
- Setup pages were one very long text column with no visual break before the related content.

## Speed
- The Google Fonts stylesheet was render-blocking, and it loaded the full Newsreader variable range (300 to 600, roman and italic).
- The hero image (the LCP element) was not preloaded.
- Scroll-spy used a `scroll` event listener. Every section was hidden behind a JS reveal, so content was invisible until the script ran.
- Images were already good: WebP and JPEG srcsets, width and height set, and lazy loading below the fold.

## SEO
- No BreadcrumbList structured data and no visible breadcrumb trail back to Home.
- No ItemList structured data on setup pages.
- Setup meta descriptions were the one-line blurb (about 100 characters) and did not say what the list contains.
- Setup pages were thin: a title, a sentence and a list. There was no explanatory copy for search engines or readers.
- No WebSite or Organization data on the home page.
- Guide thumbnails and some linked images had empty `alt` text.

## Accessibility
- Small label text (11 to 12px, uppercase, letter-spaced) was hard to read, and the terracotta numbers were below 4.5:1 contrast at small sizes.
- Content hidden until JavaScript ran (the `.reveal` classes) is fragile for assistive tech and slow devices.
- The shop tiles were `aria-hidden` links. That was acceptable, but they duplicated the real links.
- Focus styles, the skip link, landmarks and `prefers-reduced-motion` were already in place. These are kept.

## What changed (summary)
See the commit "Redesign: product cards, lead magnet, breadcrumbs, 3 new guides" for the implementation.
