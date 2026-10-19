import argparse
import os
import sys

from modulos.arbol import (
    arbol_a_corchetes,
    arbol_a_texto,
    construir_arbol,
    contar_arboles,
    restaurar_arbol_original,
)
from modulos.cyk import algoritmo_cyk
from modulos.fnc import convertir_a_fnc, obtener_violaciones_fnc
from modulos.gramatica import (
    contar_producciones,
    gramatica_a_texto,
    leer_gramatica_desde_archivo,
    obtener_terminales,
)
from modulos.utilidades import formatear_tiempo, medir_tiempo, tabla_cyk_a_texto, tokenizar_frase

CARPETA = os.path.dirname(os.path.abspath(__file__))
GRAMATICA_POR_DEFECTO = os.path.join(CARPETA, "gramaticas", "gramatica_ingles.txt")


def crear_parser_argumentos():
    parser = argparse.ArgumentParser(description="Parser CYK para frases simples en inglés.")
    parser.add_argument("frase", nargs="*", help="frase a analizar (si se omite, modo interactivo)")
    parser.add_argument("--gramatica", default=GRAMATICA_POR_DEFECTO, help="archivo de la gramática")
    parser.add_argument("--pasos", action="store_true", help="mostrar cada paso de la conversión a FNC")
    parser.add_argument("--tabla", action="store_true", help="mostrar la tabla CYK")
    return parser


def mostrar_pasos_conversion(pasos):
    for descripcion, gramatica in pasos:
        print(f"--- {descripcion} ({contar_producciones(gramatica)} producciones) ---")
        print(gramatica_a_texto(gramatica))
        print()


def cargar_gramatica_fnc(ruta, mostrar_pasos):
    original = leer_gramatica_desde_archivo(ruta)
    (fnc, pasos), segundos = medir_tiempo(convertir_a_fnc, original)
    violaciones = obtener_violaciones_fnc(fnc)
    if violaciones:
        raise RuntimeError(f"La conversión no quedó en FNC: {violaciones}")
    if mostrar_pasos:
        mostrar_pasos_conversion(pasos)
    else:
        print("Gramática en Forma Normal de Chomsky:")
        print(gramatica_a_texto(fnc))
        print()
    print(f"Tiempo de simplificación y conversión a FNC: {formatear_tiempo(segundos)}")
    print()
    return fnc


def mostrar_arboles(gramatica, tabla, n):
    (raiz, total), segundos = medir_tiempo(construir_arbol_y_contar, gramatica, tabla, n)
    print(f"Árboles de derivación posibles: {total}")
    print(f"Tiempo de construcción del árbol: {formatear_tiempo(segundos)}")
    print()
    print("Árbol de derivación (gramática en FNC):")
    print(arbol_a_texto(raiz))
    print()
    original = restaurar_arbol_original(raiz, gramatica.auxiliares)
    if arbol_a_corchetes(original) != arbol_a_corchetes(raiz):
        print("Árbol de derivación (símbolos de la gramática original):")
        print(arbol_a_texto(original))
        print()
    print("Notación con corchetes:")
    print(arbol_a_corchetes(original))


def construir_arbol_y_contar(gramatica, tabla, n):
    raiz = construir_arbol(tabla, 0, n - 1, gramatica.inicial)
    total = contar_arboles(tabla, 0, n - 1, gramatica.inicial)
    return raiz, total


def analizar_frase(gramatica, frase, mostrar_tabla):
    palabras = tokenizar_frase(frase, obtener_terminales(gramatica))
    (pertenece, tabla), segundos = medir_tiempo(algoritmo_cyk, gramatica, palabras)
    print(f"Frase: {frase}")
    print(f"Palabras: {palabras}")
    print(f"Resultado: {'SÍ' if pertenece else 'NO'}")
    print(f"Tiempo del algoritmo CYK: {formatear_tiempo(segundos)}")
    print()
    if mostrar_tabla and tabla:
        print("Tabla CYK:")
        print(tabla_cyk_a_texto(tabla, palabras))
        print()
    if pertenece and palabras:
        mostrar_arboles(gramatica, tabla, len(palabras))
    return pertenece


def modo_interactivo(gramatica, mostrar_tabla):
    print("Escriba una frase en inglés (o 'salir' para terminar).")
    while True:
        try:
            frase = input("\nw = ").strip()
        except EOFError:
            break
        if frase.lower() in {"salir", "exit", "quit"}:
            break
        if frase:
            print()
            analizar_frase(gramatica, frase, mostrar_tabla)


def main():
    argumentos = crear_parser_argumentos().parse_args()
    try:
        gramatica = cargar_gramatica_fnc(argumentos.gramatica, argumentos.pasos)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error al cargar la gramática: {error}")
        sys.exit(1)
    if argumentos.frase:
        analizar_frase(gramatica, " ".join(argumentos.frase), argumentos.tabla)
    else:
        modo_interactivo(gramatica, argumentos.tabla)


if __name__ == "__main__":
    main()
