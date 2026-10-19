import os
import unittest

from modulos.arbol import (
    construir_arbol,
    contar_arboles,
    obtener_hojas,
    restaurar_arbol_original,
)
from modulos.comparacion import comparar_lenguajes, encontrar_isomorfismo
from modulos.cyk import algoritmo_cyk
from modulos.fnc import (
    agregar_nuevo_simbolo_inicial,
    binarizar_producciones,
    convertir_a_fnc,
    es_forma_normal_chomsky,
    reemplazar_terminales_en_cuerpos_largos,
)
from modulos.gramatica import (
    es_no_terminal,
    leer_gramatica_desde_archivo,
    leer_gramatica_desde_texto,
    obtener_terminales,
)
from modulos.simplificacion import (
    calcular_anulables,
    calcular_pares_unitarios,
    calcular_simbolos_alcanzables,
    calcular_simbolos_generadores,
    eliminar_producciones_epsilon,
    eliminar_producciones_unitarias,
    eliminar_simbolos_inutiles,
)
from modulos.utilidades import tokenizar_frase

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_INGLES = os.path.join(CARPETA, "gramaticas", "gramatica_ingles.txt")
RUTA_PRUEBA = os.path.join(CARPETA, "gramaticas", "gramatica_simplificacion.txt")
RUTA_EXPRESIONES = os.path.join(CARPETA, "gramaticas", "expresiones.txt")
RUTA_EXPRESIONES_FNC = os.path.join(CARPETA, "gramaticas", "expresiones_cnf_esperada.txt")


def acepta(gramatica_fnc, frase):
    """Atajo: True si CYK acepta la frase."""
    return algoritmo_cyk(gramatica_fnc, tokenizar_frase(frase))[0]


class PruebasGramatica(unittest.TestCase):

    def test_lectura_de_archivo(self):
        g = leer_gramatica_desde_archivo(RUTA_INGLES)
        self.assertEqual(g.inicial, "S")
        self.assertIn(("NP", "VP"), g.producciones["S"])
        self.assertIn("fork", obtener_terminales(g))

    def test_epsilon_y_comentarios(self):
        g = leer_gramatica_desde_texto("# comentario\nS -> a S | ε\n")
        self.assertEqual(g.producciones["S"], {("a", "S"), ()})

    def test_e_como_epsilon(self):
        g = leer_gramatica_desde_archivo(RUTA_EXPRESIONES)
        self.assertIn((), g.producciones["X"])
        self.assertNotIn("e", obtener_terminales(g))

    def test_linea_invalida(self):
        with self.assertRaises(ValueError):
            leer_gramatica_desde_texto("S NP VP")

    def test_convencion_de_simbolos(self):
        self.assertTrue(es_no_terminal("NP"))
        self.assertFalse(es_no_terminal("cat"))


class PruebasSimplificacion(unittest.TestCase):

    def setUp(self):
        self.g = leer_gramatica_desde_archivo(RUTA_PRUEBA)

    def test_anulables(self):
        self.assertEqual(calcular_anulables(self.g), {"S", "A", "B", "C"})

    def test_eliminar_epsilon(self):
        g = eliminar_producciones_epsilon(self.g)
        for izquierda, cuerpos in g.producciones.items():
            if izquierda != g.inicial:
                self.assertNotIn((), cuerpos)
        self.assertIn(("A", "C"), g.producciones["S"])

    def test_pares_unitarios(self):
        pares = calcular_pares_unitarios(eliminar_producciones_epsilon(self.g))
        self.assertIn(("S", "A"), pares)
        self.assertIn(("S", "D"), pares)

    def test_eliminar_unitarias(self):
        g = eliminar_producciones_unitarias(eliminar_producciones_epsilon(self.g))
        for cuerpos in g.producciones.values():
            for cuerpo in cuerpos:
                self.assertFalse(len(cuerpo) == 1 and es_no_terminal(cuerpo[0]))

    def test_generadores_y_alcanzables(self):
        self.assertNotIn("D", calcular_simbolos_generadores(self.g))
        self.assertNotIn("E", calcular_simbolos_alcanzables(self.g))

    def test_eliminar_inutiles(self):
        g = eliminar_simbolos_inutiles(self.g)
        self.assertNotIn("D", g.producciones)
        self.assertNotIn("E", g.producciones)


