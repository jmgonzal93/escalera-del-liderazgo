from flask import Flask, jsonify, request, send_from_directory
from server import QUESTIONS
import os, random, uuid

app = Flask(__name__, static_folder=None)
ROOT = os.path.dirname(os.path.abspath(__file__))
CONTROL_PIN = os.environ.get('CONTROL_PIN', '').strip()
LEVELS = ['Colaborador', 'Jefe', 'Gerentes', 'Director', 'CEO']
STATE = {'teams': [], 'selected': None, 'current': None, 'used': [], 'lastResult': None}

def snapshot():
    # Keep the expected/incorrect guidance in the API state for the tablet only.
    return dict(STATE)

def selected_team():
    return next((t for t in STATE['teams'] if t['id'] == STATE['selected']), None)

def act(action, data):
    if action == 'addTeam':
        name = str(data.get('name', 'Equipo')).strip()[:28]
        if not name: return 'Escribí un nombre de equipo.'
        if len(STATE['teams']) >= 4: return 'Máximo 4 equipos.'
        team = {'id': uuid.uuid4().hex[:8], 'name': name, 'level': 0, 'color': len(STATE['teams'])}
        STATE['teams'].append(team); STATE['selected'] = team['id']
        return f'Equipo {name} agregado.'
    if action == 'selectTeam':
        if any(t['id'] == data.get('id') for t in STATE['teams']): STATE['selected'] = data['id']
        return 'Equipo seleccionado.'
    if action == 'draw':
        t = selected_team()
        if not t: return 'Primero agregá y elegí un equipo.'
        if t['level'] >= 4: return 'Este equipo ya llegó a la cima.'
        pool = [q for q in QUESTIONS if q['level'] == t['level'] and q not in STATE['used']]
        if not pool:
            STATE['used'] = [q for q in STATE['used'] if q['level'] != t['level']]
            pool = [q for q in QUESTIONS if q['level'] == t['level']]
        q = random.choice(pool); STATE['used'].append(q)
        STATE['current'] = dict(q, teamName=t['name'], teamId=t['id'])
        return f'Pregunta para {t["name"]}.'
    if action == 'answer':
        t = selected_team()
        if not t: return 'Elegí un equipo.'
        if not STATE['current']: return 'Primero sacá una pregunta.'
        if STATE['current'].get('teamId') != t['id']: return 'La pregunta corresponde a otro equipo. Seleccioná el equipo que está jugando.'
        if data.get('correct'):
            t['level'] = min(4, t['level'] + 1); STATE['lastResult'] = 'correct'
            msg = f'¡Correcto! {t["name"]} sube a {LEVELS[t["level"]]}.'
        else:
            STATE['lastResult'] = 'wrong'; msg = f'Esta vez no. {t["name"]} se queda en {LEVELS[t["level"]]}.'
        STATE['current'] = None
        return msg
    if action == 'reset':
        STATE.update({'teams': [], 'selected': None, 'current': None, 'used': [], 'lastResult': None})
        return 'Partida reiniciada.'
    return 'Acción no reconocida.'

@app.get('/')
def index():
    return send_from_directory(ROOT, 'index.html')

@app.get('/api/state')
def get_state():
    return jsonify(snapshot())

@app.post('/api/action')
def post_action():
    data = request.get_json(silent=True) or {}
    if not CONTROL_PIN:
        return jsonify({'message': 'El administrador todavía no configuró el PIN de control en el alojamiento.'}), 503
    if str(data.get('pin', '')) != CONTROL_PIN:
        return jsonify({'message': 'PIN incorrecto. Volvé a ingresarlo en la tablet.'}), 401
    message = act(data.get('action'), data)
    return jsonify({'state': snapshot(), 'message': message})

@app.get('/health')
def health():
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
