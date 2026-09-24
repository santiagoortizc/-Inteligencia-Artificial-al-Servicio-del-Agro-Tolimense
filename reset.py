"""
Limpieza previa a un nuevo entrenamiento.
Borra dataset procesado y checkpoints, conserva Insectos/ (imagenes originales).
"""

import shutil
from datetime import datetime
from config import (
    DATASET_DIR,
    MODELS_DIR,
    TRAIN_DIR,
    VALIDATION_DIR,
    TEST_DIR,
    create_directories,
    BASE_DIR,
)


def limpiar_entrenamiento_anterior(backup_modelos: bool = True):
    # 1. Backup opcional de modelos anteriores antes de borrar
    if backup_modelos and MODELS_DIR.exists() and any(MODELS_DIR.iterdir()):
        backup_dir = BASE_DIR / f"models_backup_{datetime.now():%Y%m%d}"
        shutil.copytree(MODELS_DIR, backup_dir)
        print(f"Backup de modelos en: {backup_dir}")

    # 2. Borrar splits anteriores (se regeneran desde Insectos/)
    for split_dir in [TRAIN_DIR, VALIDATION_DIR, TEST_DIR]:
        if split_dir.exists():
            shutil.rmtree(split_dir)
            print(f"Eliminado: {split_dir}")

    # 3. Borrar checkpoints/modelos anteriores
    if MODELS_DIR.exists():
        shutil.rmtree(MODELS_DIR)
        print(f"Eliminado: {MODELS_DIR}")

    # 4. Recrear estructura vacia segun PEST_CLASSES actualizado en config.py
    create_directories()
    print("Estructura recreada para las clases actuales de config.py")


if __name__ == "__main__":
    confirm = input(
        "Esto eliminara dataset/train, dataset/validation, dataset/test y models/. "
        "¿Continuar? (s/n): "
    )
    if confirm.lower() == "s":
        limpiar_entrenamiento_anterior(backup_modelos=True)
    else:
        print("Cancelado.")
