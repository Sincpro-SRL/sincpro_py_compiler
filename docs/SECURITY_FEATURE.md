# Feature de Seguridad: Compresión y Encriptación

## 📋 Descripción

Este feature permite proteger el código compilado mediante compresión con contraseña o encriptación simple, garantizando que el código distribuido no pueda ser accedido sin la licencia/contraseña correspondiente.

## 🎯 Objetivos

- **Protección del código compilado**: Impedir acceso no autorizado al código .pyc
- **Distribución segura**: Entregar código que requiera licencia para ser ejecutado
- **Flexibilidad**: Soporte para compresión con contraseña o encriptación simple
- **Simplicidad**: Implementación fácil de usar desde CLI

## 🏗️ Diseño de la Arquitectura

### Capa de Dominio
- `SecurityServiceProtocol`: Define contratos para operaciones de seguridad
- `CompressionProtocol`: Interface para compresión/descompresión
- `EncryptionProtocol`: Interface para encriptación/desencriptación

### Capa de Infraestructura
- `ZipCompressionService`: Implementa compresión ZIP con contraseña
- `SimpleEncryptionService`: Implementa encriptación básica (Fernet)
- `SecurityManager`: Orchestador de operaciones de seguridad

### Capa de Aplicación
- Extensión del CLI para soportar flags de seguridad
- Integración con el flujo de compilación existente

## 🔧 Funcionalidades

### Compresión con Contraseña
```bash
sincpro-compile ./proyecto -o ./output --compress --password "mi_licencia"
```

### Encriptación Simple
```bash
sincpro-compile ./proyecto -o ./output --encrypt --password "mi_licencia"
```

### Descompresión/Desencriptación
```bash
sincpro-decrypt ./archivo_protegido --password "mi_licencia" -o ./output
```

## 📁 Estructura de Archivos

```
sincpro_py_compiler/
├── domain/
│   ├── security_service.py      # Protocolos de seguridad
│   └── ...
├── infrastructure/
│   ├── compression_service.py   # Servicio de compresión
│   ├── encryption_service.py    # Servicio de encriptación
│   ├── security_manager.py      # Manager principal
│   └── ...
└── ...
```

## 🔒 Métodos de Protección

### 1. Compresión ZIP con Contraseña
- Utiliza zipfile con contraseña AES
- Archivo resultante: `proyecto_compilado.zip`
- Protección: Contraseña requerida para extraer

### 2. Encriptación Simple
- Utiliza cryptography.fernet
- Archivo resultante: `proyecto_compilado.enc`
- Protección: Clave derivada de contraseña

## 🚀 Flujo de Trabajo

1. **Compilación normal** → código .pyc generado
2. **Aplicar seguridad** → compresión o encriptación
3. **Distribución** → archivo protegido entregado
4. **Uso cliente** → desprotección con contraseña/licencia

## 🔐 Consideraciones de Seguridad

- La contraseña puede representar una licencia
- Protección básica, no criptográficamente robusta
- Adecuada para prevenir acceso casual al código
- Recomendada para distribución comercial básica
