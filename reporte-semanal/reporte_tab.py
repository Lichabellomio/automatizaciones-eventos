#!/usr/bin/env python3
"""Mantiene la pestaña "Reporte semanal" de un Google Doc a partir del reporte que llega por mail.
Uso:
  python3 -I reporte_tab.py parse  <dump_read_doc.txt> <tabId> <state.json>
  python3 -I reporte_tab.py apply  <state.json> <delta.json> <DD/MM/AAAA hoy>
  python3 -I reporte_tab.py build  <state.json> <tabId> <requests.json> [<dump_read_doc.txt>]
  python3 -I reporte_tab.py split  <requests.json>            (genera chunk0.json, chunk1.json...)
  python3 -I reporte_tab.py verify <state.json> <dump_read_doc.txt> <tabId>

Variables de entorno opcionales: REPORTE_REMITENTE (quién manda el reporte) y REPORTE_TITULO.
"""
import json, os, re, sys, unicodedata
from datetime import date

REMITENTE = os.environ.get("REPORTE_REMITENTE", "el área de coordinación de eventos")

EV_COLS = ["Evento", "Fecha/s", "Lugar (* = mitigación)", "Productora", "Aforo",
           "Estado – Ubicación", "Ingreso", "Últ. reporte"]
CC_COLS = ["Fecha/s", "Evento", "Lugar", "Productora", "Público / Formato",
           "Días en consulta", "Score", "Aforo"]
OB_COLS = ["Fecha/s", "Evento", "Lugar", "Productora", "Aforo", "Ingreso"]
TITLE = os.environ.get("REPORTE_TITULO", "Reporte semanal de fechas")
H_EV, H_CC, H_OB, H_HI = ("EVENTOS REPORTADOS (acumulado)", "BANDEJA EN CCOO (al último corte)",
                          "EN OBSERVACIÓN (al último corte)", "HISTORIAL DE REPORTES")
H_NV = "NOVEDADES DE LA SEMANA"


def u16(s):
    return len(s.encode("utf-16-le")) // 2


def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def load_tab(dump, tab_id):
    d = json.load(open(dump))
    d = d.get("content", d)
    def walk(tabs):
        for t in tabs:
            if t["tabProperties"]["tabId"] == tab_id:
                return t
            r = walk(t.get("childTabs", []))
            if r:
                return r
    t = walk(d.get("tabs", []))
    if not t:
        sys.exit(f"No encontré la pestaña {tab_id}")
    return t["documentTab"]["body"]["content"]


def ptext(par):
    return "".join(e.get("textRun", {}).get("content", "") for e in par["elements"])


def cell_text(cell):
    return "\n".join(ptext(c["paragraph"]).rstrip("\n") for c in cell["content"] if "paragraph" in c).strip()


def parse(dump, tab_id, out):
    body = load_tab(dump, tab_id)
    st = {"meta": {}, "resumen": "", "eventos": [], "ccoo": [], "observacion": [], "historial": []}
    paras, last_h = [], None
    keys = {H_EV: "eventos", H_CC: "ccoo", H_OB: "observacion"}
    for el in body:
        if "table" in el:
            rows = [[cell_text(c) for c in r["tableCells"]] for r in el["table"]["tableRows"]]
            if last_h in keys:
                st[keys[last_h]] = rows[1:]  # sin encabezado
        elif "paragraph" in el:
            p = ptext(el["paragraph"]).strip()
            paras.append(p)
            if p:
                last_h = p
    for p in paras:
        m = re.search(r"Último reporte incorporado: (\d{1,2}/\d{1,2}/\d{4})(?: \(corte ([\d:]+)\))?", p)
        if m:
            st["meta"]["ultimo_reporte"], st["meta"]["corte"] = m.group(1), m.group(2) or ""
    if H_NV in paras and H_EV in paras:
        r = "\n".join(p for p in paras[paras.index(H_NV) + 1:paras.index(H_EV)] if p)
        st["resumen"] = "" if r == "(sin datos)" else r
    if H_HI in paras:
        st["historial"] = [p for p in paras[paras.index(H_HI) + 1:] if p]
    for k in ("eventos", "ccoo", "observacion"):
        st[k] = [r for r in st[k] if any(x.strip() for x in r) and r[0] != "(sin datos)"]
    json.dump(st, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"Estado: {len(st['eventos'])} eventos, {len(st['ccoo'])} CCOO, {len(st['observacion'])} observación; "
          f"último reporte {st['meta'].get('ultimo_reporte', 'ninguno')}")


