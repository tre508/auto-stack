flowchart TD
  A[Webhook: /centralbrain_master] --> B[Extract Command]
  B --> C{Switch Command}
  C --> D[Freqtrade Manager HTTP]
  C --> E[Research Manager HTTP]
  C --> F[FreqAI Manager HTTP]
  C --> G[Utility Manager HTTP]
  C --> H[LLM_ParserAgent HTTP]

  H --> I[Parse Intent]
  I --> J[Route Based on NLP Result]

  D --> K[Log to Postgres]
  E --> K
  F --> K
  G --> K
  J --> K
  K --> L[Webhook Response]

  subgraph Agents
    D
    E
    F
    G
  end

  subgraph AI Routing
    H
    I
    J
  end
