# SpareBank 1 design foundations

This workshop uses the official [SpareBank 1 FFE design system](https://github.com/SpareBank1/designsystem/tree/052f1d5b3983f0ad75e743e06effb4b81995f1d3), pinned to `052f1d5b3983f0ad75e743e06effb4b81995f1d3`: light/default semantic colour tokens, SpareBank1 Regular / Medium / Title Medium fonts, rounded buttons, 8 px form corners, visible focus rings and generous spacing. The small vanilla CSS adaptation keeps the Python workshop free of frontend build dependencies. It is not an official bank product or an implementation of the full FFE component library.

Vendored assets: `docs/brand/theme.css` and `fonts/`. The fonts and token-derived styles retain the upstream [MIT notice](docs/brand/LICENSE.md). Sources: `packages/ffe-core/tokens/`, `packages/ffe-core/less/variables.less`, `packages/ffe-buttons/less/base-button.less`, and `packages/ffe-webfonts/` at the pinned revision. No legacy MuseoSans assets are used.

GitHub controls Markdown rendering; README links lead to the fully styled HTML experience. Browser materials load fonts locally and need no font CDN. Terminal output retains the user's chosen font and colours.
