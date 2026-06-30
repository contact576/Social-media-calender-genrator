import re, sys, pathlib
root = pathlib.Path('/home/user/Social-media-calender-genrator')
md = (root/'PROMPTS.md').read_text(encoding='utf-8')
html = (root/'index.html').read_text(encoding='utf-8')

def extract(heading_re, label):
    m = re.search(r'^##\s+'+heading_re+r'\b.*?\n```\n(.*?)\n```', md, re.S|re.M)
    if not m: print(f'ERROR: no code block for {label}'); sys.exit(1)
    block = m.group(1)
    if '</script>' in block: print(f'ERROR: {label} contains </script>'); sys.exit(1)
    return block

# --- the 5 chat-mode steps: class="raw-prompt" data-step="S#" ---
for n in range(1,6):
    step=f'S{n}'
    block=extract(re.escape(step), step)
    pat=re.compile(r'(<script type="text/plain" class="raw-prompt" data-step="'+step+r'">)(.*?)(</script>)', re.S)
    if not pat.search(html): print(f'ERROR: block for {step} not found in html'); sys.exit(1)
    html=pat.sub(lambda mm: mm.group(1)+block+mm.group(3), html, count=1)
    print(f'{step}: {len(block)} chars')

# --- autonomous "Claude Code" mode templates: id="..." (NOT raw-prompt, so STEPS stays 5) ---
for heading, sid, label in [('ORCHESTRATOR','orchestrator-prompt','ORCHESTRATOR'), ('S6','s6-deliverables','S6')]:
    block=extract(heading, label)
    pat=re.compile(r'(<script type="text/plain" id="'+sid+r'">)(.*?)(</script>)', re.S)
    if not pat.search(html): print(f'ERROR: block for {label} (id={sid}) not found in html'); sys.exit(1)
    html=pat.sub(lambda mm: mm.group(1)+block+mm.group(3), html, count=1)
    print(f'{label}: {len(block)} chars')

(root/'index.html').write_text(html, encoding='utf-8')
print('done')