class PruebasFNC(unittest.TestCase):

    def test_nuevo_inicial(self):
        g = agregar_nuevo_simbolo_inicial(leer_gramatica_desde_archivo(RUTA_PRUEBA))
        self.assertEqual(g.inicial, "S0")
        self.assertEqual(g.producciones["S0"], {("S",)})

    def test_sin_nuevo_inicial_si_no_hace_falta(self):
        g = agregar_nuevo_simbolo_inicial(leer_gramatica_desde_archivo(RUTA_INGLES))
        self.assertEqual(g.inicial, "S")

    def test_sin_nuevo_inicial_si_no_es_anulable(self):
        # E aparece a la derecha en F -> ( E ), pero no es anulable
        g = agregar_nuevo_simbolo_inicial(leer_gramatica_desde_archivo(RUTA_EXPRESIONES))
        self.assertEqual(g.inicial, "E")

    def test_colas_compartidas(self):
        g = binarizar_producciones(leer_gramatica_desde_texto("S -> a B c | d B c\nB -> b"))
        self.assertEqual(len(g.producciones), 2 + 1)  # S, B y una sola variable para 'B c'

    def test_reemplazar_terminales(self):
        g = reemplazar_terminales_en_cuerpos_largos(leer_gramatica_desde_texto("S -> a S b | c"))
        self.assertIn(("T_a", "S", "T_b"), g.producciones["S"])
        self.assertEqual(g.producciones["T_a"], {("a",)})

    def test_binarizar(self):
        g = binarizar_producciones(leer_gramatica_desde_texto("S -> A B C D\nA -> a\nB -> b\nC -> c\nD -> d"))
        for cuerpos in g.producciones.values():
            for cuerpo in cuerpos:
                self.assertLessEqual(len(cuerpo), 2)

    def test_resultado_en_fnc(self):
        for ruta in (RUTA_INGLES, RUTA_PRUEBA):
            g, _ = convertir_a_fnc(leer_gramatica_desde_archivo(ruta))
            self.assertTrue(es_forma_normal_chomsky(g))

    def test_lenguaje_se_conserva(self):
        # La gramática de prueba genera a^i (b | nada) c^k
        g, _ = convertir_a_fnc(leer_gramatica_desde_archivo(RUTA_PRUEBA))
        for cadena in ["", "a", "b", "c", "a a b c c", "a c", "b c", "a a a"]:
            self.assertTrue(algoritmo_cyk(g, cadena.split())[0], cadena)
        for cadena in ["b a", "c b", "b b", "d", "e", "a b c a"]:
            self.assertFalse(algoritmo_cyk(g, cadena.split())[0], cadena)


class PruebasFNCEsperada(unittest.TestCase):

    def setUp(self):
        self.obtenida, _ = convertir_a_fnc(leer_gramatica_desde_archivo(RUTA_EXPRESIONES))
        self.esperada = leer_gramatica_desde_archivo(RUTA_EXPRESIONES_FNC)

    def test_misma_estructura(self):
        self.assertIsNotNone(encontrar_isomorfismo(self.obtenida, self.esperada))

    def test_mismo_lenguaje(self):
        _, aceptadas, diferencias = comparar_lenguajes(self.obtenida, self.esperada, 5)
        self.assertGreater(aceptadas, 0)
        self.assertEqual(diferencias, [])

    def test_expresiones(self):
        terminales = obtener_terminales(self.obtenida)
        for frase in ["id", "id + id * id", "(id+id)*id", "( ( id ) )"]:
            self.assertTrue(algoritmo_cyk(self.obtenida, tokenizar_frase(frase, terminales))[0], frase)
        for frase in ["id +", "( id", "id id", "+ id", ""]:
            self.assertFalse(algoritmo_cyk(self.obtenida, tokenizar_frase(frase, terminales))[0], frase)


class PruebasTokenizador(unittest.TestCase):

    def test_quita_puntuacion(self):
        self.assertEqual(tokenizar_frase("She eats a cake."), ["she", "eats", "a", "cake"])

    def test_conserva_terminales_simbolo(self):
        self.assertEqual(tokenizar_frase("(id+id)*id", {"(", ")", "+", "*", "id"}),
                         ["(", "id", "+", "id", ")", "*", "id"])


class PruebasCYK(unittest.TestCase):

    def setUp(self):
        self.g, _ = convertir_a_fnc(leer_gramatica_desde_archivo(RUTA_INGLES))

    def test_frases_aceptadas(self):
        for frase in ["She eats a cake with a fork", "The cat drinks the beer",
                      "He cooks", "The dog eats the meat in the oven"]:
            self.assertTrue(acepta(self.g, frase), frase)

    def test_frases_rechazadas(self):
        for frase in ["She cake", "The cat", "She eats cake",
                      "eats a cake", "She eats a cake with", "He drinks quickly", ""]:
            self.assertFalse(acepta(self.g, frase), frase)

    def test_arbol_reproduce_la_frase(self):
        palabras = tokenizar_frase("She eats a cake with a fork")
        _, tabla = algoritmo_cyk(self.g, palabras)
        raiz = construir_arbol(tabla, 0, len(palabras) - 1, self.g.inicial)
        self.assertEqual(raiz.etiqueta, "S")
        self.assertEqual(obtener_hojas(raiz), palabras)

    def test_ambiguedad(self):
        with open(RUTA_INGLES, encoding="utf-8") as archivo:
            texto = archivo.read() + "\nNP -> NP PP\n"
        g, _ = convertir_a_fnc(leer_gramatica_desde_texto(texto))
        palabras = tokenizar_frase("She eats a cake with a fork")
        _, tabla = algoritmo_cyk(g, palabras)
        self.assertEqual(contar_arboles(tabla, 0, len(palabras) - 1, g.inicial), 2)

    def test_arbol_original_sin_auxiliares(self):
        g, _ = convertir_a_fnc(leer_gramatica_desde_texto("S -> a S b | a b"))
        palabras = "a a b b".split()
        _, tabla = algoritmo_cyk(g, palabras)
        raiz = restaurar_arbol_original(construir_arbol(tabla, 0, 3, g.inicial), g.auxiliares)
        self.assertEqual(raiz.etiqueta, "S")
        self.assertEqual([h.etiqueta for h in raiz.hijos], ["a", "S", "b"])
        self.assertEqual(obtener_hojas(raiz), palabras)


if __name__ == "__main__":
    unittest.main(verbosity=2)