def fechas(s):
    out = []
    for d, m, y in re.findall(r"(\d{1,2})/(\d{1,2})/(\d{4})", s or ""):
        try:
            out.append(date(int(y), int(m), int(d)))
        except ValueError:
            pass
    return out


def sort_key(s):
    y = re.search(r"/(\d{4})", s or "")
    m = re.search(r"/(\d{1,2})", s or "")
    d = re.search(r"(\d{1,2})", s or "")
    if not (y and m and d):
        return (9999, 99, 99)
    return (int(y.group(1)), int(m.group(1)), int(d.group(1)))


def apply(state_f, delta_f, hoy):
    st = json.load(open(state_f))
    de = json.load(open(delta_f))
    dd, mm, yy = map(int, hoy.split("/"))
    today = date(yy, mm, dd)
    ev = st["eventos"]
    nuevos = act = 0
    for up in de.get("upserts", []):
        row = (up["row"] + [""] * 8)[:8]
        key = norm(up.get("match") or row[0])
        idx = next((i for i, r in enumerate(ev) if norm(r[0]) == key), None)
        if idx is None:
            ev.append(row); nuevos += 1
        else:
            ev[idx] = row; act += 1
    for name in de.get("remove", []):
        ev[:] = [r for r in ev if norm(r[0]) != norm(name)]
    antes = len(ev)
    ev[:] = [r for r in ev if not fechas(r[1]) or max(fechas(r[1])) >= today]
    vencidos = antes - len(ev)
    ev.sort(key=lambda r: sort_key(r[1]))
    if "ccoo" in de:
        st["ccoo"] = [(r + [""] * 8)[:8] for r in de["ccoo"]]
    if "observacion" in de:
        st["observacion"] = [(r + [""] * 6)[:6] for r in de["observacion"]]
    st["meta"].update(de.get("meta", {}))
    if "resumen" in de:
        st["resumen"] = de["resumen"].strip()
    if de.get("historial_add"):
        st["historial"].insert(0, de["historial_add"])
    json.dump(st, open(state_f, "w"), ensure_ascii=False, indent=1)
    print(f"Nuevos: {nuevos} · Actualizados: {act} · Quitados por fecha vencida: {vencidos} · Total: {len(ev)}")


