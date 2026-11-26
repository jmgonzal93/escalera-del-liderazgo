#!/usr/bin/env python3
# La Escalera del Liderazgo — servidor local para computadora + tablet
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json, os, socket, random, uuid

ROOT=os.path.dirname(os.path.abspath(__file__))
LEVELS=["Colaborador","Jefe","Gerentes","Director","CEO"]
STATE={"teams":[],"selected":None,"current":None,"used":[],"lastResult":None}
QUESTIONS=[
# 20 preguntas: 4 por nivel, coherentes con las tarjetas impresas.
{"level":0,"q":"Tango Gestión deja de funcionar en varias computadoras y hay tareas urgentes pendientes. ¿Qué hacés?","good":"Informo a Sistemas qué sucede, identifico los sectores afectados y aviso al equipo cómo continuar mientras se resuelve.","bad":"Reinicio mi computadora varias veces y sigo trabajando sin avisar a nadie."},
{"level":0,"q":"Te asignan una tarea que nunca hiciste y no sabés bien cómo realizarla. ¿Cómo actuás?","good":"Busco información, consulto a quien corresponda y avanzo verificando que el resultado sea correcto.","bad":"La dejo pendiente hasta que alguien me explique todo, sin intentar averiguar nada."},
{"level":0,"q":"Detectás que un dato de una factura fue cargado incorrectamente. ¿Qué hacés?","good":"Informo el error y gestiono su corrección según el procedimiento para evitar que afecte otros procesos.","bad":"Lo ignoro porque el error lo cometió otra persona."},
{"level":0,"q":"Un compañero está atrasado y eso afecta tu trabajo. ¿Cómo respondés?","good":"Me comunico con él, coordino qué necesita cada uno y aviso al responsable si peligra el plazo.","bad":"Me quejo con otros compañeros y espero que el jefe lo resuelva."},
{"level":1,"q":"Un colaborador comete un error en la carga de una factura. ¿Cómo actuás?","good":"Reviso el error con la persona, explico cómo corregirlo y hago seguimiento para que pueda hacerlo bien la próxima vez.","bad":"Lo reto y hago yo todas las cargas para que no vuelva a equivocarse."},
{"level":1,"q":"Tenés diez tareas pendientes y un equipo capaz de ayudarte. ¿Cómo las organizás?","good":"Priorizo, delego según las capacidades y acordamos plazos y controles.","bad":"Hago todo personalmente porque así me aseguro de que salga rápido."},
{"level":1,"q":"Dos integrantes del equipo tienen un conflicto que afecta el trabajo. ¿Qué hacés?","good":"Escucho a ambos, aclaro expectativas y acordamos una forma concreta de trabajar juntos.","bad":"Me quedo con la versión de quien trabaja mejor y sanciono al otro."},
{"level":1,"q":"Un colaborador cumple sus tareas, pero necesita mejorar la calidad. ¿Cómo lo abordás?","good":"Doy una devolución específica, marco qué se espera y acordamos cómo medir la mejora.","bad":"Le digo que trabaja mal, sin explicar qué debe cambiar."},
{"level":2,"q":"Dos sectores se responsabilizan mutuamente por una demora. ¿Qué hacés?","good":"Reúno a las partes, reviso el proceso, defino responsabilidades y acordamos acciones con fechas.","bad":"Defiendo a mi sector y les digo que se arreglen entre ellos."},
{"level":2,"q":"Un proveedor entrega equipamiento con fallas. ¿Cómo procedés?","good":"Registro las fallas, hago el reclamo formal, gestiono la garantía y sigo el caso hasta resolverlo.","bad":"Como ya se pagó, acepto el equipo y trato de arreglarlo internamente."},
{"level":2,"q":"Un proyecto puede generar ingresos, pero también requiere recursos y trabajo adicional. ¿Qué evaluás?","good":"Analizo ingresos, costos, recursos, riesgos y beneficios antes de decidir si conviene.","bad":"Lo acepto directamente porque todo ingreso extra es positivo."},
{"level":2,"q":"Tu área alcanza sus objetivos, pero perjudica los resultados de otro sector. ¿Qué hacés?","good":"Reviso el impacto global, coordino con el otro sector y ajusto el proceso para lograr el resultado conjunto.","bad":"Me concentro en cumplir los objetivos de mi área, aunque el resto se atrase."},
{"level":3,"q":"Querés mejorar la conexión entre la sede central y los consultorios externos. ¿Qué considerás?","good":"Evalúo necesidades de ambas sedes, infraestructura, seguridad, impacto operativo y beneficio institucional.","bad":"Me concentro únicamente en lo que necesita la sede central."},
{"level":3,"q":"Un problema operativo importante se resolvió. ¿Qué hacés después?","good":"Analizo por qué ocurrió y qué cambios de proceso pueden evitar que vuelva a pasar.","bad":"Lo doy por terminado y sigo con el próximo problema."},
{"level":3,"q":"Dos gerencias solicitan recursos para proyectos importantes, pero el presupuesto no alcanza. ¿Cómo decidís?","good":"Comparo impacto estratégico, urgencia, riesgos y recursos; explico prioridades y alternativas.","bad":"Asigno recursos al gerente que más insiste o tiene más antigüedad."},
{"level":3,"q":"Detectás que cada gerencia trabaja con criterios distintos para un mismo proceso. ¿Qué proponés?","good":"Acordamos estándares comunes, responsables y seguimiento, respetando las particularidades necesarias.","bad":"Dejo que cada gerencia lo haga a su manera porque es responsabilidad de cada una."},
{"level":4,"q":"La clínica tiene fondos limitados: debe afrontar pagos a proveedores y comprar equipamiento médico. ¿Cómo decidís?","good":"Priorizo según urgencia, impacto en la atención, vencimientos y disponibilidad financiera; comunico el criterio.","bad":"Pago primero al proveedor que más insiste o genera más presión."},
{"level":4,"q":"Hay que reducir costos sin perjudicar la atención. ¿Cuál es el enfoque correcto?","good":"Identifico ineficiencias y oportunidades de ahorro sin comprometer la seguridad ni la calidad asistencial.","bad":"Recorto todos los presupuestos un 20% por igual, sin analizar el impacto."},
{"level":4,"q":"La clínica recibe una propuesta que promete ingresos importantes, pero implica riesgos y compromisos. ¿Qué hacés?","good":"Evalúo rentabilidad, riesgos, capacidad operativa, impacto institucional y condiciones antes de tomar la decisión.","bad":"La acepto porque promete muchos ingresos y después vemos cómo implementarla."},
{"level":4,"q":"La organización enfrenta un cambio importante y hay incertidumbre entre los equipos. ¿Qué debe hacer el CEO?","good":"Definir rumbo y prioridades, comunicar con claridad, escuchar inquietudes y alinear a los líderes para ejecutar el cambio.","bad":"Anunciar el cambio y dejar que cada sector interprete qué tiene que hacer."}
]
def get_state(): return json.loads(json.dumps(STATE))
def selected_team():
    return next((t for t in STATE["teams"] if t["id"]==STATE["selected"]),None)
