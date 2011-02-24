Installation
============

Système requis
--------------

Le module Account Purchase a été écrit pour la version 6.0 d'OpenERP. Le moddule *account* sera instalé automatiquement,
ainsi que le module *account_accoutant* qui vous permettra de valider les écritures comptables.

Téléchargement
--------------

Le projet est hébergé sur github à l'adresse suivante : https://github.com/thibautd/openerp-account_purchase .
Vous pouvez soit télécharger la toute dernière version, qui est une version de développement, soit télécharger
les versions dites "taggées", c'est à dire qui ont un numéro. Dans une environnement de production, nous vous
recommandons d'installer une version taggée, qui est un gage de stabilité.

Pour cela, cliquez sur le bouton *Downloads* et cliquez sur le numéro de version le plus élevé. Ensuite, décompressez
l'arhive et récupérez le dossier account_purchase : il contient le module.

Installation
------------

Copiez ensuite le dossier *account_purchase* dans votre dossier contenant les modules d'OpenERP. Vous pouvez aussi,
si vous le souhaitez faire un lien symbolique si vous êtes sous Linux (option conseillée). Normalement, vos modules
se trouvent dans le dossier *addons/* de votre serveur.

Connectez-vous sur OpenERP en administrateur, puis rafraichissez la liste des modules, vous devriez voir un
nouveau module nommé *account_purchase*, validez son installation, puis cliquez sur **Appliquez les mises à jour planifiées**.

Permissions
-----------

Le module utilise les mêmes groupes que le module account :
    - Accounting / Accoutant
    - Accounting / Manager

Permissions du groupe *Accounting / Accountant*:
    - Utiliser/voir les modèles déjà définis
    - Ecrire dans les journaux en utilisant les modèles

Permissions du groupe *Accounting / Manager*:
    - Créer, modifier, supprimer des modèles et leurs catégories
    - Sauvegarder le prix d'un modèle (le champ n'apparait pas pour l'autre groupe)
    - Importer/Exporter les modèles/catégories (uniquement en vue Étendue)

Pensez à attribuer les bons groupes à vos utilisateurs !