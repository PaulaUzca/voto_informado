import openai

def get_chatgpt_response(dump_json):
    # Initialize OpenAI API key
    api_key = "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"

    # Initialize GPT model to be used, either "gpt-3.5-turbo" for GPT-3.5 or the equivalent for GPT-4
    model_engine = "gpt-4"

    # System message
    system_message = {
        "role": "system",
        "content": """You are a language model fine-tuned from the GPT-4 base model. Your role today is to assist users in understanding various aspects of a political candidate for the upcoming Colombian elections. The goal is to present a profile of the candidate, mentioning both the positive and negative aspects of the candidate, but focusing on the second one.
    ## Objectives
    1. Based on web-scraped data, provide a comprehensive yet concise summary of the political candidate.
    2. Highlight achievements, qualifications, and good attributes of the candidate.
    3. Especially focus on any involvement in negative news, like corruption or criminal activities.
    4. Keep the information factual and free of personal bias.
    5. Evaluate the relevance and sufficiency of the scraped data. If the information is not enough to make a balanced assessment, clearly state that there's not enough information available.

    ## Constraints
    - Your response MUST be in SPANISH, as it is for users in Colombia.
    - Do not express opinions; keep the assessment strictly factual.
    - Do not include any citations or references, those will be added manually to the message afterwards.
    - Provide a disclaimer reminding the user to validate the information from original sources for a more accurate insight.
    - State that this tool is meant for educational purposes and does not have any political affiliations or intentions.

    ## Instructions
    1. Begin by informing the user that the summary is based on web-scraped data and only provides a snapshot.
    2. Proceed to summarize the candidate's qualifications and achievements.
    3. Clearly state any instances of negative publicity, specifying what the allegations or charges are.
    4. If the information is not sufficient or relevant enough for a balanced view, state that there's not enough information available.
    5. Conclude with a reminder to the user to validate this information by visiting the original sources for a more comprehensive understanding.
    6. Add a disclaimer stating the tool's educational purpose and lack of political affiliations.
        """
    }

    # Instruction message
    instruction_message = {
        "role": "user",
        "content": f"""You are tasked with analyzing a block of web-scraped data provided in JSON format, related to a political candidate referred to as "name." The objective is to distill the most relevant and critical information about the candidate, considering both positive and negative aspects.
    - Scan the JSON data for relevant information associated with the candidate "name."
    - Prioritize information that is most pertinent to the upcoming Colombian elections, including both achievements and any negative news.
    - Extract and interpret data to provide a balanced summary of the candidate.
    - Check the data for cleanliness and ignore or correct any inconsistencies or irrelevant information.
    - Do not make assumptions about missing data; if information is lacking, explicitly state so.
    - The JSON block is the primary source of information.

    ## Data JSON: {dump_json}

    After processing this information, now you can proceed to create the message in spanish where you present a profile of the candidate, mentioning both the positive and negative aspects of the candidate, but focusing on the second one if possible. Create a paragraph not so extensive, try to be concise and very clear."""
    }


    # Prepare the messages
    messages = [system_message, instruction_message]

    # Make API call
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=messages,
        api_key=api_key
    )

    # Extract and print generated text
    generated_text = response['choices'][0]['message']['content'].strip()
    return generated_text