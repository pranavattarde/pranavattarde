# Profile visual system

The section order intentionally matches the original profile: portrait and identity, social links and quick stats, who I am, toolbox, skill radar, the season, featured builds, telemetry, career log.

The artwork uses the portfolio palette: charcoal #10151f, warm ivory #eee9df and muted racing red #d35a47. Technology icons retain their original brand colors, with light backing for dark marks to preserve contrast. There are no glow effects, rainbow badges, gradients, rounded panels or external rendering services. The original dot portrait is retained unchanged.

SVGs are code-native. Barlow Condensed heading outlines are generated from the bundled font so they render consistently inside GitHub image elements without remote fonts. The font is distributed under the included SIL Open Font License. Body text uses Arial with a Helvetica/sans-serif fallback.

To rebuild the assets, install scripts/requirements.txt and run python scripts/redesign.py from the repository root. Profile data and original-color technology marks are retained in scripts/profile-data.json. The original assets are kept as source/history references.

The existing activity graphics contain saved snapshots, with different saved totals in the old ribbon and season chart. The redesign preserves those figures and labels them explicitly as snapshots instead of live data. The radar is explicitly a self-assessment. No new achievements or measurements have been invented.

The identity roles, technology ribbons, race start and four-project carousel animate in SVG without JavaScript. Each graphic provides accessible titles/descriptions and reduced-motion styles. Real Markdown links below the project image remain keyboard accessible; images embedded in GitHub cannot provide website-style JavaScript hover interactions.
