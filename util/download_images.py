import imagehash
import json
import os
import progressbar
import signal
import socket
import sys
import requests
import argparse

from PIL import Image

# Set up argument parser
parser = argparse.ArgumentParser(description='Download images from a JSON file.')
parser.add_argument('json_file', help='Path to the JSON file with image URLs')
parser.add_argument('--hash_file', default=None, help='Path to the hash file for validation')
parser.add_argument('--out_dir', default='out', help='Directory to save output files')
args = parser.parse_args()

# Set up directories
base_out_dir = args.out_dir
images_dir = os.path.join(base_out_dir, 'images')
logs_dir = os.path.join(base_out_dir, 'logs')

# Create output directories
os.makedirs(images_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

# Get filenames
json_file = args.json_file
split_name = os.path.splitext(os.path.basename(json_file))[0]

HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
TIMEOUT = 2  # Timeout of 2 seconds

# Load JSON as a single array
with open(json_file, 'r') as f:
    examples = json.load(f)

class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout()

def save_image(filename, url, img_hash, wrong_hash_file):
    save_path = os.path.join(images_dir, filename)
    if not os.path.exists(save_path):
        try:
            with Timeout(TIMEOUT):
                try:
                    request = requests.get(url, headers=HEADER, stream=True)

                    # Save the image to the specified directory
                    with open(save_path, 'wb') as f:
                        for chunk in request.iter_content(1024):
                            f.write(chunk)

                    # And make sure the hash is correct if provided
                    try:
                        saved_hash = str(imagehash.average_hash(Image.open(save_path)))

                        # Only validate hash if one was provided
                        if img_hash and not saved_hash == img_hash:
                            wrong_hash_file.write(f"{url}\t{filename}\t{saved_hash}\t{img_hash}\n")
                    except OSError as e:
                        return e
                except requests.exceptions.ConnectionError as e:
                    return e
                except requests.exceptions.TooManyRedirects as e:
                    return e
                except requests.exceptions.ChunkedEncodingError as e:
                    return e
                except requests.exceptions.ContentDecodingError as e:
                    return e
                return request.status_code
        except Timeout.Timeout as e:
            return e
    return 200  # Return 200 if file already exists

# Try to load hash file
hashes = {}
if args.hash_file:
    try:
        with open(args.hash_file, 'r') as f:
            hashes = json.load(f)
        print(f"Loaded {len(hashes)} image hashes from {args.hash_file}")
    except FileNotFoundError:
        print(f"Hash file {args.hash_file} not found. Continuing without hash validation.")

# Set up log files
failed_imgs_path = os.path.join(logs_dir, f"{split_name}_failed_imgs.txt")
checked_imgs_path = os.path.join(logs_dir, f"{split_name}_checked_imgs.txt")
failed_hashes_path = os.path.join(logs_dir, f"{split_name}_failed_hashes.txt")

# Initialize progress bar
pbar = progressbar.ProgressBar(maxval=len(examples))
pbar.start()

with open(failed_imgs_path, "a") as ofile, open(checked_imgs_path, "a") as checked_file, open(failed_hashes_path, "a") as failed_hash_file:
    # Create empty set if file doesn't exist or read existing file
    try:
        checked_urls = set([line.strip() for line in open(checked_imgs_path).readlines()])
    except FileNotFoundError:
        checked_urls = set()
        
    num_none = 0
    num_total = 0

    for i, example in enumerate(examples):
        split_id = example["identifier"].split("-")
        image_id = "-".join(split_id[:3])

        left_image_name = image_id + "-img0.png"
        right_image_name = image_id + "-img1.png"

        left_url = example["left_url"]
        right_url = example["right_url"]

        if not left_url in checked_urls:
            # Use .get() to safely access hash dictionary with a default empty string
            status_code = save_image(left_image_name, left_url, hashes.get(left_image_name, ""), failed_hash_file)
            if status_code != 200:
                ofile.write(f"{status_code}\t{left_image_name}\t{left_url}\n")
                ofile.flush()
                num_none += 1
            checked_urls.add(left_url)
            checked_file.write(f"{left_url}\n")
            num_total += 1
        if not right_url in checked_urls:
            # Use .get() to safely access hash dictionary with a default empty string
            status_code = save_image(right_image_name, right_url, hashes.get(right_image_name, ""), failed_hash_file)
            if status_code != 200:
                ofile.write(f"{status_code}\t{right_image_name}\t{right_url}\n")
                ofile.flush()
                num_none += 1
            checked_urls.add(right_url)
            checked_file.write(f"{right_url}\n")
            num_total += 1

        pbar.update(i)

pbar.finish()
print(f"Output saved to '{base_out_dir}' directory")
print(f"Images saved to '{images_dir}'")
print(f"Logs saved to '{logs_dir}'")
print(f"Number of missing images: {num_none}")
print(f"Total number of requests: {num_total}")
