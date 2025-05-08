from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import datetime
import math
import random
import statistics
import numpy as np
from decimal import Decimal, getcontext

app = Flask(__name__)
CORS(app)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Aumentar precisión para cálculos financieros
getcontext().prec = 28

# Lista para almacenar el historial de operaciones
historial_operaciones = []

# Constantes matemáticas
CONSTANTES = {
    "pi": math.pi,
    "e": math.e,
    "phi": (1 + math.sqrt(5)) / 2,  # Número áureo
    "gamma": 0.57721566490153286060,  # Constante de Euler-Mascheroni
}

# Clase de calculadora científica avanzada
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
        try:
            resultado = a ** b
            self.registrar_operacion("potencia", a, b, resultado)
            return resultado
        except OverflowError:
            return "Error: Resultado demasiado grande"
        
    def raiz(self, a, b=2):
        logger.info(f"Servidor: Calculando raíz {b}-ésima de {a}")
        if a < 0 and b % 2 == 0:
            return "Error: Raíz par de número negativo"
        try:
            resultado = a ** (1/b) if a >= 0 else -(-a) ** (1/b)
            self.registrar_operacion("raiz", a, b, resultado)
            return resultado
        except:
            return "Error: Operación no válida"
    
    def logaritmo(self, a, b=10):
        logger.info(f"Servidor: Calculando logaritmo base {b} de {a}")
        if a <= 0 or (b <= 0 or b == 1):
            return "Error: Valores no válidos para logaritmo"
        resultado = math.log(a, b)
        self.registrar_operacion("logaritmo", a, b, resultado)
        return resultado
    
    def logaritmo_natural(self, a):
        logger.info(f"Servidor: Calculando logaritmo natural de {a}")
        if a <= 0:
            return "Error: Logaritmo natural no definido para valores ≤ 0"
        resultado = math.log(a)
        self.registrar_operacion_unaria("ln", a, resultado)
        return resultado
    
    def logaritmo_base10(self, a):
        logger.info(f"Servidor: Calculando logaritmo base 10 de {a}")
        if a <= 0:
            return "Error: Logaritmo no definido para valores ≤ 0"
        resultado = math.log10(a)
        self.registrar_operacion_unaria("log10", a, resultado)
        return resultado
    
    def seno(self, a, en_radianes=True):
        logger.info(f"Servidor: Calculando seno de {a} {'radianes' if en_radianes else 'grados'}")
        valor = a if en_radianes else math.radians(a)
        resultado = math.sin(valor)
        self.registrar_operacion_unaria("seno", a, resultado, en_radianes)
        return resultado
    
    def coseno(self, a, en_radianes=True):
        logger.info(f"Servidor: Calculando coseno de {a} {'radianes' if en_radianes else 'grados'}")
        valor = a if en_radianes else math.radians(a)
        resultado = math.cos(valor)
        self.registrar_operacion_unaria("coseno", a, resultado, en_radianes)
        return resultado
    
    def tangente(self, a, en_radianes=True):
        logger.info(f"Servidor: Calculando tangente de {a} {'radianes' if en_radianes else 'grados'}")
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
    
    def arcotangente2(self, y, x, en_radianes=True):
        logger.info(f"Servidor: Calculando arcotangente2 de y={y}, x={x}")
        resultado = math.atan2(y, x)
        if not en_radianes:
            resultado = math.degrees(resultado)
        self.registrar_operacion("arcotangente2", y, x, resultado, {"en_radianes": en_radianes})
        return resultado
    
    def seno_hiperbolico(self, a):
        logger.info(f"Servidor: Calculando seno hiperbólico de {a}")
        resultado = math.sinh(a)
        self.registrar_operacion_unaria("senh", a, resultado)
        return resultado
    
    def coseno_hiperbolico(self, a):
        logger.info(f"Servidor: Calculando coseno hiperbólico de {a}")
        resultado = math.cosh(a)
        self.registrar_operacion_unaria("cosh", a, resultado)
        return resultado
    
    def tangente_hiperbolica(self, a):
        logger.info(f"Servidor: Calculando tangente hiperbólica de {a}")
        resultado = math.tanh(a)
        self.registrar_operacion_unaria("tanh", a, resultado)
        return resultado
    
    def arcoseno_hiperbolico(self, a):
        logger.info(f"Servidor: Calculando arcoseno hiperbólico de {a}")
        resultado = math.asinh(a)
        self.registrar_operacion_unaria("arcsenh", a, resultado)
        return resultado
    
    def arcocoseno_hiperbolico(self, a):
        logger.info(f"Servidor: Calculando arcocoseno hiperbólico de {a}")
        if a < 1:
            return "Error: Valor fuera del rango [1, ∞)"
        resultado = math.acosh(a)
        self.registrar_operacion_unaria("arccosh", a, resultado)
        return resultado
    
    def arcotangente_hiperbolica(self, a):
        logger.info(f"Servidor: Calculando arcotangente hiperbólica de {a}")
        if a <= -1 or a >= 1:
            return "Error: Valor fuera del rango (-1, 1)"
        resultado = math.atanh(a)
        self.registrar_operacion_unaria("arctanh", a, resultado)
        return resultado
    
    def factorial(self, a):
        logger.info(f"Servidor: Calculando factorial de {a}")
        if a < 0 or not a.is_integer():
            return "Error: Factorial requiere un entero no negativo"
        try:
            a = int(a)
            resultado = math.factorial(a)
            self.registrar_operacion_unaria("factorial", a, resultado)
            return resultado
        except OverflowError:
            return "Error: Resultado demasiado grande"
    
    def modulo(self, a, b):
        logger.info(f"Servidor: Calculando {a} mod {b}")
        if b == 0:
            return "Error: Módulo por cero"
        resultado = a % b
        self.registrar_operacion("modulo", a, b, resultado)
        return resultado
    
    def valor_absoluto(self, a):
        logger.info(f"Servidor: Calculando valor absoluto de {a}")
        resultado = abs(a)
        self.registrar_operacion_unaria("abs", a, resultado)
        return resultado
    
    def signo(self, a):
        logger.info(f"Servidor: Calculando signo de {a}")
        resultado = 0 if a == 0 else (1 if a > 0 else -1)
        self.registrar_operacion_unaria("signo", a, resultado)
        return resultado
    
    def piso(self, a):
        logger.info(f"Servidor: Calculando función piso de {a}")
        resultado = math.floor(a)
        self.registrar_operacion_unaria("piso", a, resultado)
        return resultado
    
    def techo(self, a):
        logger.info(f"Servidor: Calculando función techo de {a}")
        resultado = math.ceil(a)
        self.registrar_operacion_unaria("techo", a, resultado)
        return resultado
    
    def redondear(self, a, decimales=0):
        logger.info(f"Servidor: Redondeando {a} a {decimales} decimales")
        resultado = round(a, int(decimales))
        self.registrar_operacion("redondear", a, decimales, resultado)
        return resultado
    
    def exponencial(self, a):
        logger.info(f"Servidor: Calculando e^{a}")
        try:
            resultado = math.exp(a)
            self.registrar_operacion_unaria("exp", a, resultado)
            return resultado
        except OverflowError:
            return "Error: Resultado demasiado grande"
    
    def potencia_10(self, a):
        logger.info(f"Servidor: Calculando 10^{a}")
        try:
            resultado = 10 ** a
            self.registrar_operacion_unaria("10^x", a, resultado)
            return resultado
        except OverflowError:
            return "Error: Resultado demasiado grande"
    
    def reciproco(self, a):
        logger.info(f"Servidor: Calculando 1/{a}")
        if a == 0:
            return "Error: División por cero"
        resultado = 1 / a
        self.registrar_operacion_unaria("1/x", a, resultado)
        return resultado
    
    def porcentaje(self, a, b):
        logger.info(f"Servidor: Calculando {a}% de {b}")
        resultado = (a / 100) * b
        self.registrar_operacion("porcentaje", a, b, resultado)
        return resultado
    
    def cambio_porcentual(self, a, b):
        logger.info(f"Servidor: Calculando cambio porcentual de {a} a {b}")
        if a == 0:
            return "Error: Valor inicial no puede ser cero"
        resultado = ((b - a) / a) * 100
        self.registrar_operacion("cambio_porcentual", a, b, resultado)
        return resultado
    
    def grados_a_radianes(self, a):
        logger.info(f"Servidor: Convirtiendo {a} grados a radianes")
        resultado = math.radians(a)
        self.registrar_operacion_unaria("grados_a_radianes", a, resultado)
        return resultado
    
    def radianes_a_grados(self, a):
        logger.info(f"Servidor: Convirtiendo {a} radianes a grados")
        resultado = math.degrees(a)
        self.registrar_operacion_unaria("radianes_a_grados", a, resultado)
        return resultado
    
    def grados_a_grad(self, a):
        logger.info(f"Servidor: Convirtiendo {a} grados a gradián")
        resultado = a * (10/9)
        self.registrar_operacion_unaria("grados_a_grad", a, resultado)
        return resultado
    
    def grad_a_grados(self, a):
        logger.info(f"Servidor: Convirtiendo {a} gradián a grados")
        resultado = a * (9/10)
        self.registrar_operacion_unaria("grad_a_grados", a, resultado)
        return resultado
    
    def fraccion_a_decimal(self, a, b):
        logger.info(f"Servidor: Convirtiendo {a}/{b} a decimal")
        if b == 0:
            return "Error: Denominador no puede ser cero"
        resultado = a / b
        self.registrar_operacion("fraccion_a_decimal", a, b, resultado)
        return resultado
    
    def decimal_a_fraccion(self, a, precision=1e-10):
        logger.info(f"Servidor: Convirtiendo {a} a fracción")
        try:
            from fractions import Fraction
            fraccion = Fraction(a).limit_denominator(int(1/precision))
            numerador = fraccion.numerator
            denominador = fraccion.denominator
            self.registrar_operacion_unaria("decimal_a_fraccion", a, f"{numerador}/{denominador}")
            return {
                "numerador": numerador,
                "denominador": denominador,
                "fraccion": f"{numerador}/{denominador}"
            }
        except:
            return "Error: No se pudo convertir a fracción"
    
    def parte_entera(self, a):
        logger.info(f"Servidor: Extrayendo parte entera de {a}")
        resultado = math.trunc(a)
        self.registrar_operacion_unaria("parte_entera", a, resultado)
        return resultado
    
    def parte_decimal(self, a):
        logger.info(f"Servidor: Extrayendo parte decimal de {a}")
        resultado = a - math.trunc(a)
        self.registrar_operacion_unaria("parte_decimal", a, resultado)
        return resultado
    
    def aleatorio(self, a=0, b=1):
        logger.info(f"Servidor: Generando número aleatorio entre {a} y {b}")
        resultado = random.uniform(a, b)
        self.registrar_operacion("aleatorio", a, b, resultado)
        return resultado
    
    def combinatoria(self, n, k):
        logger.info(f"Servidor: Calculando combinatoria C({n},{k})")
        if n < 0 or k < 0 or not n.is_integer() or not k.is_integer():
            return "Error: Se requieren enteros no negativos"
        try:
            n, k = int(n), int(k)
            if k > n:
                return "Error: k no puede ser mayor que n"
            resultado = math.comb(n, k)
            self.registrar_operacion("combinatoria", n, k, resultado)
            return resultado
        except OverflowError:
            return "Error: Resultado demasiado grande"
    
    def permutacion(self, n, k):
        logger.info(f"Servidor: Calculando permutación P({n},{k})")
        if n < 0 or k < 0 or not n.is_integer() or not k.is_integer():
            return "Error: Se requieren enteros no negativos"
        try:
            n, k = int(n), int(k)
            if k > n:
                return "Error: k no puede ser mayor que n"
            resultado = math.perm(n, k)
            self.registrar_operacion("permutacion", n, k, resultado)
            return resultado
        except OverflowError:
            return "Error: Resultado demasiado grande"
    
    def media(self, valores):
        logger.info(f"Servidor: Calculando media de {valores}")
        if not valores:
            return "Error: Lista vacía"
        resultado = statistics.mean(valores)
        self.registrar_operacion_especial("media", valores, resultado)
        return resultado
    
    def mediana(self, valores):
        logger.info(f"Servidor: Calculando mediana de {valores}")
        if not valores:
            return "Error: Lista vacía"
        resultado = statistics.median(valores)
        self.registrar_operacion_especial("mediana", valores, resultado)
        return resultado
    
    def moda(self, valores):
        logger.info(f"Servidor: Calculando moda de {valores}")
        if not valores:
            return "Error: Lista vacía"
        try:
            resultado = statistics.mode(valores)
            self.registrar_operacion_especial("moda", valores, resultado)
            return resultado
        except statistics.StatisticsError:
            return "Error: No hay moda única"
    
    def desviacion_estandar(self, valores, poblacion=True):
        logger.info(f"Servidor: Calculando desviación estándar de {valores}")
        if not valores or len(valores) < 2:
            return "Error: Se requieren al menos 2 valores"
        if poblacion:
            resultado = statistics.pstdev(valores)
        else:
            resultado = statistics.stdev(valores)
        tipo = "poblacional" if poblacion else "muestral"
        self.registrar_operacion_especial(f"desviacion_estandar_{tipo}", valores, resultado)
        return resultado
    
    def varianza(self, valores, poblacion=True):
        logger.info(f"Servidor: Calculando varianza de {valores}")
        if not valores or len(valores) < 2:
            return "Error: Se requieren al menos 2 valores"
        if poblacion:
            resultado = statistics.pvariance(valores)
        else:
            resultado = statistics.variance(valores)
        tipo = "poblacional" if poblacion else "muestral"
        self.registrar_operacion_especial(f"varianza_{tipo}", valores, resultado)
        return resultado
    
    def notacion_cientifica(self, a):
        logger.info(f"Servidor: Convirtiendo {a} a notación científica")
        if a == 0:
            return {"coeficiente": 0, "exponente": 0, "notacion": "0×10^0"}
        
        exponente = math.floor(math.log10(abs(a)))
        coeficiente = a / (10 ** exponente)
        notacion = f"{coeficiente}×10^{exponente}"
        
        resultado = {
            "coeficiente": coeficiente,
            "exponente": exponente,
            "notacion": notacion
        }
        
        self.registrar_operacion_unaria("notacion_cientifica", a, notacion)
        return resultado
    
    def interes_simple(self, principal, tasa, tiempo):
        logger.info(f"Servidor: Calculando interés simple: Principal={principal}, Tasa={tasa}%, Tiempo={tiempo}")
        if principal < 0 or tasa < 0 or tiempo < 0:
            return "Error: Los valores deben ser no negativos"
        
        tasa_decimal = tasa / 100
        interes = principal * tasa_decimal * tiempo
        monto_final = principal + interes
        
        resultado = {
            "interes": interes,
            "monto_final": monto_final
        }
        
        self.registrar_operacion_financiera("interes_simple", principal, tasa, tiempo, resultado)
        return resultado
    
    def interes_compuesto(self, principal, tasa, tiempo, periodos=1):
        logger.info(f"Servidor: Calculando interés compuesto: Principal={principal}, Tasa={tasa}%, Tiempo={tiempo}, Periodos={periodos}")
        if principal < 0 or tasa < 0 or tiempo < 0 or periodos <= 0:
            return "Error: Los valores deben ser no negativos y periodos > 0"
        
        tasa_decimal = tasa / 100
        tasa_por_periodo = tasa_decimal / periodos
        periodos_totales = tiempo * periodos
        
        monto_final = principal * (1 + tasa_por_periodo) ** periodos_totales
        interes = monto_final - principal
        
        resultado = {
            "interes": interes,
            "monto_final": monto_final
        }
        
        datos_extra = {"periodos_capitalizacion": periodos}
        self.registrar_operacion_financiera("interes_compuesto", principal, tasa, tiempo, resultado, datos_extra)
        return resultado
    
    def registrar_operacion(self, operacion, a, b, resultado, datos_extra=None):
        """Registra una operación binaria en el historial"""
        entrada = {
            'operacion': operacion,
            'num1': a,
            'num2': b,
            'resultado': resultado,
            'fecha': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if datos_extra:
            entrada.update(datos_extra)
            
        historial_operaciones.append(entrada)
        
        # Mantener solo las últimas 30 operaciones
        if len(historial_operaciones) > 30:
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
        
        # Mantener solo las últimas 30 operaciones
        if len(historial_operaciones) > 30:
            historial_operaciones.pop(0)
    
    def registrar_operacion_especial(self, operacion, valores, resultado):
        """Registra una operación con múltiples valores de entrada"""
        entrada = {
            'operacion': operacion,
            'valores': valores,
            'resultado': resultado,
            'fecha': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        historial_operaciones.append(entrada)
        
        # Mantener solo las últimas 30 operaciones
        if len(historial_operaciones) > 30:
            historial_operaciones.pop(0)
    
    def registrar_operacion_financiera(self, operacion, principal, tasa, tiempo, resultado, datos_extra=None):
        """Registra una operación financiera en el historial"""
        entrada = {
            'operacion': operacion,
            'principal': principal,
            'tasa': tasa,
            'tiempo': tiempo,
            'resultado': resultado,
            'fecha': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if datos_extra:
            entrada.update(datos_extra)
            
        historial_operaciones.append(entrada)
        
        # Mantener solo las últimas 30 operaciones
        if len(historial_operaciones) > 30:
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
        
        # Obtenemos los parámetros según el tipo de operación
        if operacion in ['media', 'mediana', 'moda', 'desviacion_estandar', 'varianza']:
            valores = data.get('valores', [])
            poblacion = data.get('poblacion', True)
            
            # Realizar operación estadística
            if operacion == 'media':
                resultado = calculadora.media(valores)
            elif operacion == 'mediana':
                resultado = calculadora.mediana(valores)
            elif operacion == 'moda':
                resultado = calculadora.moda(valores)
            elif operacion == 'desviacion_estandar':
                resultado = calculadora.desviacion_estandar(valores, poblacion)
            elif operacion == 'varianza':
                resultado = calculadora.varianza(valores, poblacion)
                
            return jsonify({
                'resultado': resultado,
                'operacion': operacion,
                'valores': valores
            })
        
        elif operacion in ['interes_simple', 'interes_compuesto']:
            principal = float(data.get('principal', 0))
            tasa = float(data.get('tasa', 0))
            tiempo = float(data.get('tiempo', 0))
            
            if operacion == 'interes_simple':
                resultado = calculadora.interes_simple(principal, tasa, tiempo)
            else:  # interes_compuesto
                periodos = int(data.get('periodos', 1))
                resultado = calculadora.interes_compuesto(principal, tasa, tiempo, periodos)
                
            return jsonify({
                'resultado': resultado,
                'operacion': operacion,
                'principal': principal,
                'tasa': tasa,
                'tiempo': tiempo
            })
        
        else:  # Operaciones normales (unarias o binarias)
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
            elif operacion == 'logaritmo_natural':
                resultado = calculadora.logaritmo_natural(num1)
            elif operacion == 'logaritmo_base10':
                resultado = calculadora.logaritmo_base10(num1)
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
            elif operacion == 'arcotangente2':
                resultado = calculadora.arcotangente2(num1, num2, en_radianes)
            elif operacion == 'seno_hiperbolico':
                resultado = calculadora.seno_hiperbolico(num1)
            elif operacion == 'coseno_hiperbolico':
                resultado = calculadora.coseno_hiperbolico(num1)
            elif operacion == 'tangente_hiperbolica':
                resultado = calculadora.tangente_hiperbolica(num1)
            elif operacion == 'arcoseno_hiperbolico':
                resultado = calculadora.arcoseno_hiperbolico(num1)
            elif operacion == 'arcocoseno_hiperbolico':
                resultado = calculadora.arcocoseno_hiperbolico(num1)
            elif operacion == 'arcotangente_hiperbolica':
                resultado = calculadora.arcotangente_hiperbolica(num1)
            elif operacion == 'factorial':
                resultado = calculadora.factorial(num1)
            elif operacion == 'modulo':
                resultado = calculadora.modulo(num1, num2)
            elif operacion == 'valor_absoluto':
                resultado = calculadora.valor_absoluto(num1)
            elif operacion == 'signo':
                resultado = calculadora.signo(num1)
            elif operacion == 'piso':
                resultado = calculadora.piso(num1)
            elif operacion == 'techo':
                resultado = calculadora.techo(num1)
            elif operacion == 'redondear':
                resultado = calculadora.redondear(num1, num2 if num2 is not None else 0)
            elif operacion == 'exponencial':
                resultado = calculadora.exponencial(num1)
            elif operacion == 'potencia_10':
                resultado = calculadora.potencia_10(num1)
            elif operacion == 'reciproco':
                resultado = calculadora.reciproco(num1)
            elif operacion == 'porcentaje':
                resultado = calculadora.porcentaje(num1, num2)
            elif operacion == 'cambio_porcentual':
                resultado = calculadora.cambio_porcentual(num1, num2)
            elif operacion == 'grados_a_radianes':
                resultado = calculadora.grados_a_radianes(num1)
            elif operacion == 'radianes_a_grados':
                resultado = calculadora.radianes_a_grados(num1)
            elif operacion == 'grados_a_grad':
                resultado = calculadora.grados_a_grad(num1)
            elif operacion == 'grad_a_grados':
                resultado = calculadora.grad_a_grados(num1)
            elif operacion == 'fraccion_a_decimal':
                resultado = calculadora.fraccion_a_decimal(num1, num2)
            elif operacion == 'decimal_a_fraccion':
                precision = float(data.get('precision', 1e-10))
                resultado = calculadora.decimal_a_fraccion(num1, precision)
            elif operacion == 'parte_entera':
                resultado = calculadora.parte_entera(num1)
            elif operacion == 'parte_decimal':
                resultado = calculadora.parte_decimal(num1)
            elif operacion == 'aleatorio':
                resultado = calculadora.aleatorio(num1, num2 if num2 is not None else 1)
            elif operacion == 'combinatoria':
                resultado = calculadora.combinatoria(num1, num2)
            elif operacion == 'permutacion':
                resultado = calculadora.permutacion(num1, num2)
            elif operacion == 'notacion_cientifica':
                resultado = calculadora.notacion_cientifica(num1)
            elif operacion == 'constante':
                constante = data.get('constante', 'pi')
                if constante in CONSTANTES:
                    resultado = CONSTANTES[constante]
                else:
                    return jsonify({'error': 'Constante no disponible'}), 400
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
                
            if operacion in ['seno', 'coseno', 'tangente', 'arcoseno', 'arcocoseno', 'arcotangente', 'arcotangente2']:
                respuesta['en_radianes'] = en_radianes
                
            return jsonify(respuesta)
        
    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API para obtener el historial
@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    return jsonify(historial_operaciones)

# API para obtener constantes disponibles
@app.route('/api/constantes', methods=['GET'])
def obtener_constantes():
    return jsonify(CONSTANTES)

# Ejecutar la aplicación
if __name__ == '__main__':
    logger.info("Iniciando servidor de calculadora científica RMI web...")
    app.run(host='0.0.0.0', port=5000, debug=True)