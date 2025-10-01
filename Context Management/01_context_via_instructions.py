from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
from dotenv import load_dotenv


load_dotenv()

# --- Hotel Info Dataset ---
hotel_info = {
    "overview": "The Grand Aurora Hotel is a 5-star property in Downtown New Avalon, blending luxury with modern functionality.",
    "contact": {
        "address": "88 Aurora Boulevard, Downtown New Avalon, Avalon City, 55678",
        "phone": "+1 (555) 987-6543",
        "email": "contact@grandaurorahotel.com",
        "website": "www.grandaurorahotel.com",
        "socials": {
            "instagram": "@grandaurorahotel",
            "twitter": "@AuroraLuxuryStay",
            "facebook": "facebook.com/grandaurorahotel"
        }
    },
    "rooms": {
        "deluxe": "350 sq ft, garden or city views.",
        "executive": "Higher floors, Executive Lounge access.",
        "skyline_suite": "Separate living areas, panoramic views, soaking tubs.",
        "presidential": "2000 sq ft residence with dining area, private spa, butler.",
        "extended_apartments": "Kitchen, laundry, weekly housekeeping for long stays."
    },
    "dining": {
        "celeste": "Rooftop restaurant, Mediterranean & Asian fusion.",
        "terra_grounds": "Lobby café, artisanal pastries, coffee.",
        "velvet_bar": "Craft cocktails, global tapas, live jazz."
    },
    "wellness": {
        "spa": "Aurora Spa, signature massages, facials, holistic treatments.",
        "fitness": "24/7 gym, yoga, Pilates, hydrotherapy pool, sauna, steam."
    },
    "events": {
        "spaces": "10,000+ sq ft, ballroom (500 seats), 8 meeting rooms, 2 boardrooms.",
        "support": "Catering, décor, AV support, hybrid meeting tech.",
        "regular_events": "Jazz nights, wine tastings, art exhibitions, Sunday brunches."
    },
    "services": {
        "checkin": "3 PM, checkout 12 PM (early/late on request).",
        "airport": "Complimentary transfer to Avalon International (20 min).",
        "parking": "Valet, self-parking, EV charging.",
        "family": "Babysitting, cribs, kid-friendly menus.",
        "pets": "Pet beds, bowls, walking assistance."
    },
    "offers": {
        "city_explorer": "Private guided tours, museum passes, culinary experiences.",
        "romance": "Suite upgrade, champagne, spa credit, late checkout.",
        "business_package": "Executive room, lounge access, laundry credit."
    },
    "sustainability": {
        "energy": "Solar-powered heating, motion-sensor lighting.",
        "toiletries": "Organic, biodegradable products.",
        "certification": "Green Globe Certified 3 years in a row."
    }
}


# --- Define a tool so the agent can fetch hotel info ---
@function_tool
async def get_hotel_info(query: str) -> dict:
    """
    Retrieve structured hotel information.
    Args:
        query: The section user is asking about (e.g., 'rooms', 'dining', 'offers')
    """

# --- Build Agent ---
agent = Agent(
    name="Hotel Assistant",
    instructions=(
        "You are Grand Aurora Hotel’s virtual concierge. Be friendly, knowledgeable, "
        "and always pull details from the hotel info or the `get_hotel_info` tool "
        "when asked about hotel services, policies, or features.\n\n"
        f"Hotel dataset: {hotel_info}"
    ),
    tools=[get_hotel_info],
)



# --- Runner ---
query = input("Ask your hotel-related question: ")

result = Runner.run_sync(
    agent,
    query,
)

print(result.final_output)


# This method is not recommended for production use cases as the context is hardcoded in the instructions and it will be send in every time the whole instruction data to the LLM which can be expensive. So that's why we have other way to send the contecxt to the LLM. 