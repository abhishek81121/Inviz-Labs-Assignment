from bson import ObjectId
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from pymongo import InsertOne
from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import dotenv_values
from contextlib import asynccontextmanager

import pymongo
#loading the environment values 
config = dotenv_values(".env")

#defining the lifespan function so that to mange connection to the database efficiently and correctly
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_connection= MongoClient(config["DB_URI"])
    db=db_connection['Property']
    global collection
    collection=db['PropertyInfo']
    print("Connected to the MongoDB database!")
    yield
    db_connection.close()

app = FastAPI(lifespan=lifespan)



   

#data model for the details of the object that is to be created used at the path /create
class ItemToBeCreated(BaseModel):
    Property_name:str
    Address:str
    City:str
    State:str

#route for creating the property on the database
@app.post('/create',description="This route creates the property obeject in the database")
async def create(itemToBeCreated : ItemToBeCreated):
    itemToBeCreated.City=itemToBeCreated.City.title()
    itemToBeCreated.State=itemToBeCreated.State.title()
    property=jsonable_encoder(itemToBeCreated)
    new_property=collection.insert_one(property)
    print(new_property.inserted_id)
    return ({"id":str(new_property.inserted_id)},itemToBeCreated);


class ItemToBeUpdated(BaseModel):
    Property_id :str
    Property_name:str
    Address:str
    City:str
    State:str

@app.post('/update',description='This route updates the object in the database using the projectId')
async def update(itemToBeUpdated : ItemToBeUpdated):
    updated_property=collection.find_one_and_update({'_id' : ObjectId(itemToBeUpdated.Property_id)},{'$set':{'Property_name':itemToBeUpdated.Property_name,'Address':itemToBeUpdated.Address,'City':itemToBeUpdated.City.title(),'State':itemToBeUpdated.State.title()}},return_document=True)
    updated_property['_id']=str(updated_property['_id'])
    return updated_property




class CityName(BaseModel):
    cityName: str


@app.post('/fetch/city',description='This api fetches all the properties in one city')
async def fetchPropertyByCity(city : CityName):
    city.cityName=city.cityName.title()
    properties=collection.find({'City': city.cityName})
    items=list(properties)
    if len(items)!=0:
        for prop in items:
            prop['_id'] = str(prop['_id'])

    return {'properties': items};

class StateName(BaseModel):
    stateName : str

@app.post('/fetch/state',description='This route fetches all the property in a single state')
async def fetchPropertyByState(state : StateName):
    state.stateName=state.stateName.title()
    properties=collection.find({'State': state.stateName})
    items=list(properties)
    if len(items)!=0:
        for prop in items:
            prop['_id'] = str(prop['_id'])

    return {'properties': items};


class PropertyId(BaseModel):
    propertyId :str
@app.post('/fetch/propertyid',description='This route fetches all the properties in the same city by propertyid of a property ')
async def fetchPropertyByPropertyId(property_Id :PropertyId ):
    id=ObjectId(property_Id.propertyId)
    property=collection.find({'_id' :id})
    cityName=list(property)[0]['City']
    items=list(collection.find({'City' : cityName}))
    if len(items)!=0:
        for prop in items:
            prop['_id'] = str(prop['_id'])
    return {'properties':items}





