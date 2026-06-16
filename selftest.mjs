// Dev self-test for index.html — exercises the SHIPPED engine + templates (extracted from the file)
// and checks parity against PROMPTS.md. Not part of the app; run with: node selftest.mjs
import { readFileSync } from 'node:fs';
const root = '/home/user/Social-media-calender-genrator/';
const html = readFileSync(root+'index.html','utf8');
const md   = readFileSync(root+'PROMPTS.md','utf8');

let fails=0; const ok=(n,c,d='')=>{ console.log((c?'PASS':'FAIL')+'  '+n+(d?('  — '+d):'')); if(!c) fails++; };

// --- extract shipped pieces ---
const RAW={}; let m;
const reBlk=/<script type="text\/plain" class="raw-prompt" data-step="(S\d)">([\s\S]*?)<\/script>/g;
while(m=reBlk.exec(html)) RAW[m[1]]=m[2];
const appdata=(html.match(/<script id="appdata">([\s\S]*?)<\/script>/)||[])[1];
const engine =(html.match(/<script id="engine">([\s\S]*?)<\/script>/)||[])[1];
ok('extracted 8 templates', Object.keys(RAW).length===8, Object.keys(RAW).join(','));
ok('extracted appdata + engine', !!appdata && !!engine);

// --- eval the shipped engine ---
const api = new Function(appdata+'\n'+engine+'\n;return {reconcile,buildValues,generatePrompt,preflight,validate,renderMarkdown,FIELD_KEYS,DERIVED_KEYS,TEST_CLIENT};')();

// --- parity vs PROMPTS.md ---
for(let n=1;n<=8;n++){const s='S'+n;
  const mm=md.match(new RegExp('^##\\s+'+s+'\\b[\\s\\S]*?\\n```\\n([\\s\\S]*?)\\n```','m'));
  ok(s+' matches PROMPTS.md byte-for-byte', mm && mm[1]===RAW[s]);
}

// --- reconciler ---
const r=api.reconcile(RAW);
ok('reconciler: 0 orphans', r.orphans.length===0, r.orphans.join(','));
ok('reconciler: 0 dead fields', r.deadKeys.length===0, r.deadKeys.join(','));

// --- generate all 8 with TEST_CLIENT, pre-flight each ---
const vals=api.buildValues(api.TEST_CLIENT);
let leftover=[];
for(const s of ['S1','S2','S3','S4','S5','S6','S7','S8']){
  const t=api.generatePrompt(s, vals, RAW);
  const pf=api.preflight(t);
  if(pf.length) leftover.push(s+':'+pf.join(' '));
  ok(s+' non-empty (>200 chars)', t.length>200, t.length+' chars');
}
ok('zero leftover {{ }} / [[ ]] in any prompt', leftover.length===0, leftover.join(' | '));

