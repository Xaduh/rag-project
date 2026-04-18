"""
end-to-end RAG pipeline
Spørgsmål
  ↓
Embedding
  ↓
pgvector search (semantic retrieval)
  ↓
Top chunk (context)
  ↓
LLM (GPT)
  ↓
Svar
"""
from app.db import get_connection
from app.openai_client import client
from app.embeddings import get_embedding

# forbindelse til db
conn = get_connection()
# cursor objekt til query eksekvering
cursor = conn.cursor()

# Tekst fra bruger
query = "Hvad er hovedstaden i Danmark?"

# Embedding af spørgsmål
query_embedding = get_embedding(query)

# Find relevante chunks
# Select statement med lighedsreference
# Svar skal være tætte nok, før at der bliver taget højde for dem.
# <-> er pgvector distance operator 
cursor.execute(
  """
  SELECT content, 
  embedding <-> %s AS distance
  FROM documents
  ORDER BY embedding <-> %s
  LIMIT 5
  """,
  (query_embedding, query_embedding)
)
# Rent og simpelt select statement
# Finder bare de 3 nærmeste embeddings, uden at tage højde for hvor gode de er.
# cursor.execute(
#     """
#     SELECT content FROM documents
#     ORDER BY embedding <-> CAST(%s as vector)
#     LIMIT 3
#     """,
#     (query_embedding,)
# )

results = cursor.fetchall()

# Fortæl hvor tæt et match der er
for row in results:
  print("tekst", row[0])
  print("distance:", row[1])
  
  filtered = []
  
  # Filtrering af dårlige matches, 0.5 tærsklen skrues op og ned.
  for content, distance in results:
    if distance < 0.5:  
      filtered.append(content)

# Saml context
context = "\n\n".join(filtered) # 'Bedre context building'
# context = "\n".join([row[0] for row in results]) # Til simpel select

print("Fundet context:")
print(context)

# Byg AI prompt
prompt = f"""
Brug KUN følgende context til at svare:
{context}

Spørgsmål: {query}
"""

# Kald LLM
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Udskriv svar fra LLM
answer = completion.choices[0].message.content
print(f"\n LLM svar:\n{answer}")