def build(state_f, tab_id, out, dump=None):
    st = json.load(open(state_f))
    meta = st["meta"]
    nota = (f"Fuente: reporte semanal por mail de {REMITENTE}, que llega los viernes. "
            f"Último reporte incorporado: {meta.get('ultimo_reporte', '-')}"
            + (f" (corte {meta['corte']})" if meta.get("corte") else "") +
            f". Actualizado: {meta.get('actualizado', '-')}. La tabla de eventos acumula todos los reportes "
            f"(cada fila muestra el último dato informado) y quita los eventos cuya última fecha ya pasó. "
            f"CCOO y Observación se reemplazan con cada reporte.")
    blocks = [("p", TITLE, "HEADING_1"), ("p", nota, "NOTE"),
              ("p", H_NV, "HEADING_2"), ("p", st.get("resumen") or "(sin datos)", "NORMAL_TEXT"),
              ("p", H_EV, "HEADING_2"), ("t", EV_COLS, st["eventos"]),
              ("p", H_CC, "HEADING_2"), ("t", CC_COLS, st["ccoo"]),
              ("p", H_OB, "HEADING_2"), ("t", OB_COLS, st["observacion"]),
              ("p", H_HI, "HEADING_2")] + [("p", h, "NORMAL_TEXT") for h in st["historial"]]
    reqs = []
    if dump:
        body = load_tab(dump, tab_id)
        end = body[-1]["endIndex"]
        if end - 1 > 1:
            reqs.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end - 1, "tabId": tab_id}}})
    loc = lambda i: {"index": i, "tabId": tab_id}
    rng = lambda a, b: {"startIndex": a, "endIndex": b, "tabId": tab_id}
    prev_is_table = True  # el primer insert cae en el párrafo vacío final
    for b in reversed(blocks):
        if b[0] == "p":
            _, text, style = b
            ins = text if prev_is_table else text + "\n"
            L = u16(text)
            reqs.append({"insertText": {"text": ins, "location": loc(1)}})
            reqs.append({"updateParagraphStyle": {"range": rng(1, 1 + L + 1 if not prev_is_table else 1 + L),
                         "paragraphStyle": {"namedStyleType": "NORMAL_TEXT" if style == "NOTE" else style},
                         "fields": "namedStyleType"}})
            if L:
                reqs.append({"updateTextStyle": {"range": rng(1, 1 + L),
                             "textStyle": {"italic": style == "NOTE", "bold": False,
                                           "fontSize": {"magnitude": 9 if style == "NOTE" else (10 if style == "NORMAL_TEXT" else (18 if style == "HEADING_1" else 13)), "unit": "PT"}},
                             "fields": "italic,bold,fontSize"}})
            prev_is_table = False
        else:
            _, cols, rows = b
            rows = rows or [["(sin datos)"] + [""] * (len(cols) - 1)]
            data = [cols] + rows
            nr, nc = len(data), len(cols)
            reqs.append({"insertTable": {"rows": nr, "columns": nc, "location": loc(1)}})
            s = 2
            cells = []
            for r in range(nr):
                for c in range(nc):
                    cells.append((s + 3 + r * (1 + 2 * nc) + 2 * c, str(data[r][c] if c < len(data[r]) else ""), r == 0))
            for p, t, hdr in reversed(cells):
                if t:
                    reqs.append({"insertText": {"text": t, "location": loc(p)}})
            # posiciones finales tras el llenado
            pos, fin = s + 3, []
            for i, (_, t, _h) in enumerate(cells):
                fin.append(pos)
                pos += u16(t) + (2 if (i + 1) % nc else 3)
            last_end = fin[-1] + u16(cells[-1][1]) + 1
            hdr_end = fin[nc - 1] + u16(cells[nc - 1][1])
            reqs.append({"updateTextStyle": {"range": rng(s + 1, last_end), "textStyle": {"bold": False,
                         "italic": False, "fontSize": {"magnitude": 8, "unit": "PT"}}, "fields": "bold,italic,fontSize"}})
            reqs.append({"updateTextStyle": {"range": rng(s + 3, hdr_end), "textStyle": {"bold": True},
                         "fields": "bold"}})
            reqs.append({"updateParagraphStyle": {"range": rng(s + 1, last_end),
                         "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"}, "fields": "namedStyleType"}})
            reqs.append({"updateTableCellStyle": {"tableRange": {"tableCellLocation": {
                "tableStartLocation": loc(s), "rowIndex": 0, "columnIndex": 0}, "rowSpan": 1, "columnSpan": nc},
                "tableCellStyle": {"backgroundColor": {"color": {"rgbColor": {"red": 0.85, "green": 0.9, "blue": 0.97}}}},
                "fields": "backgroundColor"}})
            prev_is_table = True
    json.dump({"requests": reqs}, open(out, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(reqs)} requests -> {out}")


def split(req_f, max_bytes="15000"):
    reqs = json.load(open(req_f))["requests"]
    chunks, cur, size = [], [], 0
    for q in reqs:
        s = len(json.dumps(q, ensure_ascii=False, separators=(",", ":")))
        if size + s > int(max_bytes) and cur:
            chunks.append(cur); cur, size = [], 0
        cur.append(q); size += s
    chunks.append(cur)
    for i, c in enumerate(chunks):
        open(f"chunk{i}.json", "w").write(json.dumps(c, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(chunks)} tandas: " + ", ".join(f"chunk{i}.json ({len(c)} requests)" for i, c in enumerate(chunks)))


def verify(state_f, dump, tab_id):
    parse(dump, tab_id, "/tmp/_check.json")
    a, b = json.load(open(state_f)), json.load(open("/tmp/_check.json"))
    ks = ("resumen", "eventos", "ccoo", "observacion", "historial")
    ok = all(a.get(k) == b.get(k) for k in ks)
    print("VERIFICACIÓN OK" if ok else "VERIFICACIÓN CON DIFERENCIAS: " +
          ", ".join(k for k in ks if a.get(k) != b.get(k)))


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"parse": parse, "apply": apply, "build": build, "split": split, "verify": verify}[cmd](*sys.argv[2:])
