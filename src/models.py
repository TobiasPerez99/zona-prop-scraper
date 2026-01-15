from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class SourceData(Base):
    """
    Tabla: sources_data
    Representa las fuentes de datos (portales inmobiliarios)
    """
    __tablename__ = 'sources_data'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    portal_url = Column(String(255))

    # Relaciones
    properties = relationship('Property', back_populates='source')
    images = relationship('Image', back_populates='source')

    def __repr__(self):
        return f"<SourceData(id={self.id}, name='{self.name}')>"


class Publisher(Base):
    """
    Tabla: publisher
    Representa las inmobiliarias/publicadores
    """
    __tablename__ = 'publisher'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(String(255))
    logo_url = Column(String(255))
    phone = Column(String(255))
    address = Column(String(255))

    # Relaciones
    properties = relationship('Property', back_populates='publisher')

    def __repr__(self):
        return f"<Publisher(id={self.id}, name='{self.name}')>"


class Property(Base):
    """
    Tabla: properties
    Representa las propiedades scrapeadas
    Tiene clave primaria compuesta: (id, publication_id, source_id, publisher_id, location_id)
    """
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True, autoincrement=True)
    publication_id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources_data.id'), primary_key=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = Column(String(255))
    sell_price = Column(DECIMAL(10, 2))
    rent_price = Column(DECIMAL(10, 2))
    sell_currency = Column(String(255))
    rent_currency = Column(String(255))
    expenses = Column(String(255), default='')
    expenses_currency = Column(String(255), default='')
    publisher_id = Column(Integer, ForeignKey('publisher.id'), primary_key=True)
    location_id = Column(Integer, primary_key=True)
    location_description = Column(String(255))
    garage_quantity = Column(Integer, default=0)
    property_type = Column(String(255))
    url = Column(String(255))
    title = Column(String(255))
    enviroments = Column(Integer, default=0)
    bedrooms = Column(Integer, default=0)
    bathrooms = Column(Integer, default=0)
    antiquity = Column(String(255), default='')
    address = Column(String(255), default='')
    description = Column(String(255), default='')

    # Relaciones
    source = relationship('SourceData', back_populates='properties')
    publisher = relationship('Publisher', back_populates='properties')
    # No definir relación images aquí debido a la complejidad de las FK compuestas

    def __repr__(self):
        return f"<Property(id={self.id}, title='{self.title}')>"


class Image(Base):
    """
    Tabla: images
    Representa las imágenes de las propiedades
    """
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer)
    source_id = Column(Integer, ForeignKey('sources_data.id'))
    image_url = Column(String(255))
    order = Column(Integer)

    # Relaciones
    source = relationship('SourceData', back_populates='images')

    def __repr__(self):
        return f"<Image(id={self.id}, property_id={self.property_id}, order={self.order})>"
