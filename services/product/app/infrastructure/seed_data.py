from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from infrastructure.models import DishModel, RestaurantModel

RESTAURANT_SEED = [
    {
        "name": "Qazaq Et House",
        "description": "Traditional Kazakh comfort food with beshbarmak, kuyrdak, and rich broth classics.",
        "address": "Abylai Khan Avenue 121, Almaty",
        "cuisine_type": "Kazakh",
        "rating": 4.9,
        "dishes": [
            ("Beshbarmak Signature", "Hand-cut noodles with slow-cooked horse meat and onion broth.", 15.9, "Traditional"),
            ("Kazy Platter", "House-cured kazy with pickled onions and warm baursaks.", 12.4, "Traditional"),
            ("Mini Baursak Basket", "Golden fried baursaks served with honey butter.", 5.2, "Bread"),
        ],
    },
    {
        "name": "Alatau Doner & Grill",
        "description": "Fast casual grill with shawarma, skewers, and smoky street-food energy.",
        "address": "Tole Bi Street 87, Almaty",
        "cuisine_type": "Street Food",
        "rating": 4.7,
        "dishes": [
            ("Chicken Doner Wrap", "Juicy chicken doner, fries, garlic sauce, and fresh salad.", 8.9, "Wrap"),
            ("Lamb Shashlik Set", "Chargrilled lamb skewers with onion salad and lavash.", 11.8, "Grill"),
            ("Ayran Chill", "Cold salty ayran to balance the grill heat.", 2.3, "Drink"),
        ],
    },
    {
        "name": "Nomad Noodles",
        "description": "Pan-Asian bowls and noodle boxes tuned for quick lunches and late-night cravings.",
        "address": "Mangilik El Avenue 54, Astana",
        "cuisine_type": "Asian Fusion",
        "rating": 4.6,
        "dishes": [
            ("Beef Lagman Bowl", "Pull noodles with peppery beef strips and vegetables.", 10.5, "Noodles"),
            ("Spicy Udon Box", "Udon noodles with chili glaze, chicken, and sesame greens.", 9.7, "Noodles"),
            ("Kimchi Dumplings", "Steamed dumplings with fermented kimchi filling.", 6.2, "Appetizer"),
        ],
    },
    {
        "name": "Astana Brunch Bureau",
        "description": "Modern cafe menu with shakshuka, syrniki, coffee, and bright all-day breakfast plates.",
        "address": "Kabanbay Batyr Avenue 38, Astana",
        "cuisine_type": "Brunch",
        "rating": 4.8,
        "dishes": [
            ("Syrniki Deluxe", "Golden cottage-cheese pancakes with berry cream.", 7.4, "Breakfast"),
            ("Steppe Shakshuka", "Eggs in roasted pepper tomato sauce with herbs and toast.", 8.6, "Breakfast"),
            ("Honey Raf Coffee", "Velvety raf coffee with honey and cinnamon.", 3.9, "Drink"),
        ],
    },
    {
        "name": "Shymkent Plov Society",
        "description": "Big rice, bold spice, and generous Uzbek-Kazakh sharing platters.",
        "address": "Tauke Khan Avenue 63, Shymkent",
        "cuisine_type": "Central Asian",
        "rating": 4.8,
        "dishes": [
            ("Wedding Plov", "Rich plov with tender beef, yellow carrots, and chickpeas.", 12.6, "Rice"),
            ("Samsa Trio", "Oven-baked samsa filled with beef, pumpkin, and cheese.", 6.8, "Bakery"),
            ("Achichuk Salad", "Fresh tomato and onion salad with herbs.", 4.1, "Salad"),
        ],
    },
    {
        "name": "Caspian Fish Corner",
        "description": "Seafood-forward plates inspired by Aktau coast flavors and grilled river fish traditions.",
        "address": "Microdistrict 14, Aktau",
        "cuisine_type": "Seafood",
        "rating": 4.5,
        "dishes": [
            ("Grilled Zander Fillet", "Lean zander with lemon butter and herbs.", 13.8, "Fish"),
            ("Caspian Shrimp Rice", "Garlic shrimp on saffron rice with parsley oil.", 14.4, "Seafood"),
            ("Smoked Fish Spread", "Creamy smoked fish dip with warm flatbread.", 5.8, "Starter"),
        ],
    },
    {
        "name": "Baikonur Burger Lab",
        "description": "A louder burger concept with rocket fuel sauces, crispy chicken, and thick shakes.",
        "address": "Republic Avenue 22, Karagandy",
        "cuisine_type": "Burgers",
        "rating": 4.6,
        "dishes": [
            ("Launchpad Double Burger", "Double beef patty, cheddar, pickles, and spicy sauce.", 10.9, "Burger"),
            ("Cosmo Chicken Burger", "Crispy chicken, slaw, and pepper mayo on a soft bun.", 9.8, "Burger"),
            ("Orbit Fries", "Loaded fries with cheese sauce and chili crumbs.", 5.9, "Sides"),
        ],
    },
    {
        "name": "Turkistan Tea & Sweets",
        "description": "Tea house style desserts, layered pastries, and lighter bites for slow evenings.",
        "address": "Bekzat Sattarkhanov Avenue 17, Turkistan",
        "cuisine_type": "Desserts",
        "rating": 4.7,
        "dishes": [
            ("Medovik Slice", "Classic honey cake with airy sour cream layers.", 4.6, "Dessert"),
            ("Pistachio Baklava", "Buttery layers with pistachio filling and syrup glaze.", 4.9, "Dessert"),
            ("Samovar Black Tea", "Strong black tea served in a generous pot.", 2.1, "Drink"),
        ],
    },
    {
        "name": "Abay Pizza Atelier",
        "description": "Wood-fired pizza, seasonal toppings, and a city-center crowd favorite.",
        "address": "Abay Avenue 46, Almaty",
        "cuisine_type": "Italian",
        "rating": 4.8,
        "dishes": [
            ("Truffle Mushroom Pizza", "Wood-fired pizza with mushrooms, truffle cream, and mozzarella.", 13.2, "Pizza"),
            ("Burrata Verde", "Basil pesto pizza with burrata and roasted cherry tomato.", 12.8, "Pizza"),
            ("Roasted Pepper Arancini", "Crisp risotto balls with roasted pepper filling.", 6.1, "Appetizer"),
        ],
    },
    {
        "name": "Kok-Tobe Sushi Club",
        "description": "Japanese comfort menu with rolls, ramen, and polished delivery packaging.",
        "address": "Dostyk Avenue 104, Almaty",
        "cuisine_type": "Japanese",
        "rating": 4.9,
        "dishes": [
            ("Salmon Volcano Roll", "Salmon, cucumber, avocado, and spicy baked topping.", 13.7, "Sushi"),
            ("Miso Butter Ramen", "Ramen bowl with miso broth, butter corn, and sliced beef.", 12.2, "Ramen"),
            ("Tempura Ebi Bites", "Shrimp tempura with yuzu mayo dip.", 7.6, "Appetizer"),
        ],
    },
]


def seed_initial_data(session: Session) -> None:
    for restaurant_data in RESTAURANT_SEED:
        existing_restaurant = session.query(RestaurantModel).filter(RestaurantModel.name == restaurant_data["name"]).first()
        if existing_restaurant is None:
            existing_restaurant = RestaurantModel(
                id=uuid4(),
                name=restaurant_data["name"],
                description=restaurant_data["description"],
                address=restaurant_data["address"],
                cuisine_type=restaurant_data["cuisine_type"],
                rating=restaurant_data["rating"],
                is_open=True,
                image_url=None,
                created_at=datetime.utcnow(),
            )
            session.add(existing_restaurant)
            session.flush()

        existing_dish_names = {
            dish.name
            for dish in session.query(DishModel).filter(DishModel.restaurant_id == existing_restaurant.id).all()
        }

        for name, description, price, category in restaurant_data["dishes"]:
            if name in existing_dish_names:
                continue

            session.add(
                DishModel(
                    id=uuid4(),
                    restaurant_id=existing_restaurant.id,
                    name=name,
                    description=description,
                    price=price,
                    category=category,
                    is_available=True,
                    image_url=None,
                )
            )

    session.commit()
