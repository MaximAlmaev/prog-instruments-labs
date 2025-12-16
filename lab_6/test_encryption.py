# tests/test_encryption.py
import pytest
from gamma_encryption import encrypt


    
@pytest.fixture()
def alphabeth():
    return " абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    
def test_encrypt_basic(alphabeth):
    """Базовое шифрование"""
    text = "привет мир"
    gamma = "ключ"
    expected = "ыэжъряюдфэ"  
    assert encrypt(text, gamma, alphabeth) == expected
    
def test_encrypt_empty_text(alphabeth):
    """Шифрование пустого текста"""
    assert encrypt("", "ключ", alphabeth) == ""
    
def test_encrypt_gamma_longer_than_text(alphabeth):
    """Гамма длиннее текста"""
    text = "абв"
    gamma = "абвг"
    assert encrypt(text, gamma, alphabeth) == "бге"
    # Проверить что использована только часть гаммы
    
    
@pytest.mark.parametrize("text,gamma,expected", [
        ("а", "а", "б"),  
        ("я", "a", "ю"),  
        ("а", "я", " "), 
    ])
def test_encrypt_edge_alphabeth(alphabeth, text, gamma, expected):
    """Крайние значения алфавита"""
    assert encrypt(text, gamma, alphabeth) == expected
