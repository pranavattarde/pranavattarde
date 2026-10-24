"""Build the profile's code-native SVG graphics. Requires fonttools.

Run from the repository root. Saved activity is intentionally labelled as a snapshot.
"""
from pathlib import Path
import sys, json, math, re, html, copy
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.varLib.instancer import instantiateVariableFont

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
NS={'s':'http://www.w3.org/2000/svg'}
ET.register_namespace('',NS['s'])
INK='#10151f'; PANEL='#191f27'; IVORY='#eee9df'; RED='#d35a47'; MUTED='#a6a9ac'; LINE='#454b53'
SOURCE=ROOT/'scripts/profile-data.json'

def original(name): return ET.fromstring((ASSETS/name).read_text(encoding='utf-8'))
if not SOURCE.exists():
    tech=original('tech-arsenal-v2.svg'); rows=[]
    for i in range(3):
        row=tech.find(f"s:g[@clip-path='url(#rowclip{i})']/s:g",NS); children=list(row); icons=[]
        for n,element in enumerate(children):
            if element.tag.endswith('text'):
                name=''.join(element.itertext())
                icon=children[n-1].find('s:g',NS)
                if name not in [x['name'] for x in icons]:
                    if icon is None:
                        icon=ET.fromstring('<g xmlns="http://www.w3.org/2000/svg"><text x="0" y="17" font-family="Arial,sans-serif" font-size="12" font-weight="700" fill="#eee9df">AWS</text></g>')
                    icon=copy.deepcopy(icon); icon.attrib.pop('transform',None)
                    icons.append({'name':name,'icon':ET.tostring(icon,encoding='unicode')})
        rows.append(icons)
    track=original('f1-contribution-track.svg')
    cells=[dict(e.attrib) for e in track.findall('s:rect',NS) if e.get('width')=='10' and 96<=float(e.get('y','0'))<=174]
    telemetry=original('telemetry-stats.svg')
    bars=[float(g.find('s:rect',NS).get('height')) for g in telemetry.findall('s:g',NS) if g.find('s:rect',NS) is not None]
    SOURCE.write_text(json.dumps({'tech':rows,'cells':cells,'bars':bars},indent=2),encoding='utf-8')
DATA=json.loads(SOURCE.read_text(encoding='utf-8'))

font=TTFont(ASSETS/'fonts/BarlowCondensed-ExtraBold.ttf')
if 'fvar' in font: font=instantiateVariableFont(font,{'wght':800})
glyphs=font.getGlyphSet(); cmap=font.getBestCmap(); upm=font['head'].unitsPerEm

def display(value,x,y,size=50,color=IVORY,width=None):
    names=[cmap.get(ord(c),'.notdef') for c in value]
    advance=sum(glyphs[n].width for n in names); scale=size/upm
    if width: scale=min(scale,width/max(1,advance))
    result=f'<g fill="{color}" transform="translate({x} {y}) scale({scale} {-scale})">'
    offset=0
    for name in names:
        pen=SVGPathPen(glyphs); glyphs[name].draw(pen)
        result+=f'<path transform="translate({offset} 0)" d="{pen.getCommands()}"/>'
        offset+=glyphs[name].width
    return result+'</g>'

def text(value,x,y,size=17,color=MUTED,weight=400,anchor='start',spacing=0):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{spacing}">{html.escape(str(value))}</text>'
def line(x1,y1,x2,y2,color=LINE):return f'<path d="M{x1} {y1}H{x2}" stroke="{color}"/>' if y1==y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}"/>'
def rect(x,y,w,h,fill=PANEL,stroke=None):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>'
def technology_icon(entry):
    icon=entry['icon']
    if entry['name']=='AWS':
        icon=icon.replace('#eee9df','#FF9900')
    # Keep dark brand marks legible without changing their original colors.
    if entry['name'] in {'Java','Express','NumPy','Pandas','Solidity'}:
        icon=f'<circle cx="12" cy="12" r="15" fill="{IVORY}"/>'+icon
    return icon
