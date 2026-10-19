from itertools import product

from .gramatica import Gramatica, es_no_terminal, es_terminal


def calcular_anulables(gramatica):
    anulables = set()
    hubo_cambio = True
    while hubo_cambio:
        hubo_cambio = False
        for izquierda, cuerpos in gramatica.producciones.items():
            if izquierda in anulables:
                continue
            if any(all(s in anulables for s in cuerpo) for cuerpo in cuerpos):
                anulables.add(izquierda)
                hubo_cambio = True
    return anulables


def generar_variantes_sin_anulables(cuerpo, anulables):
    opciones = [((s,), ()) if s in anulables else ((s,),) for s in cuerpo]
    variantes = set()
    for combinacion in product(*opciones):
        variantes.add(tuple(s for parte in combinacion for s in parte))
    return variantes


def eliminar_producciones_epsilon(gramatica):
    anulables = calcular_anulables(gramatica)
    nuevas = {}
    for izquierda, cuerpos in gramatica.producciones.items():
        nuevas[izquierda] = set()
        for cuerpo in cuerpos:
            for variante in generar_variantes_sin_anulables(cuerpo, anulables):
                if variante:
                    nuevas[izquierda].add(variante)
    if gramatica.inicial in anulables:
        nuevas.setdefault(gramatica.inicial, set()).add(())
    return Gramatica(gramatica.inicial, nuevas, dict(gramatica.auxiliares))

def es_produccion_unitaria(cuerpo):
    return len(cuerpo) == 1 and es_no_terminal(cuerpo[0])


def calcular_pares_unitarios(gramatica):
    pares = {(a, a) for a in gramatica.producciones}
    pendientes = list(pares)
    while pendientes:
        a, b = pendientes.pop()
        for cuerpo in gramatica.producciones.get(b, ()):
            if es_produccion_unitaria(cuerpo):
                par = (a, cuerpo[0])
                if par not in pares:
                    pares.add(par)
                    pendientes.append(par)
    return pares


def eliminar_producciones_unitarias(gramatica):
    pares = calcular_pares_unitarios(gramatica)
    nuevas = {izquierda: set() for izquierda in gramatica.producciones}
    for a, b in pares:
        for cuerpo in gramatica.producciones.get(b, ()):
            if es_produccion_unitaria(cuerpo):
                continue
            if cuerpo == () and a != gramatica.inicial:
                continue
            nuevas[a].add(cuerpo)
    return Gramatica(gramatica.inicial, nuevas, dict(gramatica.auxiliares))

def calcular_simbolos_generadores(gramatica):
    generadores = set()
    hubo_cambio = True
    while hubo_cambio:
        hubo_cambio = False
        for izquierda, cuerpos in gramatica.producciones.items():
            if izquierda in generadores:
                continue
            for cuerpo in cuerpos:
                if all(es_terminal(s) or s in generadores for s in cuerpo):
                    generadores.add(izquierda)
                    hubo_cambio = True
                    break
    return generadores


def eliminar_simbolos_no_generadores(gramatica):
    generadores = calcular_simbolos_generadores(gramatica)
    nuevas = {}
    for izquierda, cuerpos in gramatica.producciones.items():
        if izquierda not in generadores:
            continue
        nuevas[izquierda] = {
            cuerpo for cuerpo in cuerpos
            if all(es_terminal(s) or s in generadores for s in cuerpo)
        }
    nuevas.setdefault(gramatica.inicial, set())  # lenguaje vacío si no genera
    return Gramatica(gramatica.inicial, nuevas, dict(gramatica.auxiliares))


def calcular_simbolos_alcanzables(gramatica):
    alcanzables = {gramatica.inicial}
    pendientes = [gramatica.inicial]
    while pendientes:
        actual = pendientes.pop()
        for cuerpo in gramatica.producciones.get(actual, ()):
            for simbolo in cuerpo:
                if es_no_terminal(simbolo) and simbolo not in alcanzables:
                    alcanzables.add(simbolo)
                    pendientes.append(simbolo)
    return alcanzables


def eliminar_simbolos_no_alcanzables(gramatica):
    alcanzables = calcular_simbolos_alcanzables(gramatica)
    nuevas = {
        izquierda: set(cuerpos)
        for izquierda, cuerpos in gramatica.producciones.items()
        if izquierda in alcanzables
    }
    return Gramatica(gramatica.inicial, nuevas, dict(gramatica.auxiliares))


def eliminar_simbolos_inutiles(gramatica):
    return eliminar_simbolos_no_alcanzables(eliminar_simbolos_no_generadores(gramatica))


def simplificar_gramatica(gramatica):
    sin_epsilon = eliminar_producciones_epsilon(gramatica)
    sin_unitarias = eliminar_producciones_unitarias(sin_epsilon)
    return eliminar_simbolos_inutiles(sin_unitarias)
