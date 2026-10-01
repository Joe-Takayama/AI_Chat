from google import genai


client = genai.Client()


def ask_ai(message, previous_interaction_id=None):

    if previous_interaction_id:

        interaction = client.interactions.create(
            model="gemini-3.7-flash",
            input=message,
            previous_interaction_id=previous_interaction_id
        )

    else:

        interaction = client.interactions.create(
            model="gemini-3.7-flash",
            input=message
        )


    return interaction.output_text, interaction.id