from files_work import *
import json
# Тесты для функций read_txt_file/ write_txt_file
def test_read_txt_file_success(tmp_path):
    """Тест успешного чтения txt файла"""
    test_content = "Hello, World!\nThis is a test."
    d = tmp_path / "test_text_path"
    d.mkdir() 
    p = d / "text.txt"
    write_txt_file(p , test_content)
    assert read_txt_file(p) == test_content

def test_read_json_file_success(tmp_path):
    """Тест успешного чтения JSON файла"""
    test_content = {
        "message": "Hello, World!",
        "test": True,
        "count": 100
    }
    
    d = tmp_path / "test_json_path"
    d.mkdir() 
    p = d / "data.json"
    

    with open(p, 'w', encoding='utf-8') as f:
        json.dump(test_content, f)
    loaded_content = read_json_file(p)
    
    assert loaded_content == test_content