// COMPETITOR_HANDLES empty → its [[IF]] blocks stripped; confirm no stray "Force-include" line in S2
const s2=api.generatePrompt('S2', vals, RAW);
ok('S2 strips empty COMPETITOR_HANDLES leg', !/Force-include these competitor handles/.test(s2));
ok('S2 keeps mandatory hashtag leg', /Leg 2 — HASHTAGS \(always run/.test(s2));

// optional ADDITIONAL_NOTES kept where present
const s6=api.generatePrompt('S6', vals, RAW), s7=api.generatePrompt('S7', vals, RAW);
ok('S6 includes operator notes when present', /Operator notes \(proof, preferred pillars/.test(s6));
ok('S7 includes operator notes when present', /Operator notes \(proof, voice, constraints\)/.test(s7));
ok('S1 keeps client scrape when handle present', /apify\/instagram-reel-scraper/.test(api.generatePrompt('S1', vals, RAW)));
// NEW/THIN ACCOUNT: empty handle strips the client scrape + learning-loop scrape, stays placeholder-clean
const valsNH=api.buildValues(Object.assign({},api.TEST_CLIENT,{CLIENT_HANDLE:''}));
const s1nh=api.generatePrompt('S1', valsNH, RAW);
ok('S1 strips client scrape when no handle', !/apify\/instagram-reel-scraper/.test(s1nh) && api.preflight(s1nh).length===0, api.preflight(s1nh).join(' '));
const s8nh=api.generatePrompt('S8', valsNH, RAW);
ok('S8 learning-loop guards no-handle', /Learning loop not\s+yet active/.test(s8nh) && !/"resultsLimit": 30/.test(s8nh) && api.preflight(s8nh).length===0);
ok('no-handle client still passes validation', Object.keys(api.validate(Object.assign({},api.TEST_CLIENT,{CLIENT_HANDLE:''}))).length===0);

// ---- process-refinement guards (two-column scripts, all-slots coverage, origin/geo, skew, S8 research) ----
const s3=api.generatePrompt('S3', vals, RAW), s4=api.generatePrompt('S4', vals, RAW),
      s5=api.generatePrompt('S5', vals, RAW), s8=api.generatePrompt('S8', vals, RAW);
ok('S7 mandates a script for every calendar slot', /COVERAGE RULE \(mandatory\)/.test(s7) && /COVERAGE CHECK/.test(s7));
ok('S7 specifies the two-column shooting-script format', /TWO-COLUMN SHOOTING SCRIPT/.test(s7) && /AUDIO — what they HEAR/.test(s7) && /VISUAL & TEXT — what they SEE & READ/.test(s7));
ok('S7 footer carries Hook / CTA / Why-viral', /WHY IT'LL GO VIRAL/.test(s7));
ok('S2 records account origin (geo/language)', /RECORD its ORIGIN/.test(s2));
ok('S3 carries an origin column', /origin \(geo\/lang\)/.test(s3));
ok('S4 stamps origin per card', /ORIGIN \(geo\/language/.test(s4));
ok('S5 runs the geo/language skew check', /GEO\/LANGUAGE SKEW CHECK/.test(s5));
ok('S8 hard-requires s2-discovery + s3-outliers', /s2-discovery and s3-outliers are NON-NEGOTIABLE/.test(s8));
ok('S8 includes every script (no flagship-only)', /include EVERY script from s7/.test(s8) && /ACCOUNTS WE DECODED/.test(s8));

// validation fires on blank
const blank=api.validate({});
const expectBlank=api.FIELD_KEYS.filter(f=>f.required && !f.default && f.key!=='VAULT_FOLDER').length;
ok('blank form flags required-without-default fields', Object.keys(blank).length===expectBlank, Object.keys(blank).length+' === '+expectBlank);
// a valid client passes
ok('TEST_CLIENT passes validation', Object.keys(api.validate(api.TEST_CLIENT)).length===0, JSON.stringify(api.validate(api.TEST_CLIENT)));
// handle regex catches bad handle
ok('bad handle rejected', !!api.validate(Object.assign({},api.TEST_CLIENT,{CLIENT_HANDLE:'bad handle!'})).CLIENT_HANDLE);
// <3 keywords rejected
ok('<3 keywords rejected', !!api.validate(Object.assign({},api.TEST_CLIENT,{NICHE_KEYWORDS:'one\ntwo'})).NICHE_KEYWORDS);

// ---- Beautifier: no silent drop ----
const sample=(html.match(/<script type="text\/plain" id="sample-report">([\s\S]*?)<\/script>/)||[])[1]||'';
const rep=api.renderMarkdown(sample);
ok('beautifier: sample has blocks', rep.blocks>0, rep.blocks+' blocks');
ok('beautifier: nothing dropped from sample', rep.dropped.length===0, 'dropped: '+rep.dropped.join(','));
ok('beautifier: unknown ::: block still rendered', /block type the renderer has never seen/.test(rep.html));
ok('beautifier: raw angle brackets escaped, not executed', /&lt;callout&gt;/.test(rep.html) && !/<callout>/.test(rep.html));
ok('beautifier: chart fence became an svg', /<svg class="rpt-chart"/.test(rep.html));
ok('beautifier: table rendered', /<table class="rpt-table"/.test(rep.html));
ok('beautifier: code fence preserved verbatim', /Comment BRUSH/.test(rep.html));
const r2=api.renderMarkdown('# T\n\n```\nunclosed code fence\nstill text');
ok('beautifier: unclosed fence drops nothing & no throw', r2.dropped.length===0, 'dropped '+r2.dropped.join(','));
ok('beautifier: empty input safe', api.renderMarkdown('').blocks===0 && api.renderMarkdown('').dropped.length===0);
const rJs=api.renderMarkdown('```js\nvar x=1;\n```\nafter the block');
ok('beautifier: ```lang fence pairs correctly', /<pre class="rpt-code">/.test(rJs.html) && /after the block/.test(rJs.html) && rJs.dropped.length===0);
const rEh=api.renderMarkdown('## \nreal text');
ok('beautifier: empty heading is not an empty tag, no drop', !/<h2[^>]*><\/h2>/.test(rEh.html) && rEh.dropped.length===0);
// two-column shooting script (S7/S8 format): h3 + 3-col table + Hook/CTA/Why footer — renders, no drops
const rScript=api.renderMarkdown(
  '### Reel 1 — "Same $1,000" · REACH · 35s · original VO\n'+
  '| TIME | AUDIO — what they HEAR | VISUAL & TEXT — what they SEE & READ |\n'+
  '|---|---|---|\n'+
  '| 0–2s | "Same $1,000 — 37 leads vs zero." | Hard split screen. OVERLAY: "Same $1,000. 37 leads vs 0." |\n'+
  '\n**HOOK:** the split-screen number gap.\n\n**CALL TO ACTION:** Comment STRUCTURE.\n\n**WHY IT’LL GO VIRAL:** transplants the 20.5× scoreboard onto a real result.');
ok('beautifier: two-column script renders with no drops', rScript.dropped.length===0 && /<table class="rpt-table"/.test(rScript.html) && /WHY/.test(rScript.html), 'dropped '+rScript.dropped.join(','));

console.log('\n'+(fails?('❌ '+fails+' check(s) failed'):'✅ all checks passed'));
process.exit(fails?1:0);
