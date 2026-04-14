from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

class RobotCartesiano:
    def __init__(self):
        self.Z_SAFE = 80
        self.WORKSPACE = {'X': (0, 500), 'Y': (0, 500)}
        self.pos_actual = {'X': 250, 'Y': 0, 'Z': self.Z_SAFE}
        self.e_stop = False

    def trayectoria_segura(self, x_dest, y_dest):
        if self.e_stop: raise Exception("E-STOP ACTIVO")
        # Abstracción de pasos requeridos
        pasos = [
            {"accion": "subir_z", "z": self.Z_SAFE},
            {"accion": "trasladar", "x": x_dest, "y": y_dest},
            {"accion": "bajar_z", "z": 10},
            {"accion": "soltar", "estado": "abierto"}
        ]
        self.pos_actual = {'X': x_dest, 'Y': y_dest, 'Z': 10}
        return pasos

robot = RobotCartesiano()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clasificar', methods=['POST'])
def clasificar():
    if robot.e_stop: return jsonify({"error": "SISTEMA BLOQUEADO"}), 403
    
    data = request.json
    tipo = data.get('sensor')
    
    # TUS COORDENADAS EXACTAS
    destino = {'X': 0, 'Y': 500} if tipo == "DEFECTO" else {'X': 500, 'Y': 500}
    
    try:
        pasos = robot.trayectoria_segura(destino['X'], destino['Y'])
        return jsonify({"status": "OK", "destino": destino, "pasos": pasos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/emergencia', methods=['POST'])
def emergencia():
    robot.e_stop = True
    return jsonify({"status": "STOP"})

if __name__ == '__main__':
    app.run(debug=True)