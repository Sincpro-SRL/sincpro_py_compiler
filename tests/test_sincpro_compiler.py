"""
Tests para SincPro Python Compiler - Arquitectura limpia
Casos de uso específicos: compilar .py a .pyc y copiar el resto tal como están
"""

import shutil
import tempfile
from pathlib import Path

from sincpro_py_compiler.infrastructure.compiler_service import CompilerService
from sincpro_py_compiler.infrastructure.file_manager import FileManager
from sincpro_py_compiler.infrastructure.python_compiler import PythonCompiler


class TestCompilerService:
    """Tests para el servicio de compilación"""

    def setup_method(self):
        self.service = CompilerService()

    def test_templates_disponibles(self):
        """Test que los templates básicos están disponibles"""
        templates = self.service.list_available_templates()

        assert "basic" in templates
        assert "django" in templates
        assert "odoo" in templates

    def test_patrones_template_basic(self):
        """Test patrones del template básico"""
        patterns = self.service.get_exclude_patterns("basic")

        assert "__pycache__/" in patterns
        assert "*.pyc" in patterns
        assert ".venv/" in patterns
        assert ".git/" in patterns

    def test_patrones_template_odoo(self):
        """Test patrones específicos de Odoo"""
        exclude_patterns = self.service.get_exclude_patterns("odoo")
        copy_faithful_patterns = self.service.get_copy_faithful_patterns("odoo")

        # Los manifests ya no deben estar en exclusión
        assert "__manifest__.py" not in exclude_patterns
        assert "__openerp__.py" not in exclude_patterns
        # Deben estar en copia fiel
        assert "__manifest__.py" in copy_faithful_patterns
        assert "__openerp__.py" in copy_faithful_patterns
        # Los directorios de datos deben estar en copia fiel
        assert "static/" in copy_faithful_patterns
        assert "data/" in copy_faithful_patterns
        assert "demo/" in copy_faithful_patterns
        assert "security/" in copy_faithful_patterns

    def test_should_exclude_archivo_pyc(self):
        """Test exclusión de archivos .pyc"""
        patterns = ["*.pyc"]
        file_path = Path("/test/archivo.pyc")

        assert self.service.should_exclude(file_path, patterns)

    def test_should_exclude_directorio_venv(self):
        """Test exclusión de directorio .venv/"""
        patterns = [".venv/"]
        file_path = Path("/proyecto/.venv/lib/python3.12/site-packages/algo.py")

        assert self.service.should_exclude(file_path, patterns)

    def test_no_exclude_archivo_python(self):
        """Test que archivos .py normales NO se excluyen"""
        patterns = ["*.pyc", ".venv/"]
        file_path = Path("/proyecto/main.py")

        assert not self.service.should_exclude(file_path, patterns)

    def test_compile_python_file_success(self):
        """Test compilación exitosa de archivo Python"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo fuente
            source_file = Path(temp_dir) / "test.py"
            source_file.write_text('print("Hello, World!")')

            # Archivo de salida
            output_file = Path(temp_dir) / "test.pyc"

            # Compilar
            success = self.service.compile_python_file(source_file, output_file)

            assert success
            assert output_file.exists()

    def test_archivo_personalizado_exclusiones(self):
        """Test carga de archivo personalizado de exclusiones"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo de exclusiones
            exclude_file = Path(temp_dir) / "mi_exclusiones.txt"
            exclude_file.write_text(
                """# Mis exclusiones
*.log
temp/
config/secret.py
"""
            )

            patterns = self.service.get_exclude_patterns(custom_file=str(exclude_file))

            assert "*.log" in patterns
            assert "temp/" in patterns
            assert "config/secret.py" in patterns


class TestFileManager:
    """Tests para el manejador de archivos"""

    def setup_method(self):
        self.manager = FileManager()

    def test_copy_file_preserva_contenido(self):
        """Test que copy_file preserva el contenido"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Archivo fuente
            source = Path(temp_dir) / "source.txt"
            content = "Contenido de prueba\nSegunda línea"
            source.write_text(content)

            # Destino
            dest = Path(temp_dir) / "dest" / "copied.txt"

            # Copiar
            success = self.manager.copy_file(source, dest)

            assert success
            assert dest.exists()
            assert dest.read_text() == content

    def test_create_directory_estructura(self):
        """Test creación de directorios anidados"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = Path(temp_dir) / "nivel1" / "nivel2" / "nivel3"

            success = self.manager.create_directory(nested_dir)

            assert success
            assert nested_dir.exists()
            assert nested_dir.is_dir()


