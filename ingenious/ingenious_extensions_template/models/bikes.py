from typing import List, Union
from pydantic import BaseModel, Field
import json
from ingenious.utils.model_utils import List_To_Csv, Listable_Object_To_Csv, Object_To_Yaml


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
    bike_stock: List[RootModel_BikeStock]


class RootModel(BaseModel):
    stores: List[RootModel_Store]

    def load_from_json(json_data: str):
        data = json.loads(json_data)
        root_model = RootModel(**data)
        print(root_model)

    def display_bike_sales_as_table(self):
        table_data = []
        headers = ["Store Name", "Location", "Product Code", "Quantity Sold", "Sale Date", "Customer Rating", "Customer Comment"]
        for store in self.stores:
            for sale in store.bike_sales:
                store_name = store.name
                location = store.location
                table_data.append([
                    store_name,
                    location,
                    sale.product_code,
                    sale.quantity_sold,
                    sale.sale_date,
                    sale.customer_review.rating,
                    sale.customer_review.comment,
                ])

        ret = List_To_Csv(table_data, headers, "bike_sales")
        print(ret)