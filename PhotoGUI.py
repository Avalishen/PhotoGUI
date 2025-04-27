import os
import shutil
from PIL import Image
import imagehash
from collections import defaultdict
import tkinter as tk
from tkinter import ttk
import random
import string


def find_and_sort_duplicates(folder_path, duplicates_folder_path):
    if not os.path.exists(duplicates_folder_path):
        os.makedirs(duplicates_folder_path)

    hashes = {}
    duplicates = defaultdict(list)

    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if not any(filename.lower().endswith(ext) for ext in valid_extensions):
            continue

        try:
            with Image.open(file_path) as img:
                img_hash = imagehash.phash(img)

                if img_hash in hashes:
                    duplicates[img_hash].append(file_path)

                    new_path = os.path.join(duplicates_folder_path, filename)
                    shutil.move(file_path, new_path)
                else:
                    hashes[img_hash] = file_path
                    duplicates[img_hash].append(file_path)
        except (IOError, SyntaxError):
            print(f"Файл {file_path} не является изображением или поврежден.")

    sorted_duplicates = sorted(duplicates.items(), key=lambda item: len(item[1]), reverse=True)

    return sorted_duplicates


def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))


def rename_photos(folder_path, rename_type, base_name=None):
    if not os.path.isdir(folder_path):
        print("Ошибка: указанной папки не существует!")
        return

    files = sorted(
        [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    )

    rename_log = []

    for count, file_name in enumerate(files, start=1):
        file_path = os.path.join(folder_path, file_name)
        ext = os.path.splitext(file_name)[1]

        if rename_type == "1":
            new_name = f"{count}{ext}"
        elif rename_type == "2":
            new_name = f"{generate_random_name()}{ext}"
        elif rename_type == "3":
            if not base_name:
                print("Ошибка: базовое название не может быть пустым!")
                return
            new_name = f"{base_name}_{count}{ext}"
        else:
            print("Ошибка: неверный выбор!")
            return

        new_path = os.path.join(folder_path, new_name)

        os.rename(file_path, new_path)
        rename_log.append(f"{file_name} -> {new_name}")
        print(f"{file_name} -> {new_name}")

    log_file_path = os.path.join(folder_path, "rename.txt")
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write("Лог переименования файлов:\n\n")
        log_file.write("\n".join(rename_log))

    print(f"Переименование завершено! Лог сохранён в файле: {log_file_path}")


def start_duplicate_process():
    folder_path = first_entry_first_frame.get().strip()
    duplicates_folder_path = second_entry_first_frame.get().strip()

    if not folder_path:
        print("Ошибка: Укажите путь к папке с фотографиями!")
        return

    if not duplicates_folder_path:
        print("Ошибка: Укажите путь к папке для дубликатов!")
        return

    if not os.path.exists(folder_path):
        print(f"Ошибка: Папка '{folder_path}' не существует!")
        return

    try:
        sorted_duplicates = find_and_sort_duplicates(folder_path, duplicates_folder_path)
    except Exception as e:
        print(f"Произошла ошибка при поиске дубликатов: {e}")
        return

    report_file_path = os.path.join(duplicates_folder_path, "duplicates.txt")
    with open(report_file_path, "w", encoding="utf-8") as report_file:
        if sorted_duplicates:
            report_file.write("Отчёт о найденных дубликатах:\n\n")
            print("\nДубликаты изображений (отсортированы по количеству):")
            for idx, (img_hash, files) in enumerate(sorted_duplicates, start=1):
                if len(files) > 1:
                    print(f"\nИзображение с хэшем {img_hash} имеет {len(files) - 1} дубликатов:")
                    report_file.write(f"{idx}. Изображение с хэшем {img_hash} имеет {len(files) - 1} дубликатов:\n")
                    for file_idx, file in enumerate(files, start=1):
                        print(f"  - {file}")
                        report_file.write(f"   {file_idx}. {file}\n")
                    report_file.write("\n")
        else:
            print("Дубликаты не найдены.")
            report_file.write("Дубликаты не найдены.\n")

    print(f"Отчёт сохранён в файле: {report_file_path}")


def start_rename_process():
    folder_path = first_entry_second_frame.get().strip()

    if not folder_path:
        print("Ошибка: Укажите путь к папке для переименования!")
        return

    if not os.path.exists(folder_path):
        print(f"Ошибка: Папка '{folder_path}' не существует!")
        return

    rename_type = rename_var.get()
    base_name = second_entry_second_frame.get().strip() if rename_type == "3" else None

    rename_photos(folder_path, rename_type, base_name)


def paste_from_clipboard(entry_widget):
    clipboard_text = root.clipboard_get()
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, clipboard_text)


