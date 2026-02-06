"""
Comprehensive Cardiovascular Disease Prediction - Complete ML Pipeline
Author: Health Data Science Team
Date: February 6, 2026
Version: 2.0

This script implements a complete machine learning pipeline including:
1. Data Preprocessing (cleaning, scaling, outlier detection)
2. Visualization & Insights (histograms, count plots, box plots)
3. Correlation Analysis
4. Model Training (5 algorithms)
5. Model Comparison & Selection
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import warnings
from datetime import datetime
import os
from pathlib import Path

# Machine Learning Libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# Metrics
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                           f1_score, confusion_matrix, classification_report, 
                           roc_auc_score, roc_curve)

warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================

class Config:
    """Configuration settings for the ML pipeline"""
    DATA_FILE = 'cardio_train (1).csv'
    OUTPUT_DIR = 'models'
    LOGS_DIR = 'logs'
    PLOTS_DIR = 'plots'
    
    # Model files
    BEST_MODEL_FILE = 'cardio_model.pkl'
    SCALER_FILE = 'scaler.pkl'
    FEATURE_NAMES_FILE = 'feature_names.pkl'
    
    # Data split ratios
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    
    # Feature scaling method
    SCALING_METHOD = 'standard'  # 'standard' or 'minmax'
    
    # Model parameters
    MODELS_CONFIG = {
        'LogisticRegression': {
            'max_iter': 1000,
            'random_state': RANDOM_STATE,
            'n_jobs': -1
        },
        'KNeighborsClassifier': {
            'n_neighbors': 5,
            'n_jobs': -1
        },
        'SVC': {
            'kernel': 'rbf',
            'probability': True,
            'random_state': RANDOM_STATE
        },
        'DecisionTreeClassifier': {
            'random_state': RANDOM_STATE,
            'max_depth': 15
        },
        'RandomForestClassifier': {
            'n_estimators': 100,
            'random_state': RANDOM_STATE,
            'n_jobs': -1,
            'max_depth': 20
        }
    }

# ==================== UTILITY FUNCTIONS ====================

class Logger:
    """Simple file and console logger"""
    def __init__(self, filepath):
        self.filepath = filepath
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        try:
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except:
            # Fallback to ASCII if UTF-8 fails
            with open(self.filepath, 'a', encoding='ascii', errors='ignore') as f:
                f.write(log_message + '\n')

# Create logger
logger = Logger(f'{Config.LOGS_DIR}/training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

def log(message, level='INFO'):
    """Log with timestamp"""
    logger.log(message, level)

def ensure_directories():
    """Create necessary directories"""
    for directory in [Config.OUTPUT_DIR, Config.LOGS_DIR, Config.PLOTS_DIR]:
        Path(directory).mkdir(exist_ok=True)
    log("[OK] Directories ready")

# ==================== PHASE 1: DATA PREPROCESSING ====================

class DataPreprocessor:
    """Handles all data preprocessing tasks"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.df_processed = None
        self.feature_names = None
        self.scaler = None
        
    def load_data(self):
        """Load CSV data"""
        log(f"[LOAD] Loading data from {self.filepath}...")
        self.df = pd.read_csv(self.filepath, sep=';')
        log(f"[OK] Data loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
        return self
    
    def check_missing_values(self):
        """Check for missing/null values"""
        log("\n[CHECK] CHECKING MISSING VALUES...")
        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            log(f"⚠ Found {missing.sum()} missing values", 'WARNING')
            print(missing[missing > 0])
            # Fill with median
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
            log("[FIXED] Missing values filled with median")
        else:
            log("[OK] No missing values found")
        return self
    
    def remove_duplicates(self):
        """Remove duplicate rows"""
        log("\n[CHECK] CHECKING DUPLICATES...")
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        after = len(self.df)
        removed = before - after
        
        if removed > 0:
            log(f"⚠ Removed {removed} duplicate rows", 'WARNING')
        else:
            log("[OK] No duplicates found")
        return self
    
    def detect_and_remove_outliers(self):
        """Detect and remove outliers using IQR method"""
        log("\n[CHECK] DETECTING OUTLIERS...")
        initial_rows = len(self.df)
        
        # IQR method for outlier detection
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Count outliers
            outliers = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound)).sum()
            if outliers > 0:
                log(f"  • {col}: {outliers} outliers detected")
        
        # Remove outliers (keep rows within 99th percentile for age and BP)
        before = len(self.df)
        self.df = self.df[
            (self.df['ap_hi'].between(self.df['ap_hi'].quantile(0.01), self.df['ap_hi'].quantile(0.99))) &
            (self.df['ap_lo'].between(self.df['ap_lo'].quantile(0.01), self.df['ap_lo'].quantile(0.99)))
        ]
        after = len(self.df)
        
        if after < before:
            log(f"[REMOVED] Removed {before - after} outlier rows")
        else:
            log("[OK] No significant outliers removed")
        
        return self
    
    def feature_scaling(self, method=None):
        """Scale features to same range"""
        log("\n[SCALE] PERFORMING FEATURE SCALING...")
        method = method or Config.SCALING_METHOD
        
        # Separate features and target
        X = self.df.drop('cardio', axis=1)
        y = self.df['cardio']
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        if method == 'standard':
            self.scaler = StandardScaler()
            log("Using StandardScaler (mean=0, std=1)")
        else:
            self.scaler = MinMaxScaler()
            log("Using MinMaxScaler (0 to 1 range)")
        
        X_scaled = self.scaler.fit_transform(X)
        self.df_processed = pd.DataFrame(X_scaled, columns=X.columns)
        self.df_processed['cardio'] = y.values
        
        log(f"[OK] Scaled {len(self.feature_names)} features")
        return self
    
    def get_processed_data(self):
        """Return processed data"""
        return self.df_processed.copy()
    
    def get_info(self):
        """Print dataset info"""
        log("\n[INFO] DATASET INFORMATION")
        log(f"  Total rows: {len(self.df)}")
        log(f"  Total columns: {len(self.df.columns)}")
        log(f"  Feature columns: {len(self.feature_names)}")
        
        # Target distribution
        target_dist = self.df_processed['cardio'].value_counts()
        log(f"  Disease cases: {target_dist[1]}")
        log(f"  Healthy cases: {target_dist[0]}")
        log(f"  Disease rate: {(target_dist[1] / len(self.df_processed)) * 100:.2f}%")

