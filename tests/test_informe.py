import json
import pathlib
import sys
import unittest
from datetime import date

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "informe-semanal"))

import informe  # noqa: E402


class TestInforme(unittest.TestCase):
    def setUp(self):
        data = json.loads((RAIZ / "informe-semanal/ejemplo/valores.json").read_text("utf-8"))
        self.eventos = informe.leer_eventos(data["values"])
        self.msg = informe.armar_mensaje(self.eventos, date(2026, 11, 19))

    def test_rango_de_ocho_dias(self):
        self.assertIn("_Del Jueves 19 de noviembre al Jueves 26 de noviembre_", self.msg)
        self.assertIn("*Jueves 26/11*", self.msg)

    def test_nota_mitigacion(self):
        linea = next(l for l in self.msg.splitlines() if "Monumental" in l)
        self.assertTrue(linea.endswith(informe.NOTA))
        linea = next(l for l in self.msg.splitlines() if "Centenario" in l)
        self.assertNotIn("Mitigación", linea)

    def test_limpia_espacio_verde_y_aforo(self):
        self.assertIn("en Parque Centenario (15.000 asistentes).", self.msg)
        self.assertIn("(s/d asistentes)", self.msg)

    def test_dia_sin_eventos(self):
        self.assertIn("*Viernes 20/11*\n- Sin eventos masivos previstos.", self.msg)

    def test_postales_vacia(self):
        self.assertTrue(self.msg.rstrip().endswith("🌆 *POSTALES* 🌆"))


if __name__ == "__main__":
    unittest.main()
