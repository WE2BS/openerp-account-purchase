Account Purchase - Documentation
================================

Le module Account Purchase pour OpenERP 6 vous permet gérer plus facilement votre comptabilité concernant les
achats qui ne passent pas forcément par le module purchase, comme par exemple des timbres, votre facture d'eau
ou encore le loyer. Mais ce n'est absolument pas restreint à ces exemples.

Le module est basé sur un système de modèles. Vous définissez un modèle, comme par exemple *Facture EDF*. Dans ce modèle
seront définis les options concernant la comptabilité : les comptes, les journaux, la TVA, etc.

Une fois votre modèle défini, un sous-menu sera automatiquement ajouté dans le menu *Comptabilité->Achats*. En cliquant
sur ce menu (qui a le même nom que votre modèle), vous aurez accès à un wizard (une petite fenêtre) qui vous permettra
de déclarer un achat très simplement. Les journaux seront correctement rempli, mais devront être validés à la main par
un comptable qui peut les vérifier.


Crédits
-------

Ce module a été développé par UIDE/WE2BS, avec l'aide du conseil général des bouches du rhônes.

Index
-----

.. toctree::

    install
    configure
    use
