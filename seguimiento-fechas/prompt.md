# Seguimiento de planificación de fechas

**Frecuencia:** cada 2 horas, de 09:04 a 19:04, de lunes a viernes (America/Buenos_Aires)
**Modelo:** Sonnet, para cuidar el límite de uso del plan
**Conectores:** Google Docs + Google Drive + Claude in Chrome (WhatsApp Web)
**Entrega:** tabla actualizada en un Google Doc y aviso breve solo si hubo cambios

> Los valores entre `{{ }}` se definen en [`config.example.md`](../config.example.md).

---

## Prompt

**Idioma (regla obligatoria):** todo lo que escribas va en español argentino: mensajes, respuesta final, resúmenes y texto del documento. Si necesitás citar un error en inglés, citalo y explicalo en español.

Tarea programada para el equipo de Eventos Masivos. Tono profesional y directo, sin introducciones de cortesía. No inventes datos: lo que no esté claro en las fuentes se marca **"a confirmar"**.

### Ahorro de uso (prioridad)

No imprimas JSON grande en pantalla ni hagas capturas salvo que sean imprescindibles. No releas documentos completos sin necesidad y terminá apenas confirmes que no hay novedades.

### Ventana de Chrome (obligatorio)

Cada corrida abre su propio grupo de pestañas. Al terminar, **siempre** cerrá todas las pestañas del grupo (`tabs_context_mcp` → `tabs_close_mcp` una por una), haya salido bien, sin novedades o con error. WhatsApp Web admite una sola pestaña activa.

### Disponibilidad

La tarea depende de que la computadora esté prendida, con Chrome, la extensión conectada y WhatsApp Web con sesión. Si algo de eso no está (por ejemplo, WhatsApp pide QR), cerrá la ventana y terminá **en silencio**: no toques el documento ni notifiques. Como cada corrida lee todo lo posterior a la última marca, la siguiente corrida disponible se pone al día sola. Solo avisá si falla Google Docs o pasa algo inesperado con WhatsApp abierto y con sesión.

### Hora

El entorno no tiene instalada la zona horaria de Argentina. Para la hora de Buenos Aires: `date -u -d '-3 hours' '+%d/%m/%Y %H:%M'`. Los horarios de WhatsApp Web ya están en hora local.

### Objetivo

Mantener actualizada la pestaña `{{TAB_SEGUIMIENTO}}` del Google Doc `{{NOMBRE_DOC_SEGUIMIENTO}}` (ID `{{ID_DOC_SEGUIMIENTO}}`) con las novedades de fechas de eventos y su avance en el circuito formal.

### Fuentes

1. **Grupo de WhatsApp `{{GRUPO_PLANIFICACION}}`.** El área de coordinación de eventos avisa las fechas que ingresan y la Dirección General (director, jefe de gabinete, equipo de seguimiento) las valida. Los mensajes propios aparecen sin nombre.
2. **Grupo de WhatsApp `{{GRUPO_LEGALES}}`.** Buscalo con el buscador de chats y verificá el nombre en el encabezado (hay grupos con nombres parecidos). Ahí el equipo de Legales y el jefe de gabinete siguen el circuito formal: prefactibilidades, documentación, cartas de intención, observaciones, firmas. Tomá **solo** lo vinculado a eventos y fechas; ignorá postales, contraprestaciones de comunicación y notas administrativas. Si un evento aparece solo en este grupo, igual se registra.
3. **Google Doc `{{NOMBRE_DOC_PUNTEO}}`** (ID `{{ID_DOC_PUNTEO}}`). Solo las secciones "Seguimiento eventos dd/mm" (reunión semanal de seguimiento; las más nuevas arriba). Ignorar "Postales" y cualquier otra sección.
4. **Criterio de validación:** pestaña `{{TAB_CIRCUITO}}` del mismo doc. Define qué venues requieren validación de la Dirección y cuáles se evalúan por saturación de corredor y fecha. Se registra **cualquier** evento que pase por los grupos, no solo los del circuito.

