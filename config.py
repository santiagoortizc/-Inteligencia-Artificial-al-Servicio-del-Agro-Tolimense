"""
Configuracion centralizada del proyecto de identificacion de plagas.
Universidad Cooperativa de Colombia - Semillero DataTech
"""

import os
from pathlib import Path

# =============================================================================
# RUTAS DEL PROYECTO
# =============================================================================

# Directorio base del proyecto (detecta automaticamente)
BASE_DIR = Path(__file__).parent.resolve()

# Directorios de datos
DATA_DIR = BASE_DIR / "Insectos"  # Imagenes originales
DATASET_DIR = BASE_DIR / "dataset"  # Dataset procesado
TRAIN_DIR = DATASET_DIR / "train"
VALIDATION_DIR = DATASET_DIR / "validation"
TEST_DIR = DATASET_DIR / "test"

# Directorio de modelos
MODELS_DIR = BASE_DIR / "models"

# =============================================================================
# CLASES DE PLAGAS
# =============================================================================

NEW_CLASSES = {
    
}

# Clases de insectos.txt con taxon_ids de iNaturalist
PEST_CLASSES = {
    "ceratitis_capitata": {
        "nombre_comun": "Mosca del Mediterráneo",
        "cultivos": ["citricos", "cafe", "mango", "frutas"],
        "taxon_id": 199404,
    },
    "heilipus_lauri": {
        "nombre_comun": "Barrenador del hueso del aguacate",
        "cultivos": ["aguacate"],
        "taxon_id": 268874,
    },
    "rhynchophorus_palmarum": {
        "nombre_comun": "Picudo negro de la palma",
        "cultivos": ["palma de aceite", "coco"],
        "taxon_id": 304994,
    },
    "strategus_aloeus": {
        "nombre_comun": "Escarabajo torito",
        "cultivos": ["palma de aceite", "coco"],
        "taxon_id": 199942,
    },
    "dalbulus_maidis": {
        "nombre_comun": "Chicharrita del maíz",
        "cultivos": ["maiz"],
        "taxon_id": 738011,
    },
    "oebalus_insularis": {
        "nombre_comun": "Chinche de la espiga",
        "cultivos": ["arroz"],
        "taxon_id": 296297,
    },
    "tagosodes_orizicolus": {
        "nombre_comun": "Sogata",
        "cultivos": ["arroz"],
        "taxon_id": 974945,
    },
    "diaphorina_citri": {
        "nombre_comun": "Psílido asiático de los cítricos",
        "cultivos": ["citricos"],
        "taxon_id": 199388,
    },
    "trichoplusia_ni": {
        "nombre_comun": "Falso medidor",
        "cultivos": ["repollo", "brocoli", "tomate"],
        "taxon_id": 202789,
    },
    "piezodorus_guildinii": {
        "nombre_comun": "Chinche de la alfalfa",
        "cultivos": ["soya", "alfalfa", "frijol"],
        "taxon_id": 330167,
    },
    "atta_cephalotes": {
        "nombre_comun": "Hormiga arriera",
        "cultivos": ["citricos", "cacao", "forestales"],
        "taxon_id": 153974,
    },
    "blissus_leucopterus": {
        "nombre_comun": "Chinche de los pastos",
        "cultivos": ["pastos", "maiz", "sorgo"],
        "taxon_id": 261572,
    },
    "spodoptera_frugiperda": {
        "nombre_comun": "Gusano cogollero",
        "cultivos": ["maiz", "arroz", "sorgo"],
        "taxon_id": 132468,
    },
    "anastrepha_curvicauda": {
        "nombre_comun": "Mosca de la fruta",
        "cultivos": ["frutas", "mango", "papaya"],
        "taxon_id": 1505368,
    },
    "diatraea_lisetta": {
        "nombre_comun": "Barrenador de cana",
        "cultivos": ["cana de azucar", "maiz"],
        "taxon_id": 218331,
    },
    "compsus_viridivittatus": {
        "nombre_comun": "Escarabajo rayado",
        "cultivos": ["citricos", "cafe"],
        "taxon_id": 464812,
    },
    "dysdercus_concinnus": {
        "nombre_comun": "Chinche hilvanero",
        "cultivos": ["algodon", "sorgo"],
        "taxon_id": 324205,
    },
    "leptinotarsa_decemlineata": {
        "nombre_comun": "Escarabajo de Colorado",
        "cultivos": ["papa", "tomate", "berenjena"],
        "taxon_id": 84778,
    },
    "cyclocephala_lunulata": {
        "nombre_comun": "Escarabajo rinoceronte",
        "cultivos": ["maiz", "pastos"],
        "taxon_id": 301455,
    },
    "helicoverpa_armigera": {
        "nombre_comun": "Gusano bellota",
        "cultivos": ["algodon", "tomate", "maiz"],
        "taxon_id": 83806,
    },
}

