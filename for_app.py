from scripts.text_to_csv import get_data
from scripts.model import get_formulas
from scripts.contexts import table_for_app

def get_all(text,filename,speakers):
    data = get_data(text,filename,speakers)
    final_table = get_formulas(data)
    table_for_app(final_table,text,speakers)