from PIL import Image
import os, random

bg_removed_folder = "output_bg_process/"         
bg_folder = "backgrounds/"    
merged_folder = "merged/"

os.makedirs(merged_folder, exist_ok=True)

TARGET_SIZE = (800, 800)

for folder in os.listdir(bg_removed_folder):
    folder_path = os.path.join(bg_removed_folder, folder)
    print(f"Traitement du dossier: {folder}")

    if os.path.isdir(folder_path):
        for fg_file in os.listdir(folder_path):
            if fg_file.endswith(".png"):

                fg_path = os.path.join(folder_path, fg_file)
                fg_img = Image.open(fg_path).convert("RGBA")

                for i in range(1, 6):
                    bg_file = random.choice(os.listdir(bg_folder))
                    bg_path = os.path.join(bg_folder, bg_file)
                    bg_img = Image.open(bg_path).convert("RGBA")

                    bg_img = bg_img.resize(TARGET_SIZE)

                    max_x = max(0, TARGET_SIZE[0] - fg_img.width)
                    max_y = max(0, TARGET_SIZE[1] - fg_img.height)
                    random_x = random.randint(0, max_x) if max_x > 0 else 0
                    random_y = random.randint(0, max_y) if max_y > 0 else 0

                    bg_img.paste(fg_img, (random_x, random_y), fg_img)

                    output_folder_path = os.path.join(merged_folder, folder)
                    os.makedirs(output_folder_path, exist_ok=True)

                    base_name = os.path.splitext(fg_file)[0]
                    out_path = os.path.join(output_folder_path, f"{base_name}_var{i}.png")
                    bg_img.save(out_path, format="PNG")

print("✅ Fusion terminée.")
