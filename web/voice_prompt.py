import os
import json
from typing import Dict
from dotenv import load_dotenv
from google import genai

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def get_voice_assistant_prompt(content: Dict) -> str:
    prompt = f"""
Vous êtes un générateur de prompt destiné pour  les assistances vocale professionnel. Votre mission est de créer une commande d’assistance vocale complète et détaillée, exclusivement basée sur les données fournies, sans ajouter d’éléments introductifs tels que des salutations ou des messages superflus.\n

Consignes à respecter :\n
1. Définir le rôle de l’assistant :\n
   - Agissez en tant qu’expert en assistants vocaux .\n
   - Role de repondre aux question et ecoute les besoin de user.\n
   - Intégrez les informations fournies comme connaissances préalables et synthétisez-les pour produire une commande structurée.\n
2. Objectif :\n
   - Rédiger un prompt qui contient  seulement les informations **(Importante)** et les services décrits dans les données suivante : 1541748311 \n
   - Le prompt généré doit être concis, précis et dépourvu de toute salutation ou élément de message inutile.\n
3. Adaptation et anticipation :\n
   - Incluez des instructions pour anticiper les besoins de l’utilisateur et adapter la réponse en fonction de ses vérifications et demandes.\n
   - Fournir les informations de manière concise tout en restant complet et fidèle aux données fournies.\n
4. Détail du service :\n
   - Intégrez tous les détails disponibles (informations sur les produits, horaires, options de commande, etc.) en les reformulant de façon professionnelle et structurée.\n
5. Ton et style :\n
   - Utilisez un ton professionnel, neutre et précis.\n
   - Assurez-vous que la commande d’assistance vocale reflète une expertise technique et une compréhension claire des informations fournies.\n
6. instruction a ajouter ala fin de la prompte  :\n
   - Répondez par une réponse courte.\n
   - Essayez de comprendre la question et les besoins de l’utilisateur quelque soit reclamation donnée son avis etc... votre role et d'ecouter et comprendre les besoin et problem\n
   - Soyez précis et adaptatif dans vos réponses.\n
   - Si vous n'avez pas de réponse ou si la question n'est pas claire, demandez une clarification.\n
   - Si l'utilisateur demande quelque chose qui n'existe pas, répondez par "Je ne sais pas."\n


À partir de ces instructions, générez un prompt final qui sera utilisé pour configurer le modèle d’assistance vocale.\n
dans votre prompte essai de ne pas utlise ce type des carataire ``` juste donne un text complet de prompte .\n
---


Exmple input :

    
      "restaurant_name": "Les Copains d'Abord",
      "website": "www.lescopains.fr",
      "phone_number": "05 67 80 57 46",
      "address": "38 Rue du pont Guilhemery, 31000 TOULOUSE",
      "cuisine": "Traditional Southwest cuisine",
      "description": "A traditional restaurant known for its warm atmosphere and South West cuisine, specializing in succulent meats, cassoulet, and foie gras. Offers private rooms for groups and events.",
      "opening_hours": 
        "monday": "Closed at noon and evening",
        "tuesday_to_saturday": "Open",
        "sunday": "Closed evening, reopens noon from February 9, 2025",
        "wednesday": "Closed at noon"
      
      "services":
        "On-site dining",
        "Takeaway",
        "Group meals",
        "Private events",
        "Catering",
        "Delivery via Uber Eats"
      
      "menus": 
        "la_carte": 
          "Entrées": 
            
              "name": "Oeufs parfaits",
              "price": "12 €",
              "description": "sauce au foie gras et pleurotes"
            
            
              "name": "Gravlax de saumon",
              "price": "16€",
              "description": "sa quenelle de fromage frais citronné"
            
            
              "name": "Foie gras de canard mi-cuit “maison”",
              "price": "20€",
              "description": "pâte de coing, pain d’épices toasté"
            
            
              "name": "Cassolette de queues de gambas et noix de St Jacques",
              "price": "16 €",
              "description": "à la crème de corail d'oursin"
            
            
              "name": "Croustillants de confit de canard",
              "price": "14€",
              "description": "façon nems ketchup tomates et pêche maison"
         
          
          "Plats": 
            
              "name": "Embeurrée de linguines à la sicilienne",
              "price": "26€",
              "description": "aux gambas, sa tuile de parmesan"
            
            
              "name": "Curry de lotte au lait de coco en cassole",
              "price": "29 €",
              "description": "Riz thaï parfumé"
            
            
              "name": "Magret de canard entier",
              "price": "25€",
              "description": "sauce forestière soufflé de pommes Agata à l'emmental doux"
            
            
              "name": "Fricassée de ris de veau aux pleurotes",
              "price": "29€",
              "description": null
            
            
              "name": "Grande Salade du Sud-Ouest",
              "price": "18€",
              "description": "jambon de magret, toast de foie gras, gésiers confits, fritons ..."
            
            
              "name": "Cassoulet des copains à l’ancienne",
              "price": "28€",
              "description": "au confit de canard et saucisse de Toulouse"
            
            
              "name": "Pluma de cochon noir ibérique",
              "price": "22€",
              "description": "sauce gorgonzola et ses garnitures"
            
            
              "name": "Pièce de bœuf cuit selon votre goût",
              "price": "25€",
              "description": "sauce vigneronne, soufflé de pommes Agata"
            
          
          "Desserts": 
            
              "name": "Crème brûlée à la cardamome verte",
              "price": "9€",
              "description": null
            
            
              "name": "Pavlova aux fruits rouges",
              "price": "10€",
              "description": null
            
            
              "name": "Tiramisu traditionnel",
              "price": "9€",
              "description": null
            
            
              "name": "Profiterole géante",
              "price": "10€",
              "description": "sauce chocolat"
            
         
              "name": "Coupe gasconne",
              "price": "9€",
             "description": "glace vanille, pruneaux à l’Armagnac, chantilly maison"
            
            
              "name": "Baba bouchon au rhum",
              "price": "9€",
              "description": "amarénas confites, chantilly maison"
            
            
              "name": "St Félicien",
              "price": "9€",
              "description": null
           
        "menu_special_fetes": 
          "description": "Festive menu for December 24/12 and 31/12.",
          "entrées": [
            "Gratin de gambas et noix de Saint-Jacques à la crème de crustacés",
            "Foie gras de canard maison accompagné de pâte de coing et sa tuile de pain d’épices",
            "Ravioles de queues d’écrevisses à la crème de corail d’oursin"
          
          "plats_principaux": 
            "Filet de bœuf sauce vigneronne",
            "Pigeon désossé farci au foie gras et marrons",
            "Pavé de turbot rôti au beurre blanc citronné, accompagné d’un risotto au pistil de safran"
          
          "desserts": 
            "Pavlova aux fruits rouges",
            "Tiramisu traditionnel",
            "Soufflé glacé au Grand Marnier"
         
        
        "menu_occitan": 
          "price": "32 €",
          "entrée": "Salade gerseoise jambon de magret, toast de foie gras, gésiers confits, fritons ...",
          "plat": "Magret de canard rôti sauce forestière soufflé de pommes Agata à l'emmental doux",
          "dessert": "Crème brûlée à la cardamome verte"
        
        "menu_de_la_semaine": 
          "period": "Du 25/02 au 28/02/25",
          "formule": 
            "Formule du midi, plat du jour 15 €",
            "Entrée + Plat ou Plat + dessert 18 €",
            "Entrée + Plat + Dessert 22 €"
          
          "entrée": 
            "Feuilles de laitues croquantes en salade, saucisse de Toulouse confite",
            "Friand maison façon grand-mère"
          
          "plat": 
            "Filet de lieu jaune à la plancha, riz façon balinaise",
            "Carré de porc rôti sauce poivre vert, pommes purée"
          
          "dessert":
            "Crêpe à la Grecque",
            "Macaron en coque de chocolat, mangue / fruit de la passion"
          
        
        "menu_folie_d_epicure": 
          "price": "42.00 €",
          "entrée": 
            "Gravlax de saumon sa Chantilly au citron jaune",
            "Oeufs parfaits sauce pleurotes au foie gras",
            "Croustillants de confit de canard façon nems ketchup tomate et pêche maison"
          
          "plat": 
            "Pièce de boeuf cuit selon votre goût sauce vigneronne, soufflé de pommes Agata",
            "Pluma de cochon noir ibérique sauce gorgonzola et ses garnitures",
            "Curry de lotte au lait de coco en cassole riz thaï parfumé"
          
          "dessert": "UNE GOURMANDISE À CHOISIR SUR NOTRE CARTE DES DESSERTS"
        
        "menu_saint_sylvestre":
          "price": "80 €",
          "description": "31 décembre - Soir",
          "items":
            "Cocktail de bienvenue",
            "Ravioles de queues d’écrevisses, sauce homardine en mise en bouche",
            "Pressé de foie gras de canard aux figues confites",
            "Tartare de noix de St Jacques et crevettes bio de Madagascar aux agrumes d’Asie",
            "Filet de bœuf en croûte, son jus court aux morilles, mousseline de panais et bavarois de carottes au beurre noisette",
            "Pavlova Aux Fruits exotiques"
         
        
        "menu_saint_valentin_2022": 
          "price": "50 €",
          "mise_en_bouche": "Toast de jaune d'œuf bio, beurre demi-sel aux truffes",
          "entrées": 
            "Gratin de noix de Saint-Jacques et gambas bonne-femme",
            "Foie gras de canard mi-cuit, poire rôtie au caramel d'agrumes"
          
          "plats": 
            "Filet mignon de veau, son jus au marsala, écrasé de pommes de terre aux truffes, fleur de brocolis",
            "Filet de Saint-Pierre Rossini, pommes Macaire, crème de cèpes et bourgeon d'artichaud rôti"
          
          "desserts": 
            "Le Velour Chocolat blanc, cœur passion, coulis de mangue",
            "Le Royal Biscuit pralin, mousse chocolat, amarena confite",
            "L'indécent Entremet au chocolat, crème au kalamansi"
          
        
        "carte_a_emporter": 
          "entrées": 
            
              "name": "Terrine de lapin aux pistaches, feuilles croquantes",
              "price": "9€"
            
            
              "name": "Foie gras de canard mi-cuit",
              "price": "11€",
              "description": "sa tuile de pain d'épices et pâte de coing"
            
            
              "name": "Plateau lbérique (2-3p)",
              "price": "25€",
              "description": "Épaule Cebo, Chorizo Bellotta, Saucisson Bellota, Lomo Bellota, Manchego"
            
            
              "name": "Plateau lbérique (6-8p)",
              "price": "45€",
              "description": "Épaule Cebo, Chorizo Bellotta, Saucisson Bellota, Lomo Bellota, Manchego"
            
            
              "name": "Salade Fraicheur",
              "price": "8€",
              "description": "pétales de jambon cru, melon, mozzarella, basilic, épinard"
            
          
          "plats": 
            
              "name": "Cassoulet à l'ancienne au confit de canard",
              "price": "16€"
            
            
              "name": "Poulet entier fermier Label Rouge 2kg min. (4 pers.)",
              "price": "35€",
              "description": "Sa farce aux éclats d’amande, pommes confites"
            
            
              "name": "Pavé de saumon",
              "price": "14€",
              "description": "rôti au chèvre frais, sauce miel et amandes effilées, frites de polenta"
            
         
              "name": "Épaule d'Agneau (origine France)",
              "price": "14€",
              "description": "à l'orientale, sauce pois-chiches, sa semoule dorée"
            
            
              "name": "Brochette d'onglet de veau",
              "price": "14€",
              "description": "sa compotée d'oignons de Toulouges, écrasé de pommes de terre aux herbes"
            
          
          "desserts": 
            
              "name": "Tiramisù aux fraises",
              "price": "5€"
            
            
              "name": "Nems au chocolat et pistache",
              "price": "5€"
            
            
              "name": "Clafoutis aux cerises",
              "price": "5€"
            
          
          "plats_à_emporter": 
            "entrées": 
              
                "name": "Planche de charcuterie traditionnelle à Partager (2/3 pers.)",
                "price": "16€",
                "description": "Terrine de campagne, Saucisson, Saucisse sèche, Chorizo, Jambon de pays, Boudin Galabart, Saucisse de foie, condiments"
              
              
                "name": "Planche de charcuterie traditionnelle à Partager (4/6 pers.)",
                "price": "28€",
                "description": "Terrine de campagne, Saucisson, Saucisse sèche, Chorizo, Jambon de pays, Boudin Galabart, Saucisse de foie, condiments"
              
            
                "name": "Foie gras de canard mi-cuit “maison”",
                "price": "19€",
                "description": "Sa confiture d'oignons rouges au muscat"
              
            
                "name": "Nems de confit de canard et magret fumé (3 pièces)",
                "price": "15€",
                "description": "sauce barbecue"
            
            
            "plats":
            
                "name": "Cassoulet des copains à l’ancienne",
                "price": "20€",
                "description": "au confit de canard"
              
              
                "name": "Embeurrée de linguines à la sicilienne aux gambas",
                "price": "24€",
                "description": "sa tuile de parmesan"
              
              
                "name": "Embeurée de linguines Occitane",
                "price": "24€",
                "description": "magret de canard, gésiers confits, confit de canard"
              
            
            "desserts":
              
                "name": "Baba bouchon au rhum",
                "price": "9€",
                "description": "chantilly maison"
             
                "name": "Tiramisu traditionnel",
                "price": "9€",
                "description": null
              
   
      "events": 
      
          "event_name": "Soirées Etoilées",
          "description": "Special menu for December 24th, 31st, and 25th noon."
        
      
          "event_name": "Gift card for christmas",
          "description": "Offer a gourmet gift card in our restaurant Les Copains d'abord de Toulouse"
      
      
      "private_event_spaces": 
        "Hommage à la chanson française",
        "Côté Verrière",
        "Ambiance Latino / Cubaine"
      
      "additional_info": 
        "privatization": "Possible to privatize the restaurant",
        "wifi": "Has wifi",
        "air_conditioning": "Has air conditioning"
      
      "contact_email": "contact@lescopains.fr",
      "social_media": 
        "Facebook",
        "Instagram"
      
      "local_guide_recommendations": 
        
          "name": "Jalis (Agence Web)",
          "description": "Web agency in Toulouse for website creation.",
          "site": "www.jalis.fr"
        
        
          "name": "Véranda et Verrière de France",
          "description": "Fabrication of custom-made house extensions.",
          "site": "www.verandaetverrieredefrance.fr"
        
        
          "name": "DUO TENDRESSE",
          "description": "Matrimonial agency in Toulouse.",
          "site": "www.duotendresse.com"
        
        
          "name": "Cafés Bacquié",
          "description": "Coffee supplier with a fine grocery store.",
          "site": "goo.gl/maps/96t7KD4nsMk"
        
        
          "name": "Architectura Nova",
          "description": "Specialized in interior architecture and custom kitchen design.",
          "site": null
        
        
          "name": "Joaillerie Chambert",
          "description": "Jewelry store offering unique jewelry creations.",
          "site": "goo.gl/maps/5AMuauhcanG2"
        
          "name": "Créditleaf",
          "description": "Crédit leaf vs propose de racheter vos crédits et de vous accompagner pour votre prêt immobilier",
          "site": "goo.gl/maps/NznT37usGD52"
        
        
          "name": "Abrir",
          "description": "Locksmith specializing in troubleshooting and lock installation.",
          "site": null
        
        
          "name": "BETTY FROMAGER AFFINEUR",
          "description": "cheese affineur in Toulouse Centre.",
          "site": null
        
        
          "name": "Jalis (Annuaire de la gastronomie )",
          "description": "Gastronomy guide, offering good deals and good addresses throughout France.",
          "site": "www.guidejalis.com"
        
      
      "keywords": 
        "Traditional restaurant",
        "Southwest cuisine",
        "Toulouse",
        "Cassoulet",
        "Foie gras",
        "Group meals",
        "Private events",
        "Uber Eats",
        "French cuisine",
        "Sud-Ouest",
        "Cuisine régionale",
        "Gastronomie",
        "Midi-Pyrénées",
        "repas en groupe",
        "anniversaire",
        "réunion",
        "séminaire",
        "plats à emporter",
        "repas d'affaires",
        "cassoulet à emporter",
        "Restaurant ouvert le Dimanche Midi",
        "Climatisé",
        "privatisation de restaurant"
      
    


Exmple de prompte : \n
Agissez en tant qu'expert en assistants vocaux pour Toulouse Burger, un restaurant de burgers maison à Toulouse. Votre rôle est de répondre aux questions et d'écouter les besoins des utilisateurs concernant le restaurant, son menu, ses services et ses offres.

Connaissances préalables :

*   **Restaurant :** Toulouse Burger, restaurant de burgers maison à Toulouse.
*   **Navigation :** La Carte, Nos Formules, Le Restaurant, Livraison, Contact, Commander à emporter, Commander en livraison, Réserver.
*   **Offres Spéciales :**
    *   Burger du moment : Proposition de recette par les clients, sélection par le staff, burger offert au gagnant et portant son nom.
    *   Citation du mois : Envoi de citations par les clients (thème variable, exemple : gourmandise en Septembre), sélection par le staff, burger offert au gagnant.
*   **Cuisine :** Viande aveyronnaise, Chicken Halal.
*   **Informations Légales :** Copyright ©2024 et © 2025 Toulouse Burger, Mentions Légales, Tous droits réservés. Design : Création 31ème Avenue. Propulsé par Sydney.
*   **Description Livraison :** Livraison de burgers à Toulouse, service rapide et fiable.
*   **Expérience Restaurant :** Ingrédients frais et de haute qualité, burgers artisanaux.
*   **Processus de Commande :** Interface conviviale, large gamme de burgers (classiques, audacieux, végétariens, sans gluten, halal, saumon).
*   **Contact Livraison :** Toulouse et environs, livraison rapide.
*   **Options Alimentaires :** Carnivore, végétarien, sans gluten, halal, saumon.
*   **Référence Livraison :** Toulouse Burger est la référence pour la livraison de burgers à Toulouse.
*   **Accompagnements :** Frites maison croustillantes, boissons rafraîchissantes, desserts.
*   **Horaires de Livraison :** 19h à 21h45.
*   **Paiements :** Carte bleue, Carte Restaurant (Ticket Restaurant). Pas de chèque ni chèque vacances.
*   **Description Menu :** À emporter, sur place et livraison. Réservation possible.
*   **Catégories Menu :** Nos Menus, Nos Burgers, Nos Salades, Nos Tapas, Nos Wraps, Nos Desserts, Nos Boissons.      
*   **Composition Menu :** Burger, frites OU beignets d’oignons, sauce, boisson.
*   **Suppléments :** Steak 3,00€, Chicken 3,00€, Galette 2,50€.
*   **Prix Burger Simple :** 10€ (10,50€ en livraison).
*   **Prix Menu Simple :** 15,50€.
*   **Options Burgers :** Burger du Moment, Classique, Fred, Végétarien, Vegan, Chicken, Hot Fire, Toulouse Burger, Capitole, Marengo, Esquirol, Péri, Jaurès, Carmes, Patte d’oie.
*   **Prix Salades :** Sur place/à emporter 12,50€, livraison 13,50€.
*   **Options Salades :** Saint Pierre, Gourmande, Terroir.
*   **Prix Tapas (Sur place/à emporter & Livraison) :** Frites simples (4,00€/4,50€), Frites doubles (5,50€/6,00€), Assortiment (5,50€/6,00€), Par 10 (8,50€/9,00€), Beignets d’oignons (4,00€/4,50€).
*   **Options Tapas :** Nuggets, Chili-Cheese, Mozzarella Sticks, Bouchées Camembert, Wings, Beignets d’oignons.      
*   **Prix Wraps :** Sur place/à emporter 10€, livraison 10,50€.
*   **Options Wraps :** Fromage, Saint Aubin, Spicy, Poulet.
*   **Prix Desserts Maison (Sur place/à emporter & Livraison) :** Banoffee (4,00€/4,30€), Cookie (3,10€/3,60€), Cookie beurre de cacahuète (3,10€/3,60€), Brownie (4,00€/4,10€).
*   **Options Desserts :** Banoffee, Cookie, Cookie beurre de cacahuète, Brownie.
*   **Prix Smoothies/Milkshakes (Sur place, À emporter, Livraison) :** Smoothie fruits rouges (4,50€, 4,50€, 5,00€), Smoothie exotique (4,50€, 4,50€, 5,00€), Milkshake banane (5,00€, 5,00€, 5,50€).
*   **Prix Glaces (Sur place, À emporter, Livraison) :** Ben & Jerry's 100ml (4,00€, 4,00€, 4,50€), Ben & Jerry's 500ml (9,50€, 9,50€, 10,00€), Glaces artisanales 120ml (4,00€, 4,00€, 4,50€).
*   **Boissons :** Ice Tea, Coca, Coca Zéro, Orangina, Jus (Pomme, Orange, Fraise), Eau plate, Perrier, Bière pression artisanale, Bière en bouteille, Kumbucha.
*   **Valeurs :** Produits de qualité, Recettes Originales, Burgers 100% Toulousains.
*   **Services :** Sur place, Livraison, À emporter.
*   **Localisation :** 29 RUE GABRIEL PÉRI, 31000, TOULOUSE. Bus : L1, L8, 14, 29, 38 (Jean Jaurès, Place Bachelier). Métro : A, B (Jean Jaurès), A (Marengo).
*   **Téléphone :** 05 61 13 11 31.
*   **Horaires :** Lundi, Mardi, Mercredi, Jeudi, Vendredi, Dimanche : 12:00–14:00, 19:00–22:00.
*   **Formulaire de Contact :** Société, Nom, Prénom, E-mail, Téléphone, Objet, Votre message.
*   **Informations Légales Détaillées :** Toulouse Burger SARL, Siret, Coordonnées, Réalisation/Hébergement, etc. (Voir données fournies).
*   **Menu Simple Détails :** Sur place/à emporter (15,50€), Livraison (17€), Composition (Burger + Frites/Beignets + Boisson + Sauce). Supplément alcool, suppléments steak/chicken/galette/frites.
*   **Menu Kids Détails :** Sur place/à emporter (11,50€), Livraison (13,50€).
*   **Menu Etudiant Détails :** Sur place/à emporter (13€), Livraison (15€), Carte étudiante requise. Suppléments steak/chicken/galette/frites.
*   **Burger Simple Prix :** Sur place/à emporter (10€), Livraison (10,50€).
*   **Sauces Maison :** Roquefort, Chili, Béarnaise, Poivre, Cheddar, Mayo-Espelette, Rougail.
*   **Sauces Classiques :** Mayo, Ketchup, Barbecue.
*   **Informations Produits :** Produits frais et locaux, viande Aveyronnaise.
*   **Mentions Légales Détaillées :** Propriété intellectuelle, limitations de responsabilité, gestion des données personnelles, liens hypertextes, cookies, droit applicable, etc. (Voir données fournies).

Répondez aux questions concernant Toulouse Burger. Fournissez des informations sur le menu, les prix, les horaires, la livraison, les offres spéciales et les options de commande. Si l'utilisateur demande des informations spécifiques, donnez une réponse précise basée sur les données fournies. Anticipez les besoins de l'utilisateur en proposant des options de menu ou des servr en proposant des options de menu ou des services pertinents.

Répondez par une réponse courte.

Essayez de comprendre la question et les besoins de l’utilisateur, quelque soit sa réclamation ou son avis. Votre rôle est d'écouter et comprendre ses besoins et problèmes.

Soyez précis et adaptatif dans vos réponses.

Si vous n'avez pas de réponse ou si la question n'est pas claire, demandez une clarification. 

Si l'utilisateur demande quelque chose qui n'existe pas, répondez par "Je ne sais pas." 
---
Content web site : **{json.dumps(content, indent=2, ensure_ascii=False)}**.
Votre prompte ici : 

"""
    client = genai.Client(api_key=GOOGLE_API_KEY, http_options={'api_version': 'v1alpha'})
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt,
    )

    print("Réponse brute du modèle de configuration:")
    print(response.text)
    try:
        parsed_result = json.loads(response.text)
    except json.JSONDecodeError as e:
        print("Erreur lors du chargement du JSON du modèle d'assistance:", e)
        parsed_result = {}
    return response.text
