from datetime import datetime, timedelta
from sqlmodel import SQLModel, Field, Relationship

from ..utils.mixins import Name, ID


class Step_Ingredient(SQLModel, table=True):
    """Ingredient used in a recipe's step"""

    step_id: int = Field(foreign_key="step.id", primary_key=True)
    """ID of Recipe's Step"""
    ingredient_id: int = Field(foreign_key="ingredient.id", primary_key=True)
    """ID of Ingriedient used"""

    quantity: float
    """Quantity of ingredient required for this step"""
    unit: str
    """Unit in which quantity is provided"""


class Ingredient(Name, table=True):
    """Ingredient metadata"""

    steps: list["Step"] = Relationship(back_populates="ingredients", link_model=Step_Ingredient)
    """Steps using this Ingredient"""


class Recipe(Name, table=True):
    """Recipe's metadata"""

    description: str
    """Recipe Description"""

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

    recipe: Recipe = Relationship(back_populates="steps")
    """Related Recipe"""
    ingredients: list[Ingredient] = Relationship(back_populates="steps", link_model=Step_Ingredient)
    """Ingredients used in this step"""


class Ingredient_Inventory(ID, table=True):
    """Ingredients in inventory"""

    ingredient_id: int = Field(foreign_key="ingredient.id")
    """ID of Ingredient"""
    quantity: float
    """Quantity currently owned"""
    unit: str
    """Unit of quantity"""
    expire_date: datetime
    """Expiration date of an item"""

    ingredient: Ingredient = Relationship()
    """Related Ingridient"""
