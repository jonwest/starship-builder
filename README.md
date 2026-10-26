# Starship Prompt Builder

A single-page, drag-and-drop builder for Starship (starship.rs) prompts.

## Files

- `starship-prompt-builder-standalone.html`: open this one locally. It's a complete
  HTML page. It needs internet access for SortableJS 1.15.2 (cdnjs) and the UI fonts
  (Google Fonts); the Nerd Font symbols are embedded.
- `starship-prompt-builder.html`: the same page without the outer `<html>`/`<head>`,
  as published to the artifact host (which adds its own skeleton).
- `build/template.html`: the source you edit (markup, CSS and JS).
- `build/build.py`: inlines module data, presets, glyph list and the Nerd Font
  subset into the template, then writes `starship-prompt-builder.html`.
- `build/extract.py`: regenerates `build/modules.json` from Starship's schema and docs.
- `build/nffull.woff2` / `nffull.b64`: the full Symbols Nerd Font (all 10,764 icons), embedded for the preview and the icon picker.
  Regenerate with `pyftsubset dl/sym/SymbolsNerdFont-Regular.ttf --unicodes='*' --flavor=woff2 --output-file=build/nffull.woff2 && base64 -w0 build/nffull.woff2 > build/nffull.b64` (needs `pip install fonttools brotli`).
- `build/glyphs.py`: builds the short "Suggested" glyph list (`curated.json`).
- `dl/schemes/`: Base16 and Base24 color schemes from github.com/tinted-theming/schemes (see dl/schemes/LICENSE), used for the preview theme list.
- `dl/glyphnames.json`: icon names for the picker, from the nerd-fonts v3.4.0 repo.
- `build/minimal.toml`: the hand-written "Minimal" preset.
- `dl/`: the inputs, taken from github.com/starship/starship (master, around v1.27.0):
  `.github/config-schema.json`, `docs/config/README.md` and the preset TOMLs, plus
  Symbols Nerd Font from the nerd-fonts v3.4.0 release (MIT, see dl/sym/LICENSE).

## Rebuild

Run these from this folder:

    python3 build/extract.py dl build/modules.json   # only after updating dl/
    python3 build/glyphs.py                          # only if you change the glyph set
    python3 build/build.py                           # writes starship-prompt-builder.html
