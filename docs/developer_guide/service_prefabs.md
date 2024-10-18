---

    weight: 3

---

# Current Service Prefabs

## Classification Agent with Simple Efficient Memory Handling

The **Classification Agent** is central to managing conversation flows and categorizing topics with smart memory handling. It integrates **group chat management** and **smart prompt-based function calls** for effective message classification and agent response generation. Key features include:

- **Smart Memory Handling**: This agent avoids redundant message loops by maintaining a streamlined, efficient memory.
- **Group Chat Functionality**: The agent uses a group chat manager to coordinate conversations across multiple specialized agents.
  
    ```python
    classification_agent = autogen.AssistantAgent(
        name="classification_agent",
        system_message="I am a classification agent responsible for analyzing the topic of conversations and routing them accordingly. "
                       "My responses are based strictly on the user input and I do not retain context from previous responses.",
        description="A core agent that classifies conversation topics and forwards them to specialized topic agents.",
        llm_config=llm_config,
    )
    ```

- **Agent Topic Assignment**: Multiple agents handle different conversation topics, such as soccer, tennis, or basketball. These agents are added dynamically to the classification flow:

    ```python
    tennis_agent = autogen.AssistantAgent(
        name="tennis",
        system_message="You are a topic agent responsible for answering queries about tennis. "
                       "Your responses should be accurate, concise, and formatted for easy readability. "
                       "Do not retain or provide memory.",
        description="A topic agent specialized in tennis-related information.",
        llm_config=llm_config,
    )

    classification_agent.add_topic_agent(tennis_agent)
    ```

- **Smart Routing**: The classification agent routes messages based on detected topics to relevant topic agents, ensuring efficient conversation flow.

    ```python
    soccer_agent = autogen.AssistantAgent(
        name="soccer",
        system_message="You are a topic agent responsible for answering queries about soccer. "
                       "Provide accurate and concise responses, without retaining memory or context.",
        description="A topic agent focused on soccer.",
        llm_config=llm_config,
    )

    classification_agent.add_topic_agent(soccer_agent)
    ```

## Knowledge Retrieval Agent

The **Knowledge Retrieval Agent** excels in extracting specific information from a predefined knowledge base with smart function calls and routing. It employs **dynamic index selection** based on the query context and supports advanced retrieval configurations:

- **Smart Index Selection**: The agent selects the relevant index for retrieving information based on the query type. For instance, health-related queries will trigger a search in the “vector-health” index, while safety-related queries will use “vector-safety.”

    ```python
    search_agent = autogen.AssistantAgent(
        name="search_agent",
        system_message="I am a search agent responsible for retrieving results from searches and passing them to the researcher. "
                       "My responses must be strictly based on the search results or guidelines, with no additional information. "
                       "If a query is ambiguous, I will search across all indices.",
        description="A search agent focused on accurate retrieval from the correct indices.",
        llm_config=llm_config,
    )
    ```

- **Chunk-Based Retrieval**: The agent uses token-based chunking for efficient retrieval from large documents.

- **Smart Function Call and Termination**: This agent is also capable of calling functions only when needed, and can terminate based on specific message content to avoid redundant queries.

## Education Agent

The **Education Agent** is in **early development** but aims to support structured learning experiences by leveraging **knowledge retrieval capabilities** and personalized **learning path generation**.
