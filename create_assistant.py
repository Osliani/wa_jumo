from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("API_KEY"))

prompt = """
Se te enviarán conversaciones entre un cliente potencial y un asistente virtual. Necesito que extraigas la información de cada uno de los productos y servicios sugeridos por el asistente y la envíes en tu respuesta. En el caso de que exista un rango de precios se pondrá la media como precio unitario. El parámetro product_id lo obtendras a partir del nombre del producto y del siguiente diccionario:
products_id = {
    "Fábrica de Empleados Virtuales": 964,
    "Implantación de Odoo Community Plus": 512,
    "Upgrade Odoo Native": 874,
    "Upgrade Odoo Plus": 874,
    "Servidor": 480,
    "Bolsa de horas de desarrollo o configuración": 478,
    "Formación y capacitación de Odoo": 507
}
El parámetro product_uom lo obtendras a partir del nombre del producto y del siguiente diccionario:
products_uom = {
    "Fábrica de Empleados Virtuales": 1,
    "Implantación de Odoo Community Plus": 1,
    "Upgrade Odoo Native": 6,
    "Upgrade Odoo Plus": 6,
    "Servidor": 1,
    "Bolsa de horas de desarrollo o configuración": 6,
    "Formación y capacitación de Odoo": 6
}
Por favor, responde estrictamente en el siguiente formato JSON (para poder convertir los datos en un dicionario python con json.loads() al recibirlos):
[
  {
    "product_name": "string",
    "product_id": "string",
    "price_unit": number,
    "description": "string",
    "product_uom": number,
    "discount": number
  }
]
Ejemplo:
[
  {
    "product_name": "Bolsa de horas",
    "product_id": 478,
    "price_unit": 80,
    "description": "De 10 horas a 40 horas: 80€ por hora - De 40 horas a 100 horas: 70€ por hora - De 100 horas a 300 horas: 65€ por hora",
    "product_uom": 6,
    "discount": 0
  }
]
Los parametros que no se encuentren enviarlos como "Empty".
"""

assistant = client.beta.assistants.create (
  name = "Extractor_14",
  instructions = prompt,
  model = "gpt-4-1106-preview",
)

print(assistant.id)