# Todas las clases en formato underscored
ALL_CLASSES = list(PEST_CLASSES.keys())

# =============================================================================
# CONFIGURACION DE INATURALIST API
# =============================================================================

INATURALIST_CONFIG = {
    "base_url": "https://api.inaturalist.org/v1",
    "observations_endpoint": "/observations",
    "per_page": 300,  # Maximo por pagina
    "quality_grade": "research",  # Solo observaciones verificadas
    "photos": True,  # Solo con fotos
    "max_images_per_class": 800,  # Limite de imagenes por clase
    "delay_between_requests": 1.0,  # Segundos entre peticiones (rate limit)
}

# =============================================================================
# CONFIGURACION DEL MODELO
# =============================================================================

MODEL_CONFIG = {
    # Arquitectura
    "base_model": "EfficientNetB0",
    "input_shape": (224, 224, 3),  # EfficientNetB0 optimo
    "weights": "imagenet",
    # Capas adicionales
    "dense_layers": [512, 256, 128],
    "dropout_rate": 0.3,
    "activation": "relu",
    # Entrenamiento
    "batch_size": 32,
    "epochs": 50,
    "initial_learning_rate": 1e-4,
    "min_learning_rate": 1e-7,
    # Fine-tuning
    "fine_tune": True,
    "fine_tune_at": 100,  # Descongelar desde esta capa
    "fine_tune_learning_rate": 1e-5,
    "fine_tune_epochs": 30,
}

# =============================================================================
# DATA AUGMENTATION
# =============================================================================

AUGMENTATION_CONFIG = {
    "rotation_range": 30,
    "width_shift_range": 0.2,
    "height_shift_range": 0.2,
    "shear_range": 0.2,
    "zoom_range": 0.2,
    "horizontal_flip": True,
    "vertical_flip": False,
    "brightness_range": [0.8, 1.2],
    "fill_mode": "nearest",
}

# =============================================================================
# DIVISION DEL DATASET
# =============================================================================

SPLIT_CONFIG = {
    "train_ratio": 0.70,
    "validation_ratio": 0.15,
    "test_ratio": 0.15,
    "random_seed": 42,
}

# =============================================================================
# CALLBACKS
# =============================================================================

CALLBACKS_CONFIG = {
    "early_stopping": {
        "monitor": "val_loss",
        "patience": 10,
        "restore_best_weights": True,
        "min_delta": 0.001,
    },
    "reduce_lr": {
        "monitor": "val_loss",
        "factor": 0.5,
        "patience": 5,
        "min_lr": 1e-7,
    },
    "model_checkpoint": {
        "monitor": "val_accuracy",
        "save_best_only": True,
        "mode": "max",
    },
}

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================


def create_directories():
    """Crea los directorios necesarios si no existen."""
    directories = [
        DATA_DIR,
        DATASET_DIR,
        TRAIN_DIR,
        VALIDATION_DIR,
        TEST_DIR,
        MODELS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    # Crear subdirectorios para cada clase
    for class_name in PEST_CLASSES.keys():
        (TRAIN_DIR / class_name).mkdir(parents=True, exist_ok=True)
        (VALIDATION_DIR / class_name).mkdir(parents=True, exist_ok=True)
        (TEST_DIR / class_name).mkdir(parents=True, exist_ok=True)
        (DATA_DIR / class_name).mkdir(parents=True, exist_ok=True)

    print(f"Directorios creados en: {BASE_DIR}")


def get_model_path(model_name: str | None = None) -> Path:
    """Retorna la ruta para guardar/cargar el modelo."""
    if model_name is None:
        model_name = f"{MODEL_CONFIG['base_model']}_plagas_v1.keras"
    return MODELS_DIR / model_name


def print_config():
    """Imprime la configuracion actual."""
    print("=" * 60)
    print("CONFIGURACION DEL PROYECTO")
    print("=" * 60)
    print(f"\nDirectorio base: {BASE_DIR}")
    print(f"Total clases: {len(ALL_CLASSES)}")
    print("\nClases configuradas:")
    for key, info in PEST_CLASSES.items():
        print(f"  - {key}: {info['nombre_comun']}")
    print(f"\nModelo: {MODEL_CONFIG['base_model']}")
    print(f"Input shape: {MODEL_CONFIG['input_shape']}")
    print(f"Batch size: {MODEL_CONFIG['batch_size']}")
    print(f"Epochs: {MODEL_CONFIG['epochs']}")
    print("=" * 60)


if __name__ == "__main__":
    print_config()
    create_directories()
