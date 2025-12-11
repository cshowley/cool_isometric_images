import requests
import base64
import os
import re
from dotenv import load_dotenv; load_dotenv()
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('image_subject')
args = parser.parse_args()

def generate_iso_image(subject):
    url = "https://api.venice.ai/api/v1/image/generate"
    payload = {
        "model": "nano-banana-pro",
        "prompt": f"Make a photo that is perfectly isometric. It is not a miniature, it is a captured photo that just happened to be perfectly isometric. It is a photo of {subject}",
        "embed_exif_metadata": False,
        "format": "webp",
        "hide_watermark": False,
        "return_binary": False,
        "variants": 3,
        "safe_mode": True,
        "seed": 0,
        "enable_web_search": False,
        "aspect_ratio": "9:16",
    }
    headers = {
        "Authorization": f"Bearer {os.environ['venice_api_key']}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response


def save_base64_image(base64_string, output_path):
    """
    Decodes a Base64 encoded string and saves it as an image file.

    Args:
        base64_string (str): The Base64 encoded string, either as a data URI
                             (e.g., 'data:image/png;base64,iVBOR...') or as
                             a raw Base64 string.
        output_path (str): The full path (including filename and extension)
                           where the image will be saved. If the extension
                           is omitted, it will be inferred from the data URI.
    """
    try:
        # Check if it's a data URI
        # Regex to capture the mime type (e.g., 'image/png') and the base64 data
        match = re.match(r'data:(image/[\w+]+);base64,(.+)', base64_string)
        
        if match:
            # It's a data URI, extract mime type and data
            mime_type = match.group(1)
            base64_data = match.group(2)
            
            # Determine file extension from mime type
            extension_map = {
                'image/png': '.png',
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/gif': '.gif',
                'image/webp': '.webp',
                'image/svg+xml': '.svg',
            }
            extension = extension_map.get(mime_type)
            
            if not extension:
                print(f"Warning: Unknown mime type '{mime_type}'. Cannot determine file extension.")
                # You might want to default to .png or raise an error
                extension = '.png' 

            # If output_path doesn't have an extension, add the inferred one
            if not os.path.splitext(output_path)[1]:
                output_path += extension

        else:
            # It's a raw Base64 string, use it directly
            base64_data = base64_string
            # If output_path doesn't have an extension, add a default one
            if not os.path.splitext(output_path)[1]:
                output_path += '.png' # Default to .png for raw strings

        # Decode the Base64 string into bytes
        image_data = base64.b64decode(base64_data)

        # Write the binary data to a file
        with open(output_path, 'wb') as image_file:
            image_file.write(image_data)
            
        print(f"Image successfully saved to {output_path}")

    except base64.binascii.Error:
        print("Error: The provided string is not valid Base64.")
    except Exception as e:
        print(f"An error occurred: {e}")


response = generate_iso_image(args.image_subject)
save_base64_image(response.json()['images'][0], 'image.png')