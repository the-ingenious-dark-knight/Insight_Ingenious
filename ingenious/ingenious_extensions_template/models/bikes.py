from typing import List, Union
from pydantic import BaseModel, Field
import json


class RootModel_Bike(BaseModel):
    brand: str
    model: str
    year: int
    price: float


class RootModel_MountainBike(RootModel_Bike):
    suspension: str = Field(..., description="Type of suspension (e.g., full, hardtail)")


class RootModel_RoadBike(RootModel_Bike):
    frame_material: str = Field(..., description="Material of the frame (e.g., carbon, aluminum)")


class RootModel_CustomerReview(BaseModel):
    rating: float
    comment: str


class RootModel_ElectricBike(RootModel_Bike):
    battery_capacity: float = Field(..., description="Battery capacity in kWh")
    motor_power: float = Field(..., description="Motor power in watts")


class RootModel_BikeStock(BaseModel):
    bike: Union[RootModel_MountainBike, RootModel_RoadBike, RootModel_ElectricBike]
    quantity: int


class RootModel_BikeSale(BaseModel):
    product_code: str
    quantity_sold: int
    sale_date: str
    year: int
    month: str
    customer_review: RootModel_CustomerReview


class RootModel_Store(BaseModel):
    name: str
    location: str
    bike_sales: List[RootModel_BikeSale]


class RootModel(BaseModel):
    store: RootModel_Store
    bike_stock: List[RootModel_BikeStock]
    bike_sales: List[RootModel_BikeSale]

    def load_from_json(json_data: str):
        data = json.loads(json_data)
        root_model = RootModel(**data)
        print(root_model)
