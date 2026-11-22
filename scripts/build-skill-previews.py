"""Render clearly labelled sample outputs; keep creator screenshots separate."""
from pathlib import Path
import argparse
import html
import json
import subprocess
import tempfile

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public/assets/previews'
GROUPS = {
    'website': 'awwwards frontend-design web-artifacts-builder motionsites-web-builder',
    'brand': 'design-dna design-inspiration theme-factory brand-guidelines',
    'polish': 'unslop emil-design-eng impeccable taste',
    'audit': 'jury break-ui',
    'canvas': 'canvas-design algorithmic-art',
    'mobile': 'apple-design mobile-native animate-expo write-swift',
    'design': 'genjutsu figma ui-ux-pro-max pick-ui-library prototype',
    'motion': 'motion-design animate animation-vocabulary find-animation-opportunities review-animations improve-animations animation-performance gsap prompt-motion-design-ideas',
    'three': 'threejs',
    'video': 'slack-gif-creator hyperframes remotion-best-practices lemo-opuscar slideshow',
    'rewrite': 'humanizer',
    'research': 'deep-research llm-council last30days',
    'paper': 'econ-write academic-paper-writer',
    'document': 'doc-coauthoring docx',
    'update': 'internal-comms',
    'slides': 'pptx',
    'sheet': 'xlsx',
    'pdf': 'pdf',
    'workflow': 'superpowers engineering claudex-loop claudex-route',
    'test': 'webapp-testing playwright-mcp',
    'connector': 'mcp-builder',
    'skill': 'skill-creator',
    'video-read': 'tiktok-reader watch',
    'memory': 'claude-mem',
    'code': 'ponytail codex-build',
    'review': 'codex-review',
    'diagram': 'diagram-design graphify',
    'convert': 'markitdown',
    'notebook': 'notebooklm',
    'reverse': 'reverse-engineer-anything',
    'terminal': 'rtk',
    'standards': 'modern-web-guidance',
    'lineart': 'line-art-animation',
    'econ': 'econ-agent-skills',
    'research-router': 'auto-empirical-research-skills',
}
CAPTIONS = {
    'website': 'A page layout with a clear headline, useful content and a main action.',
    'brand': 'A reusable set of colours, typography and spacing rules.',
    'polish': 'A before-and-after layout showing clearer spacing and hierarchy.',
    'audit': 'A visual review with specific issues and suggested fixes.',
    'canvas': 'An original graphic built from colour, composition and geometric forms.',
    'mobile': 'An app screen with navigation, readable content and touch controls.',
    'design': 'A component board showing layouts, controls and design choices.',
    'motion': 'Animation poses and timing, shown as a small motion plan.',
    'three': 'An interactive 3D object with camera and lighting controls.',
    'video': 'An editable video sequence with scenes, captions and a timeline.',
    'rewrite': 'A wordy paragraph rewritten into direct, natural language.',
    'research': 'A research brief that connects a question, sources and findings.',
    'paper': 'An academic draft with a question, method, evidence and limitations.',
    'document': 'An editable document with a clear structure and styled headings.',
    'update': 'A concise team update with progress, next steps and open questions.',
    'slides': 'A presentation with a clear story across several slides.',
    'sheet': 'A spreadsheet with organised data, formulas and a summary chart.',
    'pdf': 'A PDF page with highlighted content and structured text extraction.',
    'workflow': 'A plan moving through implementation and independent checks.',
    'test': 'A browser check that records what was tested and what needs attention.',
    'connector': 'A connector lets an agent read from a tool or data source.',
    'skill': 'A reusable skill folder with instructions, references and checks.',
    'video-read': 'A video frame paired with a transcript and useful notes.',
    'memory': 'Project decisions and next steps saved for a later session.',
    'code': 'A focused code change, with the implementation and checks together.',
    'review': 'A code review pointing to a concrete issue and a possible fix.',
    'diagram': 'A diagram showing how components connect and depend on each other.',
    'convert': 'A document converted into clean, editable Markdown text.',
    'notebook': 'A source notebook with grounded notes, citations and an audio outline.',
    'reverse': 'A view of software components, relationships and observed behaviour.',
    'terminal': 'Long command output condensed into a useful summary.',
    'standards': 'A current web-platform pattern with browser-support guidance.',
    'lineart': 'A small SVG scene with moving characters and changing light.',
    'econ': 'A research workflow linking data checks, estimation and written results.',
    'research-router': 'A research question is matched to a suitable skill, whose instructions are loaded before any analysis runs.',
}
SPECIAL = {
    'animation-vocabulary': ('Motion vocabulary', 'Anticipation', 'Ease out', 'Follow through'),
    'animation-performance': ('Frame timing', 'Input', 'Animation', 'Frame check'),
    'find-animation-opportunities': ('Where movement helps', 'Open panel', 'Change state', 'Confirm action'),
    'review-animations': ('Review the motion', 'Timing', 'Continuity', 'Reduced motion'),
    'improve-animations': ('Refine the motion', 'Before', 'Refined', 'Check'),
    'slack-gif-creator': ('A short looping GIF', 'Frame 1', 'Frame 2', 'Loop'),
    'slideshow': ('A live slide sequence', 'Question', 'Evidence', 'Next step'),
    'last30days': ('Recent discussion brief', 'Recent posts', 'Recurring themes', 'Source links'),
    'llm-council': ('Compare several answers', 'View A', 'View B', 'Synthesis'),
    'claudex-loop': ('Build and cross-check', 'Plan', 'Independent review', 'Implement'),
    'claudex-route': ('Route the coding task', 'Understand', 'Choose workflow', 'Check result'),
    'graphify': ('A code knowledge graph', 'Entry point', 'Module', 'Dependency'),
    'figma': ('An editable design file', 'Frames', 'Components', 'Prototype links'),
    'prototype': ('An interactive prototype', 'Home screen', 'Details screen', 'Tap to continue'),
    'pick-ui-library': ('Compare UI components', 'Buttons', 'Forms', 'Tables'),
    'ui-ux-pro-max': ('A UI design direction', 'Layout', 'Palette', 'Typography'),
    'tiktok-reader': ('A TikTok link, organised', 'Caption', 'Creator', 'Video notes'),
    'watch': ('Understand a video', 'A frame at 00:08', 'Transcript', 'Main points'),
    'python-panel-data': ('Panel-data analysis', 'Data checks', 'Model', 'Results'),
}
KINDS = {ident: kind for kind, values in GROUPS.items() for ident in values.split()}
ESC = lambda value: html.escape(str(value), quote=True)

