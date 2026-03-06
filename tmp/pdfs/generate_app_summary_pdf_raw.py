import os

out_path = 'output/pdf/snake_app_summary.pdf'
os.makedirs(os.path.dirname(out_path), exist_ok=True)

# Content derived only from repo files.
lines = [
    ('title', 'Snake Web App - One-Page Repo Summary'),
    ('sp', ''),
    ('h', 'What it is'),
    ('p', 'A browser-based Snake game implemented with plain HTML, CSS, and JavaScript modules.'),
    ('p', 'Gameplay runs on a fixed-interval loop with DOM rendering for a 20x20 board and HUD.'),
    ('sp', ''),
    ('h', "Who it's for"),
    ('p', 'Primary user/persona: someone who wants a lightweight, no-build Snake game in a local browser,'),
    ('p', 'including keyboard input and on-screen directional controls on small screens.'),
    ('sp', ''),
    ('h', 'What it does'),
    ('b', 'Renders a 20x20 grid board and paints snake/food cells each tick.'),
    ('b', 'Supports Arrow keys and WASD direction controls.'),
    ('b', 'Shows mobile directional buttons for touch input (under 700px CSS breakpoint).'),
    ('b', 'Tracks and displays score and status (Running, Paused, Game over).'),
    ('b', 'Pauses/resumes via Space key and Pause/Resume button.'),
    ('b', 'Restarts game state from a dedicated Restart button.'),
    ('b', 'Applies Snake rules: no instant reverse, wall/self collision ends game, food grows snake.'),
    ('sp', ''),
    ('h', 'How it works (repo-evidence architecture)'),
    ('b', 'UI layer: index.html defines board/HUD/buttons; styles.css defines layout/theme/responsive controls.'),
    ('b', 'Runtime/controller: src/game.js binds DOM events, maps inputs, runs setInterval(140ms), and renders.'),
    ('b', 'Logic module: src/snake.js exports pure state functions for init, movement, collisions, and food.'),
    ('b', 'Data flow: input -> setDirection/togglePause -> step(state) per tick -> state -> DOM + HUD update.'),
    ('b', 'Tests: tests/snake.test.mjs validates movement, growth, collisions, reverse rule, and food placement.'),
    ('sp', ''),
    ('h', 'How to run (minimal)'),
    ('n', '1. Run `npm start` from the repo root.'),
    ('n', '2. Open `http://localhost:5173` in a browser.'),
    ('n', '3. Optional: run `npm test` for logic tests.'),
    ('sp', ''),
    ('h', 'Not found in repo'),
    ('p', 'Production deployment pipeline, backend/API services, persistence/database, auth, analytics, and telemetry.'),
]

# PDF helpers

def esc(text: str) -> str:
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

page_w, page_h = 612, 792  # Letter
left = 44
start_y = 760

ops = []
current_y = start_y

for kind, text in lines:
    if kind == 'title':
        ops.append('BT')
        ops.append('/F2 16 Tf')
        ops.append(f'1 0 0 1 {left} {current_y} Tm')
        ops.append(f'({esc(text)}) Tj')
        ops.append('ET')
        current_y -= 24
    elif kind == 'h':
        ops.append('BT')
        ops.append('/F2 10.5 Tf')
        ops.append(f'1 0 0 1 {left} {current_y} Tm')
        ops.append(f'({esc(text)}) Tj')
        ops.append('ET')
        current_y -= 14
    elif kind == 'p':
        ops.append('BT')
        ops.append('/F1 9 Tf')
        ops.append(f'1 0 0 1 {left} {current_y} Tm')
        ops.append(f'({esc(text)}) Tj')
        ops.append('ET')
        current_y -= 12
    elif kind == 'b':
        ops.append('BT')
        ops.append('/F1 9 Tf')
        ops.append(f'1 0 0 1 {left + 8} {current_y} Tm')
        ops.append(f'( - {esc(text)}) Tj')
        ops.append('ET')
        current_y -= 12
    elif kind == 'n':
        ops.append('BT')
        ops.append('/F1 9 Tf')
        ops.append(f'1 0 0 1 {left} {current_y} Tm')
        ops.append(f'({esc(text)}) Tj')
        ops.append('ET')
        current_y -= 12
    elif kind == 'sp':
        current_y -= 5

if current_y < 40:
    raise SystemExit(f'Content overflowed page; last y={current_y}')

content_stream = '\n'.join(ops).encode('latin-1')

objects = []

def add_obj(data: bytes):
    objects.append(data)

add_obj(b'<< /Type /Catalog /Pages 2 0 R >>')
add_obj(b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>')
add_obj(b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>')
add_obj(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
add_obj(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>')
add_obj(f'<< /Length {len(content_stream)} >>\nstream\n'.encode('latin-1') + content_stream + b'\nendstream')

pdf = bytearray()
pdf.extend(b'%PDF-1.4\n')
offsets = [0]
for i, obj in enumerate(objects, start=1):
    offsets.append(len(pdf))
    pdf.extend(f'{i} 0 obj\n'.encode('latin-1'))
    pdf.extend(obj)
    pdf.extend(b'\nendobj\n')

xref_pos = len(pdf)
pdf.extend(f'xref\n0 {len(objects)+1}\n'.encode('latin-1'))
pdf.extend(b'0000000000 65535 f \n')
for off in offsets[1:]:
    pdf.extend(f'{off:010d} 00000 n \n'.encode('latin-1'))
pdf.extend(b'trailer\n')
pdf.extend(f'<< /Size {len(objects)+1} /Root 1 0 R >>\n'.encode('latin-1'))
pdf.extend(b'startxref\n')
pdf.extend(f'{xref_pos}\n'.encode('latin-1'))
pdf.extend(b'%%EOF\n')

with open(out_path, 'wb') as f:
    f.write(pdf)

print(out_path)
print(f'final_y={current_y}')
