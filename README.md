# DPPPS — Sistema de Consolidación de Informes Gerenciales

## Requisitos previos

- Python 3.9 o superior
- MariaDB o MySQL corriendo localmente

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

## Tipos de actividad

En el menú lateral, la pantalla **Tipos de actividad** permite consultar el catálogo y, para usuarios con permisos de escritura, agregar tipos y cambiar sus nombres. Los tipos no se pueden eliminar. El catálogo completo se usa en los formularios, filtros, importación y reportes de actividades. Cada descarga de la plantilla de importación incluye en el desplegable de tipo de actividad las opciones vigentes en la base de datos.