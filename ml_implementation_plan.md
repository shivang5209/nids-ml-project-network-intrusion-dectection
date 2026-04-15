# Machine Learning Implementation Plan for NIDS

## Objective

Develop and deploy a machine learning model that classifies network traffic as normal or malicious and, where possible, identifies attack categories.

## Recommended Tools

- Python
- `pandas`
- `numpy`
- `scikit-learn`
- `joblib`
- `matplotlib`
- `seaborn`

## Dataset Options

- NSL-KDD
- CIC-IDS2017
- UNSW-NB15

## Workflow

### 1. Data Collection

- Download and inspect dataset
- Understand feature columns
- Identify target labels

### 2. Data Preprocessing

- Remove duplicates
- Handle missing values
- Encode categorical variables
- Normalize numeric features
- Split into train, validation, and test sets

### 3. Feature Engineering

- Remove irrelevant columns
- Select informative traffic features
- Analyze correlation between features and targets

### 4. Model Training

Train and compare:

- Logistic Regression
- Decision Tree
- Random Forest
- Support Vector Machine
- Gradient Boosting

### 5. Model Evaluation

Use:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix
- False positive rate
- False negative rate

### 6. Model Export

- Save best model using `joblib`
- Save label encoder/scaler if used
- Document model version and metrics

### 7. Inference Integration

- Load model on backend startup
- Accept feature input from backend
- Return label, attack type, and confidence score

## Advanced Extensions

- Anomaly detection for zero-day attacks
- Deep learning models such as LSTM or autoencoders
- Scheduled retraining
- Drift monitoring

## Deliverables

- Dataset preprocessing script
- Training notebook or script
- Evaluation report
- Best trained model artifact
- Inference-ready wrapper module

