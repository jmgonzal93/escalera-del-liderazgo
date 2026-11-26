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
    global QUESTIONS
    if action == 'updateQuestionBank':
        incoming = data.get('questions', [])
        if not isinstance(incoming, list) or len(incoming) > 500:
            return 'El banco de preguntas no es válido (máximo 500 preguntas).'
        cleaned = []
        for item in incoming:
            if not isinstance(item, dict):
                continue
            try: level = int(item.get('level', -1))
            except (TypeError, ValueError): continue
            q = str(item.get('q', '')).strip()[:1200]
            option_a = str(item.get('good', item.get('optionA', ''))).strip()[:1200]
            option_b = str(item.get('bad', item.get('optionB', ''))).strip()[:1200]
            if level not in range(5) or not q or not option_a or not option_b:
                continue
            cleaned.append({'level': level, 'q': q, 'good': option_a, 'bad': option_b})
        if not cleaned:
            return 'El banco debe tener al menos una pregunta completa.'
        QUESTIONS = cleaned
        STATE['used'] = []
        return f'Banco actualizado: {len(QUESTIONS)} preguntas.'
    if action == 'addTeam':
        name = str(data.get('name', 'Participante')).strip()[:28]
        if not name: return 'Escribí el nombre del participante.'
        if len(STATE['teams']) >= 4: return 'Máximo 4 participantes.'
        team = {'id': uuid.uuid4().hex[:8], 'name': name, 'level': 0, 'color': len(STATE['teams'])}
        STATE['teams'].append(team); STATE['selected'] = team['id']
        return f'Participante {name} agregado.'
    if action == 'selectTeam':
        if any(t['id'] == data.get('id') for t in STATE['teams']): STATE['selected'] = data['id']
        return 'Participante seleccionado.'
    if action == 'draw':
        t = selected_team()
        if not t: return 'Primero agregá y elegí un participante.'
        if t['level'] >= 4: return 'Este participante ya llegó a la cima.'
        pool = [q for q in QUESTIONS if q['level'] == t['level'] and q not in STATE['used']]
        if not pool:
            STATE['used'] = [q for q in STATE['used'] if q['level'] != t['level']]
            pool = [q for q in QUESTIONS if q['level'] == t['level']]
        if not pool:
            return f'No hay preguntas cargadas para el nivel {LEVELS[t["level"]]}. Agregá una desde Administrar preguntas.'
        q = random.choice(pool); STATE['used'].append(q)
        q = dict(q)
        STATE['current'] = dict(q, teamName=t['name'], teamId=t['id'], selectedChoice=None)
        return f'Pregunta para {t["name"]}.'
    if action == 'answerChoice':
        t = selected_team()
        if not t: return 'Elegí un participante.'
        current = STATE['current']
        if not current: return 'Primero sacá una pregunta.'
        if current.get('teamId') != t['id']:
            return 'La pregunta corresponde a otro participante. Seleccioná a quien está jugando.'
        choice = str(data.get('choice', '')).upper()
        if choice not in ('A', 'B'): return 'Elegí la opción A o B.'
        current['selectedChoice'] = choice
        return f'{t["name"]} eligió la opción {choice}. Ahora indicá si la respuesta fue correcta o incorrecta.'
    if action == 'answer':
        t = selected_team()
        if not t: return 'Elegí un participante.'
        current = STATE['current']
        if not current: return 'Primero sacá una pregunta.'
        if current.get('teamId') != t['id']:
            return 'La pregunta corresponde a otro participante. Seleccioná a quien está jugando.'
        if current.get('selectedChoice') not in ('A', 'B'):
            return 'Primero registrá si eligió A o B.'
        is_correct = bool(data.get('correct'))
        if is_correct:
            t['level'] = min(4, t['level'] + 1)
            result_type = 'winner' if t['level'] >= 4 else 'correct'
            msg = (f'¡{t["name"]} es el nuevo CEO de la clínica! ¡Felicitaciones, a brindar!'
                   if result_type == 'winner' else f'¡Correcto! {t["name"]} sube a {LEVELS[t["level"]]}.')
        else:
            result_type = 'wrong'
            msg = f'Incorrecto. {t["name"]} se queda en {LEVELS[t["level"]]}.'
        STATE['lastResult'] = {'type': result_type, 'teamName': t['name'], 'teamId': t['id'],
                               'eventId': uuid.uuid4().hex, 'selectedChoice': current.get('selectedChoice'),
                               'level': current.get('level', t['level']), 'q': current.get('q', ''),
                               'good': current.get('good', ''), 'bad': current.get('bad', '')}
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
