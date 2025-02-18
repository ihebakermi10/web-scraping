from pydantic import BaseModel, Field
from typing import Optional

class Classe(BaseModel):
    identite_site: Optional[str] = Field(
        default=None,
        description="Nom du site, description et catégorie générale. Laissez à None si non disponible."
    )
    catalogue_produits: Optional[str] = Field(
        default=None,
        description="Détails des produits ou menus (noms, caractéristiques, prix, variantes, etc.). Laissez à None si non applicable."
    )
    offres_promotionnelles: Optional[str] = Field(
        default=None,
        description="Offres, promotions et réductions disponibles. Laissez à None si non applicable."
    )
    services_proposes: Optional[str] = Field(
        default=None,
        description="Services ou fonctionnalités principales offerts (commande en ligne, livraison, réservation, etc.). Laissez à None si non applicable."
    )
    infos_contact: Optional[str] = Field(
        default=None,
        description="Informations de contact (email, téléphone, formulaire, etc.). Laissez à None si non disponible."
    )
    horaires: Optional[str] = Field(
        default=None,
        description="Horaires d'ouverture ou disponibilité du service. Laissez à None si non applicable."
    )
    reseaux_sociaux: Optional[str] = Field(
        default=None,
        description="Liens et informations des réseaux sociaux. Laissez à None si non disponibles."
    )
    contenu_principal: Optional[str] = Field(
        default=None,
        description="Résumé du contenu principal du site (articles, vidéos, etc.). Laissez à None si non applicable."
    )
    blog_articles: Optional[str] = Field(
        default=None,
        description="Informations sur les articles ou le blog du site. Laissez à None si non applicable."
    )
    jeux_info: Optional[str] = Field(
        default=None,
        description="Détails spécifiques aux sites de jeux (jeux proposés, mises à jour, etc.). Laissez à None si non applicable."
    )
    localisation: Optional[str] = Field(
        default=None,
        description="Localisation ou adresse physique. Laissez à None si non disponible."
    )
    mentions_legales: Optional[str] = Field(
        default=None,
        description="Informations légales et mentions obligatoires. Laissez à None si non applicables."
    )
    moyens_paiement: Optional[str] = Field(
        default=None,
        description="Modes de paiement acceptés. Laissez à None si non disponibles."
    )
    evenements: Optional[str] = Field(
        default=None,
        description="Événements ou actualités liés au site. Laissez à None si non applicables."
    )
