ASIC_PREDETERMINADOS = [
    ("ASIC-01", "Andrés Bello"),
    ("ASIC-02", "Antonio Rómulo Costa"),
    ("ASIC-03", "Ayacucho"),
    ("ASIC-04", "Bolívar"),
    ("ASIC-05", "Independencia"),
    ("ASIC-06", "Capacho Libertad"),
    ("ASIC-07", "Cárdenas"),
    ("ASIC-08", "Córdoba"),
    ("ASIC-09", "Dr. Hugo Murzi"),
    ("ASIC-10", "Dr. Jacinto Convit"),
    ("ASIC-11", "Dr. José María Vargas"),
    ("ASIC-12", "Fernández Feo"),
    ("ASIC-13", "García de Hevia"),
    ("ASIC-14", "Guásimos"),
    ("ASIC-15", "Jáuregui"),
    ("ASIC-16", "Junin · Rafael Urdaneta"),
    ("ASIC-17", "Libertador"),
    ("ASIC-18", "Michelena"),
    ("ASIC-19", "Panamericano · San Judas Tadeo"),
    ("ASIC-20", "Sabaneta"),
    ("ASIC-21", "Samuel Darío Maldonado"),
    ("ASIC-22", "Sucre"),
    ("ASIC-23", "San Josecito"),
    ("ASIC-24", "Ureña"),
    ("ASIC-25", "Uribante"),
]

VOCERIA_CENTRO_DISPENSADOR_OPCIONES = [
    "Consultorio Popular TIPO I", "Consultorio Popular TIPO II",
    "Consultorio Popular TIPO III", "Clinica Popular TIPO I",
    "Clinica Popular TIPO II", "CDI", "SRI", "CAT",
    "Hospitales TIPO I", "Hospitales TIPO II", "Hospitales TIPO III",
    "Hospitales TIPO IV",
]
ACTIVIDAD_ESTABLECIMIENTO_OPCIONES = VOCERIA_CENTRO_DISPENSADOR_OPCIONES

PARROQUIAS_POR_MUNICIPIO_TACHIRA = {
    "Andrés Bello": ["Cordero"],
    "Antonio Rómulo Costa": ["Virgen del Carmen"],
    "Ayacucho": ["San Juan de Colón", "Rivas Berti", "San Pedro del Río"],
    "Bolívar": [
        "San Antonio del Táchira",
        "Palotal",
        "Juan Vicente Gómez",
        "Isaías Medina Angarita",
    ],
    "Cárdenas": ["Táriba", "Amenodoro Rangel Lamús", "La Florida"],
    "Córdoba": ["Santa Ana del Táchira"],
    "Fernández Feo": ["San Rafael del Piñal", "Alberto Adriani", "Santo Domingo"],
    "Francisco de Miranda": ["San José de Bolívar"],
    "García de Hevia": ["La Fría", "Boca de Grita", "José Antonio Páez"],
    "Guásimos": ["Palmira"],
    "Independencia": ["Capacho Nuevo", "Juan Germán Roscio", "Román Cárdenas"],
    "Jáuregui": [
        "La Grita",
        "Emilio Constantino Guerrero",
        "Monseñor Miguel Antonio Salas",
    ],
    "José María Vargas": ["El Cobre"],
    "Junín": ["Rubio", "Bramón", "La Petrólea", "Quinimarí"],
    "Libertad": ["Capacho Viejo", "Cipriano Castro", "Manuel Felipe Rugeles"],
    "Libertador": ["Abejales", "Doradas", "Emeterio Ochoa", "San Joaquín de Navay"],
    "Lobatera": ["Lobatera", "Constitución"],
    "Michelena": ["Michelena"],
    "Panamericano": ["San Pablo", "La Palmita"],
    "Pedro María Ureña": ["Ureña", "Nueva Arcadia"],
    "Rafael Urdaneta": ["Delicias"],
    "Samuel Darío Maldonado": ["La Tendida", "Boconó", "Hernández"],
    "San Cristóbal": [
        "La Concordia",
        "Pedro María Morantes",
        "San Juan Bautista",
        "San Sebastián",
        "Francisco Romero Lobo",
    ],
    "San Judas Tadeo": ["San Judas Tadeo"],
    "Seboruco": ["Seboruco"],
    "Simón Rodríguez": ["San Simón"],
    "Sucre": ["Sucre", "Eleazar López Contreras", "San Pablo"],
    "Torbes": ["San Josecito"],
    "Uribante": ["Pregonero", "Cárdenas", "Juan Pablo Peñaloza", "Potosí"],
}

MUNICIPIOS_TACHIRA = list(PARROQUIAS_POR_MUNICIPIO_TACHIRA)

ASIC_POR_MUNICIPIO = {
    "Andrés Bello": ["Andrés Bello"],
    "Antonio Rómulo Costa": ["Antonio Rómulo Costa"],
    "Ayacucho": ["Ayacucho"],
    "Bolívar": ["Bolívar"],
    "Cárdenas": ["Cárdenas"],
    "Córdoba": ["Córdoba"],
    "Fernández Feo": ["Fernández Feo"],
    "Francisco de Miranda": [],
    "García de Hevia": ["García de Hevia"],
    "Guásimos": ["Guásimos"],
    "Independencia": ["Independencia"],
    "Jáuregui": ["Jáuregui"],
    "José María Vargas": [],
    "Junín": ["Junin · Rafael Urdaneta"],
    "Libertad": ["Capacho Libertad"],
    "Libertador": ["Libertador"],
    "Lobatera": ["Michelena"],
    "Michelena": ["Michelena"],
    "Panamericano": ["Panamericano · San Judas Tadeo"],
    "Pedro María Ureña": ["Ureña"],
    "Rafael Urdaneta": ["Junin · Rafael Urdaneta"],
    "Samuel Darío Maldonado": ["Samuel Darío Maldonado"],
    "San Cristóbal": ["Dr. Hugo Murzi", "Dr. Jacinto Convit", "Dr. José María Vargas", "Sabaneta"],
    "San Judas Tadeo": ["Panamericano · San Judas Tadeo"],
    "Seboruco": ["Antonio Rómulo Costa"],
    "Simón Rodríguez": [],
    "Sucre": ["Sucre"],
    "Torbes": ["San Josecito"],
    "Uribante": ["Uribante"],
}

UBICACIONES_ASIC_PREDETERMINADAS = [
    (asic, municipio, parroquia)
    for municipio, parroquias in PARROQUIAS_POR_MUNICIPIO_TACHIRA.items()
    for parroquia in parroquias
    for asic in ASIC_POR_MUNICIPIO.get(municipio, [])
]

VOCERIA_MUNICIPIO_OPCIONES = MUNICIPIOS_TACHIRA
VOCERIA_ASIC_OPCIONES = [nombre for _, nombre in ASIC_PREDETERMINADOS]