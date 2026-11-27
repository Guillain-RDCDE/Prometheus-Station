#!/usr/bin/env python3
# Prometheus Station - radio : le garde-fou apres un reglage qui peut couper la station de sa radio (27/11/2026).
#
# Meme regle pour Meshtastic et MeshCore. prometheus-radio :
#   1. prend une sauvegarde, puis arme le garde-fou AVANT d'ecrire le reglage risque (« en cours ») ;
#   2. l'ecriture finie (ou son delai depasse), le garde-fou surveille : la radio repond encore apres RETOUR s
#      -> tout va bien, on oublie ; elle reste muette ATTENTE s -> on demande a l'outil radio (root) de remettre
#      la sauvegarde (fichier commande/radio-restaurer) ;
#   3. la demande ne fait PAS oublier le garde-fou (avant le 27/11, le fichier etait efface avant meme que
#      la demande soit acceptee : une demande perdue = radio perdue). Il reste « restauration demandee » jusqu'au
#      retour de la radio ; toujours muette REDEMANDER s plus tard -> nouvelle demande ; apres MAX_DEMANDES,
#      « abandon » : la page le montre, un humain doit intervenir.
# La demande est rejouable sans danger : l'outil radio ne remet la sauvegarde que si ce garde-fou attend toujours
# cette remise (attend_remise) ; une demande arrivee apres le retour de la radio ne defait pas le nouveau reglage.
# L'etat est dans garde-fou.json (survit a un redemarrage du service, que l'outil radio arrete pendant la remise).
# Python pur : installe dans /usr/local/lib/prometheus/ par 10-radio.sh.
import json, os, secrets, time

import prometheus_commun as pc

ATTENTE = 180         # secondes laissees a la radio pour revenir apres un reglage risque
RETOUR = 20           # la radio doit repondre encore RETOUR s apres l'ecriture (elle redemarre souvent d'abord)
EN_COURS_MAX = 150    # un reglage « en cours » depuis plus longtemps est traite comme ecrit (programme arrete net)
REDEMANDER = 600      # toujours muette 10 min apres une demande de remise : on redemande
MAX_DEMANDES = 3
REESSAI_DEPOT = 60    # la demande n'a pas pu etre deposee : on reessaie une minute plus tard


class GardeFou:
    def __init__(self, chemin, demander, horloge=time.time, dire=print):
        """demander(ordre, contenu) -> True si la demande est deposee pour l'outil radio."""
        self.chemin, self.demander, self.horloge, self.dire = chemin, demander, horloge, dire

    def lire(self):
        g = pc.lire_json(self.chemin, None)
        return g if isinstance(g, dict) and g.get('fichier') else None

    def _ecrire(self, g):
        pc.ecrire_json(self.chemin, g, 0o644)

    def oublier(self):
        try:
            os.remove(self.chemin)
        except OSError:
            pass

    def armer(self, fichier, raison, reseau):
        """Juste avant d'ecrire un reglage risque (fichier : la sauvegarde prise avant)."""
        self._ecrire({'id': secrets.token_hex(6), 'etat': 'surveille', 'en_cours': True, 'heure': self.horloge(),
                      'fichier': fichier, 'raison': raison, 'reseau': reseau, 'demandes': 0})

    def confirmer(self):
        """Le reglage est ecrit (ou peut l'etre : refus, delai depasse, erreur au milieu) : la surveillance commence.
        Meme en cas de refus on surveille : si la radio repond encore, le garde-fou s'efface seul RETOUR s plus tard."""
        g = self.lire()
        if g and g.get('en_cours'):
            g.update(en_cours=False, heure=self.horloge())
            self._ecrire(g)

    def verifier(self, repond):
        """A chaque tour de boucle. repond : la liaison avec la radio est ouverte. Renvoie ce qui s'est passe
        (None, 'revenue', 'demande', 'abandon')."""
        g = self.lire()
        if not g:
            return None
        maintenant = self.horloge()
        age = maintenant - g.get('heure', 0)
        if g.get('en_cours') and age < EN_COURS_MAX:
            return None
        etat = g.get('etat', 'surveille')
        if repond:
            if etat == 'surveille' and age <= RETOUR:
                return None
            self.oublier()
            self.dire('Garde-fou : la radio est revenue' + (' apres la demande de remise de %s' % g['fichier']
                                                            if etat != 'surveille' else ' apres le reglage'))
            return 'revenue'
        if etat == 'surveille':
            if age > ATTENTE and maintenant - g.get('essai', 0) > REESSAI_DEPOT:
                return self._demander(g, maintenant)
        elif etat == 'restauration-demandee' and maintenant - g.get('demande', 0) > REDEMANDER:
            if g.get('demandes', 0) >= MAX_DEMANDES:
                g['etat'] = 'abandon'
                self._ecrire(g)
                self.dire('Garde-fou : la radio ne revient pas apres %d demandes de remise de %s : abandon'
                          % (g.get('demandes', 0), g['fichier']))
                return 'abandon'
            return self._demander(g, maintenant)
        return None

    def _demander(self, g, maintenant):
        self.dire('Garde-fou : la radio ne revient pas, remise de', g['fichier'], 'demandee')
        g['essai'] = maintenant
        if self.demander('restaurer', json.dumps({'fichier': g['fichier'], 'auto': True, 'garde_fou': g.get('id')})):
            g.update(etat='restauration-demandee', demande=maintenant, demandes=g.get('demandes', 0) + 1)
        self._ecrire(g)
        return 'demande'


def attend_remise(g, fichier, ident=None):
    """Pour l'outil radio : une remise demandee par le garde-fou est-elle toujours attendue ?"""
    return (isinstance(g, dict) and g.get('etat') in ('restauration-demandee', 'abandon')
            and os.path.basename(str(g.get('fichier', ''))) == os.path.basename(str(fichier))
            and (not ident or g.get('id') == ident))
