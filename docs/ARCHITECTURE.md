# Arquitectura de SincPro Python Compiler

## 📋 Visión General

SincPro Python Compiler implementa **Clean Architecture** con separación clara de responsabilidades, permitiendo compilar proyectos Python (.py → .pyc) y distribuir código protegido mediante compresión/encriptación con contraseña.

## 🏗️ Estructura General del Proyecto

```mermaid
graph TB
    subgraph "📱 Application Layer"
        CLI[CLI Principal]
        DecryptCLI[CLI Desprotección]
    end
    
    subgraph "🏢 Domain Layer"
        CompilerProtocol[CompilerServiceProtocol]
        FileProtocol[FileManagerProtocol]
        SecurityProtocol[SecurityServiceProtocol]
        CompressionProtocol[CompressionProtocol]
        EncryptionProtocol[EncryptionProtocol]
    end
    
    subgraph "🔧 Infrastructure Layer"
        PythonCompiler[PythonCompiler]
        FileManager[FileManager]
        SecurityManager[SecurityManager]
        CompressionService[ZipCompressionService]
        EncryptionService[SimpleEncryptionService]
    end
    
    subgraph "📦 Resources Layer"
        Templates[Exclusion Templates]
        ResourceManager[ResourceManager]
    end
    
    CLI --> CompilerProtocol
    CLI --> SecurityProtocol
    DecryptCLI --> SecurityProtocol
    
    CompilerProtocol --> PythonCompiler
    FileProtocol --> FileManager
    SecurityProtocol --> SecurityManager
    CompressionProtocol --> CompressionService
    EncryptionProtocol --> EncryptionService
    
    PythonCompiler --> ResourceManager
    SecurityManager --> CompressionService
    SecurityManager --> EncryptionService
    
    style CLI fill:#e1f5fe
    style SecurityManager fill:#fff3e0
    style CompressionService fill:#f3e5f5
    style EncryptionService fill:#e8f5e8
```

## 📁 Matriz de Módulos y Responsabilidades

| 📂 Directorio/Módulo | 🎯 Propósito Principal | 📝 Descripción Detallada | 🔗 Dependencias |
|---------------------|------------------------|---------------------------|------------------|
| **`cli.py`** | Punto de entrada principal | Interface de línea de comandos que orquesta compilación y protección | `argparse`, `PythonCompiler`, `SecurityManager` |
| **`decrypt_cli.py`** | Desprotección de código | CLI especializado para desproteger archivos compilados | `argparse`, `SecurityManager` |
| **`domain/`** | Contratos y reglas de negocio | Define interfaces y protocolos sin implementación | Solo tipos de Python |
| **`domain/compiler_service.py`** | Protocolos de compilación | Interfaces para compilación y manejo de archivos | `typing.Protocol` |
| **`domain/security_service.py`** | Protocolos de seguridad | Interfaces para compresión y encriptación | `typing.Protocol` |
| **`infrastructure/`** | Implementaciones concretas | Servicios que implementan la lógica de negocio | Depende del dominio |
| **`infrastructure/python_compiler.py`** | Compilador Python | Compila .py a .pyc y maneja exclusiones | `py_compile`, `pathlib` |
| **`infrastructure/file_manager.py`** | Gestor de archivos | Operaciones de archivos y directorios | `shutil`, `pathlib` |
| **`infrastructure/security_manager.py`** | Orchestrador de seguridad | Coordina compresión y encriptación | `CompressionService`, `EncryptionService` |
| **`infrastructure/compression_service.py`** | Servicio de compresión | Compresión ZIP con protección por contraseña | `zipfile`, `hashlib` |
| **`infrastructure/encryption_service.py`** | Servicio de encriptación | Encriptación AES usando Fernet | `cryptography` (opcional) |
| **`resources/`** | Recursos estáticos | Templates y patrones de exclusión | - |
| **`resources/resource_manager.py`** | Gestor de recursos | Carga templates de exclusión | `pathlib` |
| **`tests/`** | Suite de pruebas | Tests unitarios e integración | `pytest`, `tempfile` |