def act(a,d):
    global QUESTIONS
    if a=="updateQuestionBank":
        incoming=d.get("questions",[])
        if not isinstance(incoming,list) or len(incoming)>500:
            return "El banco de preguntas no es válido (máximo 500 preguntas)."
        cleaned=[]
        for item in incoming:
            if not isinstance(item,dict): continue
            try: level=int(item.get("level",-1))
            except (TypeError,ValueError): continue
            q=str(item.get("q","")).strip()[:1200]
            option_a=str(item.get("good",item.get("optionA",""))).strip()[:1200]
            option_b=str(item.get("bad",item.get("optionB",""))).strip()[:1200]
            if level in range(5) and q and option_a and option_b:
                cleaned.append({"level":level,"q":q,"good":option_a,"bad":option_b})
        if not cleaned: return "El banco debe tener al menos una pregunta completa."
        QUESTIONS=cleaned
        STATE["used"]=[]
        return f"Banco actualizado: {len(QUESTIONS)} preguntas."
    if a=="addTeam":
        name=str(d.get("name","Participante")).strip()[:28]
        if not name: return "Escribí el nombre del participante."
        if len(STATE["teams"])>=4: return "Máximo 4 participantes."
        participant={"id":uuid.uuid4().hex[:8],"name":name,"level":0,"color":len(STATE["teams"])}
        STATE["teams"].append(participant);STATE["selected"]=participant["id"]
        return f"Participante {name} agregado."
    if a=="selectTeam":
        if any(t["id"]==d.get("id") for t in STATE["teams"]): STATE["selected"]=d["id"]
        return "Participante seleccionado."
    if a=="draw":
        t=selected_team()
        if not t: return "Primero agregá y elegí un participante."
        if t["level"]>=4: return "Este participante ya llegó a la cima."
        pool=[q for q in QUESTIONS if q["level"]==t["level"] and q not in STATE["used"]]
        if not pool:
            STATE["used"]=[q for q in STATE["used"] if q["level"]!=t["level"]]
            pool=[q for q in QUESTIONS if q["level"]==t["level"]]
        if not pool: return f"No hay preguntas cargadas para el nivel {LEVELS[t['level']]}."
        q=random.choice(pool);STATE["used"].append(q)
        STATE["current"]=dict(q,teamName=t["name"],teamId=t["id"],selectedChoice=None)
        return f"Pregunta para {t['name']}."
    if a=="answerChoice":
        t=selected_team()
        if not t: return "Elegí un participante."
        current=STATE["current"]
        if not current: return "Primero sacá una pregunta."
        if current.get("teamId")!=t["id"]: return "La pregunta corresponde a otro participante. Seleccioná a quien está jugando."
        choice=str(d.get("choice","")).upper()
        if choice not in ("A","B"): return "Elegí la opción A o B."
        current["selectedChoice"]=choice
        return f"{t['name']} eligió la opción {choice}. Ahora indicá si la respuesta fue correcta o incorrecta."
    if a=="answer":
        t=selected_team()
        if not t: return "Elegí un participante."
        current=STATE["current"]
        if not current: return "Primero sacá una pregunta."
        if current.get("teamId")!=t["id"]: return "La pregunta corresponde a otro participante. Seleccioná a quien está jugando."
        if current.get("selectedChoice") not in ("A","B"): return "Primero registrá si eligió A o B."
        if bool(d.get("correct")):
            t["level"]=min(4,t["level"]+1)
            result_type="winner" if t["level"]>=4 else "correct"
            msg=(f"¡{t['name']} es el nuevo CEO de la clínica! ¡Felicitaciones, a brindar!"
                 if result_type=="winner" else f"¡Correcto! {t['name']} sube a {LEVELS[t['level']]}." )
        else:
            result_type="wrong"
            msg=f"Incorrecto. {t['name']} se queda en {LEVELS[t['level']]}."
        STATE["lastResult"]={"type":result_type,"teamName":t["name"],"teamId":t["id"],
                             "eventId":uuid.uuid4().hex,"selectedChoice":current.get("selectedChoice")}
        STATE["current"]=None
        return msg
    if a=="reset":
        STATE.update({"teams":[],"selected":None,"current":None,"used":[],"lastResult":None})
        return "Partida reiniciada."
    return "Acción no reconocida."
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        p=urlparse(self.path)
        if p.path=="/api/state":
            self.send_json(get_state());return
        if p.path=="/":
            path=os.path.join(ROOT,"index.html")
        elif p.path=="/controller":
            path=os.path.join(ROOT,"index.html")
            self.send_response(302);self.send_header("Location","/?mode=controller");self.end_headers();return
        else:
            path=os.path.join(ROOT,p.path.lstrip("/"))
        if not os.path.isfile(path):
            self.send_error(404);return
        self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.end_headers()
        with open(path,"rb") as f:self.wfile.write(f.read())
    def do_POST(self):
        if self.path!="/api/action":self.send_error(404);return
        length=int(self.headers.get("Content-Length","0"))
        try:
            d=json.loads(self.rfile.read(length).decode("utf-8"))
            message=act(d.get("action"),d)
            self.send_json({"state":get_state(),"message":message})
        except Exception as e:self.send_json({"error":str(e)},500)
    def send_json(self,obj,status=200):
        raw=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(status);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Access-Control-Allow-Origin","*");self.send_header("Content-Length",str(len(raw)));self.end_headers();self.wfile.write(raw)
    def log_message(self,*args): pass
def local_ips():
    ips=set()
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(("8.8.8.8",80));ips.add(s.getsockname()[0]);s.close()
    except: pass
    return sorted(ips)
if __name__=="__main__":
    server=ThreadingHTTPServer(("0.0.0.0",8000),Handler)
    print("\n🏔️ LA ESCALERA DEL LIDERAZGO")
    print("En la computadora: http://localhost:8000")
    for ip in local_ips(): print("En la tablet (misma Wi-Fi): http://%s:8000/?mode=controller"%ip)
    print("\nDejá esta ventana abierta durante el juego. Ctrl+C para cerrar.\n")
    server.serve_forever()
