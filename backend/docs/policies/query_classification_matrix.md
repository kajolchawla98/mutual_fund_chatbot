# Query Classification Matrix

| Query Intent Category | Description | Assistant Response Action |
| :--- | :--- | :--- |
| **FACTUAL** | User asks for specific, factual information available in the official documents (e.g., expense ratio, exit load, minimum SIP amount). | Retrieve relevant facts from the vector store, generate a concise response (max 3 sentences), include exactly 1 citation link, and add the freshness footer. |
| **ADVISORY_REFUSE** | User asks for investment advice, recommendations, comparisons between funds, or requests predictions on future performance. | Refuse the query politely, state the facts-only boundary, and provide one educational link (AMFI/SEBI). |
| **OUT_OF_SCOPE_REFUSE** | User asks questions completely unrelated to mutual funds or the allowed list of funds. | Refuse the query politely, state the scope of the assistant, and provide one educational link. |
| **PERFORMANCE_REDIRECT** | User asks for historical performance data, return calculations, or subjective analysis of past performance. | Refuse to calculate or analyze performance directly. Redirect the user by providing a link to the official factsheet for the requested fund. |
