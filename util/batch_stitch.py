import os
import re
from PIL import Image
import argparse

SEPARATOR_THICKNESS = 10

def stitch_pair(img0_path, img1_path, output_path):
    img0 = Image.open(img0_path).convert("RGB")
    img1 = Image.open(img1_path).convert("RGB")

    new_height = min(img0.height, img1.height)
    img0 = img0.resize((int(img0.width * new_height / img0.height), new_height))
    img1 = img1.resize((int(img1.width * new_height / img1.height), new_height))

    total_width = img0.width + img1.width + SEPARATOR_THICKNESS
    stitched_img = Image.new("RGB", (total_width, new_height), color=(0, 0, 0))

    stitched_img.paste(img0, (0, 0))
    stitched_img.paste(img1, (img0.width + SEPARATOR_THICKNESS, 0))
    stitched_img.save(output_path)
    print(f"[✔] Saved: {output_path}")

def process_directory(input_dir, output_dir="./out/stitched_images"):
    os.makedirs(output_dir, exist_ok=True)

    pattern = re.compile(r"^(.*)-img0\.png$")
    files = os.listdir(input_dir)
    img0_files = [f for f in files if pattern.match(f)]

    stitched_count = 0

    for img0_file in img0_files:
        match = pattern.match(img0_file)
        if not match:
            continue

        identifier = match.group(1)
        img0_path = os.path.join(input_dir, img0_file)
        img1_filename = f"{identifier}-img1.png"
        img1_path = os.path.join(input_dir, img1_filename)

        if os.path.exists(img1_path):
            output_filename = f"{identifier}-stitched.png"
            output_path = os.path.join(output_dir, output_filename)
            stitch_pair(img0_path, img1_path, output_path)
            stitched_count += 1
        else:
            print(f"[!] Skipping: Missing pair for {img0_file} → {img1_filename}")

    print(f"\n[✓] Done. Total stitched images: {stitched_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stitch image pairs in a directory with a black vertical separator.")
    parser.add_argument("directory", help="Path to the folder containing image pairs")
    args = parser.parse_args()

    process_directory(args.directory)
