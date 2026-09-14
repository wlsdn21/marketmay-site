# Brunch gallery refresh — design QA

final result: passed

## Target and scope

The user requested keeping the existing website frame and refreshing its menu imagery, with one generated coffee image. The live homepage at commit `f271c68` is the layout reference. The supplied `market-may-brunch-menu.pdf` is the authority for the nine brunch names, prices, photographs, and 3 pm ordering cutoff.

- Source capture: `/workspace/scratch/marketmay-design-audit/01-home.jpg`.
- Source PDF: `/workspace/scratch/b5aeab00c150/upload/01-market-may-brunch-menu.pdf`.
- Full comparison: [home-comparison.jpg](docs/design/brunch-gallery/home-comparison.jpg), live source on the left and implementation on the right.
- Implementation: [desktop-gallery.jpg](docs/design/brunch-gallery/desktop-gallery.jpg), [desktop-menu.jpg](docs/design/brunch-gallery/desktop-menu.jpg), [mobile-gallery.jpg](docs/design/brunch-gallery/mobile-gallery.jpg), and [mobile-menu.jpg](docs/design/brunch-gallery/mobile-menu.jpg).

## Viewports and states

Desktop browser viewport: 1363 × 936 CSS px. The source and implementation screenshots were both returned at 1348 × 926 pixels by the browser capture service; they were combined side by side without resampling at 2696 × 926 pixels. Both home captures are at scroll position zero with the menu closed. The full-view comparison confirms the header, exterior hero, typography, and green information strip retain their previous proportions.

Responsive verification used the actual local page in a temporary 390 × 844 CSS px iframe. Its content width was 375 px after the browser scrollbar, equal to its scroll width, with no horizontal overflow. Mobile captures include the surrounding QA canvas; only the iframe content was evaluated. This checks responsive browser layout, not physical-device touch behavior. The temporary QA wrapper was removed before the final build.

Focused gallery and expanded-menu screenshots were inspected at readable size for photograph framing, price alignment, Korean wrapping, and menu-toggle focus visibility. The complete menu renders three columns on desktop and one at the verified mobile width.

## Findings and comparison history

- Initial P1: the coffee image was blank because its WebP output was empty. Re-encoded the generated source to a temporary WebP, verified decoding, and atomically replaced the empty file. The revised desktop and mobile gallery captures show the coffee image correctly; all 12 rendered gallery/menu image elements subsequently reported successful loading.
- Final comparison: no actionable P0/P1/P2 findings. Replacing the seasonal gallery photographs and adding captions plus a native expandable brunch menu are intentional changes requested by the user.
- The development toolbar visible at the screenshot bottom is preview-only and is absent from the static build.

## Required fidelity surfaces

- **Fonts and typography:** retained Cormorant Garamond headings and Pretendard body text. Original header and hero wrapping match the source. New captions use existing body typography, and mobile menu names wrap without colliding with prices.
- **Spacing and layout:** retained the original three-image desktop gallery and stacked mobile structure. Images use `object-fit: contain` to preserve complete dishes. Captions and the menu toggle provide readable spacing; no horizontal overflow at either verified width.
- **Colors and tokens:** retained the existing green `--brand`, background, muted text, and border tokens. Coffee cup styling follows the cream and green tableware visible in the supplied menu.
- **Image quality and assets:** nine food images are extracted from the supplied PDF and resized/encoded as WebP, with no regenerated dishes. One coffee image is AI-generated editorial imagery; its alt text identifies it as a styled image, not a claim of store photography. All ten WebP files decode and total about 0.82 MB.
- **Copy and content:** all nine menu names and prices match the supplied PDF. The approved coffee tagline is reused from `info.yaml`; the 3 pm ordering note is visible when the menu is closed or open. No new sales claims or coffee prices were invented.

## Interactions and validation

- Desktop: native menu summary opens all nine items by click and closes with Enter.
- Mobile: native summary opens by click, closes with Enter, and reopens with Space; focus outline remains visible.
- All 12 image elements in the expanded gallery/menu load successfully.
- Browser console checked: no site errors observed; extension metadata errors were unrelated to page code.
- Existing seven tests passed; final Astro static build and `git diff --check` passed.
- The static build still produces only the homepage and 404 page. No new public route or dependency was added.

## Implementation checklist

- [x] Preserve the existing homepage frame.
- [x] Replace seasonal gallery content with actual brunch photos and one generated coffee image.
- [x] Match all nine names, prices, and the ordering cutoff to the PDF.
- [x] Verify desktop/mobile rendering, image loading, and keyboard controls.
- [x] Remove temporary QA tooling from public output.

Residual coverage: responsive Chrome layout verified; no separate Safari or physical-device run. Production deployment is outside this preview change.
