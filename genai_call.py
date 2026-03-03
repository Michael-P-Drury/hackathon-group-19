from cerebras.cloud.sdk import AsyncCerebras
import os
from dotenv import load_dotenv
from get_location import get_coordinates


import asyncio

load_dotenv()

async def relevant_check(user_input):

    prompt = f"""
    here is a user report for a problem:
    
    {user_input}

    your ONLY task is to decide if it is relevant to a sound or a visual complaint (something that would affect someone who is visually impared when
    walking or someone who struggles with loud noises when walking)

    If it is relevant to noise you must return with just 'NOISE' and nothing else

    If it is relevant to vision you MUST return 'VISUAL' and nothing else

    If it is both a visual and a noise problem, you MUST return with 'BOTH'

    Is it is not relevant, reply with NONE and nothing else.
    """

    response = await invoke_cerebras(prompt, 0.05)

    return response


async def noise_scoring(user_input):
    
    prompt = f"""
    here is a user report for a sound problem:
    
    {user_input}

    you are to score the problem from 1-10 of how sever it would be for someone with trouble in loud areas while walking in a city.

    1 - minimal problem
    10 - Very loud big problem

    return with a number from 1-10 and on a new line a 5 word description of the problem.
    """

    response = await invoke_cerebras(prompt, 0.05)

    return response

async def visual_scoring(user_prompt):
    
    prompt = f"""
    here is a user report for a visual problem:
    
    {user_prompt}

    you are to score the problem from 1-10 of how sever it would be for someone with visual struggles walking in a city.

    1 - minimal problem
    10 - Very big HUGE problem

    return with a number from 1-10 and on a new line a 5 word description of the problem.
    """

    response = await invoke_cerebras(prompt, 0.05)

    return response


async def invoke_cerebras(prompt, temperature):

    run = True

    while run == True:

        try:
            client = AsyncCerebras(api_key=os.getenv('CEREBRAS_API_KEY'))

            response = await client.chat.completions.create(
                model='gpt-oss-120b',
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )

            response = response.choices[0].message.content

            run = False

            return response

        except Exception as e:
            print(f"An error occurred: {e}")

            return None


async def run_input_complaint(user_input):

    relevant_response = await relevant_check(user_input)

    if relevant_response.lower().strip() == 'visual':
        scoring_response = await visual_scoring(user_input)

        score = scoring_response.split('\n')[0].strip()
        description = scoring_response.split('\n')[1].strip()

        return {'status': True, 'type': 'visual', 'score': score, 'description': description}

    elif relevant_response.lower().strip() == 'noise':
        scoring_response = await noise_scoring(user_input)
        score = scoring_response.split('\n')

        score = scoring_response.split('\n')[0].strip()
        description = scoring_response.split('\n')[1].strip()

        return {'status': True, 'type': 'noise', 'score': score, 'description': description}

    else:
        return {'status': None, 'type': None, 'score': None, 'description': None}
    

async def create_report(report_text, location):

    response = asyncio.run(run_input_complaint(report_text))

    location = asyncio.run(get_coordinates(location))

    append_report = f"{location['latitude']}|{location['longitude']}|{response['type']}|{response['score']}|{response['description']}"

    with open("user_reports.txt", "a") as file:
        file.write(f"{append_report}\n")

    file.close()
    
