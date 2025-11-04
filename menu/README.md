# 🥗 Gemini Menu Planner (Asistente Semanal de Comidas)

Este es un asistente de planificación de menús semanal construido sobre el framework Django y potenciado por los modelos de Inteligencia Artificial Generativa de Google, desplegado de manera eficiente en Google Cloud Run.

El proyecto demuestra el uso de la API de Vertex AI para manejar conversaciones persistentes (Chat) y generación de imágenes (Text-to-Image), integradas en un entorno de producción contenedorizado (Docker).

## 🚀 Tecnologías Clave Utilizadas

| Componente | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Backend** | **Python / Django** | Framework principal para el manejo de rutas y lógica de negocio. |
| **Inteligencia Artificial** | **Google Vertex AI SDK** (Python) | Conexión con los modelos de Gemini y Imagen 3.0. |
| **Modelo de Chat** | **Gemini 2.5 Flash** | Planificación de menús conversacional con memoria (historial). |
| **Modelo de Imagen** | **Imagen 3.0 (`imagen-3.0-generate-002`)** | Generación de imágenes inspiradoras para los platos. |
| **Contenerización** | **Docker** | Empaquetado de la aplicación y sus dependencias para el despliegue. |
| **Servidor WSGI** | **Gunicorn** | Servidor de producción utilizado dentro del contenedor Docker. |
| **Despliegue** | **Google Cloud Run** | Plataforma serverless (sin servidor) para escalado automático y alta disponibilidad. |

## ⚙️ Características y Funcionalidades

* **Planificación Conversacional:** Usa el modelo **Gemini 2.5 Flash** con un `System Instruction` para mantener una personalidad constante como chef y planificador de menús.
* **Memoria de Chat:** Implementación de sesiones de chat persistentes con el objeto `client.chats.create` y el almacenamiento de `chat_sessions` en memoria (ideal para la arquitectura sin estado de Cloud Run).
* **Generación de Imagen:** Integración del modelo **Imagen 3.0** (`imagen-3.0-generate-002`) para crear contenido visual inspirador bajo demanda.
* **Despliegue Serverless:** Configuración completa con **Dockerfile** para ser ejecutado con **Gunicorn** y desplegado en **Cloud Run**, utilizando la **Cuenta de Servicio** para la autenticación automática con Vertex AI (Application Default Credentials - ADC).

## ⚠️ Desafíos Superados (Errores Críticos)

El desarrollo requirió resolver varios problemas comunes de integración y despliegue:

* **Sintaxis de la API:** Corrección de la estructura `Part.from_text()` y la sintaxis de `role='user'` para la generación de imágenes (`400 INVALID_ARGUMENT`).
* **Modelos y Endpoints:** Uso de alias de modelos estables (`gemini-2.5-flash`) y la configuración correcta del cliente con la región (`location='us-central1'`) para evitar errores `404 NOT_FOUND`.
* **Permisos de Despliegue:** Resolución de errores de permiso (`PERMISSION_DENIED`) en Cloud Build y configuración del rol **`Vertex AI User`** en las Cuentas de Servicio para asegurar el acceso a la API desde la nube.
* **Gestión de Cuotas:** Manejo del error `429 RESOURCE_EXHAUSTED` causado por la baja cuota predeterminada de Imagen 3.0.

## 🚀 Cómo Desplegar

1.  Asegúrate de tener la **Google Cloud CLI** instalada.
2.  Verifica que tu **Cuenta de Servicio** de Cloud Run tenga el rol **`Vertex AI User`**.
3.  Ejecuta el comando de despliegue desde la carpeta `/menu/`:

```bash
gcloud run deploy menu-gemini-app --source . --region us-central1 --platform managed --allow-unauthenticated