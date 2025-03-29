#This script talkes a folder of subfolders (cameras) with syncronized images and sorts them into a folder of frames with subfolders (frames) with images from each camera
import os
import shutil
import argparse
import re  # Add import for regular expressions

parser = argparse.ArgumentParser(description="Sort images from camera folders into frame folders.")
parser.add_argument("-i", type=str, help="Path to the input folder containing camera folders.")
parser.add_argument("-o", type=str, help="Path to the output folder where frame folders will be created.")

def sort_images_by_frame(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through each camera folder in the input folder
    for camera_folder in os.listdir(input_folder):
        camera_path = os.path.join(input_folder, camera_folder)
        if os.path.isdir(camera_path):
            # Iterate through each image in the camera folder
            for image_file in os.listdir(camera_path):
                # Extract the frame number from the image file name - just the numeric part
                match = re.search(r'\d+', image_file)
                if match:
                    frame_number = match.group()
                else:
                    print(f"Warning: No frame number found in {image_file}, skipping...")
                    continue
                frame_folder = os.path.join(output_folder, f"frame_{frame_number}")

                # Create the frame folder if it doesn't exist
                os.makedirs(frame_folder, exist_ok=True)

                # Copy the image to the corresponding frame folder
                shutil.copy(os.path.join(camera_path, image_file), os.path.join(frame_folder, image_file))


if __name__ == "__main__":
    args = parser.parse_args()
    input_folder = args.i
    output_folder = args.o

    sort_images_by_frame(input_folder, output_folder)
    print(f"Images sorted from {input_folder} to {output_folder}.")