# Configuración

Los prompts usan variables entre `{{ }}` para no publicar identificadores internos. Para usarlos, reemplazá cada variable por el valor real **en la tarea programada**, no en este repositorio.

## Informe semanal

| Variable | Qué es | Ejemplo |
|---|---|---|
| `{{NOMBRE_PLANILLA_INFORME}}` | Nombre de la planilla de Google Sheets | `Informe semanal` |
| `{{ID_PLANILLA_INFORME}}` | ID de la planilla (lo que va entre `/d/` y `/edit` en la URL) | `1AbC...xyz` |
| `{{HOJA_FIJA}}` | Hoja con la fórmula que trae los eventos de jueves a jueves | `Semana fija` |
| `{{SHEET_ID_HOJA_FIJA}}` | sheetId numérico de esa hoja (`gid=` en la URL) | `123456789` |

## Seguimiento de fechas

| Variable | Qué es | Ejemplo |
|---|---|---|
| `{{NOMBRE_DOC_SEGUIMIENTO}}` | Google Doc donde vive la tabla de seguimiento | `Seguimiento DG` |
| `{{ID_DOC_SEGUIMIENTO}}` | ID de ese doc | `1AbC...xyz` |
| `{{TAB_SEGUIMIENTO}}` | Pestaña con las tablas EN CURSO / CERRADOS | `t.xxxxxxxx` |
| `{{TAB_CIRCUITO}}` | Pestaña con el criterio de validación de venues | `t.yyyyyyyy` |
| `{{NOMBRE_DOC_PUNTEO}}` / `{{ID_DOC_PUNTEO}}` | Doc con las minutas de la reunión semanal | `Minutas` / `1AbC...xyz` |
| `{{GRUPO_PLANIFICACION}}` | Grupo de WhatsApp donde ingresan y se validan fechas | `Fechas eventos` |
| `{{GRUPO_LEGALES}}` | Grupo de WhatsApp del circuito formal con Legales | `Circuito legales` |

## Reporte semanal

| Variable | Qué es | Ejemplo |
|---|---|---|
| `{{MAIL_REPORTE}}` | Dirección que envía el reporte semanal | `coordinacion@ejemplo.gob.ar` |
| `{{ASUNTO_REPORTE}}` | Comienzo del asunto del mail | `Reporte semanal` |
| `{{TAB_REPORTE}}` | Pestaña del doc de seguimiento donde se vuelca el reporte | `t.zzzzzzzz` |

`reporte_tab.py` también acepta las variables de entorno `REPORTE_REMITENTE` y `REPORTE_TITULO` para el texto de la nota y el título de la pestaña.

## Roles

Los prompts nombran roles en lugar de personas:

- **Director/a** y **jefe/a de gabinete** de la Dirección General: validan las fechas según el criterio de cada venue.
- **Área de coordinación de eventos**: lleva la agenda general e informa las fechas que ingresan.
- **Legales**: sigue el circuito formal (prefactibilidad, documentación, firmas).
