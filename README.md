need .env file with following format:


CEREBRAS_API_KEY=""



make you rown api key at thsi website: https://www.cerebras.ai/


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
