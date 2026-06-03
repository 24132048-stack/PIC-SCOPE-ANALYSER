from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import hashlib
import os


def calculate_hashes(file_path):
    hashes = {
        "MD5": hashlib.md5(),
        "SHA1": hashlib.sha1(),
        "SHA256": hashlib.sha256()
    }

    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            for h in hashes.values():
                h.update(chunk)

    return {name: h.hexdigest() for name, h in hashes.items()}


def convert_to_degrees(value):
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])

    return d + (m / 60.0) + (s / 3600.0)


def extract_gps(gps_info):
    try:
        lat = convert_to_degrees(gps_info['GPSLatitude'])
        lon = convert_to_degrees(gps_info['GPSLongitude'])

        if gps_info['GPSLatitudeRef'] != 'N':
            lat = -lat

        if gps_info['GPSLongitudeRef'] != 'E':
            lon = -lon

        return lat, lon

    except:
        return None, None


def extract_metadata(image_path):

    image = Image.open(image_path)
    exif_data = image._getexif()

    if not exif_data:
        print("No EXIF metadata found.")
        return

    metadata = {}

    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)

        if tag == "GPSInfo":
            gps_data = {}

            for key in value:
                decoded = GPSTAGS.get(key, key)
                gps_data[decoded] = value[key]

            metadata["GPSInfo"] = gps_data

        else:
            metadata[tag] = value

    print("\n========== IMAGE METADATA ==========\n")

    for key, value in metadata.items():
        if key != "GPSInfo":
            print(f"{key}: {value}")

    if "GPSInfo" in metadata:

        print("\n========== GPS DATA ==========\n")

        gps = metadata["GPSInfo"]

        for k, v in gps.items():
            print(f"{k}: {v}")

        lat, lon = extract_gps(gps)

        if lat and lon:
            print(f"\nLatitude  : {lat}")
            print(f"Longitude : {lon}")

            print(
                f"\nGoogle Maps:\n"
                f"https://maps.google.com/?q={lat},{lon}"
            )


if __name__ == "__main__":

    image_path = input("Enter image path: ")

    if not os.path.exists(image_path):
        print("File not found.")
        exit()

    print("\n========== FILE HASHES ==========\n")

    hashes = calculate_hashes(image_path)

    for name, value in hashes.items():
        print(f"{name}: {value}")

    extract_metadata(image_path)
