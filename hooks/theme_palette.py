"""Restore the saved scheme before content and reconcile Material palette indices."""

import re


_PALETTE_BOOTSTRAP = """
<script>
(() => {
  try {
    const palette = __md_get("__palette");
    if (!palette || !palette.color) return;
    const scheme = palette.color.scheme;
    if (scheme !== "slate" && scheme !== "default") return;
    const index = scheme === "slate" ? 0 : 1;
    if (palette.index !== index) {
      palette.index = index;
      __md_set("__palette", palette);
    }
    for (const [key, value] of Object.entries(palette.color)) {
      document.body.setAttribute("data-md-color-" + key, value);
    }
  } catch {
    // The server-rendered dark scheme remains available when storage is blocked.
  }
})();
</script>
"""


def on_post_page(output: str, **kwargs) -> str:
    return re.sub(
        r"(<body\b[^>]*>)",
        lambda match: match.group(1) + _PALETTE_BOOTSTRAP,
        output,
        count=1,
    )
