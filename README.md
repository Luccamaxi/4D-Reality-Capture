
# RealityCapture 4D Scene Processor

This project automates the processing of 4D scenes in **RealityCapture** using its CLI. It handles camera registrations, sequential frame injection, high-quality model processing with textures, and exports the results to an output folder. The processing can be **distributed across multiple machines** with a master node managing and monitoring all workers.

## Features
- **Automated RealityCapture Processing**: The program reads pre-registered camera data and injects image sequences frame-by-frame.
- **High-Quality Model Processing**: Runs RealityCapture with high settings and generates textures.
- **Distributed Processing Support**: Multiple worker nodes can run RealityCapture in parallel.
- **Master Node Monitoring**: A central dashboard tracks all worker nodes, displaying processing status and stats.
- **Networked Storage**: All RealityCapture project files must reside in a **networked folder** to enable seamless distributed processing.
- **Interchangeable Image Formats**: Works with multiple image formats for flexibility.

## Dependencies
- **RealityCapture CLI**
- **Python** (for worker scripts)
- **Node.js** (for master node management)
- **A shared network folder** (required for distributed processing)

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/realitycapture-4d-processor.git
   cd realitycapture-4d-processor
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt  # Install Python dependencies
   npm install  # Install Node.js dependencies
   ```
3. Set up your RealityCapture CLI path in the config file.

## Usage
- **Master Node**: Run the master script to manage distributed processing.
  ```sh
  node master.js
  ```
- **Worker Node**: Run the worker script on each processing machine.
  ```sh
  python worker.py
  ```

## RealityCapture Setup
For reference on creating RealityCapture projects, see this video:  
[![RealityCapture Tutorial](https://img.youtube.com/vi/U2Pj5HRGCVg/0.jpg)](https://www.youtube.com/watch?v=U2Pj5HRGCVg)  

_(This video will be replaced later with a custom guide.)_


