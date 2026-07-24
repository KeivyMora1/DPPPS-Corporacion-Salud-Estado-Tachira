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

| Qué hacer                        | Comando                             |
| -------------------------------- | ----------------------------------- |
| Instalar dependencias            | `pip install -r requirements.txt`   |
| Setup inicial de BD (1 sola vez) | `python db.py`                      |
| Iniciar la aplicación            | `python main.py`                    |
| Cambiar configuración de BD      | Editar `db.py` → sección `DATABASE` |

---

## Actualizar la base de datos desde `schema.sql`

Recomendado: antes de aplicar cambios, haz una copia de seguridad de la base de datos.

- Copia de seguridad (Linux/macOS/Windows PowerShell):

```bash
mysqldump -h localhost -P 3306 -u root -p dppps_informes > backup_dppps_informes.sql
```

- Aplicar el `schema.sql` con el cliente MySQL:

```bash
mysql -h localhost -P 3306 -u root -p dppps_informes < schema.sql
```

- Alternativa (cross-platform): usar el helper Python incluido:

```bash
python scripts/update_db.py        # aplica schema.sql usando la configuración de db.py
python scripts/update_db.py --backup  # primero intenta crear un dump antes de aplicar
```

El script `scripts/update_db.py` lee la configuración de conexión en la sección `DATABASE` de `db.py`.
Si tu usuario no tiene contraseña, omite `-p` o ajusta `db.py` con la credencial correcta.
