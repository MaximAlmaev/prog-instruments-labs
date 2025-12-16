import json


def read_txt_file(filename: str) -> str:
    """
    Считывает данные из txt файла
    :param filename: название файла в формате txt
    :return: считанные данные из файла
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError as exc:
        print("File not found, ", exc)
    except PermissionError as exc:
        print("File access denied, ", exc)
    except Exception as exc:
        print("Error reading from file, ", exc)


def write_txt_file(filename: str, text: str) -> None:
    """
    Записывает данные в txt файл
    :param filename: название файла в формате txt
    :param text: данные для записи в файл
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(text)
    except PermissionError as exc:
        print("File access denied, ", exc)
    except Exception as exc:
        print("Error reading from file, ", exc)


def read_json_file(filename: str) -> dict:
    """
    Считывает данные из json файла
    :param filename: название файла в формате json
    :return: считанные данные из файла
    """
    try:
        if filename is not None:
            with open(filename, "r", encoding="utf-8") as file:
                    data = json.load(file)
    except PermissionError as exc:
        print("File access denied, ", exc)
    except Exception as exc:
        print("Error reading from file, ", exc)
    return data