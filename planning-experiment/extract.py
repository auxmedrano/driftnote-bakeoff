import re
import sys


def extract_html(text, lang_hint='html'):
    text = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]', '', text)
    think_end = text.rfind('</think>')
    if think_end == -1:
        done_thinking = text.rfind('done thinking')
        think_end = done_thinking if done_thinking != -1 else -1
    search_region = text[think_end:] if think_end != -1 else text
    blocks = re.findall(r'```(?:' + lang_hint + r')?\n(.*?)```', search_region, re.DOTALL)
    if not blocks:
        # fall back to scanning the whole transcript if nothing follows </think>
        blocks = re.findall(r'```(?:' + lang_hint + r')?\n(.*?)```', text, re.DOTALL)
    return blocks[-1] if blocks else None


if __name__ == '__main__':
    raw_path, out_path = sys.argv[1], sys.argv[2]
    text = open(raw_path, encoding='utf-8', errors='ignore').read()
    html = extract_html(text)
    if html is None:
        print('NO CODE BLOCK FOUND')
        sys.exit(1)
    open(out_path, 'w').write(html)
    print(f'saved {out_path}, length {len(html)}')
    print('ends with:', repr(html[-100:]))
