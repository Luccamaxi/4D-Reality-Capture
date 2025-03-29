import os
import subprocess
import time
from collections import defaultdict
import shutil
import sys
import argparse
import socket
import threading

# Add tqdm for progress bar
try:
    from tqdm import tqdm
except ImportError:
    print("tqdm not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
    from tqdm import tqdm

#suppress errors
import warnings
warnings.filterwarnings("ignore", category=UserWarning, append=True)

parser = argparse.ArgumentParser(description="Process RealityCapture project files.")
parser.add_argument('-s', '--server', action='store_true', help='Run in server mode')
parser.add_argument('-n', '--node', action='store_true', help='Run in node mode')
parser.add_argument('--port', type=int, default=5000, help='Port for server communication')
parser.add_argument('-ip', type=str, default='0.0.0.0', help='IP address for server communication (Only used for node. Enter the server IP)')
parser.add_argument('-rc', '--realitycapture', type=str, required=False, default="C:\\Program Files\\Capturing Reality\\RealityCapture\\RealityCapture.exe", help='Path to RealityCapture executable')
parser.add_argument('-r', '--root', type=str, required=True, help='Project folder path')
parser.add_argument('-p', '--project', type=str, required=False, default='scan.rcproj', help='Path to RealityCapture project file')
parser.add_argument('-i', '--images', type=str, required=False, default='images', help='Relative path to image folder')
parser.add_argument('-o', '--output', type=str, required=False, default='output', help='Relative path to output folder')
args = parser.parse_args()

RC_PATH = args.realitycapture
ROOT = args.root
if not ROOT.endswith("/"):
    ROOT += "/"

PROJECT_FILE = os.path.join(ROOT, args.project)
CAMERA_FOLDER = os.path.join(ROOT, args.images)
OUTPUT_FOLDER = os.path.join(ROOT, args.output)

TEMP_DIR = f'{ROOT}temp'
BATCH_FILE = f'{TEMP_DIR}/rc_commands.bat'  

PORT = args.port  # Port for server communication
IP = args.ip  # IP address for server communication


if not os.path.isfile(RC_PATH):
    raise FileNotFoundError(f"RealityCapture executable not found at {RC_PATH}")
if not os.path.isfile(PROJECT_FILE):
    raise FileNotFoundError(f"Project file not found at {PROJECT_FILE}")
if not os.path.isdir(CAMERA_FOLDER):
    raise FileNotFoundError(f"Image folder not found at {CAMERA_FOLDER}")
elif not CAMERA_FOLDER.endswith("/"):
    CAMERA_FOLDER += "/"
if not os.path.isdir(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
if not os.path.isfile(RC_PATH):
    raise FileNotFoundError(f"RealityCapture executable not found at {RC_PATH}")

def copy_project_to_temp(frame_number):
    """
    Copies the project file, project folder, and frame folder to a temporary location.
    Places them in a frame-specific subfolder without renaming.
    Returns the path to the temp project file.
    """
    # Create temp directory if it doesn't exist
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    
    # Create a frame-specific subfolder
    frame_subfolder = os.path.join(TEMP_DIR, f"frame_{int(frame_number):05d}")
    if os.path.exists(frame_subfolder):
        shutil.rmtree(frame_subfolder)  # Remove if already exists
    os.makedirs(frame_subfolder)
    
    # Get project file name without extension and path
    project_name = os.path.basename(PROJECT_FILE)
    
    # Define temp project file path (preserving original filename)
    temp_project_file = os.path.join(frame_subfolder, project_name)
    
    # Format the frame folder name
    frame_folder = f"frame_{int(frame_number):05d}"
    source_frame_path = os.path.join(CAMERA_FOLDER, "Sequence", frame_folder)
    
    # Preserve original folder structure in temp location
    temp_cropped_dir = os.path.join(frame_subfolder, "cropped")
    temp_sequence_path = os.path.join(temp_cropped_dir, "Sequence")
    temp_frame_path = os.path.join(temp_sequence_path, frame_folder)
    
    # 1. Copy project file (keeping original name)
    shutil.copy2(PROJECT_FILE, temp_project_file)

    
    # 2. Copy project folder (if it exists)
    source_project_folder = os.path.join(os.path.dirname(PROJECT_FILE), os.path.basename(PROJECT_FILE).split('.')[0])
    temp_project_folder = os.path.join(frame_subfolder, os.path.basename(PROJECT_FILE).split('.')[0])
    
    if os.path.exists(source_project_folder) and os.path.isdir(source_project_folder):
        shutil.copytree(source_project_folder, temp_project_folder)
        
    
    # 3. Copy frame folder - create directory structure first
    if os.path.exists(source_frame_path) and os.path.isdir(source_frame_path):
        # Create directory structure
        os.makedirs(temp_sequence_path, exist_ok=True)
        
        # Copy the frame folder with its original name
        shutil.copytree(source_frame_path, temp_frame_path)
    else:
        print(f"Warning: Source frame folder {source_frame_path} not found")
    
    return temp_project_file

def cleanup_temp_files(frame_number=None):
    """
    Removes the temporary directory and all its contents. Based on the frame number
    """
    if frame_number is not None:
        frame_subfolder = os.path.join(TEMP_DIR, f"frame_{int(frame_number):05d}")
        if os.path.exists(frame_subfolder):
            shutil.rmtree(frame_subfolder)  # Remove the specific frame subfolder
    else:
        # Remove the entire temp directory
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)  # Remove the entire temp directory

def run_rc_commands(commands):
    # Create a temporary batch file to run the commands
    with open(BATCH_FILE, "w") as f:
        for command in commands:
            f.write(f"{command}\n")

    # Run the batch file in a subprocess
    process = subprocess.Popen([BATCH_FILE], shell=True)
    process.wait()  # Wait for the process to finish

    # Clean up the batch file
    os.remove(BATCH_FILE)
 
    return process.returncode

def modify_project_file(frame_number, project_file=None):
    """
    Modifies the RealityCapture project file to use images from a specific frame.
    
    Args:
        frame_number: The frame number to use (will be formatted as frame_XXXXX)
        project_file: Optional path to project file (defaults to PROJECT_FILE)
    """
    import xml.etree.ElementTree as ET
    import re
    
    # Use provided project file or default
    project_file = project_file or PROJECT_FILE
    
    # Format the frame folder name
    frame_folder = f"frame_{int(frame_number):05d}"
    
    # Parse the project file
    tree = ET.parse(project_file)
    root = tree.getroot()
    
    # Find all input elements and update their fileName attributes
    source_element = root.find('source')
    if source_element is not None:
        for input_elem in source_element.findall('input'):
            file_path = input_elem.get('fileName', '')
            if file_path:
                # Replace only the frame folder portion in the path
                new_file_path = re.sub(r'frame_\d+', frame_folder, file_path)
                input_elem.set('fileName', new_file_path)
    
    # Save the modified project file
    tree.write(project_file)

def node():
    HOST = args.ip
    PORT = args.port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Connected to server at {HOST}:{PORT}")
    # initialize node id based on computer name
    node_id = socket.gethostname()
    print(f"Node ID: {node_id}")
    status = "idle"
    # send id and status to server
    client_socket.send(f"{node_id},{status}".encode())
    while True:
        # receive command from server
        data = client_socket.recv(1024).decode()
        if not data:
            break
        
        frame_number = int(data)
        # Skip if frame number is 0 (server has no more work)
        if frame_number == 0:
            time.sleep(5)  # Wait before asking again
            client_socket.send(f"{node_id},{status}".encode())
            continue
            
        status = "busy"
        client_socket.send(f"{node_id},{status}".encode())
        cleanup_temp_files(frame_number)
        print(f"Processing frame {frame_number}...")
        temp_project_file = copy_project_to_temp(frame_number)
        modify_project_file(frame_number, temp_project_file)
        run_rc_commands([f'"{RC_PATH}" -headless -load {temp_project_file} deleteAutosave -set appAutoClearCache=0 -set appCacheImageMetadata=false -calculateHighModel -calculateTexture -exportModel "Model 1" "{OUTPUT_FOLDER}/Frame_{frame_number}.obj" -quit'])
        cleanup_temp_files(frame_number)
        status = "idle"
        client_socket.send(f"{node_id},{status}".encode())

def server():
    #print ip address
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f"Server IP Address: {ip_address}")
    
    # Check available frames in camera folder
    SEQUENCES = os.path.join(CAMERA_FOLDER, "Sequence")
    
    # Create sequence path if it doesn't exist
    if not os.path.exists(SEQUENCES):
        os.makedirs(SEQUENCES, exist_ok=True)
        print(f"Created sequence directory at {SEQUENCES}")
    
    # More robust frame parsing with error handling
    frame_list = []
    if os.path.exists(SEQUENCES):
        for frame in os.listdir(SEQUENCES):
            frame_path = os.path.join(SEQUENCES, frame)
            if os.path.isdir(frame_path):
                try:
                    # Check if directory follows the expected format
                    if frame.startswith("frame_") and "_" in frame:
                        frame_num = int(frame.split("_")[1])
                        frame_list.append(frame_num)
                    else:
                        print(f"Skipping directory with unexpected format: {frame}")
                except (ValueError, IndexError) as e:
                    print(f"Error parsing frame number from directory: {frame} - {str(e)}")
    
    frame_list = sorted(frame_list)
    frame_amount = len(frame_list)
    print(f"Frames available: {frame_amount}")
    
    if frame_amount == 0:
        print("No frames found in the sequence folder. Check directory structure.")
        print(f"Expected frame folders like 'frame_00001' in: {SEQUENCES}")
        if os.path.exists(SEQUENCES):
            print(f"Contents of {SEQUENCES}: {os.listdir(SEQUENCES)}")
        return
    
    # Check for already processed frames
    processed_frames = set()
    for filename in os.listdir(OUTPUT_FOLDER):
        if filename.startswith("Frame_") and filename.endswith(".obj"):
            try:
                frame_num = int(filename.replace("Frame_", "").replace(".obj", ""))
                processed_frames.add(frame_num)
                print(f"Found already processed frame: {frame_num}")
            except ValueError:
                pass
    
    # Create list of frames that need processing
    frames_to_process = [f for f in frame_list if f not in processed_frames]
    total_frames = len(frames_to_process)
    print(f"Frames to process: {total_frames} out of {frame_amount}")
    
    # Thread-safe structures for node management
    nodes_lock = threading.Lock()
    nodes_status = {}  # Store node_id -> status
    next_frame_index = 0
    
    # Calculate initial completion (already processed frames)
    initial_completed = len(processed_frames)
    remaining_frames = len(frames_to_process)
    
    # Create progress bar with proper initialization
    progress_bar = tqdm(total=remaining_frames, 
                         desc="Processing frames", 
                         unit="frame",
                         position=0)
    completed_frames = 0  # Reset to track new completions
    
    print(f"Already processed: {initial_completed}, Remaining: {remaining_frames}")
    
    def handle_node(client_socket, addr):
        nonlocal next_frame_index, completed_frames
        node_id = None
        previous_status = None
        
        print(f"New connection from {addr}")
        
        while True:
            try:
                # Receive data from node
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                
                node_id, status = data.split(",")
                
                # Update node status
                with nodes_lock:
                    # Check for status transition from busy to idle
                    status_changed = (node_id in nodes_status and 
                                     nodes_status[node_id] == "busy" and 
                                     status == "idle")
                    
                    # Store current status
                    previous_status = nodes_status.get(node_id)
                    nodes_status[node_id] = status
                    
                    # Print status with colors (outside progress bar)
                    status_msg = f"Node: {node_id} - Status: {'🔴 BUSY' if status == 'busy' else '🟢 IDLE'}"
                    progress_bar.write(status_msg)
                
                # If node reports idle after being busy, it completed a frame
                if previous_status == "busy" and status == "idle":
                    with nodes_lock:
                        completed_frames += 1
                        # Use update(1) to increment by 1 (more reliable than setting .n directly)
                        progress_bar.update(1)
                        progress_bar.write(f"Progress: {completed_frames}/{remaining_frames} frames processed")
                
                # If node is idle and frames are available, assign work
                if status == "idle" and next_frame_index < len(frames_to_process):
                    frame_number = frames_to_process[next_frame_index]
                    
                    with nodes_lock:
                        next_frame_index += 1
                    
                    # Send frame number to node
                    client_socket.send(str(frame_number).encode())
                    progress_bar.write(f"Assigned frame {frame_number} to {node_id}")
                    
                elif status == "idle" and next_frame_index >= len(frames_to_process):
                    # No more frames to process, send dummy task to keep connection
                    client_socket.send("0".encode())
                    progress_bar.write(f"No more frames to assign, {node_id} waiting")
                    
            except Exception as e:
                progress_bar.write(f"Error handling node {addr}: {e}")
                break
        
        # Clean up when node disconnects
        progress_bar.write(f"Node disconnected: {addr}")
        with nodes_lock:
            if node_id in nodes_status:
                del nodes_status[node_id]
        
        try:
            client_socket.close()
        except:
            pass
    
    # Set up the server socket
    HOST = '0.0.0.0'
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)  # Allow up to 10 pending connections

    print(f"Server listening on port {PORT}")
    
    # Accept connections from nodes and spawn threads to handle them
    try:
        while True:
            client_socket, addr = server_socket.accept()
            node_thread = threading.Thread(target=handle_node, args=(client_socket, addr))
            node_thread.daemon = True
            node_thread.start()
    
    except KeyboardInterrupt:
        progress_bar.write("Server shutting down...")
    finally:
        progress_bar.close()
        server_socket.close()
        print("Server socket closed")

if args.server:
    server()
elif args.node:
    node()
else:
    print("Run Program as server with -s or as node -n")
    sys.exit(1)
