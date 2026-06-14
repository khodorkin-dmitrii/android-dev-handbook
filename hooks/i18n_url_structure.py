from __future__ import annotations

import shutil
from pathlib import Path
import re
from urllib.parse import urlsplit


def on_post_build(config, **kwargs) -> None:
    i18n = config.plugins.get("i18n")
    site_dir = Path(config["site_dir"])
    base_path = _site_base_path(config)

    if i18n and i18n.current_language != i18n.default_language:
        _rewrite_alternate_links(site_dir, base_path, i18n.build_languages)
        _rewrite_root_default_pages(site_dir, i18n.default_language)
        return

    en_dir = site_dir / "en"

    if en_dir.exists():
        shutil.rmtree(en_dir)
    en_dir.mkdir()

    excluded = {"en", "ru"}
    for path in site_dir.iterdir():
        if path.name in excluded:
            continue

        target = en_dir / path.name
        if path.is_dir():
            shutil.copytree(path, target)
        else:
            shutil.copy2(path, target)

    if i18n:
        _rewrite_alternate_links(site_dir, base_path, i18n.build_languages)

    (site_dir / "index.html").write_text(
        """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url=en/">
    <link rel="canonical" href="en/">
    <title>Redirecting to Android Dev Handbook</title>
  </head>
  <body>
    <p><a href="en/">Go to Android Dev Handbook</a></p>
  </body>
</html>
""",
        encoding="utf-8",
    )


def _site_base_path(config) -> str:
    site_url = config.get("site_url") or ""
    base_path = urlsplit(site_url).path.rstrip("/")
    return base_path


def _rewrite_alternate_links(site_dir: Path, base_path: str, locales: list[str]) -> None:
    pattern = re.compile(r'href="[^"]*" hreflang="([^"]+)"')

    for locale in locales:
        locale_dir = site_dir / locale
        if not locale_dir.exists():
            continue

        for html_file in locale_dir.rglob("*.html"):
            text = html_file.read_text(encoding="utf-8")
            page_path = _page_path_for_locale(html_file, locale_dir)

            def replace(match: re.Match[str]) -> str:
                target_locale = match.group(1)
                if target_locale not in locales:
                    return match.group(0)
                return f'href="{base_path}/{target_locale}/{page_path}" hreflang="{target_locale}"'

            updated = pattern.sub(replace, text)
            if updated != text:
                html_file.write_text(updated, encoding="utf-8")


def _page_path_for_locale(html_file: Path, locale_dir: Path) -> str:
    relative = html_file.relative_to(locale_dir)
    if relative.name == "index.html":
        parts = relative.parts[:-1]
    else:
        parts = relative.parts
    if not parts:
        return ""
    return "/".join(parts) + "/"


def _rewrite_root_default_pages(site_dir: Path, default_locale: str) -> None:
    excluded_roots = {
        default_locale,
        "ru",
        "assets",
        "search",
        "stylesheets",
    }

    for html_file in site_dir.rglob("*.html"):
        relative = html_file.relative_to(site_dir)
        if len(relative.parts) == 1:
            continue
        if relative.parts[0] in excluded_roots:
            continue

        target_parts = [default_locale, *relative.parts[:-1]]
        target = "/".join(target_parts) + "/"
        prefix = "../" * (len(relative.parts) - 1)
        html_file.write_text(
            f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url={prefix}{target}">
    <link rel="canonical" href="{prefix}{target}">
    <title>Redirecting to Android Dev Handbook</title>
  </head>
  <body>
    <p><a href="{prefix}{target}">Go to Android Dev Handbook</a></p>
  </body>
</html>
""",
            encoding="utf-8",
        )
