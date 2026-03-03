import time
from cerebras.cloud.sdk import AsyncCerebras
import os
from dotenv import load_dotenv

load_dotenv()


async def invoke_cerebras(prompt: str, temperature: float):


    try:
        start = time.time()
        
        client = AsyncCerebras(api_key=os.getenv('CEREBRAS_API_KEY'))

        response = await client.chat.completions.create(
            model='gpt-oss-120b',
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )

        response = response.choices[0].message.content

        end = time.time()
        time_taken = end - start

        return {'response': response, 'time_taken': time_taken}

    except Exception as e:
        print(f"An error occurred: {e}")

        return {'response': None, 'time_taken': None}
