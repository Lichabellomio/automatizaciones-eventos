# Automatizaciones para Eventos Masivos

Tareas programadas con [Claude](https://claude.ai) que automatizan parte del trabajo de seguimiento de eventos masivos en la Ciudad de Buenos Aires: el armado del informe semanal, la incorporación del reporte semanal de fechas que llega por mail y el seguimiento del circuito de validación de fechas.

![Tests](https://github.com/Lichabellomio/automatizaciones-eventos/actions/workflows/tests.yml/badge.svg)

> Versión pública para portfolio: los identificadores de documentos, grupos y personas están reemplazados por variables y roles. Ver [`config.example.md`](config.example.md).

## Qué hay

| Automatización | Cuándo corre | Qué hace | Herramientas |
|---|---|---|---|
| [Informe semanal](informe-semanal/) | Jueves 07:47 | Congela en una hoja nueva los eventos de jueves a jueves para revisión y arma el mensaje "Principales eventos de la semana" | Google Sheets · Python |
| [Reporte semanal](reporte-semanal/) | Lunes 08:41 | Lee el PDF del reporte semanal que llega por mail, actualiza un acumulado de eventos, la bandeja en consulta y los eventos en observación, y redacta las novedades de la semana | Gmail · Google Docs · Python |
| [Seguimiento de fechas](seguimiento-fechas/) | Cada 2 h (L a V, 9 a 19) | Lee dos grupos de WhatsApp y las minutas de la reunión semanal, y mantiene al día una tabla con el estado de cada fecha en el circuito de validación | WhatsApp Web (Claude in Chrome) · Google Docs |

## Cómo funciona

```mermaid
flowchart LR
    subgraph Informe semanal
        A[Planilla con fórmula<br/>jueves a jueves] -->|copia como valores| B[Hoja D/M al D/M<br/>para revisión]
        B --> C[informe.py]
        C --> D[Mensaje listo<br/>para WhatsApp]
    end
    subgraph Reporte semanal
        L[Mail con PDF<br/>del reporte] -->|pdftotext| M{Claude}
        M -->|delta.json| N[reporte_tab.py]
        N -->|batchUpdate por tandas| O[Pestaña con eventos,<br/>bandeja y novedades]
    end
    subgraph Seguimiento de fechas
        E[WhatsApp:<br/>planificación] --> H{Claude}
        F[WhatsApp:<br/>legales] --> H
        G[Minutas de la<br/>reunión semanal] --> H
        H --> I[Tabla EN CURSO]
        I -->|circuito terminado| J[Tabla CERRADOS]
        H -.->|solo si hubo cambios| K[Aviso con resumen]
    end
```

## Criterios de diseño

- **No inventar datos.** Lo que no está claro en las fuentes queda marcado como "a confirmar".
- **Incremental.** Cada corrida lee desde la última marca registrada en el documento, así una corrida perdida (computadora apagada) se recupera sola en la siguiente.
- **Silencio por defecto.** Solo notifica cuando hay novedades o un error real.
- **Solo lectura en WhatsApp y Gmail.** Nunca escribe, responde ni envía mensajes.
- **El modelo decide, el script escribe.** Cuando la escritura en Google Docs es compleja (índices en UTF-16, varias tablas), el modelo arma solo los cambios y un script genera y verifica los requests.
- **Cuidar el uso.** Las tareas frecuentes usan un modelo más liviano, leen primero en texto plano y terminan apenas confirman que no hay novedades.
- **Prompts estructurados:** rol, contexto, objetivo, formato y restricciones.

## Estructura

```
├── informe-semanal/
│   ├── prompt.md          prompt de la tarea programada
│   ├── informe.py         genera el mensaje a partir de la planilla
│   └── ejemplo/           datos de ejemplo
├── reporte-semanal/
│   ├── prompt.md          prompt de la tarea programada
│   └── reporte_tab.py     parse / apply / build / split / verify de la pestaña
├── seguimiento-fechas/
│   └── prompt.md          prompt de la tarea programada
├── tests/                 tests de los scripts (corren en GitHub Actions)
└── config.example.md      variables y roles
```

## Probar el script

```bash
python3 informe-semanal/informe.py informe-semanal/ejemplo/valores.json 19/11/2026
python3 -m unittest discover -s tests -v
```
