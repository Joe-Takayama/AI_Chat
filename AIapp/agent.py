from google import genai


client = genai.Client()


def ask_ai(message):

    interaction = client.interactions.create(
        model="gemini-3.7-flash",
        input=message
    )

    return interaction.output_text