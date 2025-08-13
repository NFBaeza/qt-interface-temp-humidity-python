# modulo.py
import numpy as np

def celsius_to_fahrenheit(c): return float(float(c) * 9.0 / 5.0 + 32)

def fahrenheit_to_celsius(f): return float((float(f) - 32) * (5.0 / 9.0))

def maximum(f): return np.max(f)
def minimum(f): return np.min(f)
def average(f): return np.mean(f)
