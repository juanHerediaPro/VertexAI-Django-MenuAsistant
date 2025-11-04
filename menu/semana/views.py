# semana/views.py - CÓDIGO FINAL CON TU CONFIGURACIÓN DE PROMPTS
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types
from django.conf import settings # Para acceder a la configuración de Django
from PIL import Image


import json
import base64 
import io

# --- CONFIGURACIÓN DE VERTEX AI ---
# semana/views.py (Cerca del inicio del archivo)
# ... otras constantes como MODEL_NAME ...

IMAGE_GENERATION_MODEL_NAME = "imagen-3.0-generate-002"
MODEL_NAME = "gemini-2.5-flash"

# 1. System Instruction (si_text1)
SYSTEM_INSTRUCTION = """Eres un chef y planificador de menú semanal altamente creativo y amigable. Responde de forma conversacional a preguntas generales de cocina. Tu tarea principal es ayudar al usuario a crear planes de comidas saludables y económicas, enfocándote en ingredientes sencillos. REGLA CLAVE: Cuando el usuario te pida un 'Menú Completo' o 'Menú Semanal', responde SIEMPRE con una lista clara de 7 días (Lunes a Domingo), usando viñetas o números y NUNCA incluyas encabezados como 'Día 1' o 'Menú de la Semana'."""

# 2. Ejemplos (text1 desglosados en pares de historial para el chat)
EXAMPLE_1_USER = "Dame un Menú Completo para la semana que viene."
EXAMPLE_1_MODEL = """¡Claro! Aquí tienes un menú semanal muy fácil de seguir y delicioso: \n\n* Lunes: Lentejas guisadas con chorizo vegetariano y arroz integral.\n* Martes: Pollo al curry con leche de coco y verduras salteadas.\n* Miércoles: Tostadas de aguacate y huevo revuelto con una fruta.\n* Jueves: Pasta con atún, tomate cherry y albahaca.\n* Viernes: Pizza casera rápida con queso mozarella y pimientos.\n* Sábado: Pescado al horno (tilapia) con patatas y ensalada.\n* Domingo: Sopa de pollo (sancocho) con maíz y cilantro."""

EXAMPLE_2_USER = "Necesito que me crees un plan de 7 días, pero quiero que sea bajo en costos."
EXAMPLE_2_MODEL = """¡Excelente idea! Un plan económico es siempre útil. Este menú es genial:\n\n* Lunes: Huevos revueltos con frijoles y tortilla.\n* Martes: Sopa de verduras con pan tostado.\n* Miércoles: Arroz con pollo y una porción de aguacate.\n* Jueves: Croquetas de atún con ensalada de col.\n* Viernes: Pasta con salsa de tomate y queso parmesano.\n* Sábado: Estofado de res sencillo con papas.\n* Domingo: Sopa de fideos con pollo desmenuzado y zanahorias."""

INITIAL_HISTORY_PARTS = [
    # Ejemplo 1
    types.Content(role='user', parts=[types.Part.from_text(text=EXAMPLE_1_USER)]), # <-- CORREGIDO
    types.Content(role='model', parts=[types.Part.from_text(text=EXAMPLE_1_MODEL)]), # <-- CORREGIDO
    
    # Ejemplo 2
    types.Content(role='user', parts=[types.Part.from_text(text=EXAMPLE_2_USER)]), # <-- CORREGIDO
    types.Content(role='model', parts=[types.Part.from_text(text=EXAMPLE_2_MODEL)]), # <-- CORREGIDO
]


REGION = "us-central1"
# Inicialización del cliente y almacenamiento de sesiones

chat_sessions = {} 
client = None
try:
    client = genai.Client(vertexai=True , location=REGION)
    print("Servidor Django listo. Cliente de GenAI inicializado.")
except Exception as e:
    print(f"ERROR: No se pudo inicializar el cliente de GenAI: {e}")
    pass 

def index(request):
    """Renderiza la página principal."""
    # Nota: Renderiza desde la carpeta 'semana'
    return render(request, 'semana/index.html') 

@csrf_exempt
def chat_api(request):
    """Maneja la lógica de chat con Gemini."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_prompt = data.get('prompt')
            session_id = data.get('session_id', 'default_user') 

            if not user_prompt:
                return JsonResponse({"error": "Falta el 'prompt' de usuario"}, status=400)

            if session_id not in chat_sessions:
                # Crea la sesión de chat con tu configuración exacta
                config = types.GenerateContentConfig(
                    system_instruction=types.Part.from_text(text=SYSTEM_INSTRUCTION),
                )
                
                chat = client.chats.create(
                    model=MODEL_NAME,
                    history=INITIAL_HISTORY_PARTS,
                    config=config
                )
                chat_sessions[session_id] = chat

            chat = chat_sessions[session_id]
            
            # Envía el mensaje y mantiene la conversación
            response = chat.send_message(user_prompt)

            return JsonResponse({"response": response.text})

        except Exception as e:
            return JsonResponse({"error": f"Error de API/Servidor: {e}"}, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def generate_image_api(request):
    """
    Genera una imagen inspiradora usando Imagen 3.0 y devuelve el base64.
    """
    if request.method == 'POST':
        try:
            global client

            image_prompt = "Una imagen inspiradora de un plato saludable y delicioso. Estilo fotografía gourmet, bien iluminado."

            generate_config = types.GenerateContentConfig(
                temperature=0.9,
                top_p=0.95,
                max_output_tokens=2048 
            )

            # Usamos IMAGE_GENERATION_MODEL_NAME ("imagen-3.0-generate-002")
            # y el rol 'user' (que resuelve el error 400 INVALID_ARGUMENT)
            image_response = client.models.generate_content(
                model=IMAGE_GENERATION_MODEL_NAME, 
                contents=[
                    types.Content(
                        role='user', 
                        parts=[types.Part.from_text(text=image_prompt)]
                    )
                ],
                config=generate_config
            )

            # --- Lógica de Extracción de Base64 ---
            image_data_base64 = None
            for candidate in image_response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data:
                        image_data_base64 = part.inline_data.data
                        break
                if image_data_base64:
                    break

            if image_data_base64:
                return JsonResponse({"image_data": image_data_base64})
            else:
                return JsonResponse({
                    "error": "Error: El modelo Imagen 3.0 no generó datos de imagen. Esto es inusual y puede deberse a un error temporal de la API.",
                }, status=500)

        except Exception as e:
            return JsonResponse({"error": f"Error al generar la imagen: {e}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)