CSS = '''
*{box-sizing:border-box}html,body{margin:0;width:960px;height:600px;overflow:hidden}
body{background:#eef0f5;color:#202329;font:19px/1.4 Arial,sans-serif;padding:32px}
.sample{height:536px;background:#fff;border:1px solid #dce0e8;border-radius:16px;overflow:hidden}
.top{height:46px;display:flex;align-items:center;gap:8px;padding:0 20px;background:#f7f8fa;border-bottom:1px solid #e1e4eb}
.dot{width:10px;height:10px;border-radius:50%;background:#526ed3}.dot:nth-child(2){background:#ef8f61}.dot:nth-child(3){background:#dab85c}
.top span{margin-left:12px;font-size:14px;color:#5e6572}.body{padding:26px 32px;height:446px}
h1,h2,h3,p{margin:0}h1{font-size:34px;line-height:1.12;letter-spacing:-1px}h2{font-size:27px}h3{font-size:20px}p{color:#5e6572}.muted{font-size:16px;color:#616978}
.footer{height:44px;padding:11px 20px;background:#f7f8fa;border-top:1px solid #e1e4eb;font-size:14px;color:#616978}
.row{display:flex;gap:24px}.row>*{flex:1;min-width:0}.stack{display:grid;gap:16px}.gap{margin-top:20px}.pill{display:inline-block;padding:8px 16px;border-radius:8px;background:#3657bd;color:#fff;font-size:16px}.rule{height:1px;background:#e3e6ec;margin:16px 0}
.panel{padding:18px;background:#f5f6fa;border:1px solid #e0e4ec;border-radius:12px}.paper{padding:24px;background:#fff;border:1px solid #d6dce5;box-shadow:0 8px 18px #14213d0a}.paper p{font-family:Georgia,serif;font-size:18px;line-height:1.65;color:#394253}.paper h2{font-family:Georgia,serif}
.label{font-size:15px;color:#626b7a;margin-bottom:10px}.big{font-size:47px;font-weight:700;line-height:1.05}.accent{color:#3657bd}.small{font-size:16px}.bar{height:12px;border-radius:4px;background:#d9dfed;margin:12px 0}.bar.blue{background:#4568d1}.bar.coral{background:#df7b65}.bar.gold{background:#d8b254}
.swatches{display:flex;gap:10px}.swatches i{height:80px;flex:1;border-radius:10px;background:#3657bd}.swatches i:nth-child(2){background:#e18b70}.swatches i:nth-child(3){background:#efcf7c}.swatches i:nth-child(4){background:#e9edf5}
.hero{height:225px;background:#edf1fa;border-radius:12px;padding:28px;position:relative;overflow:hidden}.hero h1{max-width:470px;font-size:44px}.hero img{position:absolute;width:200px;right:14px;bottom:5px}.nav{display:flex;justify-content:space-between;margin-bottom:22px;font-size:16px}.tile{border:1px solid #dce1eb;padding:16px;border-radius:10px}.tile b{display:block;font-size:19px;margin:6px 0}.tile span{font-size:15px;color:#626b7a}
.phone{width:224px;height:356px;margin:auto;padding:18px 14px;border:6px solid #26334d;border-radius:25px;background:#f5f6fa}.phone .tile{background:white;margin-top:12px;padding:12px;font-size:15px}.phone h2{font-size:25px}.phone .pill{font-size:14px;padding:6px 12px}.phone .nav{font-size:13px;margin-bottom:14px}
.code{font:18px/1.7 Consolas,monospace;background:#182138;color:#e3e9fc;padding:22px;border-radius:12px;white-space:pre-wrap}.code .hl{color:#ffcc78}.step{border:1px solid #ccd5e9;border-radius:10px;padding:22px 14px;text-align:center;background:#f5f7fd;min-height:110px}.arrow{flex:0!important;align-self:center;color:#7886a2;font-size:30px}.steps{display:flex;gap:14px;align-items:stretch}.steps .step{flex:1}.status{display:flex;gap:12px;align-items:center;padding:14px 0;border-bottom:1px solid #e2e6ed}.check{width:26px;height:26px;border-radius:50%;background:#e4ebfd;color:#3657bd;display:grid;place-items:center;font-size:18px;flex:none}
table{width:100%;border-collapse:collapse;font-size:19px}th{text-align:left;font-size:15px;color:#5e6572;background:#f5f7fb}td,th{padding:13px 15px;border-bottom:1px solid #e0e4ec}td:not(:first-child),th:not(:first-child){text-align:right}.formula{padding:12px 16px;background:#e9efff;color:#284794;font:18px Consolas,monospace}.plot{height:180px;display:flex;align-items:flex-end;gap:20px;padding:20px 24px;border-left:1px solid #bac5d8;border-bottom:1px solid #bac5d8}.plot i{display:block;width:70px;background:#5575ca;border-radius:5px 5px 0 0}.plot i:nth-child(2n){background:#de9579}
.slide{height:240px;padding:20px;border:1px solid #d5dce7;background:#f8f9fc;border-radius:8px}.slide h2{font-size:26px}.slide p{font-size:15px;margin-top:12px}.slide .plot{height:125px;padding:12px;gap:12px}.slide .plot i{width:32px}
.frame{height:185px;background:#e9eef8;border-radius:10px;position:relative;overflow:hidden}.frame i{position:absolute;width:54px;height:54px;border-radius:14px;background:#4266d3;top:65px;left:20%}.frame:nth-child(2) i{left:45%;transform:rotate(30deg)}.frame:nth-child(3) i{left:65%;transform:rotate(70deg)}.timeline{height:75px;margin-top:25px;background:#f2f4f9;padding:15px;display:flex;gap:8px;border-radius:9px}.timeline span{flex:1;background:#6a83cb;color:white;font-size:14px;padding:12px}.timeline span:nth-child(2){background:#bc7d6b}.timeline span:nth-child(3){background:#9b86c2}
.rough{background:#f2e9ff;border:1px solid #c9a7f2;padding:24px;border-radius:20px}.rough h2{color:#8249c4;font-size:32px}.rough .pill{background:#9151cb;border-radius:30px;margin:18px 3px 0}.clean{padding:24px;background:#f8f9fc;border:1px solid #dae0ea;border-radius:12px}.clean h2{font-size:32px}.note{padding:16px 20px;background:#fff5db;border-radius:10px;font-size:17px;color:#624c13}.quote{font:24px/1.45 Georgia,serif;color:#34405b}.tag{display:inline-block;padding:5px 9px;background:#e7ecf9;border-radius:5px;font-size:14px;color:#3f568e}
.art{height:365px;display:flex;align-items:center;justify-content:center;background:#f7f4ed;border-radius:12px;overflow:hidden}.art svg{width:100%;height:100%}.graph{display:grid;grid-template-columns:1fr 90px 1fr;align-items:center;gap:24px}.graph .tile{background:#f4f6fc}.line{height:2px;background:#9aa9cb;position:relative}.line:after{content:'';position:absolute;right:0;top:-4px;width:9px;height:9px;border-right:2px solid #9aa9cb;border-top:2px solid #9aa9cb;transform:rotate(45deg)}
'''


