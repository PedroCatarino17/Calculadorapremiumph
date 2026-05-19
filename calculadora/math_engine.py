"""
math_engine.py
Core mathematical computation engine.
Handles all calculations: basic, scientific, and financial.
"""

import math
import cmath
import json
import os
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
HISTORY_FILE = Path(__file__).parent.parent / "data" / "history.json"
HISTORY_FILE.parent.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
#  BASIC OPERATIONS
# ─────────────────────────────────────────────

def safe_eval(expression: str) -> float:
    """
    Safely evaluate a mathematical expression string.
    Supports: +, -, *, /, **, %, (, ), and math functions.
    """
    # Replace display tokens with Python equivalents
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("^", "**")
    expression = expression.replace("π", str(math.pi))
    expression = expression.replace("e", str(math.e))
    expression = expression.replace("√(", "math.sqrt(")

    # Allowed names for eval sandbox
    allowed_names = {
        "math": math,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "log": math.log10, "ln": math.log,
        "sqrt": math.sqrt, "abs": abs,
        "factorial": math.factorial,
        "exp": math.exp, "pi": math.pi, "e": math.e,
        "ceil": math.ceil, "floor": math.floor,
        "degrees": math.degrees, "radians": math.radians,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
        return float(result)
    except ZeroDivisionError:
        raise ValueError("Divisão por zero")
    except OverflowError:
        raise ValueError("Resultado muito grande")
    except Exception:
        raise ValueError("Expressão inválida")


# ─────────────────────────────────────────────
#  SCIENTIFIC FUNCTIONS
# ─────────────────────────────────────────────

class ScientificCalc:
    """Handles all scientific mathematical operations."""

    def __init__(self, angle_mode: str = "DEG"):
        self.angle_mode = angle_mode  # "DEG" or "RAD"

    def _to_rad(self, value: float) -> float:
        return math.radians(value) if self.angle_mode == "DEG" else value

    def _from_rad(self, value: float) -> float:
        return math.degrees(value) if self.angle_mode == "DEG" else value

    def sin(self, x): return math.sin(self._to_rad(x))
    def cos(self, x): return math.cos(self._to_rad(x))
    def tan(self, x):
        rad = self._to_rad(x)
        if abs(math.cos(rad)) < 1e-10:
            raise ValueError("Tangente indefinida")
        return math.tan(rad)

    def asin(self, x):
        if not -1 <= x <= 1:
            raise ValueError("Domínio: [-1, 1]")
        return self._from_rad(math.asin(x))

    def acos(self, x):
        if not -1 <= x <= 1:
            raise ValueError("Domínio: [-1, 1]")
        return self._from_rad(math.acos(x))

    def atan(self, x): return self._from_rad(math.atan(x))

    def sinh(self, x): return math.sinh(x)
    def cosh(self, x): return math.cosh(x)
    def tanh(self, x): return math.tanh(x)

    def log(self, x, base=10):
        if x <= 0:
            raise ValueError("log: x deve ser > 0")
        return math.log(x, base)

    def ln(self, x):
        if x <= 0:
            raise ValueError("ln: x deve ser > 0")
        return math.log(x)

    def sqrt(self, x):
        if x < 0:
            raise ValueError("√: x deve ser ≥ 0")
        return math.sqrt(x)

    def factorial(self, x):
        if x < 0 or x != int(x):
            raise ValueError("Fatorial: inteiro ≥ 0")
        if x > 170:
            raise ValueError("Fatorial: número muito grande")
        return math.factorial(int(x))

    def power(self, base, exp): return base ** exp
    def abs_val(self, x): return abs(x)
    def exp(self, x): return math.e ** x
    def percent(self, x): return x / 100
    def reciprocal(self, x):
        if x == 0:
            raise ValueError("1/0 indefinido")
        return 1 / x

    def to_scientific(self, x) -> str:
        return f"{x:.6e}"


# ─────────────────────────────────────────────
#  FINANCIAL CALCULATIONS
# ─────────────────────────────────────────────

class FinancialCalc:
    """Financial and business calculations."""

    @staticmethod
    def compound_interest(principal: float, rate: float, time: float, n: int = 12) -> dict:
        """
        A = P(1 + r/n)^(nt)
        Returns breakdown of compound interest calculation.
        """
        rate_dec = rate / 100
        amount = principal * (1 + rate_dec / n) ** (n * time)
        interest = amount - principal
        return {
            "principal": principal,
            "rate": rate,
            "time": time,
            "compound_freq": n,
            "final_amount": round(amount, 2),
            "interest_earned": round(interest, 2),
        }

    @staticmethod
    def simple_interest(principal: float, rate: float, time: float) -> dict:
        interest = principal * (rate / 100) * time
        return {
            "principal": principal,
            "rate": rate,
            "time": time,
            "interest": round(interest, 2),
            "total": round(principal + interest, 2),
        }

    @staticmethod
    def bmi(weight_kg: float, height_m: float) -> dict:
        if height_m <= 0 or weight_kg <= 0:
            raise ValueError("Valores inválidos")
        bmi = weight_kg / (height_m ** 2)
        if bmi < 18.5:
            category = "Abaixo do peso"
        elif bmi < 25:
            category = "Peso normal"
        elif bmi < 30:
            category = "Sobrepeso"
        elif bmi < 35:
            category = "Obesidade Grau I"
        elif bmi < 40:
            category = "Obesidade Grau II"
        else:
            category = "Obesidade Grau III"
        return {"bmi": round(bmi, 2), "category": category}

    @staticmethod
    def quadratic(a: float, b: float, c: float) -> dict:
        """Solve ax² + bx + c = 0"""
        if a == 0:
            raise ValueError("Coeficiente 'a' não pode ser zero")
        delta = b ** 2 - 4 * a * c
        if delta > 0:
            x1 = (-b + math.sqrt(delta)) / (2 * a)
            x2 = (-b - math.sqrt(delta)) / (2 * a)
            return {"delta": delta, "x1": round(x1, 6), "x2": round(x2, 6), "roots": 2}
        elif delta == 0:
            x = -b / (2 * a)
            return {"delta": delta, "x1": round(x, 6), "x2": round(x, 6), "roots": 1}
        else:
            real = -b / (2 * a)
            imag = math.sqrt(-delta) / (2 * a)
            return {
                "delta": delta,
                "x1": f"{round(real, 6)} + {round(imag, 6)}i",
                "x2": f"{round(real, 6)} - {round(imag, 6)}i",
                "roots": 0,
            }


# ─────────────────────────────────────────────
#  CONVERTERS
# ─────────────────────────────────────────────

class Converter:
    """Unit conversion utilities."""

    TEMPERATURE = {
        "C→F": lambda x: x * 9 / 5 + 32,
        "F→C": lambda x: (x - 32) * 5 / 9,
        "C→K": lambda x: x + 273.15,
        "K→C": lambda x: x - 273.15,
        "F→K": lambda x: (x - 32) * 5 / 9 + 273.15,
        "K→F": lambda x: (x - 273.15) * 9 / 5 + 32,
    }

    LENGTH = {
        "m": 1.0, "km": 1000.0, "cm": 0.01, "mm": 0.001,
        "mi": 1609.344, "yd": 0.9144, "ft": 0.3048, "in": 0.0254,
        "nmi": 1852.0,
    }

    WEIGHT = {
        "kg": 1.0, "g": 0.001, "mg": 1e-6,
        "lb": 0.453592, "oz": 0.0283495, "t": 1000.0,
    }

    AREA = {
        "m²": 1.0, "km²": 1e6, "cm²": 0.0001, "mm²": 1e-6,
        "ft²": 0.092903, "in²": 0.00064516, "ha": 10000.0, "acre": 4046.86,
    }

    VOLUME = {
        "L": 1.0, "mL": 0.001, "m³": 1000.0, "cm³": 0.001,
        "gal": 3.78541, "qt": 0.946353, "pt": 0.473176, "fl oz": 0.0295735,
    }

    SPEED = {
        "m/s": 1.0, "km/h": 1 / 3.6, "mph": 0.44704, "knot": 0.514444,
    }

    @staticmethod
    def temperature(value: float, conversion: str) -> float:
        fn = Converter.TEMPERATURE.get(conversion)
        if not fn:
            raise ValueError(f"Conversão inválida: {conversion}")
        return round(fn(value), 4)

    @staticmethod
    def convert(value: float, from_unit: str, to_unit: str, table: dict) -> float:
        if from_unit not in table or to_unit not in table:
            raise ValueError("Unidade desconhecida")
        return round(value * table[from_unit] / table[to_unit], 6)


# ─────────────────────────────────────────────
#  MEMORY SYSTEM
# ─────────────────────────────────────────────

class Memory:
    """Calculator memory (M+, M-, MR, MC)."""

    def __init__(self):
        self._value: float = 0.0

    def store(self, value: float): self._value = value
    def add(self, value: float): self._value += value
    def subtract(self, value: float): self._value -= value
    def recall(self) -> float: return self._value
    def clear(self): self._value = 0.0
    def has_value(self) -> bool: return self._value != 0.0


# ─────────────────────────────────────────────
#  HISTORY MANAGER
# ─────────────────────────────────────────────

class HistoryManager:
    """Manages calculation history with file persistence."""

    def __init__(self, max_entries: int = 200):
        self.max_entries = max_entries
        self.entries: list[dict] = []
        self._load()

    def _load(self):
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
        except Exception:
            self.entries = []

    def _save(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.entries[-self.max_entries:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add(self, expression: str, result: str):
        entry = {
            "expression": expression,
            "result": result,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        self._save()

    def clear(self):
        self.entries = []
        self._save()

    def export_txt(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("═" * 50 + "\n")
            f.write("  HISTÓRICO DE CÁLCULOS — CalcPro\n")
            f.write(f"  Exportado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("═" * 50 + "\n\n")
            for i, e in enumerate(self.entries, 1):
                f.write(f"[{i:03d}] {e['timestamp']}\n")
                f.write(f"      {e['expression']} = {e['result']}\n\n")
