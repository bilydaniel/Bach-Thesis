Systém byl implementován pomocí Python (3.6.9). Aplikace je dostupná na adrese http://athena1.fit.vutbr.cz:8078/. Pro úpravy byla použita administrátorská stránka Django (http://athena1.fit.vutbr.cz:8078/admin). Přihlašovací jméno je xbilyd01 a heslo je adminadmin.


Potřebné knihovny (v závorce je verze):
	-beautifulsoup4 (4.8.2)
	-certifi (2020.6.20)
	-django (3.0.3)
	-nltk (3.4.5)
	-numpy (1.18.1)
	-pandas (1.0.5)	
	-psycopg2 (2.8.4)
	-pycld3 (0.20)
	-requests (2.23.0)
	-scikit-learn (0.22.1)
	-scipy (1.4.1)
	-selenium (3.141.0)
	-spacy (2.2.3)
	-sqlite (3.31.1)
	-ufal-morphodita (1.9.2.3)
	-unidecode (1.1.1)
	-urllib3 (1.25.7)
	-torch (1.3.1)
	-torchtext (0.4.0)


Databáze:
	Databáze je vytvořena na serveru athena1 (http://athena1.fit.vutbr.cz/phppgadmin/) na portu 5432. 


Po nainstalování všech potřebných knihoven a připojení se k existující databázi (popřípadě vytvoření své vlastní) je potřeba provést migrace příkazy "python manage.py makemigrations" a "python manage.py migrate". Po úspěšné migraci stačí už jen spustit server příkazem "python manage.py runserver".