def status(text):
    return f'<div class="status"><span class="check">&#10003;</span><span>{ESC(text)}</span></div>'


def plot():
    return '<div class="plot">' + ''.join(f'<i style="height:{h}px"></i>' for h in [65, 100, 82, 138, 115]) + '</div>'


def make_body(skill, kind):
    if kind == 'research-router':
        return '<h1>Find a workflow for your research</h1><div class="panel gap"><span class="tag">Your question</span><h2 class="gap">Which skill fits a staggered DiD study?</h2></div><div class="steps gap"><div class="step"><h3>Search the catalog</h3><p class="small gap">Match the method and research stage</p></div><div class="arrow">&#8594;</div><div class="step"><h3>Select a skill</h3><p class="small gap">Read its instructions and references</p></div><div class="arrow">&#8594;</div><div class="step"><h3>Confirm the design</h3><p class="small gap">Check the data before estimation</p></div></div><p class="small gap">Covers econometrics, literature reviews, data work, writing and replication.</p>'
    title = ESC(skill['title'])
    special = SPECIAL.get(skill['id'], (skill['title'], 'Start', 'Refine', 'Check'))
    labels = [ESC(x) for x in special[1:]]
    topic = ESC(special[0])
    uses = skill.get('useFor') or ['Ideas', 'Examples', 'Next steps']
    if kind == 'website':
        image = (ROOT / 'public/assets/skills/frontend-design.webp').as_uri()
        return f'<div class="nav"><b>FIELDNOTES</b><span>Work &nbsp; About &nbsp; Contact</span></div><div class="hero"><h1>Make room<br>for a clear idea.</h1><p class="gap">A useful page, designed around its content.</p><img src="{image}"></div><div class="row gap">' + ''.join(f'<div class="tile"><b>{ESC(u)}</b><span>One clear place to start.</span></div>' for u in uses[:3]) + '</div>'
    if kind == 'brand':
        return f'<h1>{title}</h1><p class="gap">A consistent visual language</p><div class="swatches gap"><i></i><i></i><i></i><i></i></div><div class="row gap"><div><h2>Headings with character.</h2><p class="gap">Readable body text and one accent.</p></div><div class="panel"><h3>Spacing</h3><p class="gap">4 &nbsp; 8 &nbsp; 16 &nbsp; 24 &nbsp; 32</p><div class="bar blue"></div><div class="bar"></div></div></div>'
    if kind in ['polish', 'audit']:
        if kind == 'audit':
            return '<h1>A review you can act on</h1><div class="row gap"><div class="panel"><h2>Screen review</h2>' + ''.join(status(s) for s in ['Hierarchy', 'Text contrast', 'Aligned spacing']) + '</div><div class="stack"><div class="note">Make the primary action easier to find.</div><div class="note">Increase the contrast of secondary labels.</div><div class="note">Use one spacing rhythm across the cards.</div></div></div>'
        return '<div class="row"><div><div class="label">BEFORE</div><div class="rough"><h2>Everything<br>competes.</h2><p class="gap">Too many styles and actions.</p><span class="pill">Start now!</span><span class="pill">Learn more!</span><div class="bar coral gap"></div><div class="bar"></div></div></div><div><div class="label">AFTER</div><div class="clean"><h2>One clear<br>next step.</h2><p class="gap">Aligned spacing. Readable type.</p><span class="pill gap">Open the project</span><div class="rule"></div><p class="small">The content leads.<br>The interface supports it.</p></div></div></div>'
    if kind == 'mobile':
        return f'<div class="row"><div><h1>{title}</h1><p class="gap">A readable app screen</p><div class="gap">' + status('Clear navigation') + status('Comfortable touch controls') + status('Consistent components') + '</div></div><div class="phone"><div class="nav"><b>9:41</b><span>Today</span></div><h2>Your projects</h2><div class="tile"><b>Research notes</b><p>Ready for review</p></div><div class="tile"><b>New presentation</b><p>Continue the draft</p></div><div class="pill gap">Create a project</div></div></div>'
    if kind == 'design':
        if skill['id'] == 'prototype':
            return '<h1>An interactive prototype</h1><div class="row gap"><div class="phone"><div class="nav"><b>Home</b><span>Projects</span></div><h2>Your projects</h2><div class="tile"><b>Research notes</b><p>Open the details</p></div><span class="pill gap">View project</span></div><div class="arrow">&#8594;</div><div class="phone"><div class="nav"><b>Back</b><span>Details</span></div><h2>Research notes</h2><div class="tile"><b>Project brief</b><p>Information appears after the tap.</p></div><span class="pill gap">Continue</span></div></div>'
        return f'<h1>{topic}</h1><div class="row gap"><div class="panel"><div class="label">COMPONENTS</div><span class="pill">Continue</span><div class="tile gap">Search projects</div><div class="tile gap">A card with a clear title</div></div><div><div class="label">DESIGN CHOICES</div><div class="swatches"><i></i><i></i><i></i></div><div class="gap">' + ''.join(status(x) for x in labels) + '</div></div></div>'
    if kind in ['motion', 'video', 'lineart']:
        return f'<h1>{topic}</h1><div class="row gap">' + ''.join(f'<div><div class="frame"><i></i></div><p class="small gap">{label}</p></div>' for label in labels) + '</div><div class="timeline"><span>Scene &amp; motion</span><span>Captions</span><span>Sound / timing</span></div>'
    if kind in ['three', 'canvas']:
        art = '<svg viewBox="0 0 760 340" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-width="4">'
        if kind == 'three':
            art += '<path d="M260 95 380 40 510 110 390 175Z" fill="#b9c9ef" stroke="#3657bd"/><path d="M260 95v150l130 65V175Z" fill="#7896dc" stroke="#3657bd"/><path d="M390 175 510 110v150l-120 50Z" fill="#e4a58c" stroke="#3657bd"/><ellipse cx="385" cy="200" rx="260" ry="95" stroke="#8394b9" transform="rotate(-16 385 200)"/>'
        else:
            for i in range(12):
                art += f'<ellipse cx="380" cy="170" rx="{34+i*14}" ry="115" stroke="{["#3657bd","#d78368","#d1ad55"][i%3]}" transform="rotate({i*15} 380 170)"/>'
        return f'<h1>{title}</h1><div class="art gap">{art}</g></svg></div>'
    if kind == 'rewrite':
        return '<h1>Say it like a person.</h1><div class="row gap"><div class="panel"><div class="label">FIRST DRAFT</div><p class="quote">Utilize our robust solution to unlock seamless, cutting-edge productivity.</p></div><div class="paper"><div class="label">REWRITTEN</div><p class="quote">Turn your notes into a clear first draft.</p><div class="rule"></div><p class="small">Same idea. Fewer empty words.</p></div></div>'
    if kind == 'research':
        return f'<h1>{topic}</h1><div class="row gap"><div class="paper"><h2>Research brief</h2><div class="rule"></div><p><b>Question</b><br>What does the evidence tell us?</p><p class="gap"><b>Findings</b><br>Connect each point to a source and explain its limits.</p></div><div class="stack">' + ''.join(f'<div class="panel"><span class="tag">{i+1}</span><h3 class="gap">{x}</h3><p class="small gap">Notes and links kept together.</p></div>' for i,x in enumerate(labels)) + '</div></div>'
    if kind in ['paper', 'document', 'update']:
        heading = 'A research question, clearly stated' if kind == 'paper' else 'Project proposal' if kind == 'document' else 'Weekly project update'
        sections = ['Question and contribution', 'Data and method', 'Evidence and limitations'] if kind == 'paper' else ['Background', 'Approach', 'Deliverables'] if kind == 'document' else ['Completed', 'Next steps', 'Needs a decision']
        return f'<div class="row"><div class="paper" style="flex:1.8"><h2>{heading}</h2><p class="gap">A document with a clear purpose and a structure the reader can follow.</p>' + ''.join(f'<h3 class="gap">{x}</h3><p>Keep the point specific. Connect it to the work and record what the reader needs next.</p>' for x in sections[:2]) + '</div><div class="panel"><h3>Outline</h3>' + ''.join(f'<p class="gap">{i+1}. {x}</p>' for i,x in enumerate(sections)) + '</div></div>'
    if kind == 'slides':
        return '<h1>A story across slides</h1><div class="row gap"><div class="slide"><span class="tag">1</span><h2 class="gap">The question</h2><p>What should the audience understand?</p></div><div class="slide"><span class="tag">2</span><h2 class="gap">The evidence</h2>' + plot() + '</div><div class="slide"><span class="tag">3</span><h2 class="gap">The next step</h2><p>Finish with one clear action.</p></div></div>'
    if kind == 'sheet':
        return '<h1>A working spreadsheet</h1><div class="row gap"><div style="flex:1.7"><div class="formula">D2 &nbsp; = B2 - C2</div><table><tr><th>Month</th><th>Income</th><th>Costs</th><th>Balance</th></tr><tr><td>Jan</td><td>1,200</td><td>800</td><td>400</td></tr><tr><td>Feb</td><td>1,400</td><td>900</td><td>500</td></tr><tr><td>Mar</td><td>1,600</td><td>1,000</td><td>600</td></tr></table></div><div class="panel"><h3>Monthly balance</h3>' + plot() + '</div></div>'
    if kind in ['pdf', 'convert']:
        return '<h1>' + ('Read and work with a PDF' if kind == 'pdf' else 'Turn a file into Markdown') + '</h1><div class="row gap"><div class="paper"><h2>Project notes</h2><p class="gap">A short document with headings, paragraphs and a table.</p><p class="gap" style="background:#fff0b8">Keep the useful structure.</p><div class="rule"></div><p>Next steps and supporting notes.</p></div><div class="arrow">&#8594;</div><div class="code"># Project notes\n\nA short document.\n\n## Next steps\n- Review the draft\n- Check the sources</div></div>'
    if kind in ['workflow', 'connector', 'reverse']:
        if kind == 'connector':labels=['Your agent','Connector','Your data / app']
        if kind == 'reverse':labels=['Inspect the program','Trace components','Explain behaviour']
        return f'<h1>{topic}</h1><div class="steps gap">' + '<div class="arrow">&#8594;</div>'.join(f'<div class="step"><div class="tag">{i+1}</div><h3 class="gap">{label}</h3></div>' for i,label in enumerate(labels)) + '</div><div class="panel gap"><h3>Keep the work connected</h3><p class="gap">Inputs, decisions, implementation and checks stay visible.</p></div>'
    if kind == 'test':
        return '<h1>Check the real page</h1><div class="row gap"><div class="panel"><h2>Browser check</h2><div class="hero gap" style="height:175px;padding:22px"><h2>Your page</h2><p class="gap">Content, navigation and controls.</p><span class="pill gap">Continue</span></div></div><div><h3>Test checklist</h3>' + ''.join(status(x) for x in ['Links and navigation','Form interactions','Mobile layout','Clear error messages']) + '</div></div>'
    if kind == 'skill':
        return '<h1>A reusable skill</h1><div class="row gap"><div class="code">my-skill/\n  SKILL.md\n  references/\n  scripts/\n  examples/</div><div class="paper"><h2>When to use it</h2><p class="gap">A specific task and a clear trigger.</p><h3 class="gap">Steps</h3><p>Inputs, actions and checks.</p><h3 class="gap">Expected result</h3><p>Something the user can verify.</p></div></div>'
    if kind == 'video-read':
        return f'<h1>{topic}</h1><div class="row gap"><div><div class="frame" style="height:220px"><i style="width:70px;height:70px;left:40%;top:70px;clip-path:polygon(0 0,100% 50%,0 100%)"></i></div><p class="small gap">00:08 &nbsp; A useful frame</p></div><div class="paper"><h3>Transcript / notes</h3><p class="gap">The main idea, the tools mentioned, and the next step.</p><div class="rule"></div><p>Keep timestamps so the source is easy to revisit.</p></div></div>'
    if kind == 'memory':
        return '<h1>Pick up where you left off.</h1><div class="row gap"><div class="stack"><div class="panel"><h3>Project direction</h3><p class="gap">The choices already agreed.</p></div><div class="panel"><h3>Last session</h3><p class="gap">What changed and why.</p></div></div><div class="paper"><h2>Next session</h2><p class="gap">The relevant decisions come back with the task.</p><div class="rule"></div><h3>Next step</h3><p class="gap">Continue from the verified state.</p></div></div>'
    if kind in ['code', 'review', 'terminal', 'standards']:
        left='function total(items) {\n  return items.reduce(\n    (sum, item) => sum + item.price,\n    0\n  );\n}'
        right='Change\n  Reuse one calculation helper.\n\nCheck\n  Empty input\n  Missing values\n  Expected total'
        heading=topic
        if kind=='review':right='Review note\n\nValidate item.price before\nadding it to the total.\n\nAdd a missing-value check.'
        if kind=='terminal':
            left='test: import\n  passed\ntest: validation\n  passed\ntest: browser route\n  passed\ntest: clipboard\n  passed'
            right='Tests: 4 passed\nFailures: 0\n\nImportant output retained.\nRepetitive lines condensed.';heading='Long output, a useful summary'
        if kind=='standards':
            left='<dialog id="confirm">\n  <h2>Continue?</h2>\n  <button>Confirm</button>\n</dialog>'
            right='Native dialog\n\nFocus management\nKeyboard dismissal\nBrowser support guidance';heading='Use the web platform well'
        return f'<h1>{heading}</h1><div class="row gap"><pre class="code">{ESC(left)}</pre><pre class="code" style="background:#edf1fb;color:#334d8e">{ESC(right)}</pre></div>'
    if kind == 'diagram':
        return f'<h1>{topic}</h1><div class="graph gap"><div class="tile"><h3>Page</h3><p class="gap">The user opens a view.</p></div><div class="line"></div><div class="tile"><h3>UI module</h3><p class="gap">The view reads its content.</p></div><div class="tile"><h3>Assets</h3><p class="gap">Images and styles.</p></div><div class="line"></div><div class="tile"><h3>Data</h3><p class="gap">Structured source records.</p></div></div>'
    if kind == 'notebook':
        return '<h1>A notebook grounded in sources</h1><div class="row gap"><div class="stack"><div class="panel"><h3>Your paper</h3><p class="gap">Source 1</p></div><div class="panel"><h3>Your notes</h3><p class="gap">Source 2</p></div></div><div class="paper"><h2>Ask about the material</h2><p class="gap">A concise answer with references back to the source.</p><div class="rule"></div><span class="tag">Source 1</span> <span class="tag">Source 2</span><h3 class="gap">Audio outline</h3><p class="gap">An introduction, key ideas and a recap.</p></div></div>'
    if kind == 'econ':
        return '<h1>From research data to a paper</h1><div class="steps gap"><div class="step"><h3>Data checks</h3><p class="small gap">IDs, merges, sample log</p></div><div class="arrow">&#8594;</div><div class="step"><h3>Analysis</h3><p class="small gap">Design, model, inference</p></div><div class="arrow">&#8594;</div><div class="step"><h3>Report</h3><p class="small gap">Tables, figures, slides</p></div></div><div class="row gap"><div class="paper"><h3>Decisions log</h3><p class="gap">Unit of observation<br>Treatment definition<br>Clustering level</p></div><div class="panel"><h3>Illustrative table layout</h3><table><tr><th>Term</th><th>Estimate</th></tr><tr><td>Treatment</td><td>+0.12</td></tr><tr><td>Standard error</td><td>0.04</td></tr></table></div></div>'
    raise ValueError(kind)


