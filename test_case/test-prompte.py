import os
import json
from typing import Dict
from voice_prompt import get_voice_assistant_prompt

def main():
    sample_content = {
        "website_analysis": {
            "restaurant_name": "Toulouse Burger",
            "cuisine": "Burgers (Maison/Homemade)",
            "location": "Toulouse, France (Rue Gabriel Péri, quartier Jean Jaurès)",
            "address": "29 RUE GABRIEL PÉRI, 31000, TOULOUSE",
            "phone_number": "05 61 13 11 31",
            "email": "toulouseburgertoulouse@yahoo.com",
            "website": "https://www.toulouse-burger.fr/",
            "description": "Restaurant de burgers maison à Toulouse, proposant des produits de qualité, des recettes originales et des burgers 100% Toulousains.",
            "values": [
                "Produits de qualité",
                "Recettes Originales",
                "Burgers 100% Toulousains"
            ],
            "opening_hours": {
                "Lundi": "12:00–14:00, 19:00–22:00",
                "Mardi": "12:00–14:00, 19:00–22:00",
                "Mercredi": "12:00–14:00, 19:00–22:00",
                "Jeudi": "12:00–14:00, 19:00–22:00",
                "Vendredi": "12:00–14:00, 19:00–22:00",
                "Dimanche": "12:00–14:00, 19:00–22:00"
            },
            "access": {
                "bus": "Lignes L1 L8 14 29 38 arrêt Jean Jaurès, L8 et 14 arrêt place bachelier, lignes 23 et 27 arrêt Colombette.",
                "metro": "Ligne A et B arrêt Jean Jaurès et ligne A arrêt Marengo."
            },
            "services": [
                "Sur place",
                "Livraison (Soir: 19h à 21h45)",
                "À emporter"
            ],
            "payment_methods": [
                "Carte Bleue",
                "Carte Restaurant (Ticket Restaurant)",
                "No cheques",
                "No chèque vacances"
            ],
            "menu": {
                "burgers": [
                    "Le Burger du Moment (Demandez la recette du mois)",
                    "Le Classique (avec ou sans bacon): Steak, Cheddar, Salade, Tomate, Oignons Rouges, Cornichons, Mayonnaise et Ketchup",
                    "Le Fred (création d’un client): Steak, Tomme des Pyrénées, Mayonnaise au Piment d’Espelette Maison, Galette de Pomme de Terre, Confiture de Cerise Noire",
                    "Le Végétarien: Tous nos burgers peuvent se transformer en Végétarien. Nous remplaçons le steak par une des trois galettes végétariennes de votre choix.",
                    "Le Vegan: Galette de Pomme de Terre, Salade, Tomate Sauce au choix, etc.",
                    "Le Chicken: Poulet Pané, Cheddar, Oignons Rouges, Tomate, Salade, Sauce Béarnaise maison",
                    "Le Hot Fire: Steak, Emmental, Salade, Rougail Maison, Sauce Chili Maison",
                    "Le Toulouse Burger: Saucisse de Toulouse, Tomme des Pyrénées, Salade, Tomate, Oignons Frits, Sauce Barbecue"
                ],
                "salads": [
                    "Saint Pierre: Salade, Tomates cerises, Oignons Frits, Œuf au plat, Champignons, Galette de Pommes de terre, Emmental, Poivrons, Avocat",
                    "Gourmande: Salade, Tomates cerises, Œuf au plat, Lardons grillés, Oignons, Noix",
                    "Terroir: Salade, Tomates cerises, Œuf au plat, Oignons Frits, Chicken, Bouchées Camembert"
                ],
                "tapas": [
                    "Frites maison simple",
                    "Frites maison double",
                    "Nuggets",
                    "Chili-Cheese",
                    "Mozzarella Sticks",
                    "Bouchées Camembert",
                    "Wings (Par 6, Par 10)",
                    "Beignets d’oignons"
                ],
                "wraps": [
                    "Fromage: Tortilla de Blé, Salade, Tomate, Cheddar, Emmental, Chèvre, Sauce Roquefort",
                    "Saint Aubin: Tortilla de Blé, Salade, Tomate, Cheddar, Oignons Rouges, Galette de Pomme de Terre, Sauce Béarnaise",
                    "Spicy: Tortilla de Blé, Salade, Tomate, Cheddar, Poitrine Fumée, Sauce Chili, Chicken, Oignons Rouges",
                    "Poulet: Tortilla de Blé, Salade, Tomate, Cheddar, Ketchup, Mayonnaise, Chicken, Oignons Rouges"
                ],
                "desserts": [
                    "Banoffee",
                    "Cookie",
                    "Cookie au beurre de cacahuète",
                    "Brownie"
                ],
                "smoothies_milkshakes": [
                    "Smoothie Fruits Rouges",
                    "Smoothie Exotique",
                    "Milkshake Banane"
                ],
                "glaces": [
                    "Ben and Jerry’s 100ml",
                    "Ben and Jerry’s 500ml",
                    "Glaces artisanales 120ml"
                ],
                "drinks": [
                    "Ice Tea",
                    "Coca",
                    "Coca Zéro",
                    "Orangina",
                    "Jus – Pomme, Orange, Fraise",
                    "Eau plate",
                    "Perrier",
                    "Bière pression artisanale",
                    "Bière en bouteille",
                    "Kumbucha"
                ]
            },
            "menus": {
                "menu_simple": {
                    "description": "Burger + Frites OU 7 Beignets d’oignons OU Medley (3 beignets d’oignon & frites) + Boisson + Sauce",
                    "price_emporter_sur_place": "15,50€",
                    "price_livraison": "17€",
                    "supplement_steak": "3,00€",
                    "supplement_chicken": "3,00€",
                    "supplement_galette": "2,50€",
                    "supplement_frites": "1,50€"
                },
                "menu_kids": {
                    "price_emporter_sur_place": "11,50€",
                    "price_livraison": "13,50€"
                },
                "menu_etudiant": {
                    "description": "Disponible sur place, à emporter et en livraison. Sur présentation uniquement de votre carte étudiante.",
                    "price_emporter_sur_place": "13€",
                    "price_livraison": "15€",
                    "supplement_steak": "3,00€",
                    "supplement_chicken": "3,00€",
                    "supplement_galette": "2,50€",
                    "supplement_frites": "1,50€"
                },
                "burger_simple": {
                    "price_emporter_sur_place": "10€",
                    "price_livraison": "10,50€"
                }
            },
            "sauces": [
                "Roquefort",
                "Chili",
                "Béarnaise",
                "Poivre",
                "Cheddar",
                "Mayo-Espelette",
                "Rougail",
                "Mayo (Classique)",
                "Ketchup (Classique)",
                "Barbecue (Classique)"
            ],
            "ingredients": "Produits frais et locaux, viande de race Aveyronnaise.",
            "halal_option": "Tous nos burgers existent en version Halal en remplaçant la viande par du Chicken Halal.",
            "burger_recipe_contest": {
                "details": "Proposez-nous votre recette de burger! Le staff choisira celle qu’il préfère et le burger portera votre nom ou votre pseudo. La personne gagnante aura son burger offert!"
            },
            "quote_of_the_month": {
                "details": "Amateurs de citation, envoyez-nous votre citation préférée par mail! Vous aurez le plaisir de la découvrir dans le restaurant! Proposez-nous votre citation avec votre prénom. Chaque mois le thème change. Le staff choisira celle qu’il préfère et la personne gagnante aura son burger offert! Pour le mois de Septembre le thème est : La Gourmandise.",
                "example": "\"Pour le burger, pas de rentrée on l'apprécie tout le temps.\" - Julien"
            },
            "legal_information": {
                "company_name": "Toulouse Burger SARL",
                "siret_number": "48191093300011",
                "address": "29 rue Gabriel Péri, 31000 Toulouse",
                "phone": "05 61 13 11 31",
                "email": "toulouseburgertoulouse@yahoo.com"
            },
            "website_creation_and_hosting": {
                "company": "31ème Avenue",
                "address": "15 avenue Occitanie, 31520 Ramonville-Saint-Agne",
                "phone": "05 61 12 23 91",
                "email": "contact@31avenue.com"
            },
            "copyright": "©2024 Toulouse Burger",
            "powered_by": "Sydney",
            "mentions_legales": "Mentions Légales - Tous droits réservés",
            "update_date": "Wed, 15 Jan 2025 15:36:03 +0000"
        }
    }

    result = get_voice_assistant_prompt(sample_content)
    print("Prompt généré:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
