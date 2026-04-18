from app.openai_client import client
import json

def rerank_chunks(query: str, chunks: list[str]) -> list[str]:
    """
    Få LLM til at vælge hvilke chunks der er mest relevant. 
    Returner det som en liste af strenge, for at lave bedre chunking.
    """
    
    prompt = f"""
    Du får en liste af tekststykker.
    
    Vælg de 3 mest relevante i forhold til spørgsmålet.
    
    returner KUN et JSON array 
    Ingen markdown
    Ingen ```json
    Ingen forklaring
    Hvis ingen er relevante, vælg stadig de 3 bedste chunks
    Du skal vælge mindst 1 og maks 3 chunks.
    
    Spørgsmål:
    {query}
    
    Chunks:
    {chunks}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    
    print(text)
    
    try: return json.loads(text)
    except:
        print("Kunne ikke parse JSON! Returnere raw tekst.")
        return chunks[:3]