# ⚽ SmartStats
Trabajo de Fin de Grado - Plataforma de estadísticas deportivas con IA

SmartStats es una plataforma web para la consulta y visualización de estadísticas históricas de fútbol europeo. La aplicación combina mecanismos tradicionales de navegación con un sistema de consultas en lenguaje natural basado en inteligencia artificial, permitiendo acceder a información compleja de forma sencilla.

## Características
- Consulta de estadísticas históricas de jugadores y equipos.
- Visualización de clasificaciones de las principales ligas europeas.
- Generación de gráficos interactivos.
- Historial de consultas realizadas.
- Sistema NL → SQL basado en modelos de lenguaje.
- Arquitectura basada en microservicios.
- Procesos ETL para la obtención y transformación de datos deportivos.

## Tecnologías
### Backend
- Python
- FastAPI
- SQLAlchemy
- Pandas
### Frontend
- React
- React Router DOM
- Recharts
### Base de datos
- PostgreSQL
### ETL
- SoccerData
### Inteligencia Artificial
- Google Gemini
### Despliegue
- Docker
- Docker Compose

## Arquitectura (inicial)
La solución está compuesta por:

- Frontend web desarrollado en React.
- Conjunto de microservicios implementados con FastAPI.
- Base de datos PostgreSQL para el almacenamiento persistente.
- Procesos ETL encargados de la extracción y transformación de los datos.
- Servicio de consultas inteligentes basado en modelos Gemini.

## Uso de la IA Generativa

Durante la realización de este Trabajo de Fin de Grado hemos hecho uso de herramientas de inteligencia artificial generativa como apoyo puntual en determinadas tareas durante el proceso de desarrollo.

Se empleó para la revisión de aspectos ortográficos, gramaticales y de estilo de la memoria, así como para la detección de errores, análisis de fragmentos de código y resolución de dudas relacionadas con las tecnologías utilizadas.

El uso de estas herramientas se limitó a funciones de asistencia y apoyo al desarrollo, manteniendo en todo momento la supervisión humana sobre las decisiones adoptadas, el diseño de la solución propuesta, la implementación del software y la redacción final del documento. La responsabilidad, sobre el contenido, los resultados obtenidos y las conclusiones presentadas corresponde íntegramente al autor del trabajo, de acuerdo con las recomendaciones para el uso responsables de la inteligencia artificial en el ámbito académico establecidas por al Universidad de Granada. Fuente: https://ceprud.ugr.es/sites/centros/ceprud/public/ficheros/Recomendaciones_IA_en_UGR.pdf

## Autor

Antonio Pancorbo

Trabajo Fin de Grado en Ingeniería Informática
Universidad de Granada
