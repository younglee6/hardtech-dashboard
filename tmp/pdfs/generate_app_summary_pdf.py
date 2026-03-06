from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

out_path = 'output/pdf/snake_app_summary.pdf'

doc = SimpleDocTemplate(
    out_path,
    pagesize=letter,
    leftMargin=42,
    rightMargin=42,
    topMargin=42,
    bottomMargin=42,
)

styles = {
    'title': ParagraphStyle(
        'title',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=21,
        textColor=colors.HexColor('#1f1f1f'),
        spaceAfter=8,
    ),
    'section': ParagraphStyle(
        'section',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#1f1f1f'),
        spaceBefore=5,
        spaceAfter=2,
    ),
    'body': ParagraphStyle(
        'body',
        fontName='Helvetica',
        fontSize=9,
        leading=11.2,
        textColor=colors.HexColor('#222222'),
        spaceAfter=2,
    ),
    'bullet': ParagraphStyle(
        'bullet',
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        leftIndent=0,
        textColor=colors.HexColor('#222222'),
    ),
    'mono': ParagraphStyle(
        'mono',
        fontName='Courier',
        fontSize=8.5,
        leading=10.5,
        textColor=colors.HexColor('#111111'),
    ),
}

story = []
story.append(Paragraph('Snake Web App - One-Page Repo Summary', styles['title']))

story.append(Paragraph('What it is', styles['section']))
story.append(Paragraph(
    'A browser-based Snake game implemented with plain HTML, CSS, and JavaScript modules. '
    'Gameplay runs on a fixed-interval loop with DOM rendering for a 20x20 board and score/status HUD.',
    styles['body']
))

story.append(Paragraph('Who it\'s for', styles['section']))
story.append(Paragraph(
    'Primary user: someone who wants a lightweight, no-build Snake game playable in a local browser, including mobile directional buttons and keyboard controls.',
    styles['body']
))

story.append(Paragraph('What it does', styles['section']))
features = [
    'Renders a 20x20 grid board and updates snake/food cells each tick.',
    'Supports keyboard controls (Arrow keys and WASD).',
    'Includes mobile directional buttons for touch input.',
    'Tracks and displays score plus live game status (Running, Paused, Game over).',
    'Implements pause/resume via Space key and a Pause/Resume button.',
    'Provides a Restart button that reinitializes game state.',
    'Enforces core Snake rules: no immediate reverse direction, wall/self collision ends game, eating food grows snake and increments score.',
]
list_items = [ListItem(Paragraph(item, styles['bullet']), leftIndent=8) for item in features]
story.append(ListFlowable(list_items, bulletType='bullet', start='circle', leftIndent=11, bulletFontSize=6, spaceBefore=0, spaceAfter=2))

story.append(Paragraph('How it works (repo-evidence architecture)', styles['section']))
architecture = [
    '<b>UI layer:</b> <font face="Courier">index.html</font> defines board/HUD/buttons; <font face="Courier">styles.css</font> provides layout, theme, and responsive mobile controls.',
    '<b>Controller/runtime:</b> <font face="Courier">src/game.js</font> binds DOM events, maps inputs to directions, runs <font face="Courier">setInterval</font> at 140 ms, and renders each frame.',
    '<b>Game logic service:</b> <font face="Courier">src/snake.js</font> exports pure state functions (<font face="Courier">createInitialState</font>, <font face="Courier">setDirection</font>, <font face="Courier">step</font>, collision + food placement).',
    '<b>Data flow:</b> User input -> direction update -> tick calls <font face="Courier">step(state)</font> -> new immutable state -> DOM repaint + HUD update.',
    '<b>Quality guard:</b> <font face="Courier">tests/snake.test.mjs</font> verifies movement, growth, collisions, reverse-direction rule, and food placement behavior.',
]
arch_items = [ListItem(Paragraph(item, styles['bullet']), leftIndent=8) for item in architecture]
story.append(ListFlowable(arch_items, bulletType='bullet', start='square', leftIndent=11, bulletFontSize=6, spaceBefore=0, spaceAfter=2))

story.append(Paragraph('How to run (minimal)', styles['section']))
story.append(Paragraph('1. In the repo root, run:', styles['body']))
story.append(Paragraph('npm start', styles['mono']))
story.append(Paragraph('2. Open in browser:', styles['body']))
story.append(Paragraph('http://localhost:5173', styles['mono']))
story.append(Paragraph('3. Optional tests:', styles['body']))
story.append(Paragraph('npm test', styles['mono']))

story.append(Spacer(1, 2))
story.append(Paragraph('<b>Not found in repo:</b> production deployment pipeline, backend/API services, persistence/database, authentication, analytics, telemetry, or external integrations.', styles['body']))

doc.build(story)
print(out_path)
