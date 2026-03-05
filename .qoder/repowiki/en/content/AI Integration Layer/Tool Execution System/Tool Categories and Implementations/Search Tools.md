# Search Tools

<cite>
**Referenced Files in This Document**
- [search_tool.py](file://core/tools/search_tool.py)
- [vector_store.py](file://core/tools/vector_store.py)
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py)
- [code_indexer.py](file://core/tools/code_indexer.py)
- [rag_tool.py](file://core/tools/rag_tool.py)
- [environment_memory.py](file://core/tools/environment_memory.py)
- [context_scraper.py](file://core/tools/context_scraper.py)
- [memory_tool.py](file://core/tools/memory_tool.py)
- [hive_memory.py](file://core/tools/hive_memory.py)
- [interface.py](file://core/infra/cloud/firebase/interface.py)
- [queries.py](file://core/infra/cloud/firebase/queries.py)
- [schemas.py](file://core/infra/cloud/firebase/schemas.py)
- [requirements.txt](file://requirements.txt)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document describes the search tools category within the Aether Voice OS. It covers content retrieval, indexing, and intelligent search capabilities across local and cloud environments. It explains search algorithms, indexing strategies, query processing mechanisms, and the interfaces for content discovery, relevance ranking, and result filtering. It also addresses performance considerations for large-scale content indexing, caching strategies, and search result ranking, and documents the relationship between search tools and memory systems, including semantic search and context-aware retrieval.

## Project Structure
The search tools ecosystem spans several modules:
- Local and cloud vector stores for semantic search
- Codebase indexing and retrieval via RAG
- Environment memory for spatial grounding
- Context scraping for real-time external knowledge
- Persistent memory tools for recall and semantic search
- Firebase infrastructure for cloud persistence and caching

```mermaid
graph TB
subgraph "Search Tools"
ST["search_tool.py"]
VS["vector_store.py"]
FVS["firestore_vector_store.py"]
CI["code_indexer.py"]
RT["rag_tool.py"]
EM["environment_memory.py"]
CS["context_scraper.py"]
MT["memory_tool.py"]
HM["hive_memory.py"]
end
subgraph "Cloud Infrastructure"
FI["interface.py (FirebaseConnector)"]
Q["queries.py (Query Cache)"]
SCH["schemas.py"]
end
ST --> |"Google Search grounding"| ST
VS --> |"Local embeddings"| VS
FVS --> |"Cloud embeddings"| FI
CI --> |"Indexes codebase"| FVS
RT --> |"RAG over codebase"| FVS
EM --> |"Semantic frames"| VS
CS --> |"Real-time context"| CS
MT --> |"Persistent memory"| FI
HM --> |"Collective memory"| FI
FI --> Q
FI --> SCH
```

**Diagram sources**
- [search_tool.py](file://core/tools/search_tool.py#L26-L50)
- [vector_store.py](file://core/tools/vector_store.py#L21-L112)
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L22-L129)
- [code_indexer.py](file://core/tools/code_indexer.py#L56-L131)
- [rag_tool.py](file://core/tools/rag_tool.py#L26-L109)
- [environment_memory.py](file://core/tools/environment_memory.py#L21-L94)
- [context_scraper.py](file://core/tools/context_scraper.py#L8-L146)
- [memory_tool.py](file://core/tools/memory_tool.py#L40-L330)
- [hive_memory.py](file://core/tools/hive_memory.py#L25-L115)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L15-L259)
- [queries.py](file://core/infra/cloud/firebase/queries.py#L20-L74)
- [schemas.py](file://core/infra/cloud/firebase/schemas.py#L30-L38)

**Section sources**
- [search_tool.py](file://core/tools/search_tool.py#L1-L51)
- [vector_store.py](file://core/tools/vector_store.py#L1-L112)
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L1-L129)
- [code_indexer.py](file://core/tools/code_indexer.py#L1-L131)
- [rag_tool.py](file://core/tools/rag_tool.py#L1-L109)
- [environment_memory.py](file://core/tools/environment_memory.py#L1-L94)
- [context_scraper.py](file://core/tools/context_scraper.py#L1-L146)
- [memory_tool.py](file://core/tools/memory_tool.py#L1-L330)
- [hive_memory.py](file://core/tools/hive_memory.py#L1-L115)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L1-L259)
- [queries.py](file://core/infra/cloud/firebase/queries.py#L1-L74)
- [schemas.py](file://core/infra/cloud/firebase/schemas.py#L1-L38)

## Core Components
- Local Vector Store: Lightweight semantic index using embeddings and cosine similarity for local search.
- Cloud Vector Store: Firestore-backed vector store for enterprise-scale retrieval with embedding generation.
- Codebase Indexer: Script to chunk and embed codebase content and upload to the cloud vector store.
- RAG Tool: Semantic search over the codebase for discovery and debugging.
- Environment Memory: Semantic indexing of visual frames for spatial grounding.
- Context Scraper: Real-time web scraping for StackOverflow, GitHub, and Hacker News to augment context.
- Memory Tools: Persistent memory with recall, listing, semantic tag search, and pruning.
- Hive Memory: Collective memory for cross-session and cross-agent state sharing.
- Firebase Connector: Cloud persistence layer with session logging, telemetry, and repair events.

**Section sources**
- [vector_store.py](file://core/tools/vector_store.py#L21-L112)
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L22-L129)
- [code_indexer.py](file://core/tools/code_indexer.py#L56-L131)
- [rag_tool.py](file://core/tools/rag_tool.py#L26-L109)
- [environment_memory.py](file://core/tools/environment_memory.py#L21-L94)
- [context_scraper.py](file://core/tools/context_scraper.py#L8-L146)
- [memory_tool.py](file://core/tools/memory_tool.py#L40-L330)
- [hive_memory.py](file://core/tools/hive_memory.py#L25-L115)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L15-L259)

## Architecture Overview
The search architecture integrates local and cloud components:
- Embedding generation via Gemini
- Local and cloud vector stores for semantic similarity search
- Codebase indexing pipeline and RAG retrieval
- Environment memory for vision-grounded search
- Real-time context scraping for external knowledge
- Persistent memory and collective memory for recall and cross-agent collaboration

```mermaid
sequenceDiagram
participant User as "User"
participant Agent as "Agent"
participant RAG as "RAG Tool"
participant Index as "FirestoreVectorStore"
participant Embed as "Gemini Embeddings"
participant FB as "FirebaseConnector"
User->>Agent : "Find code related to memory persistence"
Agent->>RAG : "search_codebase(query, limit)"
RAG->>Index : "get_query_embedding(query)"
Index->>Embed : "embed_content(task_type=RETRIEVAL_QUERY)"
Embed-->>Index : "query_vector"
RAG->>Index : "search(query_vector, limit)"
Index->>FB : "stream() collection 'aether_embeddings'"
FB-->>Index : "documents with embeddings"
Index-->>RAG : "top-k results"
RAG-->>Agent : "formatted results"
Agent-->>User : "Relevant codebase chunks"
```

**Diagram sources**
- [rag_tool.py](file://core/tools/rag_tool.py#L26-L77)
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L74-L129)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L15-L259)

## Detailed Component Analysis

### Local Vector Store
The Local Vector Store provides a lightweight, local-first semantic index:
- Embedding generation using Gemini
- Cosine similarity scoring
- Pickle-based persistence for quick reloads

```mermaid
classDiagram
class LocalVectorStore {
+__init__(api_key, model)
+load(filepath) bool
+save(filepath) void
+add_text(key, text, metadata) async
+search(query_vector, limit) list
+get_query_embedding(query) async
-_client
-_model
-_vectors
-_metadata
}
```

**Diagram sources**
- [vector_store.py](file://core/tools/vector_store.py#L21-L112)

**Section sources**
- [vector_store.py](file://core/tools/vector_store.py#L21-L112)

### Cloud Vector Store (Firestore RAG)
The Cloud Vector Store scales semantic search to enterprise-grade workloads:
- Embedding generation via Gemini
- Firestore persistence with sanitized keys
- Prototype similarity scan-and-compute approach
- Local caching for reduced cloud calls

```mermaid
classDiagram
class FirestoreVectorStore {
+__init__(api_key, model)
+initialize() async bool
+add_text(key, text, metadata) async
+search(query_vector, limit) async list
+get_query_embedding(query) async
-_client
-_model
-_connector
-_collection_name
-_local_cache_vectors
-_local_cache_metadata
}
```

**Diagram sources**
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L22-L129)

**Section sources**
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L22-L129)

### Codebase Indexer and RAG Tool
The codebase indexer chunks and embeds files, uploading to the cloud vector store. The RAG tool performs semantic search over the indexed codebase.

```mermaid
flowchart TD
Start(["Start Indexing"]) --> LoadEnv["Load GOOGLE_API_KEY"]
LoadEnv --> WalkFiles["Walk repository tree<br/>Ignore dirs and filter extensions"]
WalkFiles --> Chunk["Chunk file content"]
Chunk --> Embed["Embed each chunk via Gemini"]
Embed --> Upload["Upload to Firestore 'aether_embeddings'"]
Upload --> Progress["Log progress and throttle"]
Progress --> Done(["Indexing Complete"])
subgraph "RAG Retrieval"
QStart(["User Query"]) --> GenQ["Generate query embedding"]
GenQ --> Scan["Scan Firestore vectors"]
Scan --> Similarity["Compute cosine similarity"]
Similarity --> Sort["Sort by similarity desc"]
Sort --> Limit["Limit top-k results"]
Limit --> Format["Format file/chunk/snippet"]
Format --> QEnd(["Return results"])
end
```

**Diagram sources**
- [code_indexer.py](file://core/tools/code_indexer.py#L56-L131)
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L74-L129)
- [rag_tool.py](file://core/tools/rag_tool.py#L26-L77)

**Section sources**
- [code_indexer.py](file://core/tools/code_indexer.py#L1-L131)
- [rag_tool.py](file://core/tools/rag_tool.py#L1-L109)

### Environment Memory
Environment Memory indexes visual frame descriptions using the Local Vector Store and supports semantic queries over past visual states.

```mermaid
sequenceDiagram
participant Vision as "Vision Pulse"
participant EnvMem as "EnvironmentMemory"
participant LVS as "LocalVectorStore"
Vision->>EnvMem : "add_frame_description(description, offset, metadata)"
EnvMem->>LVS : "add_text(key, text, metadata)"
LVS-->>EnvMem : "indexed"
EnvMem->>LVS : "get_query_embedding(query)"
LVS-->>EnvMem : "query_vector"
EnvMem->>LVS : "search(query_vector, limit)"
LVS-->>EnvMem : "results"
EnvMem-->>Vision : "formatted results"
```

**Diagram sources**
- [environment_memory.py](file://core/tools/environment_memory.py#L30-L82)
- [vector_store.py](file://core/tools/vector_store.py#L66-L112)

**Section sources**
- [environment_memory.py](file://core/tools/environment_memory.py#L1-L94)
- [vector_store.py](file://core/tools/vector_store.py#L1-L112)

### Context Scraper
The Context Scraper pulls real-time solutions from StackOverflow, GitHub Issues, and Hacker News, formatting results for the agent.

```mermaid
sequenceDiagram
participant Agent as "Agent"
participant Scraper as "AetherContextScraper"
participant Web as "Web Platform"
Agent->>Scraper : "scrape_context(query, platform)"
Scraper->>Scraper : "encode query"
Scraper->>Web : "GET search URL"
Web-->>Scraper : "HTML response"
Scraper->>Scraper : "CSS select links/titles"
Scraper-->>Agent : "format_as_context(results)"
```

**Diagram sources**
- [context_scraper.py](file://core/tools/context_scraper.py#L19-L97)

**Section sources**
- [context_scraper.py](file://core/tools/context_scraper.py#L1-L146)

### Persistent Memory Tools
Memory tools provide saving, recalling, listing, semantic tag search, and pruning of memories backed by Firestore.

```mermaid
flowchart TD
Save["save_memory(key, value, priority, tags)"] --> CheckDB{"Firebase connected?"}
CheckDB --> |No| LocalOnly["Return local-only message"]
CheckDB --> |Yes| Upsert["Upsert memory document"]
Upsert --> DoneSave["Return saved status"]
Recall["recall_memory(key)"] --> CheckRecall{"Firebase connected?"}
CheckRecall --> |No| Offline["Return unavailable"]
CheckRecall --> |Yes| GetDoc["Get memory document"]
GetDoc --> Found{"Exists?"}
Found --> |Yes| ReturnVal["Return value/priority/tags"]
Found --> |No| NotFound["Return not found"]
List["list_memories(limit, priority)"] --> CheckList{"Firebase connected?"}
CheckList --> |No| OfflineList["Return unavailable"]
CheckList --> |Yes| BuildQuery["Build query with optional filter"]
BuildQuery --> Stream["Stream results"]
Stream --> ReturnList["Return list"]
Semantic["semantic_search(tags, limit)"] --> CheckSem{"Firebase connected?"}
CheckSem --> |No| OfflineSem["Return unavailable"]
CheckSem --> |Yes| TagQuery["array_contains_any(tags)"]
TagQuery --> StreamSem["Stream results"]
StreamSem --> ReturnSem["Return matches"]
Prune["prune_memories(priority)"] --> CheckPrune{"Firebase connected?"}
CheckPrune --> |No| OfflinePrune["Return unavailable"]
CheckPrune --> |Yes| DelQuery["Delete docs matching priority"]
DelQuery --> ReturnPrune["Return count"]
```

**Diagram sources**
- [memory_tool.py](file://core/tools/memory_tool.py#L40-L330)

**Section sources**
- [memory_tool.py](file://core/tools/memory_tool.py#L1-L330)

### Hive Collective Memory
Hive Memory enables cross-session and cross-agent state sharing via Firestore.

```mermaid
sequenceDiagram
participant Expert as "Expert Soul"
participant Hive as "HiveMemory"
participant FB as "FirebaseConnector"
Expert->>Hive : "write_collective_memory(key, value, tags)"
Hive->>FB : "set document in 'hive_memory'"
FB-->>Hive : "ack"
Hive-->>Expert : "success message"
Expert->>Hive : "read_collective_memory(key)"
Hive->>FB : "get document"
FB-->>Hive : "document or empty"
Hive-->>Expert : "success/data or not_found/error"
```

**Diagram sources**
- [hive_memory.py](file://core/tools/hive_memory.py#L25-L115)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L15-L259)

**Section sources**
- [hive_memory.py](file://core/tools/hive_memory.py#L1-L115)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L1-L259)

### Google Search Grounding Tool
The Google Search grounding tool integrates with Gemini Live to provide factual, grounded answers with citations.

```mermaid
sequenceDiagram
participant User as "User"
participant Agent as "Gemini"
participant Tool as "get_search_tool()"
participant Web as "Google Search"
User->>Agent : "Ask factual question"
Agent->>Tool : "Use Google Search grounding"
Tool->>Web : "Execute live search"
Web-->>Tool : "Web results"
Tool-->>Agent : "Results with citations"
Agent-->>User : "Grounded response"
```

**Diagram sources**
- [search_tool.py](file://core/tools/search_tool.py#L26-L38)

**Section sources**
- [search_tool.py](file://core/tools/search_tool.py#L1-L51)

## Dependency Analysis
External dependencies relevant to search tools include:
- google-genai for embeddings and grounding
- firebase-admin and google-cloud-firestore for cloud persistence
- numpy for vector math
- scrapling for web scraping

```mermaid
graph LR
VS["vector_store.py"] --> GENAI["google-genai"]
VS --> NUMPY["numpy"]
FVS["firestore_vector_store.py"] --> GENAI
FVS --> FIRE["firebase-admin"]
FVS --> GCF["google-cloud-firestore"]
CI["code_indexer.py"] --> FVS
RT["rag_tool.py"] --> FVS
EM["environment_memory.py"] --> VS
CS["context_scraper.py"] --> SCRAP["scrapling"]
MT["memory_tool.py"] --> FIRE
HM["hive_memory.py"] --> FIRE
IF["interface.py"] --> FIRE
Q["queries.py"] --> FIRE
```

**Diagram sources**
- [requirements.txt](file://requirements.txt#L2-L11)
- [vector_store.py](file://core/tools/vector_store.py#L15-L16)
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L14-L15)
- [code_indexer.py](file://core/tools/code_indexer.py#L13)
- [rag_tool.py](file://core/tools/rag_tool.py#L12)
- [environment_memory.py](file://core/tools/environment_memory.py#L13)
- [context_scraper.py](file://core/tools/context_scraper.py#L5)
- [memory_tool.py](file://core/tools/memory_tool.py#L23-L30)
- [hive_memory.py](file://core/tools/hive_memory.py#L16-L22)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L7-L8)
- [queries.py](file://core/infra/cloud/firebase/queries.py#L6-L9)

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L52)
- [vector_store.py](file://core/tools/vector_store.py#L1-L112)
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L1-L129)
- [code_indexer.py](file://core/tools/code_indexer.py#L1-L131)
- [rag_tool.py](file://core/tools/rag_tool.py#L1-L109)
- [environment_memory.py](file://core/tools/environment_memory.py#L1-L94)
- [context_scraper.py](file://core/tools/context_scraper.py#L1-L146)
- [memory_tool.py](file://core/tools/memory_tool.py#L1-L330)
- [hive_memory.py](file://core/tools/hive_memory.py#L1-L115)
- [interface.py](file://core/infra/cloud/firebase/interface.py#L1-L259)
- [queries.py](file://core/infra/cloud/firebase/queries.py#L1-L74)

## Performance Considerations
- Embedding generation cost: Batch and throttle requests to Gemini to avoid rate limits.
- Vector search scaling: The Firestore prototype performs a scan-and-compute approach; in production, use native vector search extensions or Vertex AI Search to reduce latency and cost.
- Local caching: Use local caches for embeddings and frequent queries to minimize cloud calls.
- Query latency tiers: Tools expose latency tier hints to guide orchestration prioritization.
- Rate limiting: Introduce semaphores and backoff for embedding and upload operations.
- Index maintenance: Periodically rebuild indices after major codebase changes to keep embeddings fresh.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Missing Google API key: Ensure the environment variable is present for embedding operations.
- Firebase connectivity: Verify initialization and credentials; offline mode falls back gracefully for some tools.
- Empty or stale indices: Re-run the codebase indexer to refresh embeddings.
- Slow retrieval: Enable local caching and consider upgrading to native vector search in Firestore.
- Web scraping failures: Confirm network access and platform URLs; handle exceptions and return structured error messages.

**Section sources**
- [code_indexer.py](file://core/tools/code_indexer.py#L56-L131)
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L33-L73)
- [context_scraper.py](file://core/tools/context_scraper.py#L59-L60)
- [memory_tool.py](file://core/tools/memory_tool.py#L56-L92)
- [hive_memory.py](file://core/tools/hive_memory.py#L37-L58)

## Conclusion
The search tools category integrates local and cloud semantic search, codebase RAG, environment memory, real-time context scraping, and persistent/collaborative memory systems. By leveraging embeddings, cosine similarity, and Firestore-backed persistence, the system supports intelligent content discovery, relevance ranking, and result filtering. Performance is optimized through local caching, batching, and production-ready vector search extensions, while resilience is ensured via offline fallbacks and graceful degradation.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Search Patterns and Query Optimization
- Chunking strategies: Use overlapping chunks to preserve context boundaries.
- Query decomposition: Break complex queries into focused sub-queries for multi-stage retrieval.
- Metadata enrichment: Attach file paths, line numbers, and timestamps to improve result interpretability.
- Hybrid ranking: Combine semantic similarity with lexical match scores and recency signals.

[No sources needed since this section provides general guidance]

### Integration with External Search Services
- Google Search grounding: Use the dedicated tool to provide grounded responses with citations.
- Web scraping: Pull real-time context from StackOverflow, GitHub, and Hacker News to address outdated knowledge.
- Production vector search: Replace prototype scan-and-compute with native Firestore vector search or Vertex AI Search.

**Section sources**
- [search_tool.py](file://core/tools/search_tool.py#L26-L38)
- [context_scraper.py](file://core/tools/context_scraper.py#L19-L97)
- [firestore_vector_store.py](file://core/tools/firestore_vector_store.py#L74-L82)