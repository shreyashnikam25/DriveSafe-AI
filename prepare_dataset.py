import os
import shutil
import random
from pathlib import Path

def prepare_dataset():
    print("Organizing MRL Eye Dataset for DriveSafe-AI CNN...")

    # Path to raw extracted dataset
    raw_dir = Path("data/raw/MRL_Dataset") 
    processed_dir = Path("data/processed")
    
    categories = ['Open_Eyes', 'Closed_Eyes']
    splits = ['train', 'val']

    # Create target directories
    for split in splits:
        for category in categories:
            os.makedirs(processed_dir / split / category, exist_ok=True)

    if not raw_dir.exists():
        print(f"Error: {raw_dir} not found! Please ensure your extracted dataset is located in S:\\DriveSafe-AI\\data\\raw\\mrlEyes_2018_01\\")
        return

    all_images = []
    for root, _, files in os.walk(raw_dir):
        for file in files:
            if file.endswith('.png'):
                all_images.append(os.path.join(root, file))

    print(f"Found {len(all_images)} total images. Processing...")

    open_eyes = []
    closed_eyes = []

    for img_path in all_images:
        filename = os.path.basename(img_path)
        parts = filename.split('_')
        
        if len(parts) > 4:
            state = parts[4]
            if state == '1':
                open_eyes.append(img_path)
            elif state == '0':
                closed_eyes.append(img_path)

    random.shuffle(open_eyes)
    random.shuffle(closed_eyes)

    train_split_open = int(len(open_eyes) * 0.8)
    train_split_closed = int(len(closed_eyes) * 0.8)

    transfers = {
        'train/Open_Eyes': open_eyes[:train_split_open],
        'val/Open_Eyes': open_eyes[train_split_open:],
        'train/Closed_Eyes': closed_eyes[:train_split_closed],
        'val/Closed_Eyes': closed_eyes[train_split_closed:]
    }

    for dest, file_list in transfers.items():
        dest_folder = processed_dir / dest
        print(f"Copying {len(file_list)} images to {dest_folder}...")
        for src in file_list:
            filename = os.path.basename(src)
            shutil.copy2(src, dest_folder / filename)

    print("\nDataset preparation complete! Data is structured in S:\\DriveSafe-AI\\data\\processed\\")

if __name__ == "__main__":
    prepare_dataset()