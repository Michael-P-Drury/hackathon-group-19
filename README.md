This project contains the code for group 19 in the hackathon.
We have created a map aimed at providing additional features for individuals suffering from visual or audible impairments.

*** HOW TO RUN ***
**IMPORTANT PORT FOWARDING is needed to run on phone**

* TO RUN ON PHONE :
* install depedancies
<!-- * flet run run.py -->
* python main.py
* seperate terminal we set up port fowarding
- plug in phone with cable
- adb reverse tcp:8550 tcp:8550    ( might need 'adb start-server' before)
- adb devices (if device not showing or says no permissions this wont work)

To run locally:
python main.py


**IMPORTANT** 
**You will need API key from cerebras to run, this is free and only needs email sign up**

need .env file with following format:
CEREBRAS_API_KEY=""

make you rown api key at thsi website: https://www.cerebras.ai/

PORT: 8550


**Install dependancies**
python3 -m pip install -r requirements.txt

or 

pip install:
dotenv
cerebras
osmnx
folium
geopy
scikit-learn 


call genai using call_genai.invoke_cerebras('prompt', temperature)
