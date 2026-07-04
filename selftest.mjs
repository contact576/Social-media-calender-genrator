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
const ORCH=(html.match(/<script type="text\/plain" id="orchestrator-prompt">([\s\S]*?)<\/script>/)||[])[1]||'';
const S6  =(html.match(/<script type="text\/plain" id="s6-deliverables">([\s\S]*?)<\/script>/)||[])[1]||'';
const ALLTPL=Object.assign({}, RAW, {ORCHESTRATOR:ORCH, S6DELIV:S6});  // reconcile scope; STEPS stays from RAW only
ok('extracted 5 templates', Object.keys(RAW).length===5, Object.keys(RAW).join(','));
ok('extracted ORCHESTRATOR + S6 autonomous templates', ORCH.length>500 && S6.length>500, 'orch '+ORCH.length+' / s6 '+S6.length);
ok('extracted appdata + engine', !!appdata && !!engine);

// --- eval the shipped engine ---
const api = new Function(appdata+'\n'+engine+'\n;return {reconcile,buildValues,generatePrompt,preflight,validate,renderMarkdown,FIELD_KEYS,DERIVED_KEYS,TEST_CLIENT};')();

// --- parity vs PROMPTS.md ---
for(let n=1;n<=5;n++){const s='S'+n;
  const mm=md.match(new RegExp('^##\\s+'+s+'\\b[\\s\\S]*?\\n```\\n([\\s\\S]*?)\\n```','m'));
  ok(s+' matches PROMPTS.md byte-for-byte', mm && mm[1]===RAW[s]);
}
for(const [hd,got] of [['ORCHESTRATOR',ORCH],['S6',S6]]){
  const mm=md.match(new RegExp('^##\\s+'+hd+'\\b[\\s\\S]*?\\n```\\n([\\s\\S]*?)\\n```','m'));
  ok(hd+' matches PROMPTS.md byte-for-byte', !!mm && mm[1]===got, mm? ('len '+mm[1].length+' vs '+got.length) : 'no md block');
}

// --- reconciler (over chat steps + autonomous templates) ---
const r=api.reconcile(ALLTPL);
ok('reconciler: 0 orphans', r.orphans.length===0, r.orphans.join(','));
ok('reconciler: 0 dead fields', r.deadKeys.length===0, r.deadKeys.join(','));

// --- generate all 5 with TEST_CLIENT, pre-flight each ---
const vals=api.buildValues(api.TEST_CLIENT);
let leftover=[];
for(const s of ['S1','S2','S3','S4','S5']){
  const t=api.generatePrompt(s, vals, RAW);
  const pf=api.preflight(t);
  if(pf.length) leftover.push(s+':'+pf.join(' '));
  ok(s+' non-empty (>200 chars)', t.length>200, t.length+' chars');
}
ok('zero leftover {{ }} / [[ ]] in any prompt', leftover.length===0, leftover.join(' | '));

// generate each step once for content assertions
const s1=api.generatePrompt('S1', vals, RAW), s2=api.generatePrompt('S2', vals, RAW),
      s3=api.generatePrompt('S3', vals, RAW), s4=api.generatePrompt('S4', vals, RAW),
      s5=api.generatePrompt('S5', vals, RAW);

