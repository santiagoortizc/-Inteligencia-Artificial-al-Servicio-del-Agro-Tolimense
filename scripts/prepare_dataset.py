"""
Script para preparar y dividir el dataset en train/validation/test.
Universidad Cooperativa de Colombia - Semillero DataTech

Uso:
    python scripts/prepare_dataset.py
    python scripts/prepare_dataset.py --clean  # Limpia y recrea el dataset
"""

import os
import sys
import shutil
import random
import argparse
from pathlib import Path
from collections import defaultdict

# Agregar el directorio padre al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    DATA_DIR,
    DATASET_DIR,
    TRAIN_DIR,
    VALIDATION_DIR,
    TEST_DIR,
    ALL_CLASSES,
    SPLIT_CONFIG,
    create_directories,
)


def get_image_files(directory: Path) -> list:
    """
    Obtiene todos los archivos de imagen en un directorio.

    Args:
        directory: Ruta del directorio.

    Returns:
        Lista de rutas de archivos de imagen.
    """
    extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    files = []

    if directory.exists():
        for f in directory.iterdir():
            if f.is_file() and f.suffix.lower() in extensions:
                files.append(f)

    return files


def clean_dataset():
    """Limpia los directorios del dataset procesado."""
    print("Limpiando dataset existente...")

    for split_dir in [TRAIN_DIR, VALIDATION_DIR, TEST_DIR]:
        if split_dir.exists():
            shutil.rmtree(split_dir)
            print(f"  Eliminado: {split_dir}")

    print("Dataset limpiado.\n")


def split_dataset(
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42,
    min_images: int = 10,
):
    """
    Divide el dataset en train/validation/test.

    Args:
        train_ratio: Proporcion para entrenamiento.
        validation_ratio: Proporcion para validacion.
        test_ratio: Proporcion para test.
        random_seed: Semilla para reproducibilidad.
        min_images: Minimo de imagenes requeridas por clase.
    """
    # Verificar que las proporciones suman 1
    total = train_ratio + validation_ratio + test_ratio
    if abs(total - 1.0) > 0.01:
        raise ValueError(f"Las proporciones deben sumar 1.0, pero suman {total}")

    # Establecer semilla
    random.seed(random_seed)

    # Crear directorios
    create_directories()

    print("=" * 60)
    print("PREPARANDO DATASET")
    print("=" * 60)
    print(f"\nDirectorio fuente: {DATA_DIR}")
    print(f"Directorio destino: {DATASET_DIR}")
    print(f"\nProporciones:")
    print(f"  Train: {train_ratio:.0%}")
    print(f"  Validation: {validation_ratio:.0%}")
    print(f"  Test: {test_ratio:.0%}")
    print(f"\nSemilla aleatoria: {random_seed}")
    print()

    # Estadisticas
    stats = {
        "train": defaultdict(int),
        "validation": defaultdict(int),
        "test": defaultdict(int),
        "total": defaultdict(int),
        "skipped": [],
    }

    # Procesar cada clase
    for class_name in ALL_CLASSES:
        source_dir = DATA_DIR / class_name

        # Obtener archivos de imagen
        images = get_image_files(source_dir)

        if not images:
            print(f"[SKIP] {class_name}: No se encontraron imagenes")
            stats["skipped"].append(class_name)
            continue

        if len(images) < min_images:
            print(
                f"[WARN] {class_name}: Solo {len(images)} imagenes (minimo: {min_images})"
            )

        # Mezclar aleatoriamente
        random.shuffle(images)

        # Calcular indices de division
        n_total = len(images)
        n_train = int(n_total * train_ratio)
        n_validation = int(n_total * validation_ratio)
        # El resto va a test

        # Dividir
        train_images = images[:n_train]
        validation_images = images[n_train : n_train + n_validation]
        test_images = images[n_train + n_validation :]

        # Copiar archivos
        splits = [
            ("train", TRAIN_DIR, train_images),
            ("validation", VALIDATION_DIR, validation_images),
            ("test", TEST_DIR, test_images),
        ]

        for split_name, split_dir, split_images in splits:
            dest_dir = split_dir / class_name
            dest_dir.mkdir(parents=True, exist_ok=True)

            for img_path in split_images:
                dest_path = dest_dir / img_path.name
                shutil.copy2(img_path, dest_path)
                stats[split_name][class_name] += 1

        stats["total"][class_name] = n_total

        print(f"[OK] {class_name}: {n_total} imagenes")
        print(
            f"     -> Train: {len(train_images)}, Val: {len(validation_images)}, Test: {len(test_images)}"
        )

    # Imprimir resumen
    print_summary(stats)

    return stats


