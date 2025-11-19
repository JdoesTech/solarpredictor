# ML Pipeline

This directory contains scripts and notebooks for training and evaluating ML models for solar energy prediction.

## Structure

```
ml_pipeline/
├── notebooks/          # Jupyter notebooks for exploration and training
│   ├── 01_data_exploration.ipynb
│   └── 02_model_training.ipynb
├── models/            # Trained model files (gitignored)
└── train_model.py     # Standalone training script
```

## Usage

### Using Jupyter Notebooks

1. Install Jupyter:
```bash
pip install jupyter
```

2. Start Jupyter:
```bash
jupyter notebook
```

3. Open and run notebooks in order:
   - `01_data_exploration.ipynb` - Explore and visualize data
   - `02_model_training.ipynb` - Train and evaluate models

### Using Python Script

```bash
python train_model.py
```

This will:
- Fetch training data from Supabase
- Train a Random Forest regression model
- Save the model to `models/` directory
- Register the model in Supabase

## Model Types

Currently supported:
- **Regression**: Random Forest Regressor for energy output prediction

Future additions:
- **CNN**: Convolutional Neural Network for panel condition classification from images

## Requirements

Install additional dependencies for notebooks:

```bash
pip install jupyter matplotlib seaborn
```

## Data Requirements

Before training, ensure you have:
- Weather data uploaded to Supabase
- Production data uploaded to Supabase
- At least 100+ records for meaningful training

See `docs/datasets.md` for open datasets you can use.

