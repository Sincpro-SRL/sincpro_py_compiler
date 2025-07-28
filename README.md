# SincPro Python Compiler

Una herramienta simple y efectiva para compilar proyectos Python (.py → .pyc) y distribuir código compilado de forma segura.

## 🎯 Propósito

- **Compilar archivos .py a .pyc** para distribución segura del código
- **Copiar archivos no-Python tal como están** (XML, JS, TXT, etc.)
- **Excluir archivos específicos** según el tipo de proyecto
- **Ocultar código fuente** para distribución a clientes

## ⚡ Instalación

```bash
pip install sincpro-py-compiler
```

O desde el código fuente:

```bash
git clone https://github.com/Sincpro-SRL/sincpro_py_compiler.git
cd sincpro_py_compiler
poetry install
```

## 🚀 Uso Rápido

### Comandos básicos

```bash
# Compilar proyecto básico
sincpro-compile ./mi_proyecto

# Especificar directorio de salida
sincpro-compile ./mi_proyecto -o ./compilado

# Usar template para Django
sincpro-compile ./mi_django_app -t django

# Usar template para Odoo
sincpro-compile ./mi_addon_odoo -t odoo

# Ver templates disponibles
sincpro-compile --list-templates
```

### Uso con diferentes tipos de proyecto

#### Proyecto Python básico

```bash
sincpro-compile ./mi_app -t basic
```

#### Proyecto Django

```bash
sincpro-compile ./mi_django_project -t django -o ./dist
```

#### Addon Odoo

```bash
sincpro-compile ./mi_addon -t odoo -o ./compilado
```

## 📋 Templates Disponibles

### `basic` - Proyecto Python básico

Excluye:

- `__pycache__/`, `*.pyc`
- `.git/`, `.venv/`, `venv/`, `env/`
- Archivos de log y temporales
- Archivos de configuración de IDEs

### `django` - Proyecto Django

Incluye exclusiones básicas más:

- `migrations/`
- `static/`, `media/`
- `db.sqlite3`

### `odoo` - Addon Odoo

Incluye exclusiones básicas más:

- `__manifest__.py`, `__openerp__.py`
- `static/`, `data/`, `demo/`
- `security/`

## 🔧 Opciones Avanzadas

### Archivo de exclusiones personalizado

Crea un archivo con patrones de exclusión (uno por línea):

```text
# Mi archivo de exclusiones personalizadas
*.log
temp/
config/secret.py
docs/
```

Úsalo con:

```bash
sincpro-compile ./proyecto -e mi_exclusiones.txt
```

### Opciones del CLI

```bash
sincpro-compile [directorio] [opciones]

Opciones:
  -o, --output DIR          Directorio de salida (default: ./compiled)
  -t, --template TEMPLATE   Template: basic, django, odoo (default: basic)
  -e, --exclude-file FILE   Archivo personalizado de exclusiones
  --list-templates         Mostrar templates disponibles
  -v, --verbose           Mostrar información detallada
  -h, --help              Mostrar ayuda
```

## 💡 Ejemplos Prácticos

### Distribuir una aplicación Python

```bash
# Compilar y generar distribución limpia
sincpro-compile ./mi_app -o ./dist -t basic
```

### Preparar addon Odoo para cliente

```bash
# Compilar addon excluyendo manifests y archivos de datos
sincpro-compile ./mi_addon -t odoo -o ./cliente_dist
```

### Proyecto Django para producción

```bash
# Compilar excluyendo migraciones y archivos estáticos
sincpro-compile ./mi_web -t django -o ./produccion
```

## 🛠 Uso Programático

```python
from sincpro_py_compiler.infrastructure.python_compiler import PythonCompiler

# Crear instancia del compilador
compiler = PythonCompiler()

# Compilar proyecto
success = compiler.compile_project(
    source_dir="./mi_proyecto",
    output_dir="./compilado",
    template="basic"
)

if success:
    print("¡Compilación exitosa!")
```

## 📁 Estructura de Salida

El compilador mantiene la estructura original del proyecto:

```
mi_proyecto/
├── app.py
├── utils.py
├── config.xml
└── static/
    └── style.css

# Después de compilar:
compilado/
├── app.pyc          # Compilado
├── utils.pyc        # Compilado  
├── config.xml       # Copiado tal como está
└── static/
    └── style.css    # Copiado tal como está
```

## ⚠️ Limitaciones

- Solo compila archivos `.py` a `.pyc`
- No es cifrado ni ofuscación avanzada
- Los archivos `.pyc` pueden ser descompilados
- Para protección avanzada considerar PyArmor

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Envía un Pull Request

## � Documentación

- **[Arquitectura del Sistema](docs/ARCHITECTURE.md)** - Detalles técnicos y diseño
- **[Guía de Deployment](docs/DEPLOYMENT.md)** - Instrucciones de lanzamiento e instalación
- **[Tests](tests/)** - Suite de tests completa con casos de uso reales

## �📄 Licencia

MIT License - ver archivo LICENSE para detalles.

## 🏢 Empresa

Desarrollado por **Sincpro SRL** para distribución segura de código Python.
