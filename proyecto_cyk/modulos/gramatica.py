from dataclasses import dataclass, field

EPSILON = "ε"
PALABRAS_EPSILON = {"ε", "e", "epsilon", "eps", "λ", "lambda"}
FLECHAS = ("->", "→")


@dataclass
class Gramatica:
    inicial: str
    producciones: dict = field(default_factory=dict)
    auxiliares: dict = field(default_factory=dict)


def es_no_terminal(simbolo):
    return len(simbolo) > 0 and simbolo[0].isupper()


def es_terminal(simbolo):
    return not es_no_terminal(simbolo)


def agregar_produccion(producciones, izquierda, derecha):
    producciones.setdefault(izquierda, set()).add(tuple(derecha))


def separar_lados(linea):
    for flecha in FLECHAS:
        if flecha in linea:
            izquierda, derecha = linea.split(flecha, 1)
            return izquierda.strip(), derecha.strip()
    raise ValueError(f"La línea no contiene una flecha '->': {linea}")


def interpretar_alternativa(texto):
    simbolos = texto.split()
    if not simbolos:
        raise ValueError("Alternativa vacía. Use 'ε' para la producción vacía.")
    if len(simbolos) == 1 and simbolos[0].lower() in PALABRAS_EPSILON:
        return ()
    return tuple(simbolos)


def interpretar_linea(linea):
    linea = linea.split("#", 1)[0].strip()
    if not linea:
        return None
    izquierda, derecha = separar_lados(linea)
    if not es_no_terminal(izquierda) or " " in izquierda:
        raise ValueError(f"Lado izquierdo inválido: '{izquierda}'")
    alternativas = [interpretar_alternativa(a) for a in derecha.split("|")]
    return izquierda, alternativas


def leer_gramatica_desde_texto(texto):
    producciones = {}
    inicial = None
    for numero, linea in enumerate(texto.splitlines(), start=1):
        try:
            resultado = interpretar_linea(linea)
        except ValueError as error:
            raise ValueError(f"Error en la línea {numero}: {error}") from None
        if resultado is None:
            continue
        izquierda, alternativas = resultado
        if inicial is None:
            inicial = izquierda
        for alternativa in alternativas:
            agregar_produccion(producciones, izquierda, alternativa)
    if inicial is None:
        raise ValueError("La gramática no tiene producciones.")
    return Gramatica(inicial, producciones)


def leer_gramatica_desde_archivo(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        return leer_gramatica_desde_texto(archivo.read())


def copiar_gramatica(gramatica):
    return Gramatica(
        gramatica.inicial,
        {izq: set(cuerpos) for izq, cuerpos in gramatica.producciones.items()},
        dict(gramatica.auxiliares),
    )


def obtener_no_terminales(gramatica):
    simbolos = set(gramatica.producciones) | {gramatica.inicial}
    for cuerpos in gramatica.producciones.values():
        for cuerpo in cuerpos:
            simbolos.update(s for s in cuerpo if es_no_terminal(s))
    return simbolos


def obtener_terminales(gramatica):
    simbolos = set()
    for cuerpos in gramatica.producciones.values():
        for cuerpo in cuerpos:
            simbolos.update(s for s in cuerpo if es_terminal(s))
    return simbolos


def contar_producciones(gramatica):
    return sum(len(cuerpos) for cuerpos in gramatica.producciones.values())


def generar_nombre_unico(base, usados):
    candidato = base
    contador = 2
    while candidato in usados:
        candidato = f"{base}_{contador}"
        contador += 1
    usados.add(candidato)
    return candidato


def ordenar_no_terminales(gramatica):
    orden = [gramatica.inicial]
    orden.extend(izq for izq in gramatica.producciones if izq != gramatica.inicial)
    return orden


def cuerpo_a_texto(cuerpo):
    return " ".join(cuerpo) if cuerpo else EPSILON


def gramatica_a_texto(gramatica):
    lineas = []
    for izquierda in ordenar_no_terminales(gramatica):
        cuerpos = sorted(gramatica.producciones.get(izquierda, set()))
        if not cuerpos:
            continue
        derecha = " | ".join(cuerpo_a_texto(c) for c in cuerpos)
        lineas.append(f"{izquierda} -> {derecha}")
    return "\n".join(lineas) if lineas else "(gramática vacía)"
