import sys

from modulos.comparacion import comparar_lenguajes, encontrar_isomorfismo
from modulos.fnc import convertir_a_fnc, obtener_violaciones_fnc
from modulos.gramatica import contar_producciones, gramatica_a_texto, leer_gramatica_desde_archivo
from modulos.utilidades import formatear_tiempo, medir_tiempo


def mostrar_gramatica(titulo, gramatica):
    print(f"--- {titulo} ({len(gramatica.producciones)} no terminales, "
          f"{contar_producciones(gramatica)} producciones) ---")
    print(gramatica_a_texto(gramatica))
    print()


def mostrar_isomorfismo(obtenida, esperada):
    correspondencia = encontrar_isomorfismo(obtenida, esperada)
    if correspondencia is None:
        print("Estructura: DIFERENTE (no son iguales ni renombrando no terminales)")
        return False
    print("Estructura: IGUAL (solo cambian los nombres de los no terminales)")
    for propio, esperado in correspondencia.items():
        if propio != esperado:
            print(f"  {propio:<6} = {esperado}")
    return True


def mostrar_comparacion_lenguaje(obtenida, esperada, longitud):
    (total, aceptadas, diferencias), segundos = medir_tiempo(
        comparar_lenguajes, obtenida, esperada, longitud)
    print(f"Lenguaje: {total} cadenas probadas (longitud 0 a {longitud}), "
          f"{aceptadas} aceptadas por ambas, {len(diferencias)} diferencias "
          f"[{formatear_tiempo(segundos)}]")
    for cadena in diferencias[:10]:
        print(f"  diferencia: {' '.join(cadena) or 'ε'}")
    return not diferencias


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    longitud = int(sys.argv[3]) if len(sys.argv) > 3 else 6

    obtenida, _ = convertir_a_fnc(leer_gramatica_desde_archivo(sys.argv[1]))
    esperada = leer_gramatica_desde_archivo(sys.argv[2])
    mostrar_gramatica("FNC obtenida por el programa", obtenida)
    mostrar_gramatica("FNC esperada", esperada)

    print(f"FNC obtenida válida: {'SÍ' if not obtener_violaciones_fnc(obtenida) else 'NO'}")
    print(f"FNC esperada válida: {'SÍ' if not obtener_violaciones_fnc(esperada) else 'NO'}")
    iguales = mostrar_isomorfismo(obtenida, esperada)
    mismo_lenguaje = mostrar_comparacion_lenguaje(obtenida, esperada, longitud)
    print()
    print("RESULTADO: " + ("coincide con lo esperado" if iguales and mismo_lenguaje
                           else "NO coincide con lo esperado"))


if __name__ == "__main__":
    main()