### Año de las fechas

Si una fecha no trae año, asumí el año próximo (la mayoría de los pedidos son con mucha anticipación). Usá el año en curso solo si el mensaje lo dice o si es evidente que el evento es de las próximas semanas. Si hay una contradicción real entre fuentes, indicala en la celda.

### Pasos

1. **Marca de lectura (lectura liviana):** leé el doc en texto plano con `Google_Drive.read_file_content` y tomá del párrafo **Fuentes** hasta dónde se leyó cada fuente, más el contenido actual de las tablas. Usá `read_doc` (pesado, con índices) solo en el paso 5, si hay algo que escribir. Estructura de la pestaña:
   - título;
   - párrafo **Fuentes** con la marca `Última actualización: DD/MM/AAAA HH:MM` y hasta dónde se leyó cada fuente;
   - **EN CURSO**: tabla de 8 columnas (Evento | Fecha/s | Venue | Circuito | Situación / conflicto | Estado | Próximo paso – responsable | Última novedad);
   - **CERRADOS**: tabla de 6 columnas (Evento | Fecha/s | Venue | Resultado | Conclusión final | Fecha de cierre).
2. **WhatsApp:** cargá las herramientas de Claude in Chrome en un solo `ToolSearch`, abrí `https://web.whatsapp.com/` (si aparece "Usar aquí", hacé clic). Abrí el primer grupo y extraé los mensajes (`get_page_text`, o `javascript_tool` leyendo el `innerText` de `#main [role="row"]`, que incluye los "Leer más" y las respuestas citadas). Scrolleá hasta cubrir todo lo posterior a la marca. Repetí con el segundo grupo. **No escribas ni envíes nada en WhatsApp.**
3. **Minutas:** leelas solo los jueves y viernes, o si su marca es anterior al último jueves. Buscá las secciones "Seguimiento eventos dd/mm" más nuevas que la marca.
4. Si no hay nada nuevo en ninguna fuente, no modifiques el documento, cerrá la ventana y terminá sin notificar.
5. **Actualizá EN CURSO:** un evento = una fila (cruzá ambos grupos). Si existe, actualizá Fecha/s, Situación, Estado, Próximo paso y Última novedad (`dd/mm hh:mm – autor`, indicando el grupo de origen). Para eso, leé la pestaña con `read_doc` y procesala con Python filtrando por tabId. Si es nuevo, agregá una fila al final (`insertTableRow` + `insertText`, procesando índices de mayor a menor). Texto de la tabla a 8 pt.
   - **Situación / conflicto no es un historial:** muestra solo el estado actual, en 1 o 2 oraciones, con el formato `[dd/mm hh:mm – Autor] estado actual` (por ejemplo, `[17/11 16:53 – Jefatura] Se rechaza el 22/11; se espera un nuevo pedido por el 23/11.`). Si la novedad viene de Legales, el autor lleva "(Legales)"; si viene de las minutas, el formato es `[dd/mm – Minutas]`. Cada actualización **reemplaza** la celda. Si hay celdas con el formato viejo, reescribilas.
   Estados posibles: Ingresó / Aviso de coordinación / En análisis de la Dirección / Validado por la Dirección / Aviso a coordinación y Legales / Circuito formal iniciado / Observado / Buscando fecha alternativa / Rechazado.
6. **Cierre:** cuando un evento termina el circuito (validado con OK final, o rechazado / dado de baja), borrá su fila de EN CURSO y agregá una en CERRADOS con Resultado, Conclusión final (1-2 oraciones) y Fecha de cierre.
7. Actualizá la marca del párrafo Fuentes con la hora actual y hasta dónde se leyó cada fuente.
8. Verificá, releyendo en texto plano, que no haya celdas corridas.
9. Si hubo cambios, mandá un resumen breve: eventos nuevos, cambios de estado (indicando el grupo de origen), cerrados y dudas "a confirmar".
10. Antes de terminar, confirmá que no quedó ninguna pestaña del grupo abierta.
