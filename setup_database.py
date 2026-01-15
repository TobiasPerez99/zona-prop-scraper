"""
Script para configurar la base de datos con el esquema correcto.
Ejecutar antes de usar el scraper por primera vez.
"""

import pymysql
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_DATABASE = os.getenv('DB_DATABASE', 'xintel_network')
DB_USERNAME = os.getenv('DB_USERNAME', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')

# SQL para crear las tablas
CREATE_TABLES_SQL = """
SET FOREIGN_KEY_CHECKS = 0;

-- Table structure for sources_data
DROP TABLE IF EXISTS `sources_data`;
CREATE TABLE `sources_data`  (
  `id` int NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `portal_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Table structure for publisher
DROP TABLE IF EXISTS `publisher`;
CREATE TABLE `publisher`  (
  `id` int NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `logo_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `phone` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Table structure for properties
DROP TABLE IF EXISTS `properties`;
CREATE TABLE `properties`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `publication_id` int NOT NULL,
  `source_id` int NOT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  `created_at` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `sell_price` decimal(10, 2) NULL DEFAULT NULL,
  `rent_price` decimal(10, 2) NULL DEFAULT NULL,
  `sell_currency` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `rent_currency` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `expenses` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `expenses_currency` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `publisher_id` int NOT NULL,
  `location_id` int NOT NULL,
  `location_description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `garage_quantity` int NULL DEFAULT NULL,
  `property_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `enviroments` int NULL DEFAULT NULL,
  `bedrooms` int NULL DEFAULT NULL,
  `bathrooms` int NULL DEFAULT NULL,
  `antiquity` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`, `publication_id`, `source_id`, `publisher_id`, `location_id`) USING BTREE,
  INDEX `properties_publisher_id_foreign`(`publisher_id` ASC) USING BTREE,
  INDEX `properties_source_id_foreign`(`source_id` ASC) USING BTREE,
  CONSTRAINT `properties_publisher_id_foreign` FOREIGN KEY (`publisher_id`) REFERENCES `publisher` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `properties_source_id_foreign` FOREIGN KEY (`source_id`) REFERENCES `sources_data` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Table structure for images
DROP TABLE IF EXISTS `images`;
CREATE TABLE `images`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `property_id` int NOT NULL,
  `source_id` int NOT NULL,
  `image_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `order` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_property_source` (`property_id`, `source_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
"""

def setup_database():
    """
    Crea o actualiza el esquema de la base de datos
    """
    try:
        # Conectar a MySQL
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            charset='utf8mb4'
        )

        print(f"Conectado a MySQL: {DB_DATABASE}")

        # Ejecutar SQL
        with connection.cursor() as cursor:
            # Dividir en statements individuales y ejecutar
            statements = CREATE_TABLES_SQL.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)

        connection.commit()
        print("[OK] Esquema de base de datos creado exitosamente")
        print("[OK] Tablas: sources_data, publisher, properties, images")

        connection.close()

    except Exception as e:
        print(f"[ERROR] Error configurando base de datos: {e}")
        raise


if __name__ == '__main__':
    print("=== Configurando Base de Datos ===\n")
    setup_database()
    print("\n=== Configuración Completada ===")
