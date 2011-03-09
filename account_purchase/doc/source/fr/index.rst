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

Le module Account Purchase a été développé pour les besoin du monde associatif et en particulier pour
l'association *Une Idée derrière l'Ecran*.

L'association *Une Idée Derrière l'Ecran* a recu une subvention de fonctionnement du Conseil général
des bouches du Rhône (CG13) pour le développement du module.

Les participants à la création du modules sont :

* `Association Une Idée Derrière l'Ecran`_ : Dévelopement du module
* `SARL WE2BS`_ : Participation au éléments comptable du produit (aide au cahier des charges, gestion comptable,
suivis du bon comportement du produit.).

.. _Association Une Idée Derrière l'Ecran: http://www.idee-ecran.org
.. _SARL WE2BS: http://www.we2bs.com

Index
-----

.. toctree::

    install
    configure
    use
