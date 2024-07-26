from fetchOdooData import fetch_odoo_data
from getToken import *

def create_lead(name, contact_name, contact_email, contact_phone, description, priority='3', stage_id=None):
    """
    Crea un nuevo lead en Odoo.

    :param name: Nombre del lead.
    :param contact_name: Nombre de contacto del lead.
    :param contact_email: Correo electrónico de contacto del lead.
    :param contact_phone: Teléfono de contacto del lead.
    :param description: Descripción del lead.
    :param priority: Prioridad del lead (opcional, por defecto '3').
    :param stage_id: ID de la etapa del lead (opcional, si se especifica se asignará al lead).
    :return: ID del lead creado.
    """
    token = get_oauth_token()
    
    data = {
        'name': name,
        'contact_name': contact_name,
        'contact_email': contact_email,
        'contact_phone': contact_phone,
        'description': description,
        'priority': priority,
    }
    
    # Añadir el campo 'stage_id' solo si se proporciona
    if stage_id:
        data['stage_id'] = stage_id
    
    # Usar el método 'create' del modelo 'crm.lead' para crear el lead
    lead = fetch_odoo_data('crm.lead', 'create', data, token)
    
    return lead


# Crear un nuevo lead
lead_id = create_lead(
    name="Oportunidad de Venta XYZ",
    contact_name="Juan Pérez",
    contact_email="juan.perez@example.com",
    contact_phone="123456789",
    description="Cliente interesado en nuestro producto A.",
    priority='1',  # Alta prioridad
    stage_id=3      # Asignar a una etapa específica
)

print(f"Lead creado con ID: {lead_id}")

