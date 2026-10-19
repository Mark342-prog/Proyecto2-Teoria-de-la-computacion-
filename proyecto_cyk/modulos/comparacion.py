from itertools import product

from .cyk import algoritmo_cyk
from .gramatica import es_no_terminal, obtener_terminales


def firma_no_terminal(gramatica, no_terminal):
    cuerpos = gramatica.producciones.get(no_terminal, set())
    return tuple(sorted(
        tuple("#" if es_no_terminal(s) else s for s in cuerpo) for cuerpo in cuerpos
    ))


def renombrar_cuerpo(cuerpo, correspondencia):
    return tuple(correspondencia.get(s, s) for s in cuerpo)


def correspondencia_es_consistente(g1, g2, correspondencia):
    for a, b in correspondencia.items():
        cuerpos_b = g2.producciones.get(b, set())
        for cuerpo in g1.producciones.get(a, set()):
            if all(not es_no_terminal(s) or s in correspondencia for s in cuerpo):
                if renombrar_cuerpo(cuerpo, correspondencia) not in cuerpos_b:
                    return False
    return True


def buscar_correspondencia(g1, g2, pendientes, correspondencia, usados):
    if not pendientes:
        return dict(correspondencia)
    actual, resto = pendientes[0], pendientes[1:]
    firma = firma_no_terminal(g1, actual)
    for candidato in g2.producciones:
        if candidato in usados or firma_no_terminal(g2, candidato) != firma:
            continue
        correspondencia[actual] = candidato
        usados.add(candidato)
        if correspondencia_es_consistente(g1, g2, correspondencia):
            resultado = buscar_correspondencia(g1, g2, resto, correspondencia, usados)
            if resultado is not None:
                return resultado
        del correspondencia[actual]
        usados.discard(candidato)
    return None


def encontrar_isomorfismo(g1, g2):
    if len(g1.producciones) != len(g2.producciones):
        return None
    if obtener_terminales(g1) != obtener_terminales(g2):
        return None
    pendientes = [g1.inicial] + [a for a in g1.producciones if a != g1.inicial]
    if firma_no_terminal(g1, g1.inicial) != firma_no_terminal(g2, g2.inicial):
        return None
    correspondencia = {g1.inicial: g2.inicial}
    usados = {g2.inicial}
    if not correspondencia_es_consistente(g1, g2, correspondencia):
        return None
    return buscar_correspondencia(g1, g2, pendientes[1:], correspondencia, usados)


def generar_cadenas(terminales, longitud_maxima):
    simbolos = sorted(terminales)
    for longitud in range(longitud_maxima + 1):
        for cadena in product(simbolos, repeat=longitud):
            yield list(cadena)


def comparar_lenguajes(g1, g2, longitud_maxima):
    terminales = obtener_terminales(g1) | obtener_terminales(g2)
    total = aceptadas = 0
    diferencias = []
    for cadena in generar_cadenas(terminales, longitud_maxima):
        en_g1 = algoritmo_cyk(g1, cadena)[0]
        en_g2 = algoritmo_cyk(g2, cadena)[0]
        total += 1
        aceptadas += en_g1
        if en_g1 != en_g2:
            diferencias.append(cadena)
    return total, aceptadas, diferencias
