from app.openai_client import client

def get_embedding(query: str) -> list[float]:
    """_summary_
    Opretter embedding for en given tekst
    Embedding via OpenAI API
    Embedding laver tekst til talværdier (vektor)
    Som er det der bruges til at lave semantisk søgning i vektor databasen.
    Args:
        query (str): input tekst, kan være query eller chunk

    Returns:
        list[float]: embedding vektor (1536 dimensioner) for test-embedding-3-small
    """
    response = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
    )
    return response.data[0].embedding