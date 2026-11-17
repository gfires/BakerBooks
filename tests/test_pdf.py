import os

from tests._compat import pdf_module


def test_assets_found_and_signature_font_registered():
    assert os.path.exists(pdf_module.FONT_PATH)
    assert os.path.exists(pdf_module.TEMPLATE_PATH)
    assert pdf_module.SIGNATURE_FONT == "AguafinaScript"


def test_parse_cardholder_name_keeps_first_two_words():
    assert pdf_module.parse_cardholder_name("Gavin Firestone (Treasurer)") == "Gavin Firestone"
    assert pdf_module.parse_cardholder_name("Cher") == "Cher"