def get_skills():
    code = "const fs=require('fs'),vm=require('vm'),c={window:{}};vm.runInNewContext(fs.readFileSync('public/skills.js','utf8'),c);process.stdout.write(JSON.stringify([...c.window.SKILL_DATA.skills,...c.window.SKILL_DATA.collections]));"
    return json.loads(subprocess.check_output(['node', '-e', code], cwd=ROOT, text=True, encoding='utf-8'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only', help='comma-separated IDs');args=parser.parse_args()
    skills=get_skills();missing={s['id'] for s in skills}-KINDS.keys();assert not missing, f'Add purposeful preview content for {missing}'
    selected=set(args.only.split(',')) if args.only else {s['id'] for s in skills}
    OUT.mkdir(parents=True,exist_ok=True);work=Path(tempfile.mkdtemp(prefix='skill-preview-pages-'))
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':960,'height':600},device_scale_factor=1)
        for skill in skills:
            if skill['id'] not in selected:continue
            kind=KINDS[skill['id']];body=make_body(skill,kind)
            page_html=f'<!doctype html><html lang="en"><meta charset="utf-8"><title>Sample output: {ESC(skill["title"])}</title><style>{CSS}</style><body><div class="sample"><div class="top"><i class="dot"></i><i class="dot"></i><i class="dot"></i><span>{ESC(skill["title"])} · illustrative example</span></div><div class="body">{body}</div><div class="footer">Sample output · illustrative content and values</div></div></body></html>'
            fixture=work/(skill['id']+'.html');fixture.write_text(page_html,encoding='utf-8');page.goto(fixture.as_uri());page.screenshot(path=str(work/(skill['id']+'.png')))
            image=Image.open(work/(skill['id']+'.png')).convert('RGB');image.save(OUT/(skill['id']+'-sample.webp'),quality=86,method=6)
        browser.close()
    records=[]
    for skill in skills:
        ident=skill['id'];kind=KINDS[ident];records.append({'id':ident,'title':skill['title'],'label':'Sample output','caption':CAPTIONS[kind],'sampleSrc':f'assets/previews/{ident}-sample.webp','images':[{'src':f'assets/previews/{ident}-sample.webp','label':'Example','alt':f'Illustrative example for {skill["title"]}. {CAPTIONS[kind]}','width':960,'height':600}]})
    # Creator screenshots are added by the source-capture step, never presented as our results.
    authored=OUT/'creator-examples.json'
    if authored.exists():
        overrides=json.loads(authored.read_text(encoding='utf-8'))
        for record in records:
            if record['id'] in overrides:record.update(overrides[record['id']])
    (OUT/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'public/preview-data.js').write_text('// Generated by scripts/build-skill-previews.py.\nwindow.SKILL_PREVIEW_DATA = '+json.dumps({r['id']:r for r in records},ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
    print(f'Prepared {len(records)} preview records; rendered {len(selected)} labelled samples.')
    print(f'Preview source pages: {work}')


if __name__=='__main__':main()
