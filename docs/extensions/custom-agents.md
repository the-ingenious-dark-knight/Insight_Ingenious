---
title: "Creating Custom Agents"
layout: single
permalink: /extensions/custom-agents/
sidebar:
  nav: "docs"
toc: true
toc_label: "Custom Agents"
toc_icon: "robot"
---

# Creating Custom Agents

The next step in working with the Ingenious library is working with the creation of agents for orchestration.
This is done by defining the agent's persona, existing/prior knowledge/experience, the explicit instruction and set of examples that the model can follow for the output.

### Setting up the agent

1. Create a new agent folder in `ingenious/services/chat_services/multi_agent/agents/your_agent_name/`
2. Create these files:
   - `agent.md`: Agent definition and persona
   - `tasks/task.md`: Task description for the agent

### Agent Definition Example


```md
# Your Agent Name

## Name and Persona

* Name: Your name is Ingenious and you are a [Specialty] Expert
* Description: You are a [specialty] expert assistant. Your role is to [description of responsibilities].

## System Message

### Backstory

[Background information about the agent's role and knowledge]

### Instructions

[Detailed instructions on how the agent should operate]

### Examples

[Example interactions or outputs]
```

> **Note**: LLMs work best with a more precise syntax and information provided. It does not need to be always quite verbose, but always be mindful of the language that you use with the commands/prompt that you make.
