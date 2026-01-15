import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, SourceData, Publisher, Property, Image
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_DATABASE = os.getenv('DB_DATABASE', 'xintel_network')
DB_USERNAME = os.getenv('DB_USERNAME', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')

# Crear la URL de conexión
DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?charset=utf8mb4"

# Crear engine y session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """
    Obtiene una nueva sesión de base de datos
    """
    return SessionLocal()


def get_or_create_source(session, source_id=1, name='ZonaProp', portal_url='https://www.zonaprop.com.ar'):
    """
    Obtiene o crea el registro de la fuente de datos (ZonaProp)

    Args:
        session: Sesión de SQLAlchemy
        source_id: ID de la fuente (default: 1)
        name: Nombre de la fuente
        portal_url: URL del portal

    Returns:
        SourceData: Objeto de la fuente
    """
    source = session.query(SourceData).filter_by(id=source_id).first()

    if not source:
        source = SourceData(
            id=source_id,
            name=name,
            portal_url=portal_url
        )
        session.add(source)
        session.commit()
        print(f"Fuente de datos creada: {name} (ID: {source_id})")

    return source


def get_or_create_publisher(session, publisher_data):
    """
    Obtiene o crea un registro de publisher (inmobiliaria)

    Args:
        session: Sesión de SQLAlchemy
        publisher_data: Dict con datos del publisher

    Returns:
        Publisher: Objeto del publisher
    """
    publisher_id = int(publisher_data.get('publisher_id', 0))

    if not publisher_id:
        raise ValueError("publisher_id is required")

    publisher = session.query(Publisher).filter_by(id=publisher_id).first()

    if not publisher:
        publisher = Publisher(
            id=publisher_id,
            name=publisher_data.get('name'),
            url=publisher_data.get('url'),
            logo_url=publisher_data.get('logo_url'),
            phone=publisher_data.get('phone'),
            address=publisher_data.get('address')
        )
        session.add(publisher)
        session.commit()
        print(f"Publisher creado: {publisher.name} (ID: {publisher_id})")

    return publisher


def location_id_to_int(location_id_str):
    """
    Convierte un location_id string a un integer usando hash

    Args:
        location_id_str: String del location_id (ej: "V1-D-1003990")

    Returns:
        int: Hash numérico del location_id
    """
    if not location_id_str:
        return 0

    # Extraer el número al final del location_id
    # Ej: "V1-D-1003990" -> 1003990
    parts = location_id_str.split('-')
    if len(parts) > 0:
        try:
            return int(parts[-1])
        except ValueError:
            pass

    # Si no se puede extraer, usar hash absoluto
    return abs(hash(location_id_str)) % (10 ** 8)


def save_property_to_db(session, estate_data):
    """
    Guarda una propiedad en la base de datos junto con sus imágenes

    Args:
        session: Sesión de SQLAlchemy
        estate_data: Dict con todos los datos de la propiedad

    Returns:
        Property: Objeto de la propiedad guardada
    """
    # Asegurar que existe la fuente de datos
    source = get_or_create_source(session)

    # Obtener o crear el publisher
    publisher_data = {
        'publisher_id': estate_data.get('publisher_id'),
        'name': estate_data.get('publisher_name'),
        'url': estate_data.get('publisher_url'),
        'logo_url': estate_data.get('publisher_logo_url'),
        'phone': estate_data.get('publisher_phone'),
        'address': None
    }
    publisher = get_or_create_publisher(session, publisher_data)

    # Convertir location_id a int
    location_id = location_id_to_int(estate_data.get('location_id_raw', ''))

    # Preparar datos de la propiedad
    publication_id = int(estate_data.get('posting_id', 0))

    # Verificar si la propiedad ya existe
    existing_property = session.query(Property).filter_by(
        publication_id=publication_id,
        source_id=source.id
    ).first()

    if existing_property:
        print(f"Propiedad {publication_id} ya existe, actualizando...")
        # Actualizar campos
        existing_property.updated_at = datetime.now()
        existing_property.sell_price = estate_data.get('sell_price')
        existing_property.rent_price = estate_data.get('rent_price')
        existing_property.sell_currency = estate_data.get('sell_currency')
        existing_property.rent_currency = estate_data.get('rent_currency')
        existing_property.expenses = estate_data.get('expenses_value')
        existing_property.expenses_currency = estate_data.get('expenses_currency')
        existing_property.title = estate_data.get('title', '')[:255]
        existing_property.description = estate_data.get('description', '')[:255]
        existing_property.url = estate_data.get('url', '')[:255]

        session.commit()
        property_obj = existing_property
    else:
        # Crear nueva propiedad
        property_obj = Property(
            publication_id=publication_id,
            source_id=source.id,
            updated_at=datetime.now(),
            created_at=estate_data.get('created_at', str(datetime.now())),
            sell_price=estate_data.get('sell_price'),
            rent_price=estate_data.get('rent_price'),
            sell_currency=estate_data.get('sell_currency'),
            rent_currency=estate_data.get('rent_currency'),
            expenses=estate_data.get('expenses_value'),
            expenses_currency=estate_data.get('expenses_currency'),
            publisher_id=publisher.id,
            location_id=location_id,
            location_description=estate_data.get('location', '')[:255],
            garage_quantity=estate_data.get('cocheras') if estate_data.get('cocheras') else None,
            property_type=estate_data.get('property_type', '')[:255],
            url=estate_data.get('url', '')[:255],   
            title=estate_data.get('title', '')[:255],
            enviroments=estate_data.get('ambientes') if estate_data.get('ambientes') else None,
            bedrooms=estate_data.get('dormitorios') if estate_data.get('dormitorios') else None,
            bathrooms=estate_data.get('baños') if estate_data.get('baños') else None,
            antiquity=estate_data.get('antiguedad', '')[:255] if estate_data.get('antiguedad') else None,
            address=estate_data.get('address', '')[:255],
            description=estate_data.get('description', '')[:255]
        )

        session.add(property_obj)
        session.commit()
        print(f"Propiedad guardada: {property_obj.title} (ID: {property_obj.id})")

    # Guardar imágenes
    images_data = estate_data.get('images', [])
    if images_data:
        # Eliminar imágenes existentes si hay
        session.query(Image).filter_by(
            property_id=property_obj.id,
            source_id=source.id
        ).delete()

        for img in images_data:
            image = Image(
                property_id=property_obj.id,
                source_id=source.id,
                image_url=img.get('url', '')[:255],
                order=img.get('order')
            )
            session.add(image)

        session.commit()
        print(f"{len(images_data)} imágenes guardadas para la propiedad {property_obj.id}")

    return property_obj


def save_estates_to_db(estates_data):
    """
    Guarda múltiples propiedades en la base de datos

    Args:
        estates_data: Lista de dicts con datos de propiedades

    Returns:
        int: Número de propiedades guardadas
    """
    session = get_session()
    saved_count = 0

    try:
        for estate in estates_data:
            try:
                save_property_to_db(session, estate)
                saved_count += 1
            except Exception as e:
                print(f"Error guardando propiedad {estate.get('posting_id')}: {e}")
                session.rollback()

        print(f"\nTotal de propiedades guardadas en BD: {saved_count}")
        return saved_count

    finally:
        session.close()
