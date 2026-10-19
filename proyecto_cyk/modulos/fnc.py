from .gramatica import (
    Gramatica,
    copiar_gramatica,
    es_no_terminal,
    es_terminal,
    generar_nombre_unico,
    obtener_no_terminales,
)
from .simplificacion import (
    calcular_anulables,
    eliminar_producciones_epsilon,
    eliminar_producciones_unitarias,
    eliminar_simbolos_inutiles,
)


def inicial_aparece_a_la_derecha(gramatica):
    return any(
        gramatica.inicial in cuerpo
        for cuerpos in gramatica.producciones.values()
        for cuerpo in cuerpos
    )


def necesita_nuevo_simbolo_inicial(gramatica):
    return (inicial_aparece_a_la_derecha(gramatica)
            and gramatica.inicial in calcular_anulables(gramatica))


def agregar_nuevo_simbolo_inicial(gramatica):
    if not necesita_nuevo_simbolo_inicial(gramatica):
        return copiar_gramatica(gramatica)
    usados = obtener_no_terminales(gramatica)
    nuevo = generar_nombre_unico(gramatica.inicial + "0", usados)
    producciones = {nuevo: {(gramatica.inicial,)}}
    producciones.update({izq: set(c) for izq, c in gramatica.producciones.items()})
    auxiliares = dict(gramatica.auxiliares)
    auxiliares[nuevo] = ("inicial", gramatica.inicial)
    return Gramatica(nuevo, producciones, auxiliares)


def reemplazar_terminales_en_cuerpos_largos(gramatica):
    usados = obtener_no_terminales(gramatica)
    nuevas = {izquierda: set() for izquierda in gramatica.producciones}
    auxiliares = dict(gramatica.auxiliares)
    variable_de_terminal = {}

    for izquierda, cuerpos in gramatica.producciones.items():
        for cuerpo in sorted(cuerpos):
            if len(cuerpo) < 2:
                nuevas[izquierda].add(cuerpo)
                continue
            nuevo_cuerpo = []
            for simbolo in cuerpo:
                if es_terminal(simbolo):
                    if simbolo not in variable_de_terminal:
                        nombre = generar_nombre_unico("T_" + simbolo, usados)
                        variable_de_terminal[simbolo] = nombre
                        nuevas[nombre] = {(simbolo,)}
                        auxiliares[nombre] = ("terminal", simbolo)
                    nuevo_cuerpo.append(variable_de_terminal[simbolo])
                else:
                    nuevo_cuerpo.append(simbolo)
            nuevas[izquierda].add(tuple(nuevo_cuerpo))
    return Gramatica(gramatica.inicial, nuevas, auxiliares)


def crear_variable_para_cola(cola, izquierda, nuevas, auxiliares, usados, contador, colas):
    if cola in colas:
        return colas[cola]
    contador[izquierda] = contador.get(izquierda, 0) + 1
    nombre = generar_nombre_unico(f"{izquierda}_{contador[izquierda]}", usados)
    colas[cola] = nombre
    auxiliares[nombre] = ("binario", izquierda)
    nuevas[nombre] = set()
    if len(cola) == 2:
        nuevas[nombre].add(cola)
    else:
        resto = crear_variable_para_cola(cola[1:], izquierda, nuevas, auxiliares, usados, contador, colas)
        nuevas[nombre].add((cola[0], resto))
    return nombre


def binarizar_producciones(gramatica):
    usados = obtener_no_terminales(gramatica)
    nuevas = {izquierda: set() for izquierda in gramatica.producciones}
    auxiliares = dict(gramatica.auxiliares)
    contador = {}
    colas = {}

    for izquierda, cuerpos in list(gramatica.producciones.items()):
        for cuerpo in sorted(cuerpos):
            if len(cuerpo) <= 2:
                nuevas[izquierda].add(cuerpo)
                continue
            cola = crear_variable_para_cola(cuerpo[1:], izquierda, nuevas, auxiliares, usados, contador, colas)
            nuevas[izquierda].add((cuerpo[0], cola))
    return Gramatica(gramatica.inicial, nuevas, auxiliares)


def obtener_violaciones_fnc(gramatica):
    violaciones = []
    inicial_derecha = inicial_aparece_a_la_derecha(gramatica)
    for izquierda, cuerpos in gramatica.producciones.items():
        for cuerpo in cuerpos:
            if len(cuerpo) == 2 and all(es_no_terminal(s) for s in cuerpo):
                continue
            if len(cuerpo) == 1 and es_terminal(cuerpo[0]):
                continue
            if len(cuerpo) == 0 and izquierda == gramatica.inicial and not inicial_derecha:
                continue
            violaciones.append((izquierda, cuerpo))
    return violaciones


def es_forma_normal_chomsky(gramatica):
    return not obtener_violaciones_fnc(gramatica)


def convertir_a_fnc(gramatica):
    pasos = [("Gramática original", gramatica)]
    actual = gramatica
    transformaciones = [
        ("Paso 1: nuevo símbolo inicial (si aplica)", agregar_nuevo_simbolo_inicial),
        ("Paso 2: eliminar producciones épsilon", eliminar_producciones_epsilon),
        ("Paso 3: eliminar producciones unitarias", eliminar_producciones_unitarias),
        ("Paso 4: eliminar símbolos inútiles", eliminar_simbolos_inutiles),
        ("Paso 5: reemplazar terminales en cuerpos largos", reemplazar_terminales_en_cuerpos_largos),
        ("Paso 6: binarizar cuerpos de 3 o más símbolos", binarizar_producciones),
    ]
    for descripcion, funcion in transformaciones:
        actual = funcion(actual)
        pasos.append((descripcion, actual))
    return actual, pasos
