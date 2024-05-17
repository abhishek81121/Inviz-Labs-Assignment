from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from pymongo import InsertOne
from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import dotenv_values
from contextlib import asynccontextmanager
#loading the environment values 
config = dotenv_values(".env")

#defining the lifespan function so that to mange connection to the database efficiently and correctly
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = MongoClient(config["DB_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]   
    print("Connected to the MongoDB database!")
    yield
    app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)



   

#data model for the details of the object that is to be created used at the path /create
class ItemToBeCreated(BaseModel):
    property_name:str
    address:str
    city:str
    state:str

#route for creating the property on the database
@app.post('/create')
async def create(request: Request,itemToBeCreated : ItemToBeCreated):
    itemToBeCreated.city=itemToBeCreated.city.title()
    itemToBeCreated.state=itemToBeCreated.state.title()
    property=jsonable_encoder(itemToBeCreated)
    new_property=request.app.database['PropertyInfo'].insert_one(property)
    print(new_property.inserted_id)
    return ({"id":str(new_property.inserted_id)},itemToBeCreated);



