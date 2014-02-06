Procédure d'installation Jocondelab
===================================

Prérequis
---------

Les prérequis sont les suivants:
  - python 2.7
  - Base de donnée relationnelle (de préférence Postgres)
  - elasticsearch
  - optionnel : pip (mais recommandé)
  - optionnel : virtualenv (mais recommandé)
  - optionnel: yuglify
  - optionnel: memcached

le fichier requirements.txt donne la liste des dépendances python à installer. Il est directement utilisable par 'pip'.
Une procédure de lancement pourrait être la suivante. Attention, cette procédure est assez théorique sans un accès aux données.

  - création et activation de l'environement virtuel
  - installation des librairies python : pip install -r requirements.txt
  - créer le fichier de configuration à partir du template: `cp src/jocondelab/config.py.tmpl src/jocondelab/config.py`
  - compléter le fichier `src/jocondelab/config.py`.
  - lancer la commande `python manage.py syncdb --migrate`
  - On peut lancer un serveur de développement avec `python manage.py runserver`
