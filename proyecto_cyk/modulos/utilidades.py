import re
import time


PUNTUACION = set(".,;:!?¡¿\"")


def separar_piezas(frase):
    return re.findall(r"[\w'-]+|[^\w\s]", frase.lower())


def es_puntuacion_descartable(pieza, terminales):
    return pieza in PUNTUACION and pieza not in terminales


def tokenizar_frase(frase, terminales=frozenset()):
    return [p for p in separar_piezas(frase) if not es_puntuacion_descartable(p, terminales)]


def medir_tiempo(funcion, *argumentos):
    inicio = time.perf_counter()
    resultado = funcion(*argumentos)
    fin = time.perf_counter()
    return resultado, fin - inicio


def formatear_tiempo(segundos):
    return f"{segundos * 1000:.4f} ms"


def celda_a_texto(celda):
    return "{" + ", ".join(sorted(celda)) + "}" if celda else "{}"


def tabla_cyk_a_texto(tabla, palabras):
    n = len(palabras)
    lineas = []
    for longitud in range(1, n + 1):
        lineas.append(f"Longitud {longitud}:")
        for i in range(0, n - longitud + 1):
            j = i + longitud - 1
            fragmento = " ".join(palabras[i:j + 1])
            lineas.append(f"  [{i},{j}] {fragmento!r:<40} {celda_a_texto(tabla[i][j])}")
    return "\n".join(lineas)
