# ============================================================
# services/excel_service.py
# Servicio de importación masiva de actividades desde Excel.
#
# Flujo:
#   1. Leer el archivo .xlsx con openpyxl
#   2. Validar que las columnas requeridas existen (cabecera)
#   3. Procesar fila a fila:
#      - Validar campos obligatorios y tipos de dato
#      - Resolver id_asic / id_tipo buscando en la BD por nombre
#      - Detectar duplicados mediante ActividadDAO.verificar_duplicado
#   4. Devolver un reporte con: filas_ok, filas_error, lista de errores
#   5. Si el llamador confirma, insertar todas las filas válidas
# ============================================================

from datetime import date, datetime

import openpyxl

from models.actividad import ActividadDAO
from models.asic import AsicDAO
from models.tipo_actividad import TipoActividadDAO


# Columnas que DEBEN estar en la hoja (cabecera, case-insensitive)
COLUMNAS_REQUERIDAS = [
    "asic",
    "tipo_actividad",
    "fecha_inicio",
    "fecha_fin",
    "lugar",
    "descripcion",
    "participantes",
]


class ExcelService:
    """
    Servicio encargado de leer un archivo Excel y convertir sus filas
    en registros de actividad, con validación detallada por fila.
    """

    def __init__(self, id_usuario_registro: int):
        """
        :param id_usuario_registro: ID del usuario que realiza la importación.
                                    Se asigna a todas las actividades creadas.
        """
        self.id_usuario_registro = id_usuario_registro
        self._actividad_dao = ActividadDAO()
        self._asic_dao = AsicDAO()
        self._tipo_dao = TipoActividadDAO()

        # Cachés para evitar consultas repetidas a la BD por cada fila
        self._cache_asic: dict[str, int | None] = {}   # nombre_lower -> id_asic
        self._cache_tipo: dict[str, int | None] = {}   # nombre_lower -> id_tipo

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def previsualizar(self, ruta_archivo: str) -> dict:
        """
        Lee el Excel y valida cada fila SIN insertar en BD.

        Retorna un dict con:
          - columnas: list[str]        — cabeceras detectadas
          - filas_validas: list[dict]  — filas listas para insertar
          - filas_error: list[dict]    — filas con problemas {numero_fila, datos_crudos, errores}
          - total_filas: int
        """
        wb = openpyxl.load_workbook(ruta_archivo, data_only=True)
        ws = wb.active

        # 1. Leer cabecera (primera fila)
        cabecera_raw = [str(c.value).strip() if c.value is not None else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
        cabecera_lower = [h.lower() for h in cabecera_raw]

        # 2. Validar columnas requeridas
        faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in cabecera_lower]
        if faltantes:
            raise ValueError(
                f"El archivo no tiene las columnas requeridas: {', '.join(faltantes)}.\n"
                f"Columnas detectadas: {', '.join(cabecera_raw)}"
            )

        # 3. Mapear índice de columna por nombre
        idx = {col: cabecera_lower.index(col) for col in COLUMNAS_REQUERIDAS}

        filas_validas = []
        filas_error = []

        for numero_fila, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            # Ignorar filas completamente vacías
            if all(v is None or str(v).strip() == "" for v in fila):
                continue

            datos_crudos = {col: fila[idx[col]] for col in COLUMNAS_REQUERIDAS}
            errores = []

            # 3a. Validar y parsear campos
            asic_nombre = str(datos_crudos["asic"]).strip() if datos_crudos["asic"] else ""
            tipo_nombre = str(datos_crudos["tipo_actividad"]).strip() if datos_crudos["tipo_actividad"] else ""
            lugar = str(datos_crudos["lugar"]).strip() if datos_crudos["lugar"] else ""
            descripcion = str(datos_crudos["descripcion"]).strip() if datos_crudos["descripcion"] else ""

            # Participantes: entero ≥ 0
            try:
                participantes = int(datos_crudos["participantes"])
                if participantes < 0:
                    raise ValueError()
            except (TypeError, ValueError):
                participantes = None
                errores.append("'participantes' debe ser un número entero ≥ 0.")

            # Fechas
            fecha_inicio = self._parsear_fecha(datos_crudos["fecha_inicio"])
            fecha_fin = self._parsear_fecha(datos_crudos["fecha_fin"])

            if fecha_inicio is None:
                errores.append("'fecha_inicio' no tiene formato de fecha válido (YYYY-MM-DD o DD/MM/YYYY).")
            if fecha_fin is None:
                errores.append("'fecha_fin' no tiene formato de fecha válido (YYYY-MM-DD o DD/MM/YYYY).")
            if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
                errores.append("'fecha_fin' no puede ser anterior a 'fecha_inicio'.")

            # Campos de texto obligatorios
            if not asic_nombre:
                errores.append("El campo 'asic' está vacío.")
            if not tipo_nombre:
                errores.append("El campo 'tipo_actividad' está vacío.")
            if not lugar:
                errores.append("El campo 'lugar' está vacío.")
            if not descripcion:
                errores.append("El campo 'descripcion' está vacío.")

            # 3b. Resolver IDs en BD (solo si los nombres están presentes)
            id_asic = None
            id_tipo = None

            if asic_nombre:
                id_asic = self._resolver_asic(asic_nombre)
                if id_asic is None:
                    errores.append(f"ASIC no encontrado en BD: «{asic_nombre}».")

            if tipo_nombre:
                id_tipo = self._resolver_tipo(tipo_nombre)
                if id_tipo is None:
                    errores.append(f"Tipo de actividad no encontrado en BD: «{tipo_nombre}».")

            # 3c. Verificar duplicado (solo si todos los campos clave son válidos)
            es_duplicado = False
            if id_asic and id_tipo and fecha_inicio and descripcion and not errores:
                es_duplicado = self._actividad_dao.verificar_duplicado(
                    id_asic, id_tipo, fecha_inicio, descripcion
                )
                if es_duplicado:
                    errores.append("Duplicado: ya existe una actividad con el mismo ASIC, tipo, fecha e inicio de descripción.")

            # 3d. Clasificar la fila
            fila_procesada = {
                "numero_fila": numero_fila,
                "id_asic": id_asic,
                "id_tipo": id_tipo,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "lugar": lugar,
                "descripcion": descripcion,
                "participantes": participantes,
                "datos_crudos": datos_crudos,
            }

            if errores:
                filas_error.append({**fila_procesada, "errores": errores})
            else:
                filas_validas.append(fila_procesada)

        return {
            "columnas": cabecera_raw,
            "filas_validas": filas_validas,
            "filas_error": filas_error,
            "total_filas": len(filas_validas) + len(filas_error),
        }

    def importar(self, filas_validas: list[dict]) -> dict:
        """
        Inserta en BD todas las filas ya validadas.

        Retorna un dict con:
          - insertadas: int
          - errores_al_insertar: list[dict] — errores inesperados durante la inserción
        """
        insertadas = 0
        errores_al_insertar = []

        for fila in filas_validas:
            try:
                self._actividad_dao.crear(
                    id_asic=fila["id_asic"],
                    id_tipo=fila["id_tipo"],
                    id_usuario_registro=self.id_usuario_registro,
                    fecha_inicio=fila["fecha_inicio"],
                    fecha_fin=fila["fecha_fin"],
                    lugar=fila["lugar"],
                    descripcion=fila["descripcion"],
                    participantes=fila["participantes"],
                )
                insertadas += 1
            except Exception as exc:
                errores_al_insertar.append({
                    "numero_fila": fila["numero_fila"],
                    "error": str(exc),
                })

        return {
            "insertadas": insertadas,
            "errores_al_insertar": errores_al_insertar,
        }

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _parsear_fecha(self, valor) -> date | None:
        """
        Acepta objetos date/datetime (nativos de openpyxl) o strings
        con formato YYYY-MM-DD o DD/MM/YYYY.
        """
        if valor is None:
            return None
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        texto = str(valor).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(texto, fmt).date()
            except ValueError:
                pass
        return None

    def _resolver_asic(self, nombre: str) -> int | None:
        """
        Busca el id_asic por nombre (búsqueda por coincidencia flexible, case-insensitive).
        Usa caché para evitar N+1 queries.
        """
        key = nombre.lower().strip()
        if key in self._cache_asic:
            return self._cache_asic[key]

        todos = self._asic_dao.obtener_todos()
        for asic in todos:
            if asic["nombre"].lower().strip() == key:
                self._cache_asic[key] = asic["id_asic"]
                return asic["id_asic"]

        self._cache_asic[key] = None
        return None

    def _resolver_tipo(self, nombre: str) -> int | None:
        """
        Busca el id_tipo por nombre (búsqueda por coincidencia flexible, case-insensitive).
        Usa caché para evitar N+1 queries.
        """
        key = nombre.lower().strip()
        if key in self._cache_tipo:
            return self._cache_tipo[key]

        todos = self._tipo_dao.obtener_todos()
        for tipo in todos:
            if tipo["nombre"].lower().strip() == key:
                self._cache_tipo[key] = tipo["id_tipo"]
                return tipo["id_tipo"]

        self._cache_tipo[key] = None
        return None
