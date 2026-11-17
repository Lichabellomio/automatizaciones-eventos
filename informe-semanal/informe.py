"""Genera el mensaje semanal de "Principales eventos de la semana".

Lee la respuesta JSON de Google Sheets (values.get) con las columnas
FECHA | EVENTO | LUGAR | AFORO | APERTURA | CIERRE y arma un mensaje con
formato de WhatsApp, día por día, de jueves a jueves.

Uso:
    python3 informe.py valores.json DD/MM/AAAA
"""
import json
import re
import sys
import unicodedata
from datetime import date, timedelta

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

# Venues donde interviene en campo el equipo de Mitigación (configurable).
MITIGACION = ["river", "monumental", "ferro", "huracan", "duco", "velez", "amalfitani",
              "campo argentino de polo", "campo de polo", "parque de la ciudad",
              "parque sarmiento"]
NOTA = " _Con participación en campo del equipo de Mitigación de DGCETT_"


def norm(s):
    """Minúsculas y sin tildes, para comparar nombres de venues."""
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def parse_fecha(s):
    d, m, y = s.strip().split("/")
    return date(int(y), int(m), int(d))


def aforo(s):
    n = re.sub(r"\D", "", str(s))
    return f"{int(n):,}".replace(",", ".") if n else "s/d"


def leer_eventos(rows):
    eventos = []
    for r in rows[1:]:
        if len(r) < 3 or not r[0].strip():
            continue
        eventos.append((parse_fecha(r[0]), r[1].strip(), r[2].strip(),
                        r[3] if len(r) > 3 else ""))
    return eventos


def armar_mensaje(eventos, inicio):
    fin = inicio + timedelta(days=7)
    out = ["📅 *PRINCIPALES EVENTOS DE LA SEMANA*", "",
           f"_Del {DIAS[inicio.weekday()]} {inicio.day} de {MESES[inicio.month - 1]} al "
           f"{DIAS[fin.weekday()]} {fin.day} de {MESES[fin.month - 1]}_", "",
           "🗓️ *_RESUMEN_* 🗓️", ""]
    for i in range(8):
        dia = inicio + timedelta(days=i)
        out.append(f"*{DIAS[dia.weekday()]} {dia.day}/{dia.month}*")
        del_dia = [e for e in eventos if e[0] == dia]
        if not del_dia:
            out.append("- Sin eventos masivos previstos.")
        for _, ev, lugar, af in del_dia:
            lugar = re.sub(r"\s*\(Esp\. Verde Pub\.\)", "", lugar, flags=re.I).strip()
            linea = f"- {ev} en {lugar} ({aforo(af)} asistentes)."
            if any(k in norm(lugar) for k in MITIGACION):
                linea += NOTA
            out.append(linea)
        out.append("")
    out += ["🌆 *POSTALES* 🌆", ""]
    return "\n".join(out)


def main(argv):
    data = json.load(open(argv[1], encoding="utf-8"))
    rows = data["values"] if isinstance(data, dict) else data
    eventos = leer_eventos(rows)
    inicio = parse_fecha(argv[2]) if len(argv) > 2 else min(e[0] for e in eventos)
    print(armar_mensaje(eventos, inicio))


if __name__ == "__main__":
    main(sys.argv)
