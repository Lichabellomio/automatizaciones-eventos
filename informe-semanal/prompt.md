# Informe semanal de eventos masivos

**Frecuencia:** jueves 07:47 (America/Buenos_Aires)
**Conectores:** Google Sheets
**Entrega:** mensaje en el chat, listo para copiar y pegar en WhatsApp

> Los valores entre `{{ }}` se definen en [`config.example.md`](../config.example.md).

---

## Prompt

Tarea semanal (corre los jueves) para el equipo de Eventos Masivos. Respondé siempre en español argentino, tono profesional y directo, sin introducciones de cortesía. No inventes datos: si algo falla, decilo.

**Planilla:** Google Sheets `{{NOMBRE_PLANILLA_INFORME}}`, ID `{{ID_PLANILLA_INFORME}}`. La hoja `{{HOJA_FIJA}}` (sheetId `{{SHEET_ID_HOJA_FIJA}}`) tiene en A2 una fórmula `=SORT('Fórmula'!A2:F;1;TRUE)` que trae los eventos de HOY a HOY+7. Columnas: FECHA, EVENTO, LUGAR, AFORO, APERTURA, CIERRE.

### Paso 1 — Crear la hoja de la semana (sin fórmulas)

1. Calculá la fecha de hoy y la del jueves siguiente (hoy+7). Nombre de la hoja: `D/M al D/M` sin ceros a la izquierda (ej.: `19/11 al 26/11`).
2. Con `get_spreadsheet` listá las hojas. Si ya existe una con ese nombre, no la crees de nuevo: pasá al paso 2 usando esa hoja.
3. Con `update_spreadsheet`, en un solo batch:
   - `duplicateSheet` de la hoja fija, con el nombre calculado, en la posición 1.
   - `copyPaste` desde la hoja fija hacia la nueva, mismo rango, `PASTE_VALUES` (reemplaza la fórmula por valores).
   - `updateSheetProperties`: `frozenRowCount` 1.
   - `repeatCell` con formatos: columna A fecha `dd/mm/yyyy`; columna D número `#,##0`; columnas E–F hora `H:mm:ss`.
4. Verificá que la columna A de la hoja nueva no tenga fórmulas. Si alguna fila tiene fecha fuera del rango hoy..hoy+7, borrala.
5. Agregá un filtro básico sobre el rango de datos.

La hoja queda para que la revise el área de coordinación de eventos, que lleva la agenda general de la Ciudad e indica eventos faltantes o a quitar.

### Paso 2 — Generar el mensaje

1. Con `get_values` leé `'NOMBRE_HOJA'!A1:F1000` y guardá la respuesta JSON en `valores.json`.
2. Corré [`informe.py`](informe.py): `python3 informe.py valores.json DD/MM/AAAA` (fecha de hoy).

### Paso 3 — Entregar

Enviá: (a) una línea con el nombre de la hoja creada (o aviso de que ya existía) y cuántos eventos tiene; (b) el mensaje generado completo dentro de un bloque de código, listo para copiar. La sección POSTALES queda vacía. No modifiques ninguna otra hoja de la planilla.
