# Plant Disease Detection

## Overview

This project implements a complete computer vision pipeline for plant leaf disease detection, infection quantification, and an interactive web interface to explore results. It covers image preprocessing, lesion segmentation, feature extraction, classification model training, and deployment via a Flask application with D3.js visualization.

## Objective

* **Detect** and segment diseased regions on plant leaves from uploaded images.
* **Quantify** the percentage of infected leaf area.
* **Provide** an easy-to-use web interface for users to upload leaf photos and immediately view disease predictions, mask overlays, and infection gauges.

## Workflow Overview

1. **Leaf Extraction**

   * Read raw images and create a green-leaf mask via HSV thresholding and morphological operations.
   * Identify the largest contour, compute its convex hull, and crop the leaf region.
   
2. **Data Preprocessing & Splitting** 

   * Stratify-split into train (70%), validation (15%), and test (15%) sets.
   * Resize each image to 256×256 pixels

3. **Lesion Segmentation**

   * Segmentation of lesions is implemented using CLAHE on Lab L-channel and Otsu thresholding on the a-channel to isolate brown/yellow lesions.
   * Clean masks with morphological opening/closing.
     
4. **Feature Extraction** 

   * For each processed image and its mask: extract color features (mean & std per BGR channel) over lesion pixels.
   * Compute shape descriptors: total lesion area, perimeter, roundness, and bounding-box aspect ratio.

5. **Classification & Infection Calculation**

   * Load extracted features, scale them, and train an SVM on the training set.
   * Compute the infection percentage (lesion pixels over leaf pixels)

6. **Web Interface** 

   * Display original leaf, lesion mask overlay, and an interactive D3.js gauge showing infection percentage.

## Dependencies & Installation

   ```bash
   pip install opencv-python numpy pandas pillow scikit-learn flask joblib
   ```
