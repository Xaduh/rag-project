"""
Hele Ingestion pipeline laves her.
Text → chunking → embedding → Postgres    
"""
from app.db import get_connection
from app.embeddings import get_embedding

# Forbindelse til db
conn = get_connection()
# cursor objekt til query eksekvering
cursor = conn.cursor()

# chunking funktion
def chunk_text(text, chunk_size=100):
    """_summary_
    Deler tekst op i mindre bidder (chunks)
    så embeddings bliver mere præcise.
    Args:
        text (_type_): _description_
        chunk_size (int, optional): _description_. Defaults to 100.
    """
    chunks = []
    # Loop igennem alt tekst, i chunkstørrelses intervaller.
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

# Læs tekst fra fil
with open("data/test.txt", "r", encoding="utf-8") as file:
    text = file.read() 
"""
Split tekst om til chunks
Chunking gør tekst søgbar.
"""
chunks = chunk_text(text)    
# Tjek terminal for status
print(f"Antal chunks: {len(chunks)}")
print(f"chunks: {chunks}")

# Loop gennem hvert chunk
for chunk in chunks:      
    embedding = get_embedding()
    
    # gem chunk + embedding i db
    cursor.execute(
    """
    INSERT INTO documents (content, embedding)
    VALUES (%s, %s)    
    """,
    # Params mod sql injection, samt korrekt format.
    (chunk, embedding)
    )

# Push ændringer til db
conn.commit()

# Succes?
print("Data inserted")
print(len(embedding)) # Vil gerne lige tjekke at den er 1536