Configuration
=============

Avant de pouvoir utiliser le module, vous allez devoir le configurer.

Assujetissement à la TVA
------------------------

Il est possible que votre société ne soit pas assujetie à la TVA, c'est le cas des associations
par exemple. Si c'est votre cas, vous devez décocher l'option dans les paramètres de votre société :

.. image:: images/config.png

Si vous désactivez cette option, le champ "Taxe" du modèle ne sera pas utilisé, bien qu'il soit affiché, et les montants
TTC seront écrits dans les journaux.

Création des modèles/catégories
-------------------------------

Vous devez ensuite créer vos modèles, pour cela, rendez-vous dans le menu *Comptabilité->Achats->Modèles*. Cliquez sur
le bouton *Créer*. Vous arriverez alors sur un formulaire comme celui-ci :

.. image:: images/model.png

Description des champs
......................

Nom
~~~

Le nom du modèle. Il sera aussi utilisé dans le menu, donc évitez les nom trop longs.

Partenaire
~~~~~~~~~~

Si vous spécifiez un partenaire, il sera associés aux écritures comptables générées. Ce champ est facultatif et sera
souvent laissé vide.

Taxe
~~~~

Définit la taxe qui permet de passer du montant HT au montant TTC. En France, c'est le taux de TVA. Déclarez cette taxe
même si votre société n'est pas assujetie à la TVA , car l'application de celle-ci dépend de la configuration
de votre société (voir ci-dessus). Cela permet d'utiliser les modèles dans tous les types de sociétés.

REF
~~~

Cette référence sera utilisée dans les journaux.

**Astuce**: Vous pouvez mettre un début de référence, comme *Facture EDF n°*, et compléter au moment de déclarer un paiement.

Catégorie
~~~~~~~~~

La catégorie de votre modèle, permet d'organiser ceux-ci dans les menus (voir l'image ci-dessus).

Compte et Position HT
~~~~~~~~~~~~~~~~~~~~~

Définis dans quel compte (et avec quelle position) sera placé le montant HT de l'achat. Cette souplesse vous permet
de déclarer des avoirs.

Compte et Position Taxe
~~~~~~~~~~~~~~~~~~~~~~~

Définis dans quel compte (et avec quelle position) sera placé le montant HT de la taxe.


Comptes, journaux et position TTC
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le compte et le journal du montant TTC dépendra du moyen de paiement. Vous devez donc définir pour chaque moyen
de paiement le compte et le journal associé (exemple dans l'images ci-dessus).

.. note:: Vous ne pourrez utilisez que les moyens de paiement déclarés dans ce champ !

Une fois tous les champs remplis, enregistrez votre modèle et **actualisez la page**.