// S2 — Discover & Rank: discovery legs + origin capture + outlier ranking + cost gate
ok('S2 strips empty COMPETITOR_HANDLES leg', !/Force-include these competitor handles/.test(s2));
ok('S2 hashtag backbone on the reliable actor', /Leg A — HASHTAG \(reliable backbone/.test(s2) && /apify\/instagram-hashtag-scraper/.test(s2));
ok('S2 runs the cookieless discovery mesh (place + accounts)', /Leg B — PLACE/.test(s2) && /Leg C — ACCOUNTS/.test(s2) && /searchType": "place"/.test(s2) && /searchType": "user"/.test(s2));
ok('S2 keyword search is demoted to a bonus, not the backbone', /keyword reel-search is DEAD/.test(s2) && /Leg F — KEYWORD \(BONUS/.test(s2));
ok('S2 splits freshness windows (90d baseline / 30-45d selection)', /BASELINE window = 90 days/.test(s2) && /SELECTION window = 30–45 days/.test(s2) && /onlyPostsNewerThan": "90 days"/.test(s2));
ok('S2 records account origin (geo/language)', /RECORD its ORIGIN/.test(s2));
ok('S2 ranks with an origin column', /origin \(geo\/lang\)/.test(s2));
ok('S2 carries the scrape cost guardrail', /COST GUARDRAIL/.test(s2));

// S3 — Decode & Synthesize: per-card origin stamp + geo/language skew guard
ok('S3 stamps origin per decoded card', /ORIGIN \(geo\/language/.test(s3));
ok('S3 runs the geo/language skew check', /GEO\/LANGUAGE SKEW CHECK/.test(s3));

// S4 — Plan & Script: operator notes + full coverage + two-column shooting-script format
ok('S4 includes operator notes when present', /Operator notes \(proof, preferred pillars, voice, constraints/.test(s4));
ok('S4 mandates a script for every calendar slot', /COVERAGE RULE \(mandatory\)/.test(s4) && /COVERAGE CHECK/.test(s4));
ok('S4 specifies the two-column shooting-script format', /TWO-COLUMN SHOOTING SCRIPT/.test(s4) && /AUDIO — what they HEAR/.test(s4) && /VISUAL & TEXT — what they SEE & READ/.test(s4));
ok("S4 footer carries Hook / CTA / Why-viral", /WHY IT'LL GO VIRAL/.test(s4));

// S1 — client scrape toggles on the optional handle
ok('S1 keeps client scrape when handle present', /apify\/instagram-reel-scraper/.test(s1));
const valsNH=api.buildValues(Object.assign({},api.TEST_CLIENT,{CLIENT_HANDLE:''}));
const s1nh=api.generatePrompt('S1', valsNH, RAW);
ok('S1 strips client scrape when no handle', !/apify\/instagram-reel-scraper/.test(s1nh) && api.preflight(s1nh).length===0, api.preflight(s1nh).join(' '));

// S5 — Showcase + Learning Loop: research depth, all scripts, hard-require s2/s3, no-handle guard
ok('S5 hard-requires s2-discovery + s3-outliers', /s2-discovery and s3-outliers are NON-NEGOTIABLE/.test(s5));
ok('S5 includes every script (no flagship-only)', /include EVERY script from s7/.test(s5) && /ACCOUNTS WE DECODED/.test(s5));

// ---- autonomous "Claude Code" mode (orchestrator + S6 deliverables) ----
const vorch=api.generatePrompt('ORCHESTRATOR', vals, ALLTPL);
const vs6  =api.generatePrompt('S6DELIV', vals, ALLTPL);
ok('ORCHESTRATOR renders clean (no leftover tokens)', api.preflight(vorch).length===0, api.preflight(vorch).join(' '));
ok('S6 deliverables renders clean (no leftover tokens)', api.preflight(vs6).length===0, api.preflight(vs6).join(' '));
ok('ORCHESTRATOR encodes the autonomous gate flow + hard block', /AUTONOMOUS ORCHESTRATOR/.test(ORCH) && /NO SILENT DEGRADE/.test(ORCH) && /PASS BAR/.test(ORCH));
ok('ORCHESTRATOR sets model tiers + budget governor + CONVERT-5 bar', /MODEL TIERS/.test(ORCH) && /BUDGET GOVERNOR/.test(ORCH) && /minus 5/.test(ORCH));
ok('S6 storyboard = image PROMPTS only (no generation) + faithfulness gate', /Generate NO images/.test(S6) && /IMAGE-GEN PROMPT/.test(S6) && /FAITHFULNESS GATE/.test(S6));
// QC fixes (calibration + runnability)
ok('ORCHESTRATOR has an explicit, reproducible scoring formula', /SCORING FORMULA/.test(ORCH) && /axis_points = \(raw/.test(ORCH));
ok('ORCHESTRATOR bar is bucket-scoped (format-led minus 3)', /minus 3\)/.test(ORCH) && /minus 5\)/.test(ORCH));
ok('ORCHESTRATOR budget governor is item-first, not live $', /the hard, directly-observable cap is ITEMS/.test(ORCH));
ok('ORCHESTRATOR bundles the maker templates (self-contained run)', /APPENDED BELOW/.test(ORCH));
ok('ORCHESTRATOR grader caps the unguarded axes (retention/share)', /device asserted without a quoted script line/.test(ORCH) && /not\s*\n?\s*tied to a named §2\.3 trigger/.test(ORCH.replace(/\n\s*/g,' ')));
ok('S6 faithfulness has a SOURCE→FRAME coverage check', /SOURCE→FRAME coverage/.test(S6));
ok('S6 faithfulness binds image-prompt text + has a blind check', /IMAGE-GEN PROMPT bakes into the frame/.test(S6) && /BLIND CHECK/.test(S6));
// completion contract + QC-gate hardening (auditor findings)
ok('ORCHESTRATOR has the completion contract (degrade-vs-stop)', /COMPLETION CONTRACT/.test(ORCH) && /DEGRADE-AND-PROCEED/.test(ORCH) && /HARD-STOP/.test(ORCH));
ok('ORCHESTRATOR never waits for a human (autonomous)', /NEVER WAIT FOR A HUMAN/.test(ORCH));
ok('ORCHESTRATOR grader-call ceiling counts batched grading', /ceil\(\{\{SCRIPTS_TO_WRITE\}\} ÷ 5\)/.test(ORCH));
ok('Gate-2 spot-check verifies the outlier ratio, not just plays', /RECOMPUTE the median/.test(ORCH) && /OUTLIER_SCORE = plays ÷ recomputed median/.test(ORCH));
ok('Gate-3 spot-checks the decode layer (not just plays)', /DECODE SPOT-CHECK/.test(ORCH) && /diffs them VERBATIM/.test(ORCH));
ok('Grader verifies each cited C# mechanic against the cards', /MUST LOAD s4-decode/.test(ORCH) && /decoded mechanic must match/.test(ORCH));
ok('Gate-5 flag+number carry-through is mechanical', /FLAG \+ NUMBER DIFF/.test(ORCH) && /LOW-FRESHNESS/.test(ORCH));
ok('S4 records proof-led/format-led + forces a CONVERT slot', /proof-led\/format-led/.test(s4) && /0-CONVERT calendar is REJECTED/.test(s4));
const s5nh=api.generatePrompt('S5', valsNH, RAW);
ok('S5 learning-loop guards no-handle', /Learning loop not\s+yet active/.test(s5nh) && !/"resultsLimit": 30/.test(s5nh) && api.preflight(s5nh).length===0);
ok('no-handle client still passes validation', Object.keys(api.validate(Object.assign({},api.TEST_CLIENT,{CLIENT_HANDLE:''}))).length===0);

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