# ==================== PHASE 2: VISUALIZATION & INSIGHTS ====================

class DataVisualizer:
    """Create visualizations and extract insights"""
    
    def __init__(self, df):
        self.df = df
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (15, 12)
    
    def create_age_histogram(self):
        """Age distribution histogram"""
        log("[PLOT] Creating Age Distribution Histogram...")
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Overall age distribution
        self.df['age_years'] = self.df['age'] / 365
        axes[0].hist(self.df['age_years'], bins=30, color='skyblue', edgecolor='black')
        axes[0].set_title('Age Distribution of All Patients', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Age (years)')
        axes[0].set_ylabel('Number of Patients')
        
        # Age distribution by disease status
        disease = self.df[self.df['cardio'] == 1]['age_years']
        healthy = self.df[self.df['cardio'] == 0]['age_years']
        axes[1].hist([healthy, disease], label=['Healthy', 'Disease'], 
                    color=['green', 'red'], alpha=0.7, bins=30)
        axes[1].set_title('Age Distribution by Disease Status', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Age (years)')
        axes[1].set_ylabel('Number of Patients')
        axes[1].legend()
        
        plt.tight_layout()
        plt.savefig(f'{Config.PLOTS_DIR}/01_age_distribution.png', dpi=300, bbox_inches='tight')
        log(f"[OK] Saved: 01_age_distribution.png")
        plt.close()
    
    def create_gender_countplot(self):
        """Gender count plot"""
        log("[PLOT] Creating Gender Analysis...")
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Overall gender distribution
        gender_counts = self.df['gender'].value_counts()
        axes[0].bar(['Female', 'Male'], [gender_counts[1], gender_counts[2]], 
                   color=['pink', 'lightblue'], edgecolor='black')
        axes[0].set_title('Gender Distribution', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Count')
        axes[0].set_ylim(0, max(gender_counts) * 1.1)
        
        # Gender vs Disease
        gender_disease = pd.crosstab(self.df['gender'], self.df['cardio'])
        gender_disease.plot(kind='bar', ax=axes[1], color=['green', 'red'], alpha=0.7)
        axes[1].set_title('Disease Distribution by Gender', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Gender (1=Female, 2=Male)')
        axes[1].set_ylabel('Count')
        axes[1].legend(['Healthy', 'Disease'])
        axes[1].set_xticklabels(['Female', 'Male'], rotation=0)
        
        plt.tight_layout()
        plt.savefig(f'{Config.PLOTS_DIR}/02_gender_analysis.png', dpi=300, bbox_inches='tight')
        log(f"[OK] Saved: 02_gender_analysis.png")
        plt.close()
    
    def create_boxplots(self):
        """Box plots for numeric features"""
        log("[PLOT] Creating Box Plots for Outlier Detection...")
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        axes = axes.flatten()
        
        features = ['ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'age_years', 'weight']
        
        for idx, feature in enumerate(features):
            data = [self.df[self.df['cardio']==0][feature], 
                   self.df[self.df['cardio']==1][feature]]
            axes[idx].boxplot(data, labels=['Healthy', 'Disease'])
            axes[idx].set_title(f'{feature.upper()} Distribution', fontsize=12, fontweight='bold')
            axes[idx].set_ylabel('Value')
        
        plt.tight_layout()
        plt.savefig(f'{Config.PLOTS_DIR}/03_boxplots_outliers.png', dpi=300, bbox_inches='tight')
        log(f"[OK] Saved: 03_boxplots_outliers.png")
        plt.close()
    
    def create_correlation_heatmap(self):
        """Create correlation matrix heatmap"""
        log("[PLOT] Creating Correlation Heatmap...")
        
        # Calculate correlation
        corr_matrix = self.df.corr()
        
        plt.figure(figsize=(14, 10))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        plt.title('Correlation Matrix - Feature Relationships', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{Config.PLOTS_DIR}/04_correlation_heatmap.png', dpi=300, bbox_inches='tight')
        log(f"[OK] Saved: 04_correlation_heatmap.png")
        plt.close()
        
        # Print top correlations with target
        cardio_corr = corr_matrix['cardio'].sort_values(ascending=False)
        log("\n[CORR] TOP FEATURES CORRELATED WITH DISEASE:")
        for feature, corr in cardio_corr.items():
            if feature != 'cardio':
                log(f"  • {feature}: {corr:.4f}")
        
        return corr_matrix

# ==================== PHASE 3: MODEL TRAINING & COMPARISON ====================

class ModelTrainer:
    """Train and evaluate multiple models"""
    
    def __init__(self):
        self.results = {}
        self.models = {}
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
    
    def prepare_data(self, df):
        """Split data into train/test"""
        log("\n[PREP] PREPARING DATA FOR TRAINING...")
        X = df.drop('cardio', axis=1)
        y = df['cardio']
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=Config.TEST_SIZE, random_state=Config.RANDOM_STATE
        )
        
        log(f"[OK] Data split: {len(self.X_train)} train, {len(self.X_test)} test")
        return self
    
    def train_model(self, model_name, model_class, **kwargs):
        """Train a single model"""
        log(f"\n[TRAIN] TRAINING: {model_name}...")
        
        try:
            model = model_class(**kwargs)
            model.fit(self.X_train, self.y_train)
            
            # Make predictions
            y_pred_train = model.predict(self.X_train)
            y_pred_test = model.predict(self.X_test)
            
            # Calculate metrics
            train_acc = accuracy_score(self.y_train, y_pred_train)
            test_acc = accuracy_score(self.y_test, y_pred_test)
            precision = precision_score(self.y_test, y_pred_test)
            recall = recall_score(self.y_test, y_pred_test)
            f1 = f1_score(self.y_test, y_pred_test)
            
            # ROC-AUC for probabilistic models
            try:
                y_pred_proba = model.predict_proba(self.X_test)[:, 1]
                roc_auc = roc_auc_score(self.y_test, y_pred_proba)
            except:
                y_pred_proba = model.decision_function(self.X_test)
                try:
                    roc_auc = roc_auc_score(self.y_test, y_pred_proba)
                except:
                    roc_auc = 0
            
            # Store results
            self.results[model_name] = {
                'train_accuracy': train_acc,
                'test_accuracy': test_acc,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'roc_auc': roc_auc,
                'model': model
            }
            
            self.models[model_name] = model
            
            log(f"[OK] {model_name} trained")
            log(f"  Train Accuracy: {train_acc:.4f}")
            log(f"  Test Accuracy: {test_acc:.4f}")
            log(f"  Precision: {precision:.4f}")
            log(f"  Recall: {recall:.4f}")
            
        except Exception as e:
            log(f"[ERROR] Error training {model_name}: {str(e)}", 'ERROR')
    
    def train_all_models(self):
        """Train all 5 models"""
        log("\n" + "="*60)
        log("[PHASE 4] TRAINING 5 DIFFERENT MODELS")
        log("="*60)
        
        model_configs = [
            ('Logistic Regression', LogisticRegression, Config.MODELS_CONFIG['LogisticRegression']),
            ('K-Nearest Neighbors', KNeighborsClassifier, Config.MODELS_CONFIG['KNeighborsClassifier']),
            ('Support Vector Machine', SVC, Config.MODELS_CONFIG['SVC']),
            ('Decision Tree', DecisionTreeClassifier, Config.MODELS_CONFIG['DecisionTreeClassifier']),
            ('Random Forest', RandomForestClassifier, Config.MODELS_CONFIG['RandomForestClassifier'])
        ]
        
        for model_name, model_class, config in model_configs:
            self.train_model(model_name, model_class, **config)
        
        return self
    
    def compare_models(self):
        """Compare all models"""
        log("\n" + "="*60)
        log("[PHASE 5] MODEL COMPARISON & SELECTION")
        log("="*60)
        
        # Create comparison dataframe
        comparison_df = pd.DataFrame(self.results).T
        comparison_df = comparison_df.drop('model', axis=1).round(4)
        
        log("\n[COMPARE] MODEL PERFORMANCE COMPARISON:")
        log("\n" + str(comparison_df))
        
        # Find best model by accuracy
        best_model_name = comparison_df['test_accuracy'].idxmax()
        best_accuracy = comparison_df.loc[best_model_name, 'test_accuracy']
        
        log("\n[WINNER] BEST MODEL SELECTED:")
        log(f"  Model: {best_model_name}")
        log(f"  Test Accuracy: {best_accuracy:.4f}")
        log(f"  F1-Score: {comparison_df.loc[best_model_name, 'f1_score']:.4f}")
        log(f"  ROC-AUC: {comparison_df.loc[best_model_name, 'roc_auc']:.4f}")
        
        return best_model_name, comparison_df
    
    def plot_comparison(self):
        """Plot model comparison"""
        log("\n[PLOT] Creating Model Comparison Plot...")
        comparison_df = pd.DataFrame(self.results).T.drop('model', axis=1)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Accuracy comparison
        comparison_df[['train_accuracy', 'test_accuracy']].plot(kind='bar', ax=axes[0, 0])
        axes[0, 0].set_title('Train vs Test Accuracy', fontweight='bold')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend(['Train', 'Test'])
        axes[0, 0].set_xticklabels(axes[0, 0].get_xticklabels(), rotation=45, ha='right')
        
        # Precision vs Recall
        comparison_df[['precision', 'recall']].plot(kind='bar', ax=axes[0, 1], color=['blue', 'orange'])
        axes[0, 1].set_title('Precision vs Recall', fontweight='bold')
        axes[0, 1].set_ylabel('Score')
        axes[0, 1].set_xticklabels(axes[0, 1].get_xticklabels(), rotation=45, ha='right')
        
        # F1-Score
        comparison_df['f1_score'].plot(kind='bar', ax=axes[1, 0], color='green')
        axes[1, 0].set_title('F1-Score Comparison', fontweight='bold')
        axes[1, 0].set_ylabel('F1-Score')
        axes[1, 0].set_xticklabels(axes[1, 0].get_xticklabels(), rotation=45, ha='right')
        
        # ROC-AUC
        comparison_df['roc_auc'].plot(kind='bar', ax=axes[1, 1], color='red')
        axes[1, 1].set_title('ROC-AUC Comparison', fontweight='bold')
        axes[1, 1].set_ylabel('ROC-AUC')
        axes[1, 1].set_xticklabels(axes[1, 1].get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(f'{Config.PLOTS_DIR}/05_model_comparison.png', dpi=300, bbox_inches='tight')
        log(f"[OK] Saved: 05_model_comparison.png")
        plt.close()

# ==================== PHASE 6: SAVE BEST MODEL ====================

class ModelSaver:
    """Save and load models"""
    
    @staticmethod
    def save_model(model, model_name, scaler, feature_names):
        """Save trained model and scaler"""
        log("\n[SAVE] SAVING MODEL...")
        
        try:
            # Save model
            with open(Config.BEST_MODEL_FILE, 'wb') as f:
                pickle.dump(model, f)
            log(f"[OK] Model saved: {Config.BEST_MODEL_FILE}")
            
            # Save scaler
            with open(Config.SCALER_FILE, 'wb') as f:
                pickle.dump(scaler, f)
            log(f"[OK] Scaler saved: {Config.SCALER_FILE}")
            
            # Save feature names
            with open(Config.FEATURE_NAMES_FILE, 'wb') as f:
                pickle.dump(feature_names, f)
            log(f"[OK] Feature names saved: {Config.FEATURE_NAMES_FILE}")
            
            log(f"\n[SUCCESS] Best model ({model_name}) ready for deployment!")
            
        except Exception as e:
            log(f"[ERROR] Error saving model: {str(e)}", 'ERROR')

# ==================== MAIN PIPELINE ====================

def run_complete_pipeline():
    """Execute complete ML pipeline"""
    
    log("=" * 70)
    log("[PHASE 0] CARDIOVASCULAR DISEASE PREDICTION - COMPLETE ML PIPELINE")
    log("=" * 70)
    
    # Setup
    ensure_directories()
    
    # ============ PHASE 1: DATA PREPROCESSING ============
    log("\n" + "="*70)
    log("[PHASE 1] DATA PREPROCESSING")
    log("="*70)
    
    preprocessor = DataPreprocessor(Config.DATA_FILE)
    (preprocessor
     .load_data()
     .check_missing_values()
     .remove_duplicates()
     .detect_and_remove_outliers()
     .feature_scaling()
    )
    preprocessor.get_info()
    
    df_processed = preprocessor.get_processed_data()
    
    # ============ PHASE 2: VISUALIZATION & INSIGHTS ============
    log("\n" + "="*70)
    log("[PHASE 2] VISUALIZATION & INSIGHTS")
    log("="*70)
    
    visualizer = DataVisualizer(preprocessor.df)  # Use original df for age calculation
    visualizer.create_age_histogram()
    visualizer.create_gender_countplot()
    visualizer.create_boxplots()
    corr_matrix = visualizer.create_correlation_heatmap()
    
    # ============ PHASE 3: FEATURE SELECTION ============
    log("\n" + "="*70)
    log("[PHASE 3] FEATURE SELECTION FROM CORRELATION")
    log("="*70)
    
    log("\n[SELECT] Features with highest correlation to disease:")
    top_features = corr_matrix['cardio'].abs().sort_values(ascending=False)[1:6]
    for feature, corr_val in top_features.items():
        log(f"  {feature}: {corr_val:.4f}")
    
    # ============ PHASE 4 & 5: MODEL TRAINING & COMPARISON ============
    trainer = ModelTrainer()
    trainer.prepare_data(df_processed)
    trainer.train_all_models()
    best_model_name, comparison_df = trainer.compare_models()
    trainer.plot_comparison()
    
    # ============ SAVE BEST MODEL ============
    best_model = trainer.results[best_model_name]['model']
    ModelSaver.save_model(best_model, best_model_name, preprocessor.scaler, preprocessor.feature_names)
    
    # ============ SUMMARY ============
    log("\n" + "="*70)
    log("[SUCCESS] PIPELINE COMPLETED SUCCESSFULLY!")
    log("="*70)
    log(f"\n[RESULTS] FINAL RESULTS SUMMARY:")
    log(f"  Dataset: {len(preprocessor.df)} patients")
    log(f"  Features: {len(preprocessor.feature_names)}")
    log(f"  Best Model: {best_model_name}")
    log(f"  Test Accuracy: {comparison_df.loc[best_model_name, 'test_accuracy']:.4f}")
    log(f"  Training completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"\n[FILES] Outputs:")
    log(f"  Models: {Config.BEST_MODEL_FILE}, {Config.SCALER_FILE}")
    log(f"  Plots: {Config.PLOTS_DIR}/ (5 visualization files)")
    log(f"  Logs: {Config.LOGS_DIR}/training_*.log")
    
    return trainer, preprocessor

if __name__ == '__main__':
    trainer, preprocessor = run_complete_pipeline()
    print("\n[DONE] All phases completed! Check logs/ and plots/ directories for outputs.")