def document(name,height,title,content,width=900,styles=''):
    (ASSETS/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title><desc id="desc">Pranav Attarde. Portfolio colors: charcoal, warm ivory and muted racing red.</desc><style>text{{font-kerning:normal}}@media(prefers-reduced-motion:reduce){{.motion{{animation:none!important}}}}{styles}</style>{rect(0,0,width,height,INK)}{content}</svg>',encoding='utf-8')

# Keep the portrait -> identity -> social links -> quick stats flow.
content=text('FULL STACK DEVELOPMENT / AI & ML',34,30,14,IVORY,600,spacing=1.2)
content+=display('PRANAV ATTARDE.',28,145,136,width=840)
roles=['FULL STACK DEVELOPER','AI / ML ENGINEER','BUILDING FRONTWING','FORMULA 1 ENTHUSIAST']
for i,role in enumerate(roles):content+=f'<g class="motion role r{i}">'+text(role,34,184,16,RED,600,spacing=1.8)+'</g>'
content+=line(34,210,866,210)
document('paddock-identity.svg',220,'Pranav Attarde. Full stack developer, AI/ML engineer and Formula 1 enthusiast.',content,styles='@keyframes role{0%,19%{opacity:1;transform:translateY(0)}23%,96%{opacity:0;transform:translateY(-5px)}100%{opacity:1;transform:translateY(0)}}.role{opacity:0;animation:role 16s infinite}.r0{animation-delay:0s}.r1{animation-delay:-12s}.r2{animation-delay:-8s}.r3{animation-delay:-4s}@media(prefers-reduced-motion:reduce){.role{opacity:0}.r0{opacity:1}}')
for label,slug in [('PORTFOLIO','portfolio'),('LINKEDIN','linkedin'),('EMAIL','email'),('GITHUB','github'),('LEETCODE','leetcode')]:
    w=170 if slug in ['portfolio','leetcode'] else 150
    document('link-'+slug+'.svg',44,label,rect(0.5,.5,w-1,43,INK,LINE)+text(label,15,28,14,IVORY,600,spacing=1.3)+text('↗',w-22,28,17,RED),width=w)

quick=''
for i,(value,label) in enumerate([('409','CONTRIBUTIONS'),('12','REPOSITORIES'),('5','LIVE PROJECTS'),('40','DAY STREAK'),('4','CERTIFICATIONS')]):
    x=30+i*174;quick+=display(value,x,65,58,RED if i==0 else IVORY)+text(label,x,93,12,MUTED,spacing=.6)
    if i<4:quick+=line(x+150,26,x+150,98)
quick+=line(30,118,870,118)
document('paddock-quick-stats.svg',124,'Saved profile snapshot: 409 contributions, 12 repositories, 5 live projects, 40 day streak, 4 certifications.',quick)

# Original-color stack marks, larger labels and three smooth continuous strips.
content=text('TOOLS OF THE TRADE',30,35,14,RED,600,spacing=1.6)
content+=text('LANGUAGES / PRODUCTS / SYSTEMS',870,35,12,MUTED,anchor='end',spacing=.7)+line(30,55,870,55)
styles=''
for i,row in enumerate(DATA['tech']):
    y=82+i*91; full=0;pieces=''
    for entry in row:
        icon=technology_icon(entry)
        pieces+=f'<g transform="translate({full+5} 3) scale(1.25)">{icon}</g>'+text(entry['name'],full+50,28,21,IVORY,500)
        full+=max(158,len(entry['name'])*12+88)
        pieces+=line(full-28,7,full-28,31)
    content+=f'<defs><clipPath id="strip{i}"><rect x="30" y="{y}" width="840" height="55"/></clipPath></defs><g clip-path="url(#strip{i})"><g transform="translate(30 {y})"><g class="motion strip{i}">{pieces}<g transform="translate({full} 0)">{pieces}</g></g></g></g>'+line(30,y+66,870,y+66)
    styles+=f'@keyframes strip{i}{{to{{transform:translateX(-{full}px)}}}}.strip{i}{{animation:strip{i} {35+i*7}s linear infinite}}'
document('paddock-toolbox.svg',370,'Technology stack: '+', '.join(e['name'] for row in DATA['tech'] for e in row),content,styles=styles)

# Keep the seven-axis radar and the existing self-assessment values.
skills=[('Full-Stack Development',92),('Backend & APIs',90),('AI / ML',82),('Cloud & DevOps',75),('System Design',78),('Web3 / Blockchain',65),('DSA',80)]
content=text('ENGINEERING RANGE',30,35,14,RED,600,spacing=1.6)+text('SELF-ASSESSED / NOT A CERTIFICATION',870,35,12,MUTED,anchor='end')+line(30,55,870,55)
cx,cy=237,255
def point(i,r):
    a=-math.pi/2+i*math.tau/7;return (cx+math.cos(a)*r,cy+math.sin(a)*r)
for r in [36,72,108,144,180]:
    points=' '.join(f'{x:.2f},{y:.2f}' for x,y in [point(i,r) for i in range(7)])
    content+=f'<polygon points="{points}" fill="none" stroke="{LINE}" stroke-width=".8"/>'
for i in range(7):
    x,y=point(i,180);content+=line(cx,cy,x,y)
    content+=text(f'{i+1:02}',*point(i,201),14,IVORY,600,anchor='middle')
points=' '.join(f'{x:.2f},{y:.2f}' for i,(_,score) in enumerate(skills) for x,y in [point(i,180*score/100)])
content+=f'<polygon points="{points}" fill="{RED}" fill-opacity=".13" stroke="{RED}" stroke-width="2.5"/>'
for i,(_,score) in enumerate(skills):
    x,y=point(i,180*score/100);content+=f'<circle cx="{x}" cy="{y}" r="4" fill="{IVORY}"/>'
for i,(label,score) in enumerate(skills):
    y=103+i*47;content+=text(f'{i+1:02}',485,y,13,RED)+text(label,520,y,18,IVORY)+text(score,866,y,20,IVORY,600,anchor='end')+line(520,y+12,866,y+12)
content+=text('The tools change. The work connects.',30,487,17,MUTED)
document('paddock-radar.svg',510,'Self-assessed skill radar. '+', '.join(f'{label}: {score}' for label,score in skills),content)

# Preserve the original contribution cells while changing the visual presentation.
content=text('THE SEASON',30,35,14,RED,600,spacing=1.6)+text('SAVED CONTRIBUTION SNAPSHOT',870,35,12,MUTED,anchor='end')+line(30,55,870,55)
for i in range(5):
    content+=f'<circle class="motion light l{i}" cx="{366+i*42}" cy="85" r="9" fill="{RED}"/>'
styles='@keyframes light{0%,8%,76%,100%{opacity:.14}14%,62%{opacity:1}}'
for i in range(5):styles+=f'.l{i}{{animation:light 12s {i*.35}s infinite}}'
content+=line(30,140,870,140)+line(30,174,870,174)
car=rect(8,6,15,15,'#080b0e')+rect(8,41,15,15,'#080b0e')+rect(65,6,15,15,'#080b0e')+rect(65,41,15,15,'#080b0e')+f'<path d="M12 23L65 18L83 25V37L65 44L12 39Z" fill="{RED}"/>'+rect(3,14,6,34,IVORY)+rect(68,17,6,28,IVORY)+f'<ellipse cx="47" cy="31" rx="10" ry="7" fill="{INK}"/>'
content+='<g transform="translate(-100 126)"><g class="motion car">'+car+'</g></g>'
styles+='@keyframes race{0%,32%{transform:translateX(0)}68%,100%{transform:translateX(1100px)}}.car{animation:race 12s cubic-bezier(.5,0,.7,1) infinite}'
colors={'#161b22':'#252b33','#0d3d24':'#55372f','#186a3a':'#854332','#25a24a':'#ad4d3b','#42e070':RED}
for cell in DATA['cells']:
    content+=rect(30+(float(cell['x'])-34)*1.21,223+(float(cell['y'])-96)*1.21,11.7,11.7,colors.get(cell['fill'],RED))
for i,month in enumerate(['SEP','OCT','NOV','DEC','JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG']):content+=text(month,30+i*70,210,11,MUTED)
content+=line(30,344,870,344)
for i,(v,l) in enumerate([('423','CONTRIBUTIONS'),('40','LONGEST STREAK'),('53','WEEKS RACED')]):
    x=30+i*290;content+=display(v,x,403,52)+text(l,x+85,400,12,MUTED)
document('paddock-season.svg',430,'Racing contribution graph. Saved snapshot: 423 contributions, 40 longest streak and 53 weeks tracked.',content,styles=styles)

# Four projects rotate between a readable main plate and the three following slots.
projects=[
('FrontWing','01','F1 INTELLIGENCE','Multi-agent F1 analytics for race strategy','simulation and natural-language investigation.','5 agents / 6 services / dual LLM','React / FastAPI / PostgreSQL / Redis','LIVE'),
('PanCred','02','MICROFINANCE / WEB3','Peer-to-peer lending, EMI tracking and','on-chain repayment validation.','3 modules / Sepolia / 4 risk parameters','React / Node.js / Solidity / MongoDB','LIVE'),
('HawkWatch','03','COMPUTER VISION','Secure examinations with multimodal','proctoring and behavioral risk scoring.','4 CV pipelines / real-time / 2 dashboards','React / Node.js / Rekognition / MediaPipe','SOURCE'),
('LS-Reborn Portal','04','COMMUNITY PLATFORM','Player onboarding and server access','with automated roles and application scoring.','3 roles / OAuth2 / 4 workflows','React / Node.js / MySQL / Discord API','LIVE')]
content=text('FEATURED BUILDS',30,35,14,RED,600,spacing=1.6)+text('FOUR PROJECTS / ONE SPOTLIGHT',870,35,12,MUTED,anchor='end')+line(30,55,870,55)
styles=''
positions=[(30,80,1),(30,470,.303),(320,470,.303),(610,470,.303)]
for i,(name,num,category,d1,d2,metrics,stack,status) in enumerate(projects):
    frames=[positions[(i+j)%4] for j in range(5)]
    transforms=''.join(f'{pct}%{{transform:translate({x}px,{y}px) scale({scale});opacity:{1 if scale==1 else .55}}}' for pct,(x,y,scale) in zip([0,25,50,75,100],frames))
    styles+=f'@keyframes card{i}{{{transforms}}}.card{i}{{animation:card{i} 28s cubic-bezier(.65,0,.35,1) infinite}}'
    content+=f'<g class="motion card{i}" transform="translate({positions[i][0]} {positions[i][1]}) scale({positions[i][2]})">'
    content+=rect(0,0,840,355,PANEL,LINE)+text(category,26,34,15,RED,600,spacing=1.7)+text(status,812,34,13,IVORY,600,anchor='end')
    content+=display(name.upper(),24,122,84,width=695)+display(num,744,122,77,RED,width=69)
    content+=text(d1,28,168,23,IVORY)+text(d2,28,202,23,IVORY)+line(28,227,812,227)
    content+=text(metrics,28,264,18,MUTED)+text(stack,28,308,17,IVORY)
    content+='</g>'
document('paddock-projects.svg',606,'Rotating project showcase: FrontWing, PanCred, HawkWatch and LS-Reborn Portal.',content,styles=styles)

content=text('TELEMETRY',30,35,14,RED,600,spacing=1.6)+text('SAVED ACTIVITY / NOT LIVE COUNTERS',870,35,12,MUTED,anchor='end')+line(30,55,870,55)
content+=text('WEEKLY CONTRIBUTIONS / 16 WEEKS',30,91,13,MUTED,spacing=.7)
for i,value in enumerate(DATA['bars']):
    height=value;content+=rect(30+i*31,256-height,20,height,RED if i in [6,9,13] else '#8f8173')
content+=line(30,257,528,257)
for cx,value,label,portion in [(645,'25%','ACTIVE DAYS',.25),(800,'40','LONGEST STREAK',2/3)]:
    content+=f'<circle cx="{cx}" cy="168" r="44" fill="none" stroke="{LINE}" stroke-width="5"/><circle cx="{cx}" cy="168" r="44" fill="none" stroke="{RED}" stroke-width="5" stroke-dasharray="{portion*276.46} 276.46" transform="rotate(-90 {cx} 168)"/>'+text(value,cx,177,25,IVORY,600,anchor='middle')+text(label,cx,239,12,MUTED,anchor='middle')
content+=line(30,287,870,287)
for i,(value,label) in enumerate([('409','CONTRIBUTIONS'),('12','PUBLIC REPOS'),('53','WEEKS TRACKED'),('1','STREAK AT SNAPSHOT')]):
    x=30+i*216;content+=display(value,x,353,55,IVORY)+text(label,x,384,12,MUTED)
document('paddock-telemetry.svg',415,'Saved GitHub activity snapshot: sixteen weekly bars, 25 percent active days, 40 day longest streak, 409 contributions, 12 public repositories.',content)

# The same career milestones, laid out as a starting order instead of a terminal.
milestones=[('2026 / AUG','Smart India Hackathon','National nominee'),('2026 / MAR','Project Morpheus','National finalist'),('2026 / JAN','CEC VIIT / Samsung Campus Ambassador','Team leadership'),('2025 / NOV','Freelance engagement','Production website shipped'),('2025 / JUN','MHT-CET','97.75 percentile')]
content=text('CAREER LOG',30,35,14,RED,600,spacing=1.6)+text('MILESTONES / FORMATION ORDER',870,35,12,MUTED,anchor='end')+line(30,55,870,55)
for i,(date,title,detail) in enumerate(milestones):
    y=86+i*82;content+=display(f'{i+1:02}',30,y+40,45,RED)+text(date,110,y+11,13,MUTED,spacing=.7)+text(title,110,y+41,21,IVORY,600)+text(detail,870,y+41,16,MUTED,anchor='end')+line(110,y+59,870,y+59)
content+=text('CERTIFICATIONS',30,543,14,RED,600,spacing=1.3)
for i,(org,title) in enumerate([('IBM','Generative AI Fundamentals'),('Coursera','Fundamentals of NLP'),('Coursera','Tableau Business Intelligence'),('LinkedIn Learning','Six Sigma Green Belt')]):
    col=i%2;row=i//2;x=30+col*440;y=584+row*61
    content+=text(org.upper(),x,y,12,MUTED,spacing=1)+text(title,x,y+25,18,IVORY)
document('paddock-career.svg',700,'Career milestones and certifications, in the same order as the original profile.',content)
# Mobile artwork keeps the same content and order with readable type at profile width.
content=text('TOOLS OF THE TRADE',24,34,15,RED,600,spacing=1.1)+line(24,55,456,55)
styles=''
for i,row in enumerate(DATA['tech']):
    y=82+i*91;full=0;pieces=''
    for entry in row:
        icon=technology_icon(entry)
        pieces+=f'<g transform="translate({full+5} 3) scale(1.25)">{icon}</g>'+text(entry['name'],full+50,28,21,IVORY,500)
        full+=max(158,len(entry['name'])*12+88);pieces+=line(full-28,7,full-28,31)
    content+=f'<defs><clipPath id="mstrip{i}"><rect x="24" y="{y}" width="432" height="55"/></clipPath></defs><g clip-path="url(#mstrip{i})"><g transform="translate(24 {y})"><g class="motion strip{i}">{pieces}<g transform="translate({full} 0)">{pieces}</g></g></g></g>'+line(24,y+66,456,y+66)
    styles+=f'@keyframes strip{i}{{to{{transform:translateX(-{full}px)}}}}.strip{i}{{animation:strip{i} {35+i*7}s linear infinite}}'
document('paddock-toolbox-mobile.svg',370,'Technology stack, mobile layout.',content,width=480,styles=styles)

content=text('ENGINEERING RANGE',24,34,15,RED,600,spacing=1)+text('SELF-ASSESSED',24,60,12,MUTED)+line(24,77,456,77)
cx,cy=240,270
for r in [34,68,102,136,170]:
    pts=' '.join(f'{x:.2f},{y:.2f}' for x,y in [point(i,r) for i in range(7)])
    content+=f'<polygon points="{pts}" fill="none" stroke="{LINE}"/>'
for i in range(7):
    content+=line(cx,cy,*point(i,170))+text(f'{i+1:02}',*point(i,190),14,IVORY,600,anchor='middle')
pts=' '.join(f'{x:.2f},{y:.2f}' for i,(_,score) in enumerate(skills) for x,y in [point(i,170*score/100)])
content+=f'<polygon points="{pts}" fill="{RED}" fill-opacity=".13" stroke="{RED}" stroke-width="2.5"/>'
for i,(label,score) in enumerate(skills):
    y=493+i*38;content+=text(f'{i+1:02}',24,y,13,RED)+text(label,56,y,18,IVORY)+text(score,456,y,20,IVORY,600,anchor='end')+line(56,y+12,456,y+12)
document('paddock-radar-mobile.svg',766,'Self-assessed skill radar, mobile layout.',content,width=480)

content=text('CAREER LOG',24,34,15,RED,600,spacing=1)+line(24,55,456,55)
for i,(date,title,detail) in enumerate(milestones):
    y=84+i*101;content+=display(f'{i+1:02}',24,y+35,42,RED)+text(date,86,y,13,MUTED)
    if len(title)>33:
        content+=text('CEC VIIT / Samsung',86,y+27,19,IVORY,600)+text('Campus Ambassador',86,y+50,19,IVORY,600)+text(detail,86,y+74,15,MUTED)
    else:content+=text(title,86,y+29,20,IVORY,600)+text(detail,86,y+55,16,MUTED)
    content+=line(86,y+83,456,y+83)
content+=text('CERTIFICATIONS',24,623,15,RED,600,spacing=1)
for i,(org,title) in enumerate([('IBM','Generative AI Fundamentals'),('Coursera','Fundamentals of NLP'),('Coursera','Tableau Business Intelligence'),('LinkedIn Learning','Six Sigma Green Belt')]):
    y=661+i*61;content+=text(org.upper(),24,y,12,MUTED,spacing=1)+text(title,24,y+24,18,IVORY)
document('paddock-career-mobile.svg',899,'Career milestones and certifications, mobile layout.',content,width=480)

content=text('FEATURED BUILDS',24,34,15,RED,600,spacing=1)+line(24,55,456,55);styles=''
pos=[(24,80,1),(24,525,.30),(175,525,.30),(326,525,.30)]
for i,(name,num,category,d1,d2,metrics,stack,status) in enumerate(projects):
    frames=[pos[(i+j)%4] for j in range(5)]
    transforms=''.join(f'{pct}%{{transform:translate({x}px,{y}px) scale({scale});opacity:{1 if scale==1 else .55}}}' for pct,(x,y,scale) in zip([0,25,50,75,100],frames))
    styles+=f'@keyframes card{i}{{{transforms}}}.card{i}{{animation:card{i} 28s cubic-bezier(.65,0,.35,1) infinite}}'
    content+=f'<g class="motion card{i}" transform="translate({pos[i][0]} {pos[i][1]}) scale({pos[i][2]})">'+rect(0,0,432,410,PANEL,LINE)
    content+=text(category,20,31,13,RED,600)+display(name.upper(),18,107,65,width=398)
    import textwrap
    lines=textwrap.wrap(d1+' '+d2,32)
    for n,ln in enumerate(lines):content+=text(ln,20,151+n*30,21,IVORY)
    content+=line(20,266,412,266)+text(metrics,20,302,15,MUTED)
    for n,ln in enumerate(textwrap.wrap(stack,37)):content+=text(ln,20,337+n*25,16,IVORY)
    content+=text(status,20,388,13,RED,600)+text(num,412,388,17,IVORY,600,anchor='end')+'</g>'
document('paddock-projects-mobile.svg',666,'Four rotating projects, mobile layout.',content,width=480,styles=styles)

content=text('TELEMETRY',24,34,15,RED,600,spacing=1)+text('SAVED SNAPSHOT',456,34,11,MUTED,anchor='end')+line(24,55,456,55)
content+=text('WEEKLY CONTRIBUTIONS / 16 WEEKS',24,91,12,MUTED)
for i,value in enumerate(DATA['bars']):content+=rect(24+i*27,245-value,18,value,RED if i in [6,9,13] else '#8f8173')
content+=line(24,246,456,246)
for center,value,label,portion in [(131,'25%','ACTIVE DAYS',.25),(349,'40','LONGEST STREAK',2/3)]:
    content+=f'<circle cx="{center}" cy="337" r="43" fill="none" stroke="{LINE}" stroke-width="5"/><circle cx="{center}" cy="337" r="43" fill="none" stroke="{RED}" stroke-width="5" stroke-dasharray="{portion*270.18} 270.18" transform="rotate(-90 {center} 337)"/>'+text(value,center,345,25,IVORY,600,anchor='middle')+text(label,center,411,13,MUTED,anchor='middle')
content+=line(24,440,456,440)
for i,(value,label) in enumerate([('409','CONTRIBUTIONS'),('12','PUBLIC REPOS'),('53','WEEKS TRACKED'),('1','STREAK AT SNAPSHOT')]):
    x=24+(i%2)*224;y=504+(i//2)*113;content+=display(value,x,y,56)+text(label,x,y+32,13,MUTED)
document('paddock-telemetry-mobile.svg',680,'Saved GitHub activity statistics, mobile layout.',content,width=480)

print('Built desktop and mobile profile graphics. Portrait and section flow retained.')
