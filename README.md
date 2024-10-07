
# INSTALL
Install python virtual env lib if not exists

```console
virtualenv -p python3 venv ; chmod +x venv/bin/activate
```
# INSTALL LOCAL VENV
Install python local virtual env if not exists

```console
virtualenv -p python3 venv
chmod +x venv/bin/activate
```

Install python lib

```console
source ./venv/bin/activate
pip install -r requirements.txt
```

Modifier l’environnement des variables

```console
cp -r src/.env.example src/.env

```

# HOW IT WORK

Copier les fichiers JSON des conventions collectives nationales à convertir dans le répertoire `resources/kali-data`

retrouver en ligne les fichiers 
https://github.com/SocialGouv/kali-data/tree/master/data

# RUN

Activate python venv
```console
source ./venv/bin/activate
```

## genereration du contenu

```console
python src/scrapping_travail_emploi.py 
```
