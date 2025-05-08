from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import datetime
import math

app = Flask(__name__)
CORS(app)  # Esto permite peticiones desde otros dominios (útil para desarrollo)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista para almacenar el historial de operaciones
historial_operaciones = []

# Clase de calculadora científica
class CalculadoraCientifica:
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
    
    def potencia(self, a, b):
        logger.info(f"Servidor: Calculando potencia de {a} ^ {b}")
        resultado = a ** b
        self.registrar_operacion("potencia", a, b, resultado)
        return resultado
        
    def raiz(self, a, b=2):
        logger.info(f"Servidor: Calculando raíz {b}-ésima de {a}")
        if a < 0 and b % 2 == 0:
            return "Error: Raíz par de número negativo"
        resultado = a ** (1/b) if a >= 0 else -(-a) ** (1/b)
        self.registrar_operacion("raiz", a, b, resultado)
        return resultado
    
    def logaritmo(self, a, b=10):
        logger.info(f"Servidor: Calculando logaritmo base {b} de {a}")
        if a <= 0 or (b <= 0 or b == 1):
            return "Error: Valores no válidos para logaritmo"
        resultado = math.log(a, b)
        self.registrar_operacion("logaritmo", a, b, resultado)
        return resultado
    
    def seno(self, a, en_radianes=True):
        logger.info(f"Servidor: Calculando seno de {a}")
        valor = a if en_radianes else math.radians(a)
        resultado = math.sin(valor)
        self.registrar_operacion_unaria("seno", a, resultado, en_radianes)
        return resultado
    
    def coseno(self, a, en_radianes=True):
        logger.info(f"Servidor: Calculando coseno de {a}")
        valor = a if en_radianes else math.radians(a)
        resultado = math.cos(valor)
        self.registrar_operacion_unaria("coseno", a, resultado, en_radianes)
        return resultado
    
    def tangente(self, a, en_radianes=True):
        logger.info(f"Servidor: Calculando tangente de {a}")
        valor = a if en_radianes else math.radians(a)
        if abs(math.cos(valor)) < 1e-10:
            return "Error: Tangente indefinida"
        resultado = math.tan(valor)
        self.registrar_operacion_unaria("tangente", a, resultado, en_radianes)
        return resultado
    
    def arcoseno(self, a, en_radianes=True):
        logger.info(f"Servidor: Calculando arcoseno de {a}")
        if a < -1 or a > 1:
            return "Error: Valor fuera del rango [-1, 1]"
        resultado = math.asin(a)
        if not en_radianes:
            resultado = math.degrees(resultado)
        self.registrar_operacion_unaria("arcoseno", a, resultado, en_radianes)
        return resultado
    
    def arcocoseno(self, a, en_radianes=True):
        logger.info(f"Servidor: Calculando arcocoseno de {a}")
        if a < -1 or a > 1:
            return "Error: Valor fuera del rango [-1, 1]"
        resultado = math.acos(a)
        if not en_radianes:
            resultado = math.degrees(resultado)
        self.registrar_operacion_unaria("arcocoseno", a, resultado, en_radianes)
        return resultado
    
    def arcotangente(self, a, en_radianes=True):
        logger.info(f"Servidor: Calculando arcotangente de {a}")
        resultado = math.atan(a)
        if not en_radianes:
            resultado = math.degrees(resultado)
        self.registrar_operacion_unaria("arcotangente", a, resultado, en_radianes)
        return resultado
    
    def factorial(self, a):
        logger.info(f"Servidor: Calculando factorial de {a}")
        if a < 0 or not a.is_integer():
            return "Error: Factorial requiere un entero no negativo"
        a = int(a)
        resultado = math.factorial(a)
        self.registrar_operacion_unaria("factorial", a, resultado)
        return resultado
    
    def registrar_operacion(self, operacion, a, b, resultado):
        """Registra una operación binaria en el historial"""
        historial_operaciones.append({
            'operacion': operacion,
            'num1': a,
            'num2': b,
            'resultado': resultado,
            'fecha': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # Mantener solo las últimas 20 operaciones
        if len(historial_operaciones) > 20:
            historial_operaciones.pop(0)
    
    def registrar_operacion_unaria(self, operacion, a, resultado, en_radianes=None):
        """Registra una operación unaria en el historial"""
        entrada = {
            'operacion': operacion,
            'num1': a,
            'resultado': resultado,
            'fecha': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if en_radianes is not None:
            entrada['en_radianes'] = en_radianes
            
        historial_operaciones.append(entrada)
        
        # Mantener solo las últimas 20 operaciones
        if len(historial_operaciones) > 20:
            historial_operaciones.pop(0)

# Creamos una instancia de la calculadora
calculadora = CalculadoraCientifica()

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
        num2 = float(data.get('num2', 0)) if 'num2' in data else None
        en_radianes = data.get('en_radianes', True)
        
        # Realizamos la operación solicitada
        if operacion == 'suma':
            resultado = calculadora.suma(num1, num2)
        elif operacion == 'resta':
            resultado = calculadora.resta(num1, num2)
        elif operacion == 'multiplicacion':
            resultado = calculadora.multiplicacion(num1, num2)
        elif operacion == 'division':
            resultado = calculadora.division(num1, num2)
        elif operacion == 'potencia':
            resultado = calculadora.potencia(num1, num2)
        elif operacion == 'raiz':
            resultado = calculadora.raiz(num1, num2 if num2 is not None else 2)
        elif operacion == 'logaritmo':
            resultado = calculadora.logaritmo(num1, num2 if num2 is not None else 10)
        elif operacion == 'seno':
            resultado = calculadora.seno(num1, en_radianes)
        elif operacion == 'coseno':
            resultado = calculadora.coseno(num1, en_radianes)
        elif operacion == 'tangente':
            resultado = calculadora.tangente(num1, en_radianes)
        elif operacion == 'arcoseno':
            resultado = calculadora.arcoseno(num1, en_radianes)
        elif operacion == 'arcocoseno':
            resultado = calculadora.arcocoseno(num1, en_radianes)
        elif operacion == 'arcotangente':
            resultado = calculadora.arcotangente(num1, en_radianes)
        elif operacion == 'factorial':
            resultado = calculadora.factorial(num1)
        else:
            return jsonify({'error': 'Operación no válida'}), 400
        
        # Devolvemos el resultado
        respuesta = {
            'resultado': resultado,
            'operacion': operacion,
            'num1': num1
        }
        
        if num2 is not None:
            respuesta['num2'] = num2
            
        if operacion in ['seno', 'coseno', 'tangente', 'arcoseno', 'arcocoseno', 'arcotangente']:
            respuesta['en_radianes'] = en_radianes
            
        return jsonify(respuesta)
    
    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API para obtener el historial
@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    return jsonify(historial_operaciones)

# Ejecutar la aplicación
if __name__ == '__main__':
    logger.info("Iniciando servidor de calculadora científica RMI web...")
    app.run(host='0.0.0.0', port=5000, debug=True)