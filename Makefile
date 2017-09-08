
build: municipios_export.csv.xls provincias_export.csv.xls data.json

municipios_export.csv.xls:
	curl --output municipios_export.csv.xls http://ssweb.seap.minhap.es/REL/frontend/export_data/file_export/export_excel/municipios/all/all

provincias_export.csv.xls:
	curl --output provincias_export.csv.xls http://ssweb.seap.minhap.es/REL/frontend/export_data/file_export/export_excel/provincias/all/all

data.json:
	python main.py > data.json