"""
Tests de integración completa para el feature de seguridad
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class TestSecurityIntegration:
    """Tests de integración completa del feature de seguridad"""

    def setup_method(self):
        """Configuración para cada test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_dir = self.temp_dir / "test_project"
        self.project_dir.mkdir()

        # Crear proyecto de prueba
        (self.project_dir / "main.py").write_text(
            """
def main():
    print("Código Python compilado y protegido")
    return "success"

if __name__ == "__main__":
    main()
"""
        )

        (self.project_dir / "utils.py").write_text(
            """
class Helper:
    def calculate(self, x, y):
        return x + y

def get_version():
    return "1.0.0"
"""
        )

        (self.project_dir / "submodule").mkdir()
        (self.project_dir / "submodule" / "__init__.py").write_text("")
        (self.project_dir / "submodule" / "processor.py").write_text(
            """
def process_data(data):
    return [x * 2 for x in data]
"""
        )

    def teardown_method(self):
        """Limpieza después de cada test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_full_workflow_compression(self):
        """Test del flujo completo: compilar -> comprimir -> descomprimir -> ejecutar"""

        # Paso 1: Compilar y comprimir
        password = "integration_test_license_2025"

        compile_cmd = [
            sys.executable,
            "-m",
            "sincpro_py_compiler.cli",
            str(self.project_dir),
            "--compress",
            "--password",
            password,
        ]

        result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=Path.cwd())
        assert result.returncode == 0, f"Compilación falló: {result.stderr}"

        # Verificar que se creó el archivo protegido
        expected_zip = Path.cwd() / "compiled.zip"
        assert expected_zip.exists(), "Archivo ZIP protegido no fue creado"

        # Paso 2: Descomprimir
        extracted_dir = self.temp_dir / "extracted"

        decrypt_cmd = [
            sys.executable,
            "-m",
            "sincpro_py_compiler.decrypt_cli",
            str(expected_zip),
            "--password",
            password,
            "-o",
            str(extracted_dir),
        ]

        result = subprocess.run(decrypt_cmd, capture_output=True, text=True, cwd=Path.cwd())
        assert result.returncode == 0, f"Descompresión falló: {result.stderr}"

        # Verificar estructura extraída
        assert extracted_dir.exists()
        assert (extracted_dir / "main.pyc").exists()
        assert (extracted_dir / "utils.pyc").exists()
        assert (extracted_dir / "submodule" / "__init__.pyc").exists()
        assert (extracted_dir / "submodule" / "processor.pyc").exists()

        # Paso 3: Ejecutar código descomprimido
        exec_cmd = [sys.executable, str(extracted_dir / "main.pyc")]
        result = subprocess.run(exec_cmd, capture_output=True, text=True)

        assert result.returncode == 0, f"Ejecución falló: {result.stderr}"
        assert "Código Python compilado y protegido" in result.stdout

        # Limpiar
        if expected_zip.exists():
            expected_zip.unlink()

    def test_wrong_password_protection(self):
        """Test que verifica protección contra contraseñas incorrectas"""

        # Compilar y comprimir con una contraseña
        correct_password = "correct_license_key"
        wrong_password = "wrong_license_key"

        compile_cmd = [
            sys.executable,
            "-m",
            "sincpro_py_compiler.cli",
            str(self.project_dir),
            "--compress",
            "--password",
            correct_password,
        ]

        result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=Path.cwd())
        assert result.returncode == 0

        expected_zip = Path.cwd() / "compiled.zip"
        assert expected_zip.exists()

        # Intentar descomprimir con contraseña incorrecta
        extracted_dir = self.temp_dir / "should_fail"

        decrypt_cmd = [
            sys.executable,
            "-m",
            "sincpro_py_compiler.decrypt_cli",
            str(expected_zip),
            "--password",
            wrong_password,
            "-o",
            str(extracted_dir),
        ]

        result = subprocess.run(decrypt_cmd, capture_output=True, text=True, cwd=Path.cwd())
        assert result.returncode != 0, "Debería fallar con contraseña incorrecta"
        assert "Contraseña incorrecta" in result.stderr or "Error" in result.stderr

        # Limpiar
        if expected_zip.exists():
            expected_zip.unlink()

    def test_cli_help_shows_security_options(self):
        """Test que verifica que las opciones de seguridad aparecen en la ayuda"""

        help_cmd = [sys.executable, "-m", "sincpro_py_compiler.cli", "--help"]
        result = subprocess.run(help_cmd, capture_output=True, text=True, cwd=Path.cwd())

        assert result.returncode == 0
        assert "--compress" in result.stdout
        assert "--encrypt" in result.stdout
        assert "--password" in result.stdout
        assert "contraseña" in result.stdout.lower()

    def test_decrypt_cli_help(self):
        """Test que verifica que el CLI de desprotección tiene ayuda apropiada"""

        help_cmd = [sys.executable, "-m", "sincpro_py_compiler.decrypt_cli", "--help"]
        result = subprocess.run(help_cmd, capture_output=True, text=True, cwd=Path.cwd())

        assert result.returncode == 0
        assert "--password" in result.stdout
        assert "desproteger" in result.stdout.lower() or "decrypt" in result.stdout.lower()

    def test_compression_file_extension(self):
        """Test que verifica que los archivos tienen las extensiones correctas"""

        password = "test_extension_password"

        # Test compresión - debe generar .zip
        compile_cmd = [
            sys.executable,
            "-m",
            "sincpro_py_compiler.cli",
            str(self.project_dir),
            "--compress",
            "--password",
            password,
        ]

        result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=Path.cwd())
        assert result.returncode == 0

        zip_file = Path.cwd() / "compiled.zip"
        assert zip_file.exists(), "Archivo .zip no fue creado"
        assert zip_file.suffix == ".zip"

        # Limpiar
        if zip_file.exists():
            zip_file.unlink()

    def test_project_structure_preservation(self):
        """Test que verifica preservación de estructura de directorios"""

        password = "structure_test_2025"

        # Compilar y proteger
        compile_cmd = [
            sys.executable,
            "-m",
            "sincpro_py_compiler.cli",
            str(self.project_dir),
            "--compress",
            "--password",
            password,
        ]

        result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=Path.cwd())
        assert result.returncode == 0

        zip_file = Path.cwd() / "compiled.zip"

        # Desproteger
        extracted_dir = self.temp_dir / "structure_test"
        decrypt_cmd = [
            sys.executable,
            "-m",
            "sincpro_py_compiler.decrypt_cli",
            str(zip_file),
            "--password",
            password,
            "-o",
            str(extracted_dir),
        ]

        result = subprocess.run(decrypt_cmd, capture_output=True, text=True, cwd=Path.cwd())
        assert result.returncode == 0

        # Verificar estructura completa preservada
        assert (extracted_dir / "main.pyc").exists()
        assert (extracted_dir / "utils.pyc").exists()
        assert (extracted_dir / "submodule").is_dir()
        assert (extracted_dir / "submodule" / "__init__.pyc").exists()
        assert (extracted_dir / "submodule" / "processor.pyc").exists()

        # Limpiar
        if zip_file.exists():
            zip_file.unlink()


class TestSecurityUseCases:
    """Tests específicos para casos de uso de distribución comercial"""

    def setup_method(self):
        """Configuración para cada test"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Limpieza después de cada test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_commercial_distribution_simulation(self):
        """Simula distribución comercial con licencias únicas por cliente"""

        # Crear producto comercial
        product_dir = self.temp_dir / "my_commercial_product"
        product_dir.mkdir()

        (product_dir / "app.py").write_text(
            """
print("Software Comercial v1.0")
print("Licenciado para uso autorizado únicamente")

def main_feature():
    return "Funcionalidad principal del software"

if __name__ == "__main__":
    result = main_feature()
    print(f"Resultado: {result}")
"""
        )

        # Simular 3 clientes diferentes
        clients = {
            "Cliente_A": "LICENSE_CLIENTE_A_2025_ABC123",
            "Cliente_B": "LICENSE_CLIENTE_B_2025_XYZ789",
            "Cliente_C": "LICENSE_CLIENTE_C_2025_DEF456",
        }

        for client_name, license_key in clients.items():
            # Compilar y proteger para cada cliente
            compile_cmd = [
                sys.executable,
                "-m",
                "sincpro_py_compiler.cli",
                str(product_dir),
                "--compress",
                "--password",
                license_key,
            ]

            result = subprocess.run(
                compile_cmd, capture_output=True, text=True, cwd=Path.cwd()
            )
            assert result.returncode == 0, f"Compilación para {client_name} falló"

            protected_file = Path.cwd() / "compiled.zip"
            client_file = self.temp_dir / f"product_{client_name}.zip"

            # Mover archivo protegido
            shutil.move(str(protected_file), str(client_file))
            assert client_file.exists()

            # Verificar que el cliente puede usar su licencia
            extracted_dir = self.temp_dir / f"extracted_{client_name}"
            decrypt_cmd = [
                sys.executable,
                "-m",
                "sincpro_py_compiler.decrypt_cli",
                str(client_file),
                "--password",
                license_key,
                "-o",
                str(extracted_dir),
            ]

            result = subprocess.run(
                decrypt_cmd, capture_output=True, text=True, cwd=Path.cwd()
            )
            assert result.returncode == 0, f"Cliente {client_name} no puede usar su licencia"

            # Verificar que otros clientes NO pueden usar esta licencia
            for other_client, other_license in clients.items():
                if other_client != client_name:
                    wrong_extract_dir = self.temp_dir / f"wrong_{other_client}"
                    wrong_decrypt_cmd = [
                        sys.executable,
                        "-m",
                        "sincpro_py_compiler.decrypt_cli",
                        str(client_file),
                        "--password",
                        other_license,
                        "-o",
                        str(wrong_extract_dir),
                    ]

                    wrong_result = subprocess.run(
                        wrong_decrypt_cmd, capture_output=True, text=True, cwd=Path.cwd()
                    )
                    assert (
                        wrong_result.returncode != 0
                    ), f"{other_client} puede usar licencia de {client_name}"

    def test_license_validation_edge_cases(self):
        """Test casos edge de validación de licencias"""

        # Crear código simple
        code_dir = self.temp_dir / "simple_app"
        code_dir.mkdir()
        (code_dir / "main.py").write_text('print("Hello World")')

        valid_password = "VALID_LICENSE_2025"

        # Compilar con licencia válida
        compile_cmd = [
            sys.executable,
            "-m",
            "sincpro_py_compiler.cli",
            str(code_dir),
            "--compress",
            "--password",
            valid_password,
        ]

        result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=Path.cwd())
        assert result.returncode == 0

        protected_file = Path.cwd() / "compiled.zip"
        assert protected_file.exists()

        # Test casos edge
        edge_cases = [
            "",  # Contraseña vacía
            " ",  # Solo espacios
            "wrong",  # Contraseña incorrecta
            "VALID_LICENSE_2024",  # Similar pero incorrecta
            valid_password + " ",  # Con espacio extra
            " " + valid_password,  # Con espacio al inicio
        ]

        for edge_password in edge_cases:
            extract_dir = self.temp_dir / f"edge_{hash(edge_password)}"
            decrypt_cmd = [
                sys.executable,
                "-m",
                "sincpro_py_compiler.decrypt_cli",
                str(protected_file),
                "--password",
                edge_password,
                "-o",
                str(extract_dir),
            ]

            result = subprocess.run(
                decrypt_cmd, capture_output=True, text=True, cwd=Path.cwd()
            )
            assert (
                result.returncode != 0
            ), f"Contraseña edge case '{edge_password}' debería fallar"

        # Verificar que la contraseña correcta sí funciona
        correct_extract_dir = self.temp_dir / "correct"
        correct_decrypt_cmd = [
            sys.executable,
            "-m",
            "sincpro_py_compiler.decrypt_cli",
            str(protected_file),
            "--password",
            valid_password,
            "-o",
            str(correct_extract_dir),
        ]

        result = subprocess.run(
            correct_decrypt_cmd, capture_output=True, text=True, cwd=Path.cwd()
        )
        assert result.returncode == 0, "Contraseña correcta debería funcionar"

        # Limpiar
        if protected_file.exists():
            protected_file.unlink()
