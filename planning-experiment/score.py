import re
import sys


def score(html):
    checks = {}

    # "sticky" per the brief means "stays visible while scrolling" -- position:fixed on the
    # header achieves the same visible behavior as position:sticky when the header starts at
    # the top of the page, so accept either.
    checks['sticky_header'] = bool(re.search(r'<header', html)) and bool(re.search(
        r'header[\s\S]{0,300}position\s*:\s*(sticky|fixed)|position\s*:\s*(sticky|fixed)[\s\S]{0,300}header',
        html, re.I))

    media_queries = re.findall(r'@media[^{]*\(m(?:ax|in)-width\s*:\s*([\d.]+)px\)', html)
    checks['hamburger_breakpoint_700_800'] = any(700 <= float(w) <= 800 for w in media_queries)
    total_media_rules = len(re.findall(r'@media', html))

    checks['h1_present'] = bool(re.search(r'<h1', html))
    checks['hero_has_button_or_cta_link'] = bool(re.search(r'<h1.{0,1500}?(<button|<a\s[^>]*class="[^"]*(btn|cta)[^"]*")', html, re.S | re.I))

    # accept generic "card" class naming too -- not every model names feature-grid items
    # with the literal word "feature"
    feature_like = len(re.findall(r'class="[^"]*(feature|card)[^"]*"', html, re.I))
    checks['features_3plus'] = feature_like >= 3

    pricing_like = len(re.findall(r'class="[^"]*(pricing|tier|plan)[^"]*"', html, re.I))
    checks['pricing_2plus_tiers'] = pricing_like >= 2
    faq_section_match = re.search(r'(<section[^>]*faq[^>]*>|class="[^"]*faq[^"]*")', html, re.I)
    faq_block = ''
    if faq_section_match:
        start = faq_section_match.start()
        faq_block = html[start:start+6000]
    pricing_section_match = re.search(r'class="[^"]*pricing[^"]*"', html, re.I)
    pricing_block = html[pricing_section_match.start():pricing_section_match.start()+4000] if pricing_section_match else ''
    checks['pricing_marked_recommended'] = 'recommend' in pricing_block.lower()

    checks['faq_present'] = bool(faq_section_match)
    checks['faq_js_click_toggle'] = bool(re.search(r"addEventListener\(['\"]click['\"]", html)) and 'faq' in html.lower()
    # heuristic for "closes other open items": a forEach/loop that resets/collapses siblings,
    # either inline (classList.remove / aria-expanded=false) or via a named close-like helper
    # function called from within the loop (e.g. items.forEach(closeItem)).
    checks['faq_closes_others_heuristic'] = bool(re.search(
        r'forEach[\s\S]{0,400}(remove|false|close)',
        html, re.I))

    checks['dark_mode_media_query'] = 'prefers-color-scheme' in html
    checks['manual_theme_toggle_present'] = bool(re.search(r'class="[^"]*theme[^"]*toggle[^"]*"|id="[^"]*theme[^"]*toggle[^"]*"|theme-toggle', html, re.I))
    checks['theme_persisted_localstorage'] = 'localStorage' in html and 'theme' in html.lower()

    checks['semantic_header'] = '<header' in html
    checks['semantic_nav'] = '<nav' in html
    checks['semantic_footer'] = '<footer' in html
    checks['multiple_sections'] = len(re.findall(r'<section', html)) >= 3

    menu_toggle_is_button = bool(re.search(r'<button[^>]*(menu|hamburger|nav)', html, re.I))
    # a <button> carrying both aria-expanded and aria-controls together is itself a reliable,
    # naming-independent signal of a proper disclosure/accordion trigger.
    accordion_trigger_is_button = (
        bool(re.search(r'<button[^>]*(faq|accordion|question)', html, re.I))
        or bool(re.search(r'<h[1-6]>\s*<button', html))
        or bool(re.search(r'<button(?=[^>]*aria-expanded)(?=[^>]*aria-controls)[^>]*>', html, re.I))
    )
    checks['menu_toggle_is_button'] = menu_toggle_is_button
    checks['accordion_trigger_is_button'] = accordion_trigger_is_button

    aria_expanded_count = len(re.findall(r'aria-expanded', html))
    checks['aria_expanded_2plus_contexts'] = aria_expanded_count >= 2
    checks['aria_controls_present'] = 'aria-controls' in html

    external_link = re.findall(r'<link[^>]*href="https?://', html)
    external_script = re.findall(r'<script[^>]*src="https?://', html)
    external_import = re.findall(r'@import\s+url\(["\']?https?://', html)
    checks['no_external_dependencies'] = not (external_link or external_script or external_import)

    tag_balance_ok = True
    for tag in ['html', 'head', 'body', 'style', 'script']:
        opens = len(re.findall(rf'<{tag}[ >]', html))
        closes = len(re.findall(rf'</{tag}>', html))
        if opens != closes:
            tag_balance_ok = False
    checks['tag_balance_ok'] = tag_balance_ok

    total = sum(1 for v in checks.values() if v)
    return checks, total, len(checks), total_media_rules


if __name__ == '__main__':
    path = sys.argv[1]
    html = open(path, encoding='utf-8', errors='ignore').read()
    checks, total, maxscore, total_media_rules = score(html)
    print(f'{path}: {total}/{maxscore}  (total @media rules: {total_media_rules})')
    for k, v in checks.items():
        print(f'  [{"x" if v else " "}] {k}')
