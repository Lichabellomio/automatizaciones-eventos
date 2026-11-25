import json
import os
import pathlib
import sys
import tempfile
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "reporte-semanal"))

import reporte_tab  # noqa: E402


def fila(evento, fechas, lugar="Estadio *", aforo="30.000", estado="PLANIFICACIÓN"):
    return [evento, fechas, lugar, "Productora", aforo, estado, "01/11/2026", "20/11/2026"]


class TestApply(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.state = os.path.join(self.dir.name, "state.json")
        self.delta = os.path.join(self.dir.name, "delta.json")
        json.dump({"meta": {}, "resumen": "", "ccoo": [], "observacion": [],
                   "historial": ["13/11/2026 (corte 12:00) – reporte anterior"],
                   "eventos": [fila("Recital A", "10/12/2026"),
                               fila("Festival viejo", "01/11/2026")]},
                  open(self.state, "w"))

    def aplicar(self, delta, hoy="24/11/2026"):
        json.dump(delta, open(self.delta, "w"))
        reporte_tab.apply(self.state, self.delta, hoy)
        return json.load(open(self.state))

    def test_upsert_actualiza_sin_duplicar(self):
        st = self.aplicar({"upserts": [{"match": "recital a",
                                        "row": fila("Recital A", "13/12/2026 (antes 10/12)",
                                                    estado="CONFIRMADO")}]})
        nombres = [r[0] for r in st["eventos"]]
        self.assertEqual(nombres.count("Recital A"), 1)
        self.assertIn("CONFIRMADO", st["eventos"][0][5])

    def test_quita_vencidos_y_ordena(self):
        st = self.aplicar({"upserts": [{"match": None, "row": fila("Show B", "05/12/2026")}]})
        self.assertEqual([r[0] for r in st["eventos"]], ["Show B", "Recital A"])

    def test_reemplaza_bandejas_e_historial(self):
        st = self.aplicar({"ccoo": [["10/12/2026", "Recital A"]],
                           "historial_add": "20/11/2026 (corte 12:00) – nuevo"})
        self.assertEqual(len(st["ccoo"][0]), 8)
        self.assertTrue(st["historial"][0].startswith("20/11/2026"))


class TestBuildYSplit(unittest.TestCase):
    def test_tandas_respetan_el_tamano(self):
        with tempfile.TemporaryDirectory() as d:
            state = os.path.join(d, "state.json")
            req = os.path.join(d, "requests.json")
            eventos = [fila(f"Evento {i}", f"{i % 28 + 1:02d}/12/2026") for i in range(60)]
            json.dump({"meta": {"ultimo_reporte": "20/11/2026"}, "resumen": "Sin cambios.",
                       "eventos": eventos, "ccoo": [], "observacion": [], "historial": []},
                      open(state, "w"))
            reporte_tab.build(state, "t.test", req)
            total = len(json.load(open(req))["requests"])
            cwd = os.getcwd()
            os.chdir(d)
            try:
                reporte_tab.split(req)
                tandas = sorted(pathlib.Path(d).glob("chunk*.json"))
                self.assertGreater(len(tandas), 1)
                self.assertEqual(sum(len(json.loads(t.read_text())) for t in tandas), total)
                for t in tandas:
                    self.assertLess(len(t.read_text().encode()), 16000)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
