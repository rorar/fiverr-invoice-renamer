import os
import csv
from datetime import datetime
from tkinter import Tk, filedialog

# Benutzerdefinierte Header-Namen
CUSTOM_DATE_HEADER = "Datum"
CUSTOM_NUMBER_HEADER = "Anzahl"

def get_system_language():
    """
    Funktion zur Ermittlung der Systemsprache.
    """
    return os.getenv('LANG', 'en').split('.')[0]

def get_translation(message, lang):
    """
    Funktion zur Bereitstellung von Übersetzungen für die Ausgabemeldungen.
    """
    translations = {
        'en': {
            "select_pdf": "Select PDF files",
            "select_csv": "Select CSV file",
            "already_renamed": "File '{}' has already been renamed, skipping.",
            "rename_success": "File '{}' renamed to '{}'.",
            "no_order_match": "File '{}' does not match any order number in the CSV file, skipping."
        },
        'de': {
            "select_pdf": "PDF-Dateien auswählen",
            "select_csv": "CSV-Datei auswählen",
            "already_renamed": "Datei '{}' wurde bereits umbenannt, wird übersprungen.",
            "rename_success": "Datei '{}' umbenannt zu '{}'.",
            "no_order_match": "Datei '{}' entspricht keiner Bestellnummer in der CSV-Datei, wird übersprungen."
        }
    }
    return translations[lang][message]

def read_csv(file_path):
    """
    Funktion zum Lesen einer CSV-Datei und Extrahieren von Datum und Bestellnummer.
    """
    dates_and_orders = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date_str = row[CUSTOM_DATE_HEADER]
            order_number = row[CUSTOM_NUMBER_HEADER]
            # Datum konvertieren von dd.mm.yyyy zu yyyymmdd
            date_obj = datetime.strptime(date_str, '%d.%m.%Y')
            formatted_date = date_obj.strftime('%Y%m%d')
            dates_and_orders.append((formatted_date, order_number))
    return dates_and_orders

def is_already_renamed(filename):
    """
    Funktion zur Überprüfung, ob die Datei bereits mit dem Datumspräfix umbenannt wurde.
    """
    parts = filename.split(' ', 1)
    if len(parts) == 2:
        date_part = parts[0]
        try:
            datetime.strptime(date_part, '%Y%m%d')
            return True
        except ValueError:
            pass
    return False

def rename_files(directory, dates_and_orders, selected_files, lang):
    """
    Funktion zum Umbenennen von ausgewählten Dateien im ausgewählten Ordner.
    """
    for filename in selected_files:
        if os.path.isfile(os.path.join(directory, filename)):
            if is_already_renamed(filename):
                print(get_translation("already_renamed", lang).format(filename))
                continue
            renamed = False
            for date, order_number in dates_and_orders:
                if order_number in filename:
                    file_name, file_extension = os.path.splitext(filename)
                    new_filename = f"{date} {order_number}{file_extension}"
                    # Datei umbenennen
                    os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
                    print(get_translation("rename_success", lang).format(filename, new_filename))
                    renamed = True
                    break  # Datei wurde umbenannt, daher kann die Schleife abgebrochen werden
            if not renamed:
                print(get_translation("no_order_match", lang).format(filename))

def select_files(lang):
    """
    Funktion zum Auswählen von PDF- und CSV-Dateien über eine GUI.
    """
    root = Tk()
    root.withdraw()  # Verstecke das Hauptfenster

    # PDF-Dateien auswählen
    pdf_file_paths = filedialog.askopenfilenames(
        title=get_translation("select_pdf", lang), filetypes=(("PDF-Dateien", "*.pdf"), ("Alle Dateien", "*.*"))
    )

    # CSV-Datei auswählen
    csv_file_path = filedialog.askopenfilename(
        title=get_translation("select_csv", lang), filetypes=(("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*"))
    )

    return pdf_file_paths, csv_file_path

if __name__ == "__main__":
    # Systemsprache abrufen
    lang = get_system_language()

    # Dateien auswählen
    pdf_files, csv_file = select_files(lang)

    if pdf_files and csv_file:
        # CSV-Datei lesen
        dates_and_orders = read_csv(csv_file)

        # Ordner des ersten ausgewählten PDFs
        directory = os.path.dirname(pdf_files[0])
        
        # Dateien im Ordner umbenennen
        rename_files(directory, dates_and_orders, pdf_files, lang)
