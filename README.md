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

En [constants.py](./constants.py), configura `MODO` y los datos de conexión a MySQL/MariaDB (`DATABASE`).

Indica el correo que se guardará en la cuenta propietaria. Para ello, crea un archivo `.env` a partir de `.env.example` y reemplaza el valor de `OWNER_EMAIL`:

```env
OWNER_EMAIL=escribe_aqui_el_correo
```

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

Ejecuta este comando para crear la base de datos, sus tablas y el usuario propietario con el correo configurado en `OWNER_EMAIL`:

```bash
python -m db.setup
```

Si la base de datos ya existe, aplica los cambios del esquema antes de iniciar la aplicación:

```bash
python scripts/update_db.py
```

El catálogo geográfico vigente de Táchira (municipios y parroquias) está definido en la aplicación y no requiere borrar ni modificar registros existentes en la tabla legada `parroquia`.

### 5️⃣ Respaldar y restaurar la base de datos

**Crear un respaldo** (opcional pero recomendado antes de aplicar cambios de esquema):

```powershell
python scripts\update_db.py --backup
```

- El comando genera un archivo `backup_<nombre_bd>.sql` en el directorio del proyecto.
- Si `mysqldump` no está disponible en el PATH, el script mostrará un mensaje de error claro y abortará la operación. En ese caso, instala las *MySQL client tools* o elimina la opción `--backup`.

**Restaurar un respaldo**

```powershell
# Ejemplo: restaurar el backup creado anteriormente
mysql -u root -p dppps_informes < backup_dppps_informes.sql
```

> ⚠️ Asegúrate de que la base de datos `dppps_informes` exista antes de restaurar. Puedes crearla rápidamente con:
>
> ```powershell
> python -m db.setup
> ```
>
> Si la base ya contiene datos, el `mysqldump` restaurará los contenidos tal cual estaban al momento del backup.

**Nota**: El script `scripts/update_db.py` también permite aplicar el nuevo esquema sin crear respaldo:

```powershell
python scripts\update_db.py          # Usa mysql‑connector‑python
# o
python scripts\update_db.py --use-cli  # Usa el cliente mysql
```

---


**Credenciales por defecto:**

- Usuario: `admin`
- Contraseña: `12345678`

El setup crea esta cuenta con rol de **propietario** al inicializar una base de datos sin usuarios. Si la tabla ya contiene usuarios, no los modifica ni crea otra cuenta. Cambia la contraseña predeterminada después del primer inicio de sesión.

## Tipos de actividad

En el menú lateral, la pantalla **Tipos de actividad** permite consultar el catálogo y, para usuarios con permisos de escritura, agregar tipos y cambiar sus nombres. Los tipos no se pueden eliminar. El catálogo completo se usa en los formularios, filtros, importación y reportes de actividades. Cada descarga de la plantilla de importación incluye en el desplegable de tipo de actividad las opciones vigentes en la base de datos.

## Cuentas

La opción **Cuentas**, debajo de **Tipos de actividad** en el menú, solo está disponible para el usuario propietario. Desde allí puede crear cuentas de usuario asignando nombre, apellido, nombre de usuario, correo, contraseña inicial y, opcionalmente, el rol de administrador. Las cuentas nuevas quedan pendientes de verificación: al iniciar sesión por primera vez con sus credenciales, el usuario recibirá un código en su correo y deberá verificarlo antes de acceder.

Las plantillas incluyen la hoja visible **Catalogos** con las opciones que alimentan los desplegables de ubicación. No la elimines ni la ocultes.

## Actualizar el ejecutable

Para actualizar el ejecutable de la aplicación, ejecuta desde la raíz del proyecto:

```bash
python -m PyInstaller --clean DPPPS.spec
```