## 🔄 Flujo de Ejecución Principal

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Compiler
    participant Security
    participant FileSystem
    
    User->>CLI: sincpro-compile ./proyecto --compress --password "lic123"
    CLI->>CLI: Validar argumentos
    CLI->>Compiler: compile_project()
    
    loop Para cada archivo .py
        Compiler->>Compiler: ¿Debe excluirse?
        Compiler->>FileSystem: Compilar .py → .pyc
        Compiler->>FileSystem: Copiar otros archivos
    end
    
    Compiler->>CLI: ✅ Compilación exitosa
    CLI->>Security: protect_compiled_code(method="compress")
    Security->>Security: Codificar nombres archivos
    Security->>FileSystem: Crear ZIP protegido
    Security->>CLI: ✅ Protección exitosa
    CLI->>User: 🎉 Código protegido: ./compiled.zip
```

## 🔐 Arquitectura del Sistema de Seguridad

```mermaid
graph LR
    subgraph "🎛️ Control Layer"
        SecurityManager[SecurityManager<br/>Orchestrator]
    end
    
    subgraph "🗜️ Compression Path"
        ZipService[ZipCompressionService<br/>• Codifica nombres<br/>• Crea metadata<br/>• ZIP protegido]
    end
    
    subgraph "🔒 Encryption Path"
        EncService[SimpleEncryptionService<br/>• TAR.GZ + Fernet<br/>• PBKDF2 derivation<br/>• AES encryption]
    end
    
    subgraph "🔍 Detection"
        Detector[ProtectionDetector<br/>• Auto-detect ZIP<br/>• Auto-detect ENC<br/>• Metadata parsing]
    end
    
    SecurityManager --> ZipService
    SecurityManager --> EncService
    SecurityManager --> Detector
    
    ZipService --> FileOutput[📁 .zip file]
    EncService --> FileOutput2[📁 .enc file]
    
    style SecurityManager fill:#fff3e0
    style ZipService fill:#e3f2fd
    style EncService fill:#e8f5e8
    style Detector fill:#fce4ec
```

## 📊 Matriz de Funcionalidades por Comando

| 🎯 Comando | 📝 Función | 🔧 Parámetros | 📤 Salida | 🔄 Flujo Interno |
|------------|------------|---------------|-----------|------------------|
| `sincpro-compile ./proyecto` | Compilación básica | `source`, `--output`, `--template` | Directorio con .pyc | CLI → Compiler → FileSystem |
| `sincpro-compile ./proyecto --compress --password "lic"` | Compilar + Comprimir | Básicos + `--compress`, `--password` | Archivo .zip protegido | CLI → Compiler → SecurityManager → ZipService |
| `sincpro-compile ./proyecto --encrypt --password "key"` | Compilar + Encriptar | Básicos + `--encrypt`, `--password` | Archivo .enc encriptado | CLI → Compiler → SecurityManager → EncryptionService |
| `sincpro-decrypt ./archivo.zip --password "lic" -o ./salida` | Desproteger ZIP | `source`, `--password`, `--output` | Directorio con .pyc | DecryptCLI → SecurityManager → ZipService |
| `sincpro-decrypt ./archivo.enc --password "key" -o ./salida` | Desencriptar | `source`, `--password`, `--output` | Directorio con .pyc | DecryptCLI → SecurityManager → EncryptionService |
| `sincpro-compile --list-templates` | Listar templates | `--list-templates` | Lista de templates | CLI → ResourceManager |

## 🎭 Escenarios de Uso Detallados

### 📦 Escenario 1: Compilación Básica

```mermaid
flowchart TD
    A[👤 Usuario ejecuta<br/>sincpro-compile ./mi_app] --> B{🔍 Validar argumentos}
    B -->|✅ Válidos| C[📂 Escanear directorio fuente]
    B -->|❌ Inválidos| Z[❌ Error y ayuda]
    
    C --> D{📄 Para cada archivo}
    D -->|.py| E[🔄 Compilar a .pyc]
    D -->|otros| F[📋 Copiar tal como está]
    D -->|excluidos| G[🚫 Ignorar]
    
    E --> H[✅ Archivo compilado]
    F --> H
    G --> H
    H --> I{🔄 ¿Más archivos?}
    I -->|Sí| D
    I -->|No| J[🎉 Compilación exitosa<br/>📁 ./compiled/]
    
    style A fill:#e1f5fe
    style J fill:#e8f5e8
    style Z fill:#ffebee
```

### 🔒 Escenario 2: Compilación con Protección

```mermaid
flowchart TD
    A[👤 Usuario ejecuta<br/>sincpro-compile ./app --compress --password 'lic123'] --> B[📦 Compilación básica]
    B --> C{🔐 ¿Protección solicitada?}
    C -->|compress| D[🗜️ ZipCompressionService]
    C -->|encrypt| E[🔒 SimpleEncryptionService]
    C -->|ninguna| F[✅ Solo compilación]
    
    D --> G[🔑 Codificar nombres archivos]
    G --> H[📋 Crear metadata con mapeo]
    H --> I[🗜️ Crear ZIP con contraseña]
    I --> J[✅ Archivo .zip protegido]
    
    E --> K[🏗️ Crear TAR.GZ temporal]
    K --> L[🔑 Derivar clave con PBKDF2]
    L --> M[🔒 Encriptar con Fernet/AES]
    M --> N[✅ Archivo .enc encriptado]
    
    J --> O[🗑️ Eliminar directorio temporal]
    N --> O
    F --> P[📁 Mantener directorio]
    O --> Q[🎉 Proceso completado]
    P --> Q
    
    style A fill:#e1f5fe
    style D fill:#fff3e0
    style E fill:#e8f5e8
    style Q fill:#e8f5e8
```

### 🔓 Escenario 3: Desprotección de Código

```mermaid
flowchart TD
    A[👤 Usuario ejecuta<br/>sincpro-decrypt ./app.zip --password 'lic123'] --> B[🔍 Detectar método protección]
    B -->|ZIP detected| C[🗜️ Método: Compresión]
    B -->|ENC detected| D[🔒 Método: Encriptación]
    B -->|Unknown| E[❌ Error: Formato no reconocido]
    
    C --> F[📖 Leer metadata ZIP]
    F --> G{🔑 ¿Contraseña correcta?}
    G -->|✅ Correcta| H[📂 Extraer archivos codificados]
    G -->|❌ Incorrecta| I[❌ Error: Contraseña incorrecta]
    
    D --> J[📖 Leer metadata encriptado]
    J --> K{🔑 ¿Contraseña correcta?}
    K -->|✅ Correcta| L[🔓 Desencriptar TAR.GZ]
    K -->|❌ Incorrecta| M[❌ Error: Contraseña incorrecta]
    
    H --> N[🔄 Restaurar nombres originales]
    L --> O[📂 Extraer archivos]
    N --> P[✅ Código desprotegido]
    O --> P
    
    style A fill:#e1f5fe
    style P fill:#e8f5e8
    style I fill:#ffebee
    style M fill:#ffebee
    style E fill:#ffebee
```

## 🔧 Lógica de Copias Fieles en la Infraestructura

El flujo de compilación en SincPro Python Compiler ahora incluye la capacidad de **copiar archivos y carpetas fielmente** según patrones definidos en cada template. Esta lógica está implementada en la capa de infraestructura (`PythonCompiler` y `CompilerService`).

- Los archivos y carpetas definidos como "copias fieles" en el template (por ejemplo, `odoo`) se copian tal cual al directorio de salida, sin ser compilados ni excluidos.
- El resto de archivos `.py` se compilan a `.pyc`.
- Los patrones de exclusión siguen aplicándose normalmente.

Esta funcionalidad permite mantener la integridad de archivos requeridos por frameworks como Odoo, facilitando la distribución y despliegue sin perder información esencial.

**Ejemplo:**

- Template `odoo`: Copia fiel de `__manifest__.py`, `__openerp__.py`, `static/`, `data/`, `demo/`, `security/`.
- Template `django`: Excluye carpetas como `migrations/`, `static/`, pero no realiza copias fieles por defecto.

La lógica puede ser extendida o personalizada editando los templates en `resources/exclude_patterns/`.

## 🧪 Arquitectura de Testing

```mermaid
graph TB
    subgraph "🧪 Test Layers"
        UnitTests[Unit Tests<br/>Servicios individuales]
        IntegrationTests[Integration Tests<br/>Flujo completo CLI]
        CommercialTests[Commercial Tests<br/>Casos uso real]
    end
    
    subgraph "🎯 Test Targets"
        CompilerTests[Compiler Service Tests]
        SecurityTests[Security Features Tests]
        FileTests[File Manager Tests]
        CLITests[CLI Integration Tests]
    end
    
    subgraph "🔧 Test Infrastructure"
        TempDirs[Temporary Directories]
        MockFiles[Mock Files]
        Subprocess[Subprocess Calls]
    end
    
    UnitTests --> CompilerTests
    UnitTests --> SecurityTests
    UnitTests --> FileTests
    
    IntegrationTests --> CLITests
    CommercialTests --> CLITests
    
    CompilerTests --> TempDirs
    SecurityTests --> TempDirs
    CLITests --> Subprocess
    
    style UnitTests fill:#e3f2fd
    style IntegrationTests fill:#fff3e0
    style CommercialTests fill:#e8f5e8
```

## ⚙️ Configuración y Dependencias

### 📦 Dependencias Core
```mermaid
graph LR
    Core[SincPro Core] --> Python[Python 3.10+]
    Core --> Pathlib[pathlib]
    Core --> PyCompile[py_compile]
    Core --> Zipfile[zipfile]
    Core --> Argparse[argparse]
    
    Optional[Encryption Optional] --> Crypto[cryptography]
    Optional --> Fernet[Fernet/AES]
    Optional --> PBKDF2[PBKDF2HMAC]
    
    Dev[Development] --> Pytest[pytest]
    Dev --> TempFile[tempfile]
    Dev --> Subprocess[subprocess]
    
    style Core fill:#e1f5fe
    style Optional fill:#fff3e0
    style Dev fill:#f3e5f5
```

### 🎛️ Matriz de Configuración por Template

| 🏷️ Template | 📂 Tipo Proyecto | 🚫 Exclusiones Específicas | 📋 Casos de Uso |
|-------------|-------------------|----------------------------|------------------|
| **basic** | Proyecto Python estándar | `__pycache__/`, `.git/`, `.venv/`, `*.log` | Scripts, aplicaciones simples |
| **django** | Proyecto Django | Basic + `migrations/`, `static/`, `db.sqlite3` | Aplicaciones web Django |
| **odoo** | Addon Odoo | Basic + `__manifest__.py`, `security/`, `data/` | Módulos Odoo/OpenERP |
| **custom** | Proyecto personalizado | Definido por archivo `.sincpro_exclude` | Cualquier proyecto específico |

## 🔍 Monitoreo y Logging

```mermaid
flowchart LR
    subgraph "📊 Logging Levels"
        DEBUG[DEBUG<br/>Detalles internos]
        INFO[INFO<br/>Progreso general]
        WARNING[WARNING<br/>Dependencias opcionales]
        ERROR[ERROR<br/>Fallos críticos]
    end
    
    subgraph "📍 Log Sources"
        CLI_Log[CLI Operations]
        Compiler_Log[Compilation Process]
        Security_Log[Security Operations]
        File_Log[File Operations]
    end
    
    CLI_Log --> INFO
    Compiler_Log --> DEBUG
    Compiler_Log --> INFO
    Security_Log --> DEBUG
    Security_Log --> WARNING
    Security_Log --> ERROR
    File_Log --> DEBUG
    
    style DEBUG fill:#e3f2fd
    style INFO fill:#e8f5e8
    style WARNING fill:#fff3e0
    style ERROR fill:#ffebee
```

## 🚀 Rendimiento y Escalabilidad

### 📈 Características de Rendimiento

| 🎯 Aspecto | 📊 Métrica | 🔧 Optimización | 📝 Notas |
|------------|------------|------------------|----------|
| **Compilación** | ~100 archivos/seg | Procesamiento secuencial | Limitado por I/O de disco |
| **Compresión** | ~50MB/seg | Nivel 6 ZIP | Balance compresión/velocidad |
| **Encriptación** | ~30MB/seg | AES hardware acelerado | Depende de cryptography |
| **Memoria** | <100MB típico | Streaming para archivos grandes | Sin cargar todo en RAM |
| **Concurrencia** | Secuencial actual | Potencial paralelización futura | Thread-safe por diseño |

### 🔮 Extensibilidad Futura

```mermaid
graph TB
    Current[🎯 Implementación Actual] --> Future[🔮 Extensiones Futuras]
    
    subgraph Current
        BasicComp[Compilación Básica]
        ZipProt[Protección ZIP]
        EncProt[Encriptación Fernet]
    end
    
    subgraph Future
        ParallelComp[Compilación Paralela]
        CloudProt[Protección Cloud]
        AdvancedEnc[Encriptación RSA/ECC]
        LicenseServer[Servidor Licencias]
        GUIInterface[Interfaz Gráfica]
    end
    
    BasicComp -.-> ParallelComp
    ZipProt -.-> CloudProt
    EncProt -.-> AdvancedEnc
    Current -.-> LicenseServer
    Current -.-> GUIInterface
    
    style Current fill:#e8f5e8
    style Future fill:#fff3e0
```

Esta arquitectura garantiza **mantenibilidad**, **extensibilidad** y **robustez** siguiendo principios SOLID y Clean Architecture, permitiendo evolucionar el sistema sin romper funcionalidades existentes.
