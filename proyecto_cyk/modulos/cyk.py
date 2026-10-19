def construir_indice_lexico(gramatica):
    indice = {}
    for izquierda, cuerpos in gramatica.producciones.items():
        for cuerpo in cuerpos:
            if len(cuerpo) == 1:
                indice.setdefault(cuerpo[0], []).append(izquierda)
    for lista in indice.values():
        lista.sort()
    return indice


def construir_indice_binario(gramatica):
    indice = {}
    for izquierda, cuerpos in gramatica.producciones.items():
        for cuerpo in cuerpos:
            if len(cuerpo) == 2:
                indice.setdefault(cuerpo, []).append(izquierda)
    for lista in indice.values():
        lista.sort()
    return indice


def crear_tabla_vacia(n):
    return [[{} for _ in range(n)] for _ in range(n)]


def llenar_diagonal(tabla, palabras, indice_lexico):
    for i, palabra in enumerate(palabras):
        for no_terminal in indice_lexico.get(palabra, []):
            tabla[i][i].setdefault(no_terminal, []).append(("hoja", palabra))


def llenar_celda(tabla, i, j, indice_binario):
    for k in range(i, j):
        izquierda = tabla[i][k]
        derecha = tabla[k + 1][j]
        if not izquierda or not derecha:
            continue
        for b in izquierda:
            for c in derecha:
                for a in indice_binario.get((b, c), []):
                    tabla[i][j].setdefault(a, []).append(("rama", k, b, c))


def llenar_tabla(tabla, n, indice_binario):
    for longitud in range(2, n + 1):
        for i in range(0, n - longitud + 1):
            j = i + longitud - 1
            llenar_celda(tabla, i, j, indice_binario)


def acepta_cadena_vacia(gramatica):
    return () in gramatica.producciones.get(gramatica.inicial, set())


def algoritmo_cyk(gramatica, palabras):
    n = len(palabras)
    if n == 0:
        return acepta_cadena_vacia(gramatica), []
    tabla = crear_tabla_vacia(n)
    llenar_diagonal(tabla, palabras, construir_indice_lexico(gramatica))
    llenar_tabla(tabla, n, construir_indice_binario(gramatica))
    return gramatica.inicial in tabla[0][n - 1], tabla
