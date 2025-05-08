from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import datetime

app = Flask(__name__)
CORS(app)  # Esto permite peticiones desde otros dominios (útil para desarrollo)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista para almacenar el historial de operaciones
historial_operaciones = []

# Clase de calculadora 
class Calculadora:
    def suma(self, a, b):
        logger.info(f"Servidor: Calculando suma de {a} + {b}")
        resultado = a + b
        self.registrar_operacion("suma", a, b, resultado)
        return resultado
    
    def resta(self, a, b):
        logger.info(f"Servidor: Calculando resta de {a} - {b}")
        resultado = a - b
        self.registrar_operacion("resta", a, b, resultado)
        return resultado
    
    def multiplicacion(self, a, b):
        logger.info(f"Servidor: Calculando multiplicación de {a} * {b}")
        resultado = a * b
        self.registrar_operacion("multiplicacion", a, b, resultado)
        return resultado
    
    def division(self, a, b):
        logger.info(f"Servidor: Calculando división de {a} / {b}")
        if b == 0:
            return "Error: División por cero"
        resultado = a / b
        self.registrar_operacion("division", a, b, resultado)
        return resultado
    
    def registrar_operacion(self, operacion, a, b, resultado):
        """Registra una operación en el historial"""
        historial_operaciones.append({
            'operacion': operacion,
            'num1': a,
            'num2': b,
            'resultado': resultado,
            'fecha': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # Mantener solo las últimas 10 operaciones
        if len(historial_operaciones) > 10:
            historial_operaciones.pop(0)

# Creamos una instancia de la calculadora
calculadora = Calculadora()

# Ruta principal - Sirve la interfaz de usuario
@app.route('/')
def index():
    return render_template('index.html')

# API para realizar operaciones
@app.route('/api/calcular', methods=['POST'])
def calcular():
    try:
        # Obtenemos los datos de la solicitud
        data = request.json
        operacion = data.get('operacion')
        num1 = float(data.get('num1', 0))
        num2 = float(data.get('num2', 0))
        
        # Realizamos la operación solicitada
        if operacion == 'suma':
            resultado = calculadora.suma(num1, num2)
        elif operacion == 'resta':
            resultado = calculadora.resta(num1, num2)
        elif operacion == 'multiplicacion':
            resultado = calculadora.multiplicacion(num1, num2)
        elif operacion == 'division':
            resultado = calculadora.division(num1, num2)
        else:
            return jsonify({'error': 'Operación no válida'}), 400
        
        # Devolvemos el resultado
        return jsonify({
            'resultado': resultado,
            'operacion': operacion,
            'num1': num1,
            'num2': num2
        })
    
    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API para obtener el historial
@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    return jsonify(historial_operaciones)

# Ejecutar la aplicación
if __name__ == '__main__':
    logger.info("Iniciando servidor de calculadora RMI web...")
    app.run(host='0.0.0.0', port=5000, debug=True)