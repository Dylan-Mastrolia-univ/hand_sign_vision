import os
import shutil
import random

output_folder_train = "./dataset_train"
output_folder_eval = "./dataset_eval"

def extract_image(path):
    last = path.split("/")[-1].lower()
    os.makedirs(os.path.join(output_folder_train, last), exist_ok=True)
    for file in os.listdir(path):
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
            shutil.copy(os.path.join(path, file), os.path.join(output_folder_train, last, file))

def crawl_file(path):
    if os.path.isdir(path):
        last = path.split("/")[-1]
        if len(last) == 1 and last.isalpha():
            extract_image(path)
        elif len(last) == 1 and last.isdigit():
            pass
        else:
            for file in os.listdir(path):
                rec_path = os.path.join(path, file)
                crawl_file(rec_path)


def make_val_dataset():
    for folder in os.listdir(output_folder_train):
        if os.path.isdir(os.path.join(output_folder_train, folder)):
            for file in os.listdir(os.path.join(output_folder_train, folder)):
                if random.random() < 0.2:
                    os.makedirs(os.path.join(output_folder_eval, folder),exist_ok=True)
                    shutil.move(os.path.join(output_folder_train, folder, file), os.path.join(output_folder_eval, folder, file))


if __name__ == "__main__":
    crawl_file("./")
    #make_val_dataset()