import os

from modulos.arbol import arbol_a_corchetes, construir_arbol, restaurar_arbol_original
from modulos.cyk import algoritmo_cyk
from modulos.fnc import convertir_a_fnc
from modulos.gramatica import contar_producciones, gramatica_a_texto, leer_gramatica_desde_archivo
from modulos.utilidades import formatear_tiempo, medir_tiempo, tokenizar_frase

CARPETA = os.path.dirname(os.path.abspath(__file__))

FRASES_EN_EL_LENGUAJE = [
    "She eats a cake with a fork",
    "The cat drinks the beer",
    "He cooks",
    "she eats",
    "The dog eats the meat in the oven",
    "He cuts the cake with a knife",
    "She drinks the juice with a spoon in the oven",
    "A cat cooks a dog",
    "The fork eats the soup",
]

FRASES_FUERA_DEL_LENGUAJE = [
    "Eats she",
    "eats a cake",
    "She cake",
    "The cat",
    "She eats cake",
    "Cat drinks the beer",
    "She eats a cake with",
    "He drinks the juice quickly",
    "she she eats",
    "The cat the dog eats",
]


def evaluar_frase(gramatica, frase):
    palabras = tokenizar_frase(frase)
    (pertenece, tabla), segundos = medir_tiempo(algoritmo_cyk, gramatica, palabras)
    arbol = "-"
    if pertenece:
        raiz = construir_arbol(tabla, 0, len(palabras) - 1, gramatica.inicial)
        arbol = arbol_a_corchetes(restaurar_arbol_original(raiz, gramatica.auxiliares))
    return ("SÍ" if pertenece else "NO"), formatear_tiempo(segundos), arbol


def mostrar_grupo(gramatica, titulo, frases):
    print(titulo)
    print(f"  {'Res':<3} {'Tiempo CYK':>12}   Frase")
    for frase in frases:
        resultado, tiempo, arbol = evaluar_frase(gramatica, frase)
        print(f"  {resultado:<3} {tiempo:>12}   {frase}")
        if arbol != "-":
            print(f"      {arbol}")
    print()


def mostrar_simplificacion(ruta):
    _, pasos = convertir_a_fnc(leer_gramatica_desde_archivo(ruta))
    for descripcion, gramatica in pasos:
        print(f"--- {descripcion} ({contar_producciones(gramatica)} producciones) ---")
        print(gramatica_a_texto(gramatica))
        print()


def main():
    ruta_ingles = os.path.join(CARPETA, "gramaticas", "gramatica_ingles.txt")
    ruta_prueba = os.path.join(CARPETA, "gramaticas", "gramatica_simplificacion.txt")

    gramatica, _ = convertir_a_fnc(leer_gramatica_desde_archivo(ruta_ingles))
    mostrar_grupo(gramatica, "=== Frases que pertenecen al lenguaje ===", FRASES_EN_EL_LENGUAJE)
    mostrar_grupo(gramatica, "=== Frases que NO pertenecen al lenguaje ===", FRASES_FUERA_DEL_LENGUAJE)

    print("=== Simplificación y FNC de la gramática de prueba ===")
    mostrar_simplificacion(ruta_prueba)


if __name__ == "__main__":
    main()
