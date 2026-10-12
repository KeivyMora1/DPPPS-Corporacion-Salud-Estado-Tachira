import re

with open('db.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the generation of UBICACIONES_ASIC_PREDETERMINADAS
replacement = '''ASIC_POR_MUNICIPIO = {
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
    "Independencia": ["Capacho Independencia"],
    "Jáuregui": ["Jáuregui"],
    "José María Vargas": [],
    "Junín": ["Junín"],
    "Libertad": ["Capacho Libertad"],
    "Libertador": ["Libertador"],
    "Lobatera": ["Michelena"],
    "Michelena": ["Michelena"],
    "Panamericano": ["Panamericano"],
    "Pedro María Ureña": ["Ureña"],
    "Rafael Urdaneta": [],
    "Samuel Darío Maldonado": ["Samuel Darío Maldonado"],
    "San Cristóbal": ["Dr. Hugo Murzi", "Dr. Jacinto Convit", "Dr. José María Vargas", "Sabaneta"],
    "San Judas Tadeo": [],
    "Seboruco": ["Antonio Rómulo Costa"],
    "Simón Rodríguez": [],
    "Sucre": ["Sucre"],
    "Torbes": ["Torbes"],
    "Uribante": ["Uribante"],
}

UBICACIONES_ASIC_PREDETERMINADAS = [
    (asic, municipio, parroquia)
    for municipio, parroquias in PARROQUIAS_POR_MUNICIPIO_TACHIRA.items()
    for parroquia in parroquias
    for asic in ASIC_POR_MUNICIPIO.get(municipio, [])
]'''

# Fix encoding issue before replacing (the user has ANSI vs UTF-8 mixed in db.py)
# We'll just replace the exact block.
old_block = r'''UBICACIONES_ASIC_PREDETERMINADAS = \[
    \(asic, municipio, parroquia\)
    for _, asic in ASIC_PREDETERMINADOS
    for municipio, parroquias in PARROQUIAS_POR_MUNICIPIO_TACHIRA\.items\(\)
    for parroquia in parroquias
\]'''

new_content = re.sub(old_block, replacement, content)

with open('db.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Replaced!")
