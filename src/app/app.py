import os
import sys
import uvicorn
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
from typing import List
from fastapi.templating import Jinja2Templates
from src.utils import load_pickle
from src.module import Inputs
from src.utils import make_prediction,output_batch, return_columns


# Create an instance of FastAPI
app = FastAPI(debug=True)

# get absolute path
DIRPATH = os.path.dirname(os.path.realpath(__file__))

# set path for pickle files
model_path = os.path.join(DIRPATH, '..', 'models', 'model-1.pkl')
transformer_path = os.path.join(DIRPATH, '..', 'models', 'preprocessor.pkl')
properties_path = os.path.join(DIRPATH, '..', 'models', 'other-components.pkl')

# Load the trained model, pipeline, and other properties
model = load_pickle(model_path)
transformer = load_pickle(transformer_path)
properties = load_pickle(properties_path)

# Configure static and template files
app.mount("/static", StaticFiles(directory="src/app/static"), name="static") # Mount static files
templates = Jinja2Templates(directory="src/app/templates") # Mount templates for HTML


# Root endpoint to serve index.html template
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})


# Health check endpoint
@app.get("/health")
def check_health():
    return {"status": "ok"}

# Model information endpoint
@app.post('/model-info')
async def model_info():
    model_name = model.__class__.__name__ # get model name 
    model_params = model.get_params() # get model parameters
    features = properties['train features'] # get training feature
    model_information =  {'model info': {
            'model name ': model_name,
            'model parameters': model_params,
            'train feature': features}
            }
    return model_information # return model information

# prediction endpoint
async def predict(plasma_glucose: float, blood_work_result_1: float, 
                  blood_pressure: float, blood_work_result_2: float, 
                  blood_work_result_3: float, body_mass_index: float, 
                  blood_work_result_4: float, age: int, insurance: bool):
    
    # Create a dataframe from inputs 
    data = pd.DataFrame([[plasma_glucose,blood_work_result_1,blood_pressure,
                           blood_work_result_2,blood_work_result_3,body_mass_index, 
                           blood_work_result_4, age,insurance]], columns=return_columns())

    # data_copy = data.copy() # Create a copy of the dataframe
    labels, prob = make_prediction(data, transformer, model) # Get the labels  
    response = output_batch(data, labels) # output results
    return response


# Batch prediction endpoint
@app.post('/predict-batch')
async def predict_batch(inputs: Inputs):
    # Create a dataframe from inputs
    data = pd.DataFrame(inputs.return_dict_inputs())
    labels, probs = make_prediction(data, transformer, model) # Get the labels
    response = output_batch(data, labels) # output results
    return response

# Run the FastAPI application
if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)


