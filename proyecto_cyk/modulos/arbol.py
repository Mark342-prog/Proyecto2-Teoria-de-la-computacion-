from dataclasses import dataclass, field


@dataclass
class Nodo:
    etiqueta: str
    hijos: list = field(default_factory=list)


def es_hoja(nodo):

    return not nodo.hijos


def construir_arbol(tabla, i, j, simbolo):
    referencia = tabla[i][j][simbolo][0]
    if referencia[0] == "hoja":
        return Nodo(simbolo, [Nodo(referencia[1])])
    _, k, izquierdo, derecho = referencia
    return Nodo(simbolo, [
        construir_arbol(tabla, i, k, izquierdo),
        construir_arbol(tabla, k + 1, j, derecho),
    ])


def contar_arboles(tabla, i, j, simbolo, memo=None):
    if memo is None:
        memo = {}
    clave = (i, j, simbolo)
    if clave in memo:
        return memo[clave]
    total = 0
    for referencia in tabla[i][j].get(simbolo, []):
        if referencia[0] == "hoja":
            total += 1
        else:
            _, k, izquierdo, derecho = referencia
            total += (contar_arboles(tabla, i, k, izquierdo, memo)
                      * contar_arboles(tabla, k + 1, j, derecho, memo))
    memo[clave] = total
    return total


def revertir_nodo(nodo, auxiliares):
    if es_hoja(nodo):
        return [Nodo(nodo.etiqueta)]
    hijos = []
    for hijo in nodo.hijos:
        hijos.extend(revertir_nodo(hijo, auxiliares))
    informacion = auxiliares.get(nodo.etiqueta)
    if informacion is None:
        return [Nodo(nodo.etiqueta, hijos)]
    tipo, origen = informacion
    if tipo == "inicial":
        return [Nodo(origen, hijos)]
    return hijos


def restaurar_arbol_original(raiz, auxiliares):
    return revertir_nodo(raiz, auxiliares)[0]


def obtener_hojas(nodo):
    if es_hoja(nodo):
        return [nodo.etiqueta]
    hojas = []
    for hijo in nodo.hijos:
        hojas.extend(obtener_hojas(hijo))
    return hojas


def arbol_a_corchetes(nodo):
    if es_hoja(nodo):
        return nodo.etiqueta
    interior = " ".join(arbol_a_corchetes(h) for h in nodo.hijos)
    return f"[{nodo.etiqueta} {interior}]"


def arbol_a_lineas(nodo, prefijo="", es_ultimo=True, es_raiz=True):
    if es_raiz:
        lineas = [nodo.etiqueta]
        prefijo_hijos = ""
    else:
        conector = "`-- " if es_ultimo else "|-- "
        lineas = [prefijo + conector + nodo.etiqueta]
        prefijo_hijos = prefijo + ("    " if es_ultimo else "|   ")
    for indice, hijo in enumerate(nodo.hijos):
        ultimo = indice == len(nodo.hijos) - 1
        lineas.extend(arbol_a_lineas(hijo, prefijo_hijos, ultimo, False))
    return lineas


def arbol_a_texto(nodo):
    return "\n".join(arbol_a_lineas(nodo))
