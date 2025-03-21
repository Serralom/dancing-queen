# 🕺 Dancing Queens - Telegram Bot

**Dancing Queens** es un bot de **Telegram** desarrollado en **Python** que permite a los usuarios registrar y consultar los resultados de los **puzzles diarios de LinkedIn**, específicamente **"Queens" y "Tango"**. Utiliza **PostgreSQL** para gestionar los datos y está diseñado con una arquitectura modular y buenas prácticas de desarrollo.

## ✨ Características

- 📊 Registro de tiempos de los juegos **Queens** y **Tango**.
- 🏆 Consulta de rankings diarios, anuales e históricos.
- ⚡ Visualización de los mejores tiempos y promedios de los jugadores.
- 🗄️ Base de datos PostgreSQL con consultas optimizadas.
- ☁️ Despliegue en Railway para acceso remoto.
- 🔒 Seguridad y modularidad en el código.

## 🛠️ Tecnologías utilizadas

- **Lenguaje**: Python
- **Base de datos**: PostgreSQL
- **Framework de Telegram**: [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **Gestión de dependencias**: requirements.txt
- **Cloud Hosting**: Railway
- **ORM / Conexión DB**: psycopg2

## 🚀 Instalación y ejecución

### 1️⃣ Clonar el repositorio

```
git clone https://github.com/Serralom/dancing-queen.git
cd dancing-queen
```

### 2️⃣ Crear un entorno virtual e instalar dependencias

```
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scriptsctivate
pip install -r requirements.txt
```

### 3️⃣ Configurar las variables de entorno

Crear un archivo `.env` en la raíz del proyecto con los siguientes valores:

```
BOT_TOKEN=TU_TOKEN_DE_TELEGRAM
DATABASE_HOST=tu_host
DATABASE_USER=tu_usuario
DATABASE_PASSWORD=tu_contraseña
DATABASE_NAME=tu_basededatos
DATABASE_PORT=5432
```

### 4️⃣ Ejecutar el bot

```
python main.py
```

El bot comenzará a escuchar y responder a comandos en Telegram.

## 📌 Comandos disponibles

| Comando        | Descripción |
|---------------|------------|
| /start        | Mensaje de bienvenida. |
| /record       | Registra los tiempos de Queens y Tango. |
| /results      | Muestra opciones de ranking. |
| /hoy         | Ranking del día. |
| /anual       | Ranking anual. |
| /historico   | Ranking histórico. |
| /mejores_tiempos | Mejores tiempos y promedios. |
| /todo        | Muestra todos los rankings y estadísticas. |

## 📖 Estructura del proyecto

```
dancing-queen/
│── main.py             # Punto de entrada del bot
│── commands.py         # Manejo de los comandos de Telegram
│── queries.py          # Interacciones con la base de datos
│── utils.py            # Funciones auxiliares
│── requirements.txt    # Dependencias del proyecto
└── .env                # Configuración de variables de entorno
```

## ⚠️ Notas y consideraciones

- **El bot requiere un token de Telegram** que puedes obtener en [BotFather](https://core.telegram.org/bots/tutorial#obtain-your-bot-token).
- **Se recomienda PostgreSQL 12 o superior** para garantizar compatibilidad.
- **El bot solo acepta tiempos en el formato adecuado** (Ej: `1:25 40` o `85 243`).

---