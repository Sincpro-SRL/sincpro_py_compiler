"""
Tests para funcionalidades de seguridad (compresión y encriptación)
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from sincpro_py_compiler.infrastructure.compression_service import ZipCompressionService
from sincpro_py_compiler.infrastructure.security_manager import SecurityManager


class TestZipCompressionService:
    """Tests para el servicio de compresión ZIP"""

    def setup_method(self):
        """Configuración para cada test"""
        self.compression_service = ZipCompressionService()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_files_dir = self.temp_dir / "test_files"
        self.test_files_dir.mkdir()

        # Crear archivos de prueba
        (self.test_files_dir / "test1.pyc").write_text("compiled python code 1")
        (self.test_files_dir / "test2.pyc").write_text("compiled python code 2")
        (self.test_files_dir / "subdir").mkdir()
        (self.test_files_dir / "subdir" / "test3.pyc").write_text("compiled python code 3")
        (self.test_files_dir / "data.txt").write_text("some data file")

    def teardown_method(self):
        """Limpieza después de cada test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_compress_directory_success(self):
        """Test compresión exitosa de directorio"""
        output_file = self.temp_dir / "compressed.zip"
        password = "test_password_123"

        result = self.compression_service.compress_directory(
            self.test_files_dir, output_file, password
        )

        assert result is True
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_decompress_file_success(self):
        """Test descompresión exitosa"""
        # Primero comprimir
        compressed_file = self.temp_dir / "test.zip"
        password = "test_password_123"

        self.compression_service.compress_directory(
            self.test_files_dir, compressed_file, password
        )

        # Luego descomprimir
        output_dir = self.temp_dir / "decompressed"
        result = self.compression_service.decompress_file(
            compressed_file, output_dir, password
        )

        assert result is True
        assert output_dir.exists()
        assert (output_dir / "test1.pyc").exists()
        assert (output_dir / "test2.pyc").exists()
        assert (output_dir / "subdir" / "test3.pyc").exists()
        assert (output_dir / "data.txt").exists()

    def test_decompress_wrong_password(self):
        """Test descompresión con contraseña incorrecta"""
        # Comprimir con una contraseña
        compressed_file = self.temp_dir / "test.zip"
        self.compression_service.compress_directory(
            self.test_files_dir, compressed_file, "correct_password"
        )

        # Intentar descomprimir con contraseña incorrecta
        output_dir = self.temp_dir / "decompressed"
        result = self.compression_service.decompress_file(
            compressed_file, output_dir, "wrong_password"
        )

        assert result is False

    def test_compress_nonexistent_directory(self):
        """Test compresión de directorio inexistente"""
        nonexistent_dir = self.temp_dir / "nonexistent"
        output_file = self.temp_dir / "test.zip"

        result = self.compression_service.compress_directory(
            nonexistent_dir, output_file, "password"
        )

        assert result is False

    def test_decompress_nonexistent_file(self):
        """Test descompresión de archivo inexistente"""
        nonexistent_file = self.temp_dir / "nonexistent.zip"
        output_dir = self.temp_dir / "output"

        result = self.compression_service.decompress_file(
            nonexistent_file, output_dir, "password"
        )

        assert result is False


class TestSecurityManager:
    """Tests para el manager de seguridad"""

    def setup_method(self):
        """Configuración para cada test"""
        self.security_manager = SecurityManager()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_code_dir = self.temp_dir / "compiled_code"
        self.test_code_dir.mkdir()

        # Crear código compilado de prueba
        (self.test_code_dir / "module1.pyc").write_bytes(b"compiled bytecode 1")
        (self.test_code_dir / "module2.pyc").write_bytes(b"compiled bytecode 2")
        (self.test_code_dir / "package").mkdir()
        (self.test_code_dir / "package" / "__init__.pyc").write_bytes(b"package init")
        (self.test_code_dir / "package" / "submodule.pyc").write_bytes(b"submodule code")

    def teardown_method(self):
        """Limpieza después de cada test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_protect_with_compression(self):
        """Test protección usando compresión"""
        output_file = self.temp_dir / "protected.zip"
        password = "license_key_123"

        result = self.security_manager.protect_compiled_code(
            self.test_code_dir, output_file, password, method="compress"
        )

        assert result is True
        assert output_file.exists()

    @pytest.mark.skipif(
        not SecurityManager().is_encryption_available(),
        reason="cryptography package not available",
    )
    def test_protect_with_encryption(self):
        """Test protección usando encriptación"""
        output_file = self.temp_dir / "protected.enc"
        password = "license_key_123"

        result = self.security_manager.protect_compiled_code(
            self.test_code_dir, output_file, password, method="encrypt"
        )

        assert result is True
        assert output_file.exists()

    def test_unprotect_compressed_code(self):
        """Test desprotección de código comprimido"""
        # Proteger primero
        protected_file = self.temp_dir / "protected.zip"
        password = "license_key_123"

        self.security_manager.protect_compiled_code(
            self.test_code_dir, protected_file, password, method="compress"
        )

        # Desproteger
        output_dir = self.temp_dir / "unprotected"
        result = self.security_manager.unprotect_code(protected_file, output_dir, password)

        assert result is True
        assert output_dir.exists()
        assert (output_dir / "module1.pyc").exists()
        assert (output_dir / "package" / "submodule.pyc").exists()

    @pytest.mark.skipif(
        not SecurityManager().is_encryption_available(),
        reason="cryptography package not available",
    )
    def test_unprotect_encrypted_code(self):
        """Test desprotección de código encriptado"""
        # Proteger primero
        protected_file = self.temp_dir / "protected.enc"
        password = "license_key_123"

        self.security_manager.protect_compiled_code(
            self.test_code_dir, protected_file, password, method="encrypt"
        )

        # Desproteger
        output_dir = self.temp_dir / "unprotected"
        result = self.security_manager.unprotect_code(protected_file, output_dir, password)

        assert result is True
        assert output_dir.exists()
        assert (output_dir / "module1.pyc").exists()
        assert (output_dir / "package" / "submodule.pyc").exists()

    def test_detect_protection_method_zip(self):
        """Test detección de método de protección ZIP"""
        protected_file = self.temp_dir / "protected.zip"
        password = "test_password"

        # Crear archivo ZIP protegido
        self.security_manager.protect_compiled_code(
            self.test_code_dir, protected_file, password, method="compress"
        )

        # Detectar método
        method = self.security_manager.detect_protection_method(protected_file)
        assert method == "compress"

    @pytest.mark.skipif(
        not SecurityManager().is_encryption_available(),
        reason="cryptography package not available",
    )
    def test_detect_protection_method_encrypted(self):
        """Test detección de método de protección encriptado"""
        protected_file = self.temp_dir / "protected.enc"
        password = "test_password"

        # Crear archivo encriptado
        self.security_manager.protect_compiled_code(
            self.test_code_dir, protected_file, password, method="encrypt"
        )

        # Detectar método
        method = self.security_manager.detect_protection_method(protected_file)
        assert method == "encrypt"

    def test_protect_invalid_method(self):
        """Test protección con método inválido"""
        output_file = self.temp_dir / "protected"
        password = "test_password"

        result = self.security_manager.protect_compiled_code(
            self.test_code_dir, output_file, password, method="invalid"
        )

        assert result is False

    def test_protect_empty_password(self):
        """Test protección con contraseña vacía"""
        output_file = self.temp_dir / "protected.zip"

        result = self.security_manager.protect_compiled_code(
            self.test_code_dir, output_file, "", method="compress"
        )

        assert result is False

    def test_protect_nonexistent_directory(self):
        """Test protección de directorio inexistente"""
        nonexistent_dir = self.temp_dir / "nonexistent"
        output_file = self.temp_dir / "protected.zip"
        password = "test_password"

        result = self.security_manager.protect_compiled_code(
            nonexistent_dir, output_file, password, method="compress"
        )

        assert result is False

    def test_unprotect_wrong_password(self):
        """Test desprotección con contraseña incorrecta"""
        # Proteger con una contraseña
        protected_file = self.temp_dir / "protected.zip"
        correct_password = "correct_password"

        self.security_manager.protect_compiled_code(
            self.test_code_dir, protected_file, correct_password, method="compress"
        )

        # Intentar desproteger con contraseña incorrecta
        output_dir = self.temp_dir / "unprotected"
        result = self.security_manager.unprotect_code(
            protected_file, output_dir, "wrong_password"
        )

        assert result is False


@pytest.mark.skipif(
    not SecurityManager().is_encryption_available(),
    reason="cryptography package not available",
)
class TestEncryptionService:
    """Tests para el servicio de encriptación (solo si está disponible)"""

    def setup_method(self):
        """Configuración para cada test"""
        from sincpro_py_compiler.infrastructure.encryption_service import (
            SimpleEncryptionService,
        )

        self.encryption_service = SimpleEncryptionService()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_files_dir = self.temp_dir / "test_files"
        self.test_files_dir.mkdir()

        # Crear archivos de prueba
        (self.test_files_dir / "test.pyc").write_bytes(b"compiled bytecode")
        (self.test_files_dir / "data.json").write_text('{"key": "value"}')

    def teardown_method(self):
        """Limpieza después de cada test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_encrypt_decrypt_roundtrip(self):
        """Test encriptación y desencriptación completa"""
        encrypted_file = self.temp_dir / "encrypted.enc"
        password = "test_encryption_key"

        # Encriptar
        encrypt_result = self.encryption_service.encrypt_directory(
            self.test_files_dir, encrypted_file, password
        )
        assert encrypt_result is True
        assert encrypted_file.exists()

        # Desencriptar
        output_dir = self.temp_dir / "decrypted"
        decrypt_result = self.encryption_service.decrypt_file(
            encrypted_file, output_dir, password
        )
        assert decrypt_result is True
        assert (output_dir / "test.pyc").exists()
        assert (output_dir / "data.json").exists()

        # Verificar contenido
        assert (output_dir / "test.pyc").read_bytes() == b"compiled bytecode"
        assert (output_dir / "data.json").read_text() == '{"key": "value"}'
