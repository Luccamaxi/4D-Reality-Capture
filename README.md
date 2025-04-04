
# RealityCapture 4D Scene Processor

This project automates the processing of 4D scenes in **RealityCapture** using its CLI. It handles camera registrations, sequential frame injection, high-quality model processing with textures, and exports the results to an output folder. The processing can be **distributed across multiple machines** with a master node managing and monitoring all workers.

## Features
- **Automated RealityCapture Processing**: The program reads pre-registered camera data and injects image sequences frame-by-frame.
- **High-Quality Model Processing**: Runs RealityCapture with high settings and generates textures.
- **Distributed Processing Support**: Multiple worker nodes can run RealityCapture in parallel.
- **Master Node Monitoring**: A central dashboard tracks all worker nodes, displaying processing status.
- **Networked Storage**: All RealityCapture project files must reside in a **networked folder** to enable seamless distributed processing.

## Dependencies
- **RealityCapture**
- **Python** (I used 3.10)
- **A shared network folder** (required for distributed processing)

## Folder Structure
If you have different names make sure to reference them via relaive paths see how with:

   ```sh
   python ./WebNode.py --help
   ```

   ```markdown
   M:\                    # Network Drive/Folder
   │── images\
      │──Sequence          # Folder containing multi image sequences
          |──frame_0000\   # Folder containing camera images 
          ...
   │── scene\             # Scene-related files
   │── scene.rcproj       # RealityCapture project file
   │── output\            # Folder for processed outputs
   ```

## Installation
Clone this repository:
   ```sh
   git clone https://github.com/yourusername/realitycapture-4d-processor.git
   cd realitycapture-4d-processor
   ```
## Usage

**Create Folder Structure**: 
To sort your images into the rigth format use the "camera_to_frames.py" tool to create subfolders per frame if you have images sorted by your camera instead of the individual frames

**Create Peality Capture Project**: 
Imprt you first frame into RC, align all images and adjust the reconstruction region.
Save the file in your project folder

- **Server**: Run WebNode.py -s to manage distributed processing.
  ```sh
  python ./WebNode.py --server --root M:/ # REPLACE WITH YOUR NETWORK FOLDER
  ```
  
- **Node**: Run WebNode.py -n on each processing machine.
  I like to create a batch file for that that lies in the network folder.
  ```sh
  python ./WebNode.py --node -ip 192.168.178.22 -r M: # REPLACE WITH YOUR IP AND NETWORK FOLDER
  ```

## RealityCapture Setup
For reference on creating RealityCapture projects, see this video:  
[![RealityCapture Tutorial](https://img.youtube.com/vi/U2Pj5HRGCVg/0.jpg)](https://www.youtube.com/watch?v=U2Pj5HRGCVg)  

_(This video will be replaced later with a custom guide.)_


