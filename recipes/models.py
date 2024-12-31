from datetime import datetime, timedelta
from sqlmodel import SQLModel, Field, Relationship

from ..utils.mixins import Name, ID


class Ingredient_Alias(Name, table=True):
    ingredient_id: int = Field(foreign_key="ingredient.id", primary_key=True)


class Unit_Alias(Name, table=True):
    unit_id: int = Field(foreign_key="unit.id", primary_key=True)


class Unit(ID, table=True):
    aliases: list[Unit_Alias]


class Category(Name, table=True):
    color: str


class LocalizedIngredient(SQLModel, table=True):
    locale: str = Field(primary_key=True)
    ingredient_id: int = Field(foreign_key="ingredient.id", primary_key=True)
    name: str
    plural: str
    abbreviation: str


class LocalizedUnit(SQLModel, table=True):
    locale: str = Field(primary_key=True)
    unit_id: int = Field(foreign_key="unit.id", primary_key=True)
    name: str
    plural: str
    abbreviation: str


class Step_Ingredient(SQLModel, table=True):
    """Ingredient used in a recipe's step"""

    step_id: int = Field(foreign_key="step.id", primary_key=True)
    """ID of Recipe's Step"""
    ingredient_id: int = Field(foreign_key="ingredient.id", primary_key=True)
    """ID of Ingriedient used"""

    quantity: float
    """Quantity of ingredient required for this step"""
    unit_id: int = Field(foreign_key="unit.id")
    """Unit in which quantity is provided"""
    note: str


class Ingredient(Name, table=True):
    """Ingredient metadata"""

    steps: list["Step"] = Relationship(back_populates="ingredients", link_model=Step_Ingredient)
    """Steps using this Ingredient"""
    category_id: int
    description: str
    aliases: list[Ingredient_Alias]


class RecipeVariation(ID, table=True):
    """Variation of a recipe"""

    description: str
    """Recipe Description"""

    sub_recipes: list["Recipe"]  # List of sub recipes this recipe uses
    steps: list["Step"] = Relationship(back_populates="recipe")
    """Steps related to this Recipe"""

    @property
    def ingredients(self) -> list[Ingredient]:
        """Ingredients used by this Recipe"""
        _ = []
        return [_.extend(i.ingredients) for i in self.steps]

    @property
    def time(self) -> float:
        """Time required to make this recipe"""
        return sum([s.time for s in self.steps])


class Recipe(Name, table=True):
    """Recipe's metadata"""

    variations: list[RecipeVariation]
    """Variations of this recipe"""

    default_variation_id: int
    default_variation: RecipeVariation
    """Default variation of this recipe"""


class Step(SQLModel, table=True):
    """Step of a recipe"""

    recipe_id: int = Field(foreign_key="recipe.id", primary_key=True)
    """Recipe's ID this step is part of"""
    order: int = Field(primary_key=True)
    """Order of this step in Recipe"""
    description: str
    """Description of step"""
    time: timedelta
    """Time requred for this step"""

    recipe: RecipeVariation = Relationship(back_populates="steps")
    """Related Recipe"""
    ingredients: list[Ingredient] = Relationship(back_populates="steps", link_model=Step_Ingredient)
    """Ingredients used in this step"""


class Step_Recipe:  # This would allow us to reuse steps between different recipes
    recipe_id: int
    step_id: int
    ingredients: list[Step_Ingredient]


class Ingredient_Inventory(ID, table=True):
    """Ingredients in inventory"""

    ingredient_id: int = Field(foreign_key="ingredient.id")
    """ID of Ingredient"""
    quantity: float
    """Quantity currently owned"""
    unit: int = Field(foreign_key="unit.id")
    """Unit of quantity"""
    expire_date: datetime
    """Expiration date of an item"""

    ingredient: Ingredient = Relationship()
    """Related Ingridient"""
