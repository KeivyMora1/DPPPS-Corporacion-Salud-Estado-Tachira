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

Abre `config/settings.py` y ajusta la contraseña de tu MariaDB/MySQL:

```python
"password": "tu_contraseña_aqui"
```

### 3. Ejecutar el setup inicial

> Solo se hace **una vez** para crear la base de datos y el usuario admin.

```bash
python db/setup.py
```

Cuando lo pida, ingresa la contraseña que quieres para el usuario `admin`.

### 4. Iniciar la aplicación

```bash
python main.py
```

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: la que ingresaste en el paso 3 (o `admin123` si presionaste Enter)
