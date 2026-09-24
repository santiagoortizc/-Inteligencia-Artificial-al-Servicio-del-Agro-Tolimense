"""
Script para descargar imagenes de plagas desde iNaturalist API.
Universidad Cooperativa de Colombia - Semillero DataTech

Uso:
    python scripts/download_images.py --class spodoptera_frugiperda --max 200
    python scripts/download_images.py --all --max 300
"""

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

# from concurrent.futures import ThreadPoolExecutor, as_completed  
from typing import Optional

import requests

# Agregar el directorio padre al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    ALL_CLASSES,
    DATA_DIR,
    INATURALIST_CONFIG,
    NEW_CLASSES,
    create_directories,
)


class INaturalistDownloader:
    """Clase para descargar imagenes desde iNaturalist API."""

    def __init__(self, delay: float = 1.0):
        """
        Inicializa el descargador.

        Args:
            delay: Segundos de espera entre peticiones a la API.
        """
        self.base_url = INATURALIST_CONFIG["base_url"]
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "PlagasAgricolasProject/1.0 (Universidad Cooperativa de Colombia)"
            }
        )

    def search_observations(
        self,
        taxon_id: int,
        per_page: int = 200,
        page: int = 1,
        quality_grade: str = "research",
    ) -> dict:
        """
        Busca observaciones en iNaturalist por taxon_id.

        Args:
            taxon_id: ID del taxon en iNaturalist.
            per_page: Numero de resultados por pagina.
            page: Numero de pagina.
            quality_grade: Calidad de la observacion ('research', 'needs_id', 'casual').

        Returns:
            Diccionario con los resultados de la API.
        """
        url = f"{self.base_url}/observations"
        params = {
            "taxon_id": taxon_id,
            "per_page": per_page,
            "page": page,
            "quality_grade": quality_grade,
            "photos": "true",
            "order": "desc",
            "order_by": "votes",  # Priorizar las mas votadas
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            time.sleep(self.delay)  # Rate limiting
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en la peticion: {e}")
            return {"results": [], "total_results": 0}

    def get_taxon_id(self, species_name: str) -> Optional[int]: 
        """
        Obtiene el taxon_id a partir del nombre cientifico.

        Args:
            species_name: Nombre cientifico de la especie (ej: "spodoptera_frugiperda").

        Returns:
            taxon_id o None si no se encuentra.
        """
        # Convertir nombre de carpeta a nombre de busqueda
        search_name = species_name.replace("_", " ")

        url = f"{self.base_url}/taxa"
        params = {
            "q": search_name,
            "per_page": 1,
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data["results"]:
                taxon = data["results"][0]
                print(f"  Encontrado: {taxon['name']} (ID: {taxon['id']})")
                return taxon["id"]
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error buscando taxon: {e}")
            return None

    def extract_photo_urls(self, observations: list) -> list:
        """
        Extrae las URLs de fotos de las observaciones.

        Args:
            observations: Lista de observaciones de la API.

        Returns:
            Lista de URLs de fotos.
        """
        urls = []
        for obs in observations:
            if "photos" in obs:
                for photo in obs["photos"]:
                    # Obtener la version de mayor resolucion disponible
                    url = photo.get("url", "")
                    if url:
                        # Reemplazar 'square' por 'large' para mejor calidad
                        url = url.replace("square", "large")
                        urls.append(url)
        return urls

    def download_image(self, url: str, save_path: Path) -> bool:
        """
        Descarga una imagen y la guarda en disco.

        Args:
            url: URL de la imagen.
            save_path: Ruta donde guardar la imagen.

        Returns:
            True si la descarga fue exitosa, False en caso contrario.
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Verificar que es una imagen
            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                return False

            # Guardar la imagen
            with open(save_path, "wb") as f:
                f.write(response.content)

            return True
        except Exception as e:
            return False

    def download_class_images(
        self, class_name: str, max_images: int = 200, taxon_id: Optional[int] = None
    ) -> int:
        """
        Descarga imagenes para una clase especifica.

        Args:
            class_name: Nombre de la clase (ej: "spodoptera_frugiperda").
            max_images: Numero maximo de imagenes a descargar.
            taxon_id: ID del taxon en iNaturalist (opcional).

        Returns:
            Numero de imagenes descargadas.
        """
        print(f"\n{'=' * 60}")
        print(f"Descargando: {class_name}")
        print(f"{'=' * 60}")

        # Crear directorio si no existe
        class_dir = DATA_DIR / class_name
        class_dir.mkdir(parents=True, exist_ok=True)

        # Obtener imagenes existentes para evitar duplicados
        existing_files = set(f.stem for f in class_dir.glob("*.jpeg"))
        existing_files.update(f.stem for f in class_dir.glob("*.jpg"))
        existing_files.update(f.stem for f in class_dir.glob("*.png"))
        print(f"  Imagenes existentes: {len(existing_files)}")

        # Obtener taxon_id
        if taxon_id is None:
            if class_name in NEW_CLASSES:
                taxon_id = NEW_CLASSES[class_name].get("taxon_id")

            if taxon_id is None:
                taxon_id = self.get_taxon_id(class_name)

            if taxon_id is None:
                print(f"  ERROR: No se encontro taxon_id para {class_name}")
                return 0

        print(f"  Taxon ID: {taxon_id}")

        # Recolectar URLs de fotos
        all_urls = []
        page = 1
        per_page = INATURALIST_CONFIG["per_page"]

        while len(all_urls) < max_images:
            print(f"  Buscando pagina {page}...")
            data = self.search_observations(taxon_id, per_page=per_page, page=page)

            if not data["results"]:
                break

            urls = self.extract_photo_urls(data["results"])
            all_urls.extend(urls)

            # Verificar si hay mas paginas
            total_results = data.get("total_results", 0)
            if page * per_page >= total_results:
                break

            page += 1

            # Limite de seguridad
            if page > 10:
                break

        print(f"  URLs encontradas: {len(all_urls)}")

        # Descargar imagenes
        downloaded = 0
        skipped = 0

        for i, url in enumerate(all_urls[:max_images]):
            # Generar nombre unico basado en URL
            url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
            filename = f"{class_name}_{i + 1}_{url_hash}"

            # Verificar si ya existe
            if filename in existing_files:
                skipped += 1
                continue

            # Determinar extension
            if ".png" in url.lower():
                ext = ".png"
            else:
                ext = ".jpeg"

            save_path = class_dir / f"{filename}{ext}"

            if self.download_image(url, save_path):
                downloaded += 1
                if downloaded % 10 == 0:
                    print(f"  Descargadas: {downloaded}/{max_images}")

            # Rate limiting
            time.sleep(0.2)

        print(f"\n  Resumen para {class_name}:")
        print(f"    - Descargadas: {downloaded}")
        print(f"    - Omitidas (duplicados): {skipped}")
        print(f"    - Total en carpeta: {len(list(class_dir.glob('*.*')))}")

        return downloaded


def main():
    """Funcion principal del script."""
    parser = argparse.ArgumentParser(
        description="Descargar imagenes de plagas desde iNaturalist"
    )
    parser.add_argument(
        "--class",
        "-c",
        dest="class_name",
        type=str,
        help="Nombre de la clase a descargar (ej: spodoptera_frugiperda)",
    )
    parser.add_argument(
        "--all", "-a", action="store_true", help="Descargar todas las clases nuevas"
    )
    parser.add_argument(
        "--max",
        "-m",
        type=int,
        default=200,
        help="Numero maximo de imagenes por clase (default: 200)",
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="Listar todas las clases disponibles"
    )

    args = parser.parse_args()

    # Listar clases
    if args.list:
        print("\nClases disponibles para descarga:")
        print("-" * 40)
        for class_name, info in NEW_CLASSES.items():
            print(f"  {class_name}")
            print(f"    Nombre comun: {info['nombre_comun']}")
            print(f"    Cultivos: {', '.join(info['cultivos'])}")
            print(f"    Taxon ID: {info.get('taxon_id', 'Auto-detectar')}")
            print()
        return

    # Crear directorios
    create_directories()

    # Inicializar descargador
    downloader = INaturalistDownloader(
        delay=INATURALIST_CONFIG["delay_between_requests"]
    )

    total_downloaded = 0

    if args.all:
        # Descargar todas las clases nuevas
        print("\nDescargando todas las clases nuevas...")
        for class_name in NEW_CLASSES.keys():
            downloaded = downloader.download_class_images(
                class_name, max_images=args.max
            )
            total_downloaded += downloaded

    elif args.class_name:
        # Descargar una clase especifica
        if args.class_name not in ALL_CLASSES and args.class_name not in NEW_CLASSES:
            print(
                f"Advertencia: '{args.class_name}' no esta en la lista de clases conocidas."
            )
            print("Intentando descargar de todos modos...")

        downloaded = downloader.download_class_images(
            args.class_name, max_images=args.max
        )
        total_downloaded = downloaded

    else:
        parser.print_help()
        return

    print("\n" + "=" * 60)
    print("DESCARGA COMPLETADA")
    print(f"Total de imagenes descargadas: {total_downloaded}")
    print("=" * 60)


if __name__ == "__main__":
    main()
