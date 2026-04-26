from flask import Flask, render_template_string, request, jsonify
import chess
import random

app = Flask(__name__)

# --- GLOBAL STATE ---
# We use a dictionary to store games for different users (basic session handling)
games = {}

def get_ai_move(board):
    """
    A simulated AI that plays valid chess moves.
    It prioritizes capturing pieces to look intelligent.
    """
    legal_moves = list(board.legal_moves)
    
    # 1. Priority: Capture a piece if possible
    for move in legal_moves:
        if board.piece_at(move.to_square):
            return move
            
    # 2. Priority: Control the center (e4, d4, etc)
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    for move in legal_moves:
        if move.to_square in center_squares:
            return move

    # 3. Fallback: Random valid move
    return random.choice(legal_moves) if legal_moves else None

# --- HTML UI ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>CyberChess | AI Portfolio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --bg: #121212; --panel: #1e1e1e; --text: #e0e0e0; --accent: #2979ff; --green: #00e676; --white-sq: #eeeed2; --black-sq: #769656; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; height: 100vh; display: flex; flex-direction: column; }
        .nav { padding: 15px 25px; background: #000; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-weight: 800; color: var(--accent); font-size: 20px; letter-spacing: 1px; }
        .game-area { flex: 1; display: flex; justify-content: center; align-items: center; background: #181818; flex-direction: column; position: relative; }
        
        /* BOARD STYLES */
        .board { display: grid; grid-template-columns: repeat(8, min(11vw, 65px)); border: 8px solid #2a2a2a; border-radius: 4px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        .sq { width: min(11vw, 65px); height: min(11vw, 65px); display: flex; justify-content: center; align-items: center; font-size: min(9vw, 50px); cursor: pointer; user-select: none; }
        .w { background: var(--white-sq); color: #000; } .b { background: var(--black-sq); color: #000; }
        .selected { background: #baca2b !important; }
        .last-move { background: rgba(155, 255, 50, 0.5) !important; }
        
        /* CONTROLS */
        .sidebar { width: 100%; max-width: 400px; padding: 20px; display: flex; gap: 10px; justify-content: center; }
        button { flex: 1; padding: 12px; background: var(--panel); color: white; border: 1px solid #444; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; transition: 0.2s; }
        button:hover { background: var(--accent); border-color: var(--accent); transform: translateY(-2px); }
        .status-bar { margin-top: 15px; color: #888; font-size: 14px; font-family: monospace; }
        
        @media(max-width: 600px) { .nav { padding: 10px; } .logo { font-size: 16px; } }
    </style>
</head>
<body>

<div class="nav">
    <div class="logo"><i class="fas fa-chess-knight"></i> CyberChess AI</div>
    <div style="color: #666; font-size: 12px;">v2.4.0 | Stable</div>
</div>

<div class="game-area">
    <div class="board" id="board"></div>
    <div class="status-bar" id="status">System Ready. White to move.</div>
    
    <div class="sidebar">
        <button onclick="undo()"><i class="fas fa-undo"></i> Undo</button>
        <button onclick="location.reload()"><i class="fas fa-sync"></i> New Game</button>
    </div>
</div>

<script>
    const pieces = {'p':'♟','r':'♜','n':'♞','b':'♝','q':'♛','k':'♚','P':'♙','R':'♖','N':'♘','B':'♗','Q':'♕','K':'♔'};
    let fen = "{{ fen }}";
    let selected = null;
    let locked = false;
    let lastMove = [];

    function draw() {
        const b = document.getElementById('board'); b.innerHTML = '';
        let rows = fen.split(' ')[0].split('/');
        for(let r=0; r<8; r++) {
            let cIdx = 0;
            for(let char of rows[r]) {
                if(isNaN(char)) { createSq(r, cIdx++, char); }
                else { for(let k=0; k<parseInt(char); k++) createSq(r, cIdx++, ''); }
            }
        }
    }

    function createSq(r, c, p) {
        let div = document.createElement('div');
        div.className = `sq ${(r+c)%2?'b':'w'}`;
        div.id = `sq-${r}-${c}`;
        if(selected === ""+r+c) div.classList.add('selected');
        if(lastMove.includes(""+r+c)) div.classList.add('last-move');
        div.innerHTML = pieces[p] || '';
        div.onclick = () => click(r, c, p);
        document.getElementById('board').appendChild(div);
    }

    function click(r, c, p) {
        if(locked) return;
        let coord = String.fromCharCode(97+c) + (8-r);
        if(!selected) { if(p) { selected = ""+r+c; draw(); } }
        else {
            let prevR = parseInt(selected[0]); let prevC = parseInt(selected[1]);
            let move = String.fromCharCode(97+prevC) + (8-prevR) + coord;
            selected = null;
            
            // UI Feedback
            document.getElementById(`sq-${r}-${c}`).innerHTML = pieces[p] || ''; 
            draw();
            makeMove(move);
        }
    }

    function makeMove(uci) {
        locked = true;
        document.getElementById('status').innerText = "Calculating Response...";
        
        fetch('/move', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({move: uci})
        }).then(r=>r.json()).then(data => {
            setTimeout(() => {
                if(data.error) { 
                    document.getElementById('status').innerText = "Invalid Move"; 
                    locked=false; draw(); return; 
                }
                fen = data.fen;
                document.getElementById('status').innerText = data.msg;
                locked = false;
                // Highlight AI Move
                if(data.ai_move) {
                    // Simple parsing for visual effect (optional)
                }
                draw();
                if(data.game_over) alert("Game Over! Result: " + data.result);
            }, 500); // Fast response
        });
    }

    function undo() {
        fetch('/undo', {method:'POST'}).then(r=>r.json()).then(d => { fen=d.fen; draw(); });
    }

    draw();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    global board
    board = chess.Board()
    return render_template_string(HTML_PAGE, fen=board.fen())

@app.route('/move', methods=['POST'])
def move():
    try:
        uci = request.json['move']
        move = chess.Move.from_uci(uci)
        
        if move in board.legal_moves:
            board.push(move) # Human Move
            
            if not board.is_game_over():
                # --- AI SIMULATION (Runs inside Python, No File Needed) ---
                ai_move = get_ai_move(board)
                if ai_move:
                    board.push(ai_move)
                    
            return jsonify({
                'fen': board.fen(), 
                'msg': "Your Turn", 
                'game_over': board.is_game_over(),
                'result': board.result() if board.is_game_over() else None
            })
            
    except Exception as e:
        print(e)
    return jsonify({'error': True}), 400

@app.route('/undo', methods=['POST'])
def undo():
    if len(board.move_stack) >= 2:
        board.pop(); board.pop()
    return jsonify({'fen': board.fen()})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
