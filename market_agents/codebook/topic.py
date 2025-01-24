from enum import Enum

class Topic(str, Enum):
    """
    Name for the Doing Business topic.
    """
    STARTING_A_BUSINESS = "Starting a business"
    DEALING_WITH_CONSTRUCTION_PERMITS = "Dealing with construction permits"
    GETTING_ELECTRICITY = "Getting electricity"
    REGISTERING_PROPERTY = "Registering property"
    GETTING_CREDIT = "Getting credit"
    PROTECTING_MINORITY_INVESTORS = "Protecting minority investors"
    PAYING_TAXES = "Paying taxes"
    TRADING_ACROSS_BORDERS = "Trading across borders"
    ENFORCING_CONTRACTS = "Enforcing contracts"
    RESOLVING_INSOLVENCY = "Resolving insolvency"
    EASE_OF_DOING_BUSINESS = "Ease of doing business"