def insert_text():
    first_entry_first_frame.insert(0, "C:/Users/Example/")
    second_entry_first_frame.insert(0, "C:/Users/Example/")
    first_entry_second_frame.insert(0, "C:/Users/Example/")
    second_entry_second_frame.insert(0, "C:/Users/Example/")


root = tk.Tk()
root.title("PhotoEditor")
root.geometry("350x508")
root.resizable(False, False)


style = ttk.Style()
style.configure("Custom.TFrame", background="#639be6")
style.configure("Custom.TLabel", background="#639be6", font=("Arial", 11, "bold"))
style.configure("Custom.TButton", font=("Arial", 11))
style.configure("Custom.TRadiobutton", background="#639be6", font = ("Arial", 11))

"""Первый фрейм"""
first_frame = ttk.Frame(root, style="Custom.TFrame", relief = "ridge")
first_frame.pack(anchor=tk.NW, fill=tk.X, padx=5)


firs_title_label_first_frame = ttk.Label(first_frame, text = "Поиск Дубликатов", font = ("Arial", 14, "bold"), background = "#05f5f1")
firs_title_label_first_frame.pack(anchor = tk.SW, padx = 5, pady = 5)


first_label_first_frame = ttk.Label(first_frame, text="Введите путь к папке с фотографиями", style="Custom.TLabel")
first_label_first_frame.pack(anchor=tk.SW, padx=5, pady=5)

first_entry_first_frame = ttk.Entry(first_frame)
first_entry_first_frame.pack(anchor=tk.SW, fill=tk.X, padx=5, pady=5)

second_label_second_frame = ttk.Label(first_frame, text="Введите путь к папке для дубликатов", style="Custom.TLabel")
second_label_second_frame.pack(anchor=tk.SW, padx=5, pady=5)

second_entry_first_frame = ttk.Entry(first_frame)
second_entry_first_frame.pack(anchor=tk.SW, fill=tk.X, padx=5, pady=5)

first_button_first_frame = ttk.Button(first_frame, text = "Начать поиск дубликатов", style = "Custom.TButton", command = start_duplicate_process)
first_button_first_frame.pack(anchor = tk.SW, padx = 5, pady = 5)

"""Второй фрейм"""
second_frame = ttk.Frame(root, style="Custom.TFrame", relief = "ridge")
second_frame.pack(anchor=tk.NW, fill=tk.X, padx=5, pady=5)

second_title_label_second_frame = ttk.Label(second_frame, text = "Переименование", font = ("Arial", 14, "bold"), background = "#05f5f1")
second_title_label_second_frame.pack(anchor = tk.SW, padx = 5, pady = 5)

first_label_second_frame = ttk.Label(second_frame, text="Введите путь к папке для переименования", style="Custom.TLabel")
first_label_second_frame.pack(anchor=tk.SW, padx=5, pady=5)

first_entry_second_frame = ttk.Entry(second_frame)
first_entry_second_frame.pack(anchor=tk.SW, fill=tk.X, padx=5, pady=5)

second_label_second_frame = ttk.Label(second_frame, text="Выберите способ переименования", style="Custom.TLabel")
second_label_second_frame.pack(anchor=tk.SW, padx=5, pady=5)

rename_var = tk.StringVar(value="1")

first_radiobutton_second_frame = ttk.Radiobutton(second_frame, text="Нумерация", variable=rename_var, value="1", style="Custom.TRadiobutton")
first_radiobutton_second_frame.pack(anchor=tk.SW, padx=5, pady=5)

second_radiobutton_second_frame = ttk.Radiobutton(second_frame, text="Рандомное название", variable=rename_var, value="2", style="Custom.TRadiobutton")
second_radiobutton_second_frame.pack(anchor=tk.SW, padx=5, pady=5)

third_radiobutton_second_frame = ttk.Radiobutton(second_frame, text="Собственное название", variable=rename_var, value="3", style="Custom.TRadiobutton")
third_radiobutton_second_frame.pack(anchor=tk.SW, padx=5, pady=5)

second_entry_second_frame = ttk.Entry(second_frame)
second_entry_second_frame.pack(anchor=tk.SW, fill=tk.X, padx=5, pady=5)

second_button_second_frame = ttk.Button(second_frame, text="Начать переименование", style="Custom.TButton", command=start_rename_process)
second_button_second_frame.pack(anchor=tk.SW, padx=5, pady=5)

root.mainloop()