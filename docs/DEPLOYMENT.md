# Guía de Lanzamiento y Deployment

## 🚀 Preparación para Lanzamiento

### Verificación Pre-Lanzamiento

```bash
# 1. Ejecutar todos los tests
make test

# 2. Verificar formateo del código
make format

# 3. Verificar tipos
make type-check

# 4. Verificar que el CLI funciona
python -m sincpro_py_compiler.cli --help
python -m sincpro_py_compiler.cli --list-templates

# 5. Prueba de compilación real
python -m sincpro_py_compiler.cli ./proyecto_ejemplo -o ./compilado -t basic -v
```

### Build del Paquete (con Poetry + Makefile)

```bash
# Build automático con configuración Gemfury
make build

# O manualmente con Poetry
poetry build
```

### Deployment

```bash
# Deploy a Gemfury + PyPI automático
GEMFURY_PUSH_TOKEN=tu_token POETRY_PYPI_TOKEN=tu_token make publish

# O paso a paso:
poetry publish -r fury --build
poetry publish -u __token__ -p $POETRY_PYPI_TOKEN
```

## 📦 Instalación

### Desde PyPI (cuando esté publicado)

```bash
pip install sincpro-py-compiler
```

### Desde Gemfury (repositorio privado)

```bash
# Configurar repositorio Gemfury
pip install --index-url https://pypi.fury.io/sincpro/ sincpro-py-compiler
```

### Desde Código Fuente

```bash
# Clonar repositorio
git clone https://github.com/Sincpro-SRL/sincpro_py_compiler.git
cd sincpro_py_compiler

# Setup inicial completo
make init

# O solo instalar
make install
```

## 🔧 Configuración del Entorno de Desarrollo

### Setup Automático con Makefile

```bash
# Instala Poetry, herramientas de desarrollo y pre-commit hooks
make prepare-environment

# Instala dependencias del proyecto
make install

# Setup completo (todo en uno)
make init
```

### Dependencias Mínimas para Uso

- Python 3.8+
- No hay dependencias externas (solo stdlib)

### Dependencias de Desarrollo (ya en pyproject.toml)

- pytest: Testing
- black, isort, autoflake: Formateo
- pyright: Type checking
- jupyterlab: Desarrollo interactivo

## 📋 Checklist de Release

### Pre-Release

- [ ] ✅ Todos los tests pasan: `make test`
- [ ] ✅ Código formateado: `make format`
- [ ] ✅ Type checking: `make type-check`
- [ ] ✅ CLI funciona correctamente
- [ ] ✅ Documentación actualizada
- [ ] ✅ Templates funcionando (basic, django, odoo)
- [ ] ✅ pyproject.toml limpio sin dependencias innecesarias

### Build & Test

- [ ] Limpiar archivos temporales: `make clean-pyc`
- [ ] Build: `make build`
- [ ] Test de instalación en entorno limpio

### Deployment

- [ ] Configurar tokens: `GEMFURY_PUSH_TOKEN` y `POETRY_PYPI_TOKEN`
- [ ] Tag de versión en Git
- [ ] Deploy: `make publish`
- [ ] Crear release en GitHub

## 🏗️ Estructura Final del Proyecto

```
sincpro_py_compiler/
├── docs/
│   ├── ARCHITECTURE.md      # Arquitectura real (no teórica)
│   └── DEPLOYMENT.md        # Esta guía
├── sincpro_py_compiler/
│   ├── infrastructure/      # Todas las implementaciones
│   ├── resources/           # Templates de exclusión (archivos)
│   └── cli.py              # Interfaz CLI
├── tests/
│   └── test_sincpro_compiler.py  # 16 tests de casos reales
├── Makefile                # Comandos de build/deploy/dev
├── pyproject.toml          # Configuración Poetry (limpia)
├── requirements.txt        # Dependencias para pip
└── README.md              # Documentación principal
```

## ⚡ Comandos Rápidos con Makefile

### Para Desarrolladores

```bash
# Setup inicial completo
make init

# Desarrollo diario
make test                    # Tests
make format                  # Formatear código
make lint                    # Format + Type check
make clean-pyc              # Limpiar .pyc

# Build y deploy
make build                   # Build con Poetry
make publish                 # Deploy a Gemfury + PyPI
```

### Para Usuarios Finales

```bash
# Instalación
pip install sincpro-py-compiler

# Uso básico
sincpro-compile ./mi_proyecto -o ./compilado -t basic

# Ver opciones
sincpro-compile --help
sincpro-compile --list-templates
```

## 🎯 Casos de Uso Validados (16 Tests)

Todos cubiertos por tests automatizados:

1. **Proyecto Python Básico**: .py → .pyc, copiar otros archivos
2. **Proyecto Django**: Excluir migrations/, static/, compilar código
3. **Addon Odoo**: Excluir manifests, data/, security/, compilar lógica  
4. **Estructura Compleja**: Preservar directorios anidados
5. **Exclusiones Personalizadas**: Archivo custom de exclusiones

## 🔍 Verificación Post-Instalación

```bash
# Test básico
mkdir test_proj
echo 'print("test")' > test_proj/main.py
sincpro-compile test_proj -o compiled
ls compiled/  # Debe mostrar main.pyc
rm -rf test_proj compiled
```

## 📞 Soporte

- **Repositorio**: <https://github.com/Sincpro-SRL/sincpro_py_compiler>
- **Issues**: GitHub Issues
- **Documentación**: `docs/ARCHITECTURE.md`
- **Empresa**: Sincpro SRL