def print_summary(stats: dict):
    """Imprime un resumen del dataset procesado."""
    print("\n" + "=" * 60)
    print("RESUMEN DEL DATASET")
    print("=" * 60)

    # Tabla de clases
    print(f"\n{'Clase':<35} {'Total':>8} {'Train':>8} {'Val':>8} {'Test':>8}")
    print("-" * 75)

    total_train = 0
    total_val = 0
    total_test = 0
    total_images = 0

    for class_name in sorted(stats["total"].keys()):
        n_total = stats["total"][class_name]
        n_train = stats["train"][class_name]
        n_val = stats["validation"][class_name]
        n_test = stats["test"][class_name]

        # Truncar nombre si es muy largo
        display_name = class_name[:33] + ".." if len(class_name) > 35 else class_name

        print(f"{display_name:<35} {n_total:>8} {n_train:>8} {n_val:>8} {n_test:>8}")

        total_train += n_train
        total_val += n_val
        total_test += n_test
        total_images += n_total

    print("-" * 75)
    print(
        f"{'TOTAL':<35} {total_images:>8} {total_train:>8} {total_val:>8} {total_test:>8}"
    )

    # Porcentajes reales
    if total_images > 0:
        print(f"\nPorcentajes reales:")
        print(f"  Train:      {total_train / total_images:.1%}")
        print(f"  Validation: {total_val / total_images:.1%}")
        print(f"  Test:       {total_test / total_images:.1%}")

    # Clases omitidas
    if stats["skipped"]:
        print(f"\nClases omitidas (sin imagenes): {len(stats['skipped'])}")
        for class_name in stats["skipped"]:
            print(f"  - {class_name}")

    # Numero de clases activas
    n_classes = len([c for c in stats["total"].keys() if stats["total"][c] > 0])
    print(f"\nClases con imagenes: {n_classes}")
    print(f"Total de imagenes: {total_images}")

    print("=" * 60)


def verify_dataset():
    """Verifica la integridad del dataset."""
    print("\nVerificando integridad del dataset...")

    issues = []

    for split_name, split_dir in [
        ("train", TRAIN_DIR),
        ("validation", VALIDATION_DIR),
        ("test", TEST_DIR),
    ]:
        if not split_dir.exists():
            issues.append(f"Directorio no existe: {split_dir}")
            continue

        for class_dir in split_dir.iterdir():
            if class_dir.is_dir():
                images = get_image_files(class_dir)
                if len(images) == 0:
                    issues.append(f"Directorio vacio: {class_dir}")

    if issues:
        print("\nProblemas encontrados:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Dataset verificado correctamente.")

    return len(issues) == 0


def main():
    """Funcion principal del script."""
    parser = argparse.ArgumentParser(
        description="Preparar y dividir el dataset de plagas agricolas"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Limpiar el dataset existente antes de procesar",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=SPLIT_CONFIG["train_ratio"],
        help=f"Proporcion para entrenamiento (default: {SPLIT_CONFIG['train_ratio']})",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=SPLIT_CONFIG["validation_ratio"],
        help=f"Proporcion para validacion (default: {SPLIT_CONFIG['validation_ratio']})",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=SPLIT_CONFIG["test_ratio"],
        help=f"Proporcion para test (default: {SPLIT_CONFIG['test_ratio']})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SPLIT_CONFIG["random_seed"],
        help=f"Semilla aleatoria (default: {SPLIT_CONFIG['random_seed']})",
    )
    parser.add_argument(
        "--verify", action="store_true", help="Solo verificar el dataset existente"
    )

    args = parser.parse_args()

    if args.verify:
        verify_dataset()
        return

    if args.clean:
        clean_dataset()

    # Dividir dataset
    stats = split_dataset(
        train_ratio=args.train_ratio,
        validation_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        random_seed=args.seed,
    )

    # Verificar
    verify_dataset()

    print("\nDataset preparado exitosamente!")
    print(f"Ubicacion: {DATASET_DIR}")


if __name__ == "__main__":
    main()
