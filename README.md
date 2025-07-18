# AELF - Lectures du jour (Serveur)

AELF - Lecture du jour est une application toute simple qui accompagne chaque jour des dizaines de milliers de chrétiens francophone dans leur prière.

La cerise sur le gâteau ? Comme l'Église est d'abord une communauté, qu'elle chérie la liberté: cette application est OpenSource. Ça veut dire que vous pouvez l'utiliser, l'améliorer, l'inspecter sous toutes ses coutures ou même la copier.

La fonction "confession" du code n'est pas (encore) implémentée.

## Comment contribuer ?

 - en installant l'application (https://play.google.com/store/apps/details?id=co.epitre.aelf_lectures)
 - en rejoignant le programme "bêta" (https://play.google.com/apps/testing/co.epitre.aelf_lectures)
 - en contribuant au code de l'application (https://github.com/HackMyChurch/aelf-dailyreadings/pulls)
 - en contribuant aux tests, rapport d'erreur et échanges sur Github (https://github.com/HackMyChurch/aelf-dailyreadings/issues)
 - en améliorant les textes de présentation
 - en en parlant autour de vous

## Commencer à coder

Ce dépôt de contient la partie "serveur" de l'application. C'est la partie qui tourne une machine sur laquelle vient se connecter l'application. C'est elle qui est en première ligne pour effectuer les mises en formes les plus importantes et surtout, s'assurer que l'application reste toujours disponible, même si, parfois, le serveur d'AELF tousse un peu ;).

C'est aussi la partie la plus ingrate si vous commencer à coder: elle ne produit pas grand chose de visible. Si vous souhaiter contribuer, envoyer moi un mail, je me ferait un plaisir de vous aiguiller.

Prêt ? On attaque.

### Récupérer le code

Tout d'abord, assurez vous de bien avoir ``git`` et ``docker`` sur votre machine. Puis, c'est aussi simple que:

```console
git clone https://github.com/HackMyChurch/aelf-dailyreadings-server.git
cd aelf-dailyreadings-server
```

Puis installer les dépendances Python:

```console
python3 -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

Et enfin, manuellement lancer le serveur en local:

```console
AELF_STATUS_DAYS_TO_MONITOR=0 AELF_DEBUG=1 ./server.py
``` 

Votre serveur tourne à présent sur le port 4000 de votre machine. Pour avoir un état de la synchronisation, rendez-vous sur http://0.0.0.0:4000/status.html

### Faire tourner les tests

Vous pouvez aussi faire tourner les tests automatiques (et, oui, on aime faire les choses bien !)

```console
pip install -r requirements-dev.txt
pytest
```

Les tests fonctionnent avec une copie des données. Si vous ajoutez un nouveau test et avez besoin de nouvelles données, vous pouvez les télécharger automatiquement
en activant la variable d'environnement ``AELF_DEBUG=1``:

```console
AELF_DEBUG=1 nosetests
```

## Licence

MIT, 2025 Jean-Tiare Le Bigot <support@epitre.co>
