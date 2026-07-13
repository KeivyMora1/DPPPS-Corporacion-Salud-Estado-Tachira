# DPPPS — Sistema de Consolidación de Informes Gerenciales

## Requisitos previos

- Python 3.9 o superior
- MariaDB o MySQL corriendo localmente

---

## Estructura del proyecto

```
PROYECTO-TRAYECTO-2/
├── db.py            ← Toda la lógica: conexión, DAOs, controladores, servicios
├── utils.py         ← Funciones de soporte (query, scalar, centrar_ventana)
├── main.py          ← Punto de entrada: inicia el login y la ventana principal
├── schema.sql       ← Script SQL para crear las tablas de la base de datos
├── pantallas/       ← Todas las vistas Tkinter
│   ├── login.py
│   ├── principal.py
│   ├── dashboard.py
│   ├── actividades.py
│   ├── catalogos.py
│   ├── importacion.py
│   └── reportes.py
├── assets/          ← Recursos estáticos (plantillas, íconos)
├── exports/         ← Reportes PDF y Excel generados
└── uploads/         ← Archivos de evidencia adjuntados
```

---

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar la base de datos

Abre `db.py` y ajusta la sección **CONFIGURACIÓN GENERAL** (inicio del archivo):

```python
MODO = "local"   # o "lan" si usas un servidor en red

DATABASE = {
    "local": {
        "host":     "localhost",
        "port":     3306,
        "user":     "root",
        "password": "tu_contraseña_aqui",   # ← cambia esto
        "database": "dppps_informes"
    },
    ...
}
```

### 3. Ejecutar el setup inicial

> Solo se hace **una vez** para crear la base de datos, las tablas y el usuario admin.

```bash
python db.py
```

Cuando lo pida, ingresa la contraseña que quieres para el usuario `admin`.

### 4. Iniciar la aplicación

```bash
python main.py
```

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: la que ingresaste en el paso 3 (o `admin123` si presionaste Enter)

---

## Configuración rápida (resumen)

| Qué hacer | Comando |
|-----------|---------|
| Instalar dependencias | `pip install -r requirements.txt` |
| Setup inicial de BD (1 sola vez) | `python db.py` |
| Iniciar la aplicación | `python main.py` |
| Cambiar configuración de BD | Editar `db.py` → sección `DATABASE` |
