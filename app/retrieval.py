"""
end-to-end RAG pipeline
(Vector search er det gamle flow, Embedding search --> top 5 chunks --> LLM. Hurtigt og grovt)
(Reranking, 2-Trins søgning. Langsom, men mere præcis)
Spørgsmål
  ↓
Embedding
  ↓
pgvector search (semantic retrieval)
  ↓
Reranking (LLM)
  ↓
LLM (GPT)
  ↓
Svar
"""
from app.db import get_connection
from app.openai_client import client
from app.embeddings import get_embedding
from app.reranking import rerank_chunks

# forbindelse til db
conn = get_connection()
# cursor objekt til query eksekvering
cursor = conn.cursor()

# Tekst fra bruger
query = "Hvad er et han?"

# Embedding af spørgsmål
query_embedding = get_embedding(query)

# Find relevante chunks
# Select statement med lighedsreference
# Svar skal være tætte nok, før at der bliver taget højde for dem.
# <-> er pgvector distance operator 
cursor.execute(
  """
  SELECT content, 
  embedding <-> %s::vector AS distance
  FROM documents
  ORDER BY embedding <-> %s::vector
  LIMIT 10
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

chunks = [row[0] for row in results]

# Fortæl hvor tæt et match der er, filtering
# for row in results:
#   print("tekst", row[0])
#   print("distance:", row[1])
  
#   filtered = []
  
#   # Filtrering af dårlige matches, 0.5 tærsklen skrues op og ned.
#   for content, distance in results:
#     if distance < 0.5:  
#       filtered.append(content)
reranked_chunks = rerank_chunks(query, chunks)

print("\n Reranked chunks:")
print(reranked_chunks)
# Saml context
context = "\n\n".join(reranked_chunks)

# context = "\n\n".join(filtered) # 'Bedre context building' Efter filter
# print("Fundet context:")
# print(context)
# context = "\n".join([row[0] for row in results]) # Til simpel select

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