"""
Connect Four Relay Server
Run this on a cloud service (Replit, Heroku, Railway, etc.)
or on a computer accessible from both players
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import string
import time

app = Flask(__name__)
CORS(app)

# Store active games: {room_code: {'moves': [], 'players': set(), 'created': timestamp}}
games = {}

# Clean up old games (older than 2 hours)
def cleanup_old_games():
    current_time = time.time()
    expired = [code for code, data in games.items() 
               if current_time - data['created'] > 7200]
    for code in expired:
        del games[code]

@app.route('/create_room', methods=['POST'])
def create_room():
    """Create a new game room and return room code"""
    cleanup_old_games()
    
    # Generate unique 6-character room code
    while True:
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if room_code not in games:
            break
    
    games[room_code] = {
        'moves': [],
        'players': set(),
        'created': time.time()
    }
    
    return jsonify({'room_code': room_code})

@app.route('/join_room/<room_code>', methods=['POST'])
def join_room(room_code):
    """Join an existing room"""
    cleanup_old_games()
    
    if room_code not in games:
        return jsonify({'error': 'Room not found'}), 404
    
    data = request.json
    player_id = data.get('player_id')
    
    games[room_code]['players'].add(player_id)
    
    return jsonify({
        'success': True,
        'player_count': len(games[room_code]['players'])
    })

@app.route('/send_move/<room_code>', methods=['POST'])
def send_move(room_code):
    """Send a move to the room"""
    if room_code not in games:
        return jsonify({'error': 'Room not found'}), 404
    
    data = request.json
    move = data.get('move')
    player_id = data.get('player_id')
    
    games[room_code]['moves'].append({
        'move': move,
        'player_id': player_id,
        'timestamp': time.time()
    })
    
    return jsonify({'success': True})

@app.route('/get_moves/<room_code>/<int:since_index>', methods=['GET'])
def get_moves(room_code, since_index):
    """Get moves since a specific index"""
    if room_code not in games:
        return jsonify({'error': 'Room not found'}), 404
    
    moves = games[room_code]['moves'][since_index:]
    return jsonify({
        'moves': moves,
        'total_moves': len(games[room_code]['moves'])
    })

@app.route('/room_status/<room_code>', methods=['GET'])
def room_status(room_code):
    """Check if room exists and how many players"""
    if room_code not in games:
        return jsonify({'exists': False}), 404
    
    return jsonify({
        'exists': True,
        'player_count': len(games[room_code]['players']),
        'move_count': len(games[room_code]['moves'])
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'active_games': len(games)
    })

@app.route('/')
def home():
    """Home page to verify server is running"""
    return jsonify({
        'status': 'Connect Four Relay Server is running!',
        'active_games': len(games),
        'endpoints': ['/create_room', '/join_room', '/send_move', '/get_moves', '/room_status']
    })

if __name__ == '__main__':
    # Replit automatically sets the PORT environment variable
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)