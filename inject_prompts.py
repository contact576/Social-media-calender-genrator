import re, sys, pathlib
root = pathlib.Path('/home/user/Social-media-calender-genrator')
md = (root/'PROMPTS.md').read_text(encoding='utf-8')
html = (root/'index.html').read_text(encoding='utf-8')
for n in range(1,6):
    step=f'S{n}'
    m = re.search(r'^##\s+'+step+r'\b.*?\n```\n(.*?)\n```', md, re.S|re.M)
    if not m: print(f'ERROR: no code block for {step}'); sys.exit(1)
    block=m.group(1)
    if '</script>' in block: print(f'ERROR: {step} contains </script>'); sys.exit(1)
    pat=re.compile(r'(<script type="text/plain" class="raw-prompt" data-step="'+step+r'">)(.*?)(</script>)', re.S)
    if not pat.search(html): print(f'ERROR: block for {step} not found in html'); sys.exit(1)
    html=pat.sub(lambda mm: mm.group(1)+block+mm.group(3), html, count=1)
    print(f'{step}: {len(block)} chars')
(root/'index.html').write_text(html, encoding='utf-8')
print('done')
