---

    weight: 2

---

# Developer Guide
Please use this to guide through our framework (revise this sentence)


## AutoGen: Multi-Agent Conversation Framework

AutoGen offers a unified multi-agent conversation framework as a high-level abstraction of using foundation models. It features capable, customizable, and conversable agents which integrate LLMs, tools, and humans via automated agent chat. By automating chat among multiple agents, one can easily make them collectively perform tasks autonomously or with human feedback, including tasks that require using tools via code.

This framework simplifies the orchestration, automation, and optimization of a complex LLM workflow. It maximizes the performance of LLM models and overcomes their weaknesses. It enables building next-gen LLM applications based on multi-agent conversations with minimal effort.

AutoGen abstracts and implements conversable agents designed to solve tasks through inter-agent conversations. Specifically, the agents in AutoGen have the following features:

- **Conversable:** Agents in AutoGen can send and receive messages to initiate or continue a conversation.
- **Customizable:** Agents can be customized to integrate LLMs, humans, tools, or a combination of these.

The figure below shows the built-in agents in AutoGen.
![img.png](images/img.png)



## Insight Service Prefabs

We have designed a generic service framework -service prefabs- that can let agents converse with each other through message exchanges to jointly finish a task.
Different prefabs can perform different actions after receiving messages.

You can locate them under `services/chat_services`  [folder structure](./folder_structure).


```powershell title="view service prefabs"
.
├── __init__.py
├── chat_service.py
├── chat_services
│  ├── __init__.py
│  ├── fast_agent
│  │  └── __init__.py
│  └── multi_agent
│      ├── __init__.py
│      ├── tool_factory.py
│      ├── agents
│      ├── conversation_flows
│      ├── conversation_patterns
│      └── service.py
├── message_feedback_service.py
└── tool_service.py
```

Each prefab has 2 components 

- conversation_flows
- conversation_patterns



