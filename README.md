# archivomex-web
Proyecto de Archivomex Estadísticas históricas de México. CIDE-INEGI-CentroGEO

Esta aplicación, en versión preliminar de “Alpha”, es un experimento para visualizar las estadísticas históricas de México por equipo de cómputo, tableta o smartphone. La biblioteca de Población está disponible para consultar.

**Web Xtractor**

La versión web de Xtractor es un wrapper que se encarga de replicar el funcionamiento de las herramientas de escritorio de manera web.

Esta aplicación web utiliza Django como framework.

Para correr el proyecto es necesario replicar los siguientes pasos:

1. Clonar el repositorio.
2. Crear un entorno virtual.
3. Instalar los requerimientos.
4. Crear la base de datos con sqlite3.
5. Generar una nueva llave secreta.
6. Hacer las migraciones.
7. Actualizar las llaves para la API de Cloudinary

Debido a la arquitectura y capacidad de los servidores, únicamente se encuentra funcional el módulo de *Xtractor EHM 2014*.