class TestPythonCompiler:
    """Tests para el compilador principal - Casos de uso específicos"""

    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.compiler = PythonCompiler()

    def teardown_method(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_caso_uso_proyecto_basico(self):
        """Test: Compilar proyecto Python básico"""
        # Crear estructura de proyecto
        (self.temp_dir / "main.py").write_text('print("Aplicación principal")')
        (self.temp_dir / "utils.py").write_text('def helper(): return "ayuda"')
        (self.temp_dir / "config.xml").write_text("<config><debug>true</debug></config>")
        (self.temp_dir / "README.md").write_text("# Mi Proyecto")

        # Directorio de salida
        output_dir = self.temp_dir / "compiled"

        # Compilar
        success = self.compiler.compile_project(
            source_dir=str(self.temp_dir), output_dir=str(output_dir), template="basic"
        )

        assert success

        # Verificar archivos Python compilados
        assert (output_dir / "main.pyc").exists()
        assert (output_dir / "utils.pyc").exists()

        # Verificar archivos no-Python copiados tal como están
        assert (output_dir / "config.xml").exists()
        assert (output_dir / "README.md").exists()

        # Verificar contenido preservado
        assert (
            output_dir / "config.xml"
        ).read_text() == "<config><debug>true</debug></config>"

    def test_caso_uso_proyecto_django(self):
        """Test: Compilar proyecto Django excluyendo migraciones"""
        # Crear estructura Django
        (self.temp_dir / "views.py").write_text("def index(request): pass")
        (self.temp_dir / "models.py").write_text("class User: pass")

        # Crear migraciones (deben excluirse)
        migrations_dir = self.temp_dir / "migrations"
        migrations_dir.mkdir()
        (migrations_dir / "0001_initial.py").write_text("# migración")

        # Archivos estáticos (deben excluirse)
        static_dir = self.temp_dir / "static"
        static_dir.mkdir()
        (static_dir / "style.css").write_text("body { color: red; }")

        # Compilar con template Django
        output_dir = self.temp_dir / "dist"
        success = self.compiler.compile_project(
            source_dir=str(self.temp_dir), output_dir=str(output_dir), template="django"
        )

        assert success

        # Archivos Python compilados
        assert (output_dir / "views.pyc").exists()
        assert (output_dir / "models.pyc").exists()

        # Migraciones y estáticos excluidos
        assert not (output_dir / "migrations").exists()
        assert not (output_dir / "static").exists()

    def test_caso_uso_addon_odoo(self):
        """Test: Compilar addon Odoo copiando manifests y carpetas fielmente"""
        # Crear estructura Odoo
        (self.temp_dir / "models.py").write_text("class Partner: pass")
        (self.temp_dir / "views.py").write_text("# vistas")
        (self.temp_dir / "__manifest__.py").write_text("{'name': 'Mi Addon'}")

        # Archivos de datos (deben copiarse fielmente)
        data_dir = self.temp_dir / "data"
        data_dir.mkdir()
        (data_dir / "records.xml").write_text("<data></data>")

        # Security (debe copiarse fielmente)
        security_dir = self.temp_dir / "security"
        security_dir.mkdir()
        (security_dir / "groups.xml").write_text("<security></security>")

        # Compilar con template Odoo
        output_dir = self.temp_dir / "client_dist"
        success = self.compiler.compile_project(
            source_dir=str(self.temp_dir), output_dir=str(output_dir), template="odoo"
        )

        assert success

        # Código Python compilado
        assert (output_dir / "models.pyc").exists()
        assert (output_dir / "views.pyc").exists()

        # Manifest y carpetas deben copiarse fielmente
        assert (output_dir / "__manifest__.py").exists()
        assert (output_dir / "data" / "records.xml").exists()
        assert (output_dir / "security" / "groups.xml").exists()

    def test_caso_uso_proyecto_con_estructura_compleja(self):
        """Test: Proyecto con estructura de subdirectorios"""
        # Crear estructura compleja
        src_dir = self.temp_dir / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("from utils import helper")

        utils_dir = src_dir / "utils"
        utils_dir.mkdir()
        (utils_dir / "__init__.py").write_text("from .helper import helper")
        (utils_dir / "helper.py").write_text('def helper(): return "help"')

        # Archivos de configuración
        (self.temp_dir / "config.json").write_text('{"debug": true}')

        # Scripts
        scripts_dir = self.temp_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "deploy.sh").write_text('#!/bin/bash\necho "deploying"')

        # Compilar
        output_dir = self.temp_dir / "release"
        success = self.compiler.compile_project(
            source_dir=str(self.temp_dir), output_dir=str(output_dir), template="basic"
        )

        assert success

        # Verificar estructura preservada
        assert (output_dir / "src" / "main.pyc").exists()
        assert (output_dir / "src" / "utils" / "__init__.pyc").exists()
        assert (output_dir / "src" / "utils" / "helper.pyc").exists()

        # Archivos no-Python copiados
        assert (output_dir / "config.json").exists()
        assert (output_dir / "scripts" / "deploy.sh").exists()

    def test_caso_uso_exclusiones_personalizadas(self):
        """Test: Usar archivo de exclusiones personalizado"""
        # Crear archivos
        (self.temp_dir / "main.py").write_text('print("main")')
        (self.temp_dir / "secret.py").write_text('API_KEY = "secret"')
        (self.temp_dir / "config.py").write_text("DEBUG = True")

        # Crear archivo de exclusiones personalizado
        exclude_file = self.temp_dir / "my_excludes.txt"
        exclude_file.write_text(
            """# Exclusiones personalizadas
secret.py
*.tmp
"""
        )

        # Compilar con exclusiones personalizadas
        output_dir = self.temp_dir / "secure_dist"
        success = self.compiler.compile_project(
            source_dir=str(self.temp_dir),
            output_dir=str(output_dir),
            template="basic",
            exclude_file=str(exclude_file),
        )

        assert success

        # main.py y config.py compilados
        assert (output_dir / "main.pyc").exists()
        assert (output_dir / "config.pyc").exists()

        # secret.py excluido
        assert not (output_dir / "secret.pyc").exists()
        assert not (output_dir / "secret.py").exists()

    def test_list_templates_output(self, capsys):
        """Test que list_templates muestra información correcta"""
        self.compiler.list_templates()

        captured = capsys.readouterr()
        output = captured.out

        assert "Templates disponibles:" in output
        assert "basic:" in output
        assert "django:" in output
        assert "odoo:" in output
        assert "__pycache__/" in output

    def test_copia_fiel_archivos_odoo(self):
        """Test: Archivos/carpeta de Odoo se copian fielmente"""
        temp_dir = Path(tempfile.mkdtemp())
        output_dir = temp_dir / "output"
        temp_dir.mkdir(exist_ok=True)
        (temp_dir / "__manifest__.py").write_text("{'name': 'Mi Addon'}")
        (temp_dir / "__openerp__.py").write_text("{'name': 'Mi Addon'}")
        static_dir = temp_dir / "static"
        static_dir.mkdir()
        (static_dir / "file.js").write_text("console.log('test')")
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        (data_dir / "records.xml").write_text("<data></data>")
        demo_dir = temp_dir / "demo"
        demo_dir.mkdir()
        (demo_dir / "demo.xml").write_text("<demo></demo>")
        security_dir = temp_dir / "security"
        security_dir.mkdir()
        (security_dir / "groups.xml").write_text("<security></security>")

        compiler = PythonCompiler()
        success = compiler.compile_project(
            source_dir=str(temp_dir), output_dir=str(output_dir), template="odoo"
        )
        assert success
        # Verificar que los archivos/carpeta se copiaron fielmente
        assert (output_dir / "__manifest__.py").exists()
        assert (output_dir / "__openerp__.py").exists()
        assert (output_dir / "static" / "file.js").exists()
        assert (output_dir / "data" / "records.xml").exists()
        assert (output_dir / "demo" / "demo.xml").exists()
        assert (output_dir / "security" / "groups.xml").exists()
        shutil.rmtree(temp_dir)
