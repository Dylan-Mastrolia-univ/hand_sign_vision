from rembg import remove, new_session
import os

session = new_session("u2net")

input_folder = "input_bg_process/"
output_folder = "output_bg_process/"

os.makedirs(output_folder, exist_ok=True)

for folder in os.listdir(input_folder):
    folder_path = os.path.join(input_folder, folder)
    print(folder)
    if os.path.isdir(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith((".png", ".jpg", ".jpeg")):
                with open(os.path.join(folder_path, file), "rb") as inp:
                    output = remove(inp.read(), session=session)
                    output_path = os.path.join(output_folder, folder)
                    os.makedirs(output_path,exist_ok=True)
                    with open(os.path.join(output_path, file.replace(".jpg", ".png").replace(".jpeg", ".png")), "wb") as out:
                        out.write(output)