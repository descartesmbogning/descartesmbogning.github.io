import json,html,sys
D=sys.argv[1]+'/src/data/';J=lambda f:json.load(open(D+f))
p=J('profile.json');e=J('experience.json');pr=J('projects.json');pubs=J('publications.json');q=J('qualifications.json');sk=J('skills.json');ce=J('certificates.json')
E=lambda s:html.escape(str(s))
feat=sorted([x for x in pr if x['featured']],key=lambda x:x['featured'])
sel=[x for x in pubs if x['firstAuthor'] and not x['notice'] and 'rxiv' not in x['venue'].lower()][:3]
for t in ["A microbiota-modulated checkpoint","The determinants of COVID-19 case reporting"]:
    sel+= [x for x in pubs if x['title'].startswith(t)]
links=" · ".join(f'<a href="{E(l["url"])}">{E(l["label"])}</a>' for l in p['links'])
jobs="".join(f'<div class="job"><div class="when">{E(j["period"])}</div><div><b>{E(j["role"])}</b> — {E(j["organisation"])}, {E(j["place"])}<br><span>{E(j["summary"])}</span></div></div>' for j in e['jobs'])
proj="".join(f'<li><b>{E(x["title"])}.</b> {E(x["result"] or x["summary"])}</li>' for x in feat)
skills="".join(f'<div><b>{E(g["group"])}:</b> {E(", ".join(i["name"] for i in g["items"]))}</div>' for g in sk)
pub="".join(f'<li>{'<b>Mbogning Fonkou MD</b> et al.' if x['firstAuthor'] else E(x['authors'].split(';')[0].split(',')[0])+' et al., incl. Mbogning Fonkou MD'} ({E(x["year"])}). {E(x["title"])}. <i>{E(x["venue"])}</i>.</li>' for x in sel)
edu="".join(f'<div class="job"><div class="when">{E(x["year"])}</div><div><b>{E(x["title"])}</b> — {E(x["institution"])}</div></div>' for x in sorted(q,key=lambda x:-int(x['year'])))
certs=[c for c in ce if c['category']=='Healthcare & safety' and c['url']][:3]+[c for c in ce if c['category']=='AI & data' and int(c['year'] or 0)>=2021][:3]
cert=", ".join(f'{E(c["title"])} ({E(c["issuer"])}, {E(c["year"])})' for c in certs)
beyond="; ".join(f'{E(b["skill"])} ({E(b["where"])})' for b in e['beyond']['items'])
html_out=f'''<!doctype html><html><head><meta charset="utf-8"><title>CV – {E(p["name"])}</title><style>
@page{{size:Letter;margin:12mm 14mm}}
body{{font:9.2pt/1.36 Helvetica,Arial,sans-serif;color:#111;margin:0}}
h1{{font-size:19pt;margin:0;letter-spacing:-.01em}} h2{{font-size:10.5pt;text-transform:uppercase;letter-spacing:.08em;margin:9px 0 4px;padding-bottom:3px;border-bottom:2.5px solid #FFC81E}}
.head{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:4px solid #0B0B0B;padding-bottom:8px}}
.head .t{{font-size:11.5pt;font-weight:bold;margin-top:2px}} .head .c{{text-align:right;font-size:9pt}}
a{{color:#111;text-decoration:none}} .x{{color:#B88A00;font-weight:bold}}
.job{{display:grid;grid-template-columns:78px 1fr;gap:8px;margin:3px 0 5px}} .when{{font-weight:bold;font-variant-numeric:tabular-nums}} .job span{{color:#333}}
ul{{margin:0;padding-left:15px}} li{{margin:2px 0}} .nums{{display:flex;gap:14px;margin:6px 0 2px;font-size:9pt}} .nums b{{font-size:11pt}}
p{{margin:5px 0}} .skills div{{margin:2px 0}}
</style></head><body>
<div class="head"><div><h1>{E(p["name"])}, PhD</h1><div class="t">{E(p["headline"].replace(", PhD",""))} · Founder, Cognos<span class="x">X.</span></div></div>
<div class="c">{E(p["email"])}<br>{E(p["location"])}<br><a href="https://descartesmbogning.github.io">descartesmbogning.github.io</a></div></div>
<p>{E(p["summary"])} {E(p["languages"])}.</p>
<div class="nums">{"".join(f'<div><b>{E(m["value"])}</b> {E(m["label"])}</div>' for m in p["metrics"][:5])}</div>
<h2>Experience</h2>{jobs}
<h2>Selected work</h2><ul>{proj}</ul>
<h2>Skills</h2><div class="skills">{skills}</div>
<h2>Transferable experience</h2><p>{beyond}.</p>
<h2>Education</h2>{edu}
<h2>Selected publications</h2><ul>{pub}</ul><p>Full list: descartesmbogning.github.io/publications · {links}</p>
<h2>Recent certificates</h2><p>{cert}.</p>
</body></html>'''
open(sys.argv[2],'w').write(html_out)
