---

    weight: 3

---


## Your First Conversation

**Navigate to the `Insight_Ingenious` root folder**:
   After the package installation, the first step is to navigate to the `Insight_Ingenious` root directory. This folder contains all the necessary files required to run the conversation test script. By moving to this folder, you ensure that you're in the correct environment where the test files are located.

   Use the following command:

   ```bash
   cd ..
   ```

   This will move you one level up from your current directory into the `Insight_Ingenious` folder, assuming it's located in the parent directory.


**Run the first test conversation**:
   Now that you're in the root directory, you can proceed to run the test script. This script will simulate a conversation and check if the memory and conversation pattern are working correctly. The test showcases how agents interact, share information, and call necessary functions for tasks like retrieving data or responding to queries.

   Run the following command:

   ```bash
   python3 ./conversation_pattern_example/test_multitool.py
   ```

   If the test runs successfully, you will see a detailed conversation output like the one shown below:

   ```bash
   Adding content of doc 48971743 to context.
   classifier (to chat_manager):

   general

   --------------------------------------------------------------------------------
   researcher (to chat_manager):

   AMBIGUOUS-contact number

   --------------------------------------------------------------------------------
   search_agent (to chat_manager):

   ***** Suggested tool call (call_kfc4ayrKcfqWobcGGQNuA63z): search_tool *****
   Arguments: 
   {"search": "contact number", "index_name": "vector-health"}
   ****************************************************************************
   ***** Suggested tool call (call_YvbHsb24X4yl6ZGgee4gfz1c): search_tool *****
   Arguments: 
   {"search": "contact number", "index_name": "vector-safety"}
   ****************************************************************************

   --------------------------------------------------------------------------------

   >>>>>>>> EXECUTING ASYNC FUNCTION search_tool...
   Config loaded from file
   Profile loaded from file

   >>>>>>>> EXECUTING ASYNC FUNCTION search_tool...
   Config loaded from file
   Profile loaded from file
   researcher (to chat_manager):

   researcher (to chat_manager):

   ***** Response from calling tool (call_kfc4ayrKcfqWobcGGQNuA63z) *****
   ; - Stabilize the injured person using available safety equipment and contact emergency services if necessary 3 **Heat Stress and Hydration:** - Encourage regular hydration breaks, especially in high temperatures - Provide shaded areas or cooling stations and educate personnel on the symptoms of heat stress, dehydration, and how to respond 4...
   **********************************************************************

   --------------------------------------------------------------------------------
   researcher (to chat_manager):

   ***** Response from calling tool (call_YvbHsb24X4yl6ZGgee4gfz1c) *****
   ; **Emergency Contact Numbers:** - Display essential emergency contacts (e.g., 0412 133 777) for fire services, police, ambulance, and utilities prominently throughout the site - Ensure all personnel have ready access to these numbers via their phones or radios --- ### **Evacuation Procedures:** 1 **Evacuation Plan:** - Cle...
   **********************************************************************

   --------------------------------------------------------------------------------
   search_agent (to chat_manager):

   Emergency contact numbers such as 0412 133 777 for fire services, police, ambulance, and utilities should be prominently displayed throughout the site. Ensure all personnel have ready access to these numbers via their phones or radios.

   --------------------------------------------------------------------------------
   reporter (to chat_manager):

   ***** Suggested tool call (call_vD0w7mRYACpJRuQdgG5RcRgC): chat_memory_recorder *****
   Arguments: 
   {"conversation_text":"User's question: Tell me about contact number?\n\nContext: new conversation, please derive context from question\n\nClassified topic: general\n\nResearcher note: AMBIGUOUS-contact number\n\nSearch results: ['; - Stabilize the injured person using available safety equipment and contact emergency services if necessary 3 **Heat Stress and Hydration:** - Encourage regular hydration breaks, especially in high temperatures - Provide shaded areas or cooling stations and educate personnel on the symptoms of heat stress, dehydration, and how to respond 4...', '; **Emergency Contact Numbers:** - Display essential emergency contacts (e.g., 0412 133 777) for fire services, police, ambulance, and utilities prominently throughout the site - Ensure all personnel have ready access to these numbers via their phones or radios --- ### **Evacuation Procedures:** 1 **Evacuation Plan:** - Cle...']\n\nSearch agent answer: Emergency contact numbers such as 0412 133 777 for fire services, police, ambulance, and utilities should be prominently displayed throughout the site. Ensure all personnel have ready access to these numbers via their phones or radios.","last_response":"Emergency contact numbers such as 0412 133 777 for fire services, police, ambulance, and utilities should be prominently displayed throughout the site. Ensure all personnel have ready access to these numbers via their phones or radios."}
   *************************************************************************************

   --------------------------------------------------------------------------------

   >>>>>>>> EXECUTING ASYNC FUNCTION chat_memory_recorder...
   Config loaded from file
   Profile loaded from file
   Memory Updated: User's question: Tell me about contact number?

   Context: new conversation, please derive context from question

   Classified topic: general

   Researcher note: AMBIGUOUS-contact number

   Search results: ['; - Stabilize the injured person using available safety equipment and contact emergency services if necessary 3 **Heat Stress and Hydration:** - Encourage regular hydration breaks, especially in high temperatures - Provide shaded areas or cooling stations and educate personnel on the symptoms of heat stress, dehydration, and how to respond 4...', '; **Emergency Contact Numbers:** - Display essential emergency contacts (e.g., 0412 133 777) for fire services, police, ambulance, and utilities prominently throughout the site - Ensure all personnel have ready access to these numbers via their phones or radios.']

   Search agent answer: Emergency contact numbers such as 0412 133 777 for fire services, police, ambulance, and utilities should be prominently displayed throughout the site. Ensure all personnel have ready access to these numbers via their phones or radios.
   ```

## Insights

  
- **Classification**: The conversation is classified as a 'general' query and flagged as "AMBIGUOUS-contact number." This ambiguity prompts the search agent to query different indexes (`vector-health` and `vector-safety`) to find relevant information.

- **Suggested Tool Calls**: The output shows two suggestions for tool calls to the `search_tool`, each targeting a specific index to find relevant details about the contact numbers.

- **Async Function Execution**: The conversation flow shows asynchronous function calls for `search_tool`, which loads necessary configurations and profiles before executing the search.

- **Search Results**: Two search results are returned, each providing detailed information such as emergency contact numbers and procedures for dealing with emergencies.

- **Response Generation**: The `search_agent` generates a response based on the search results, ensuring that the contact number is prominently displayed throughout the site for all personnel.

- **Memory Recording**: The script then records the conversation in memory for future reference, capturing both the user’s question and the corresponding response.

- **Error Handling**: In the sample, an error occurs due to a missing `reporter` function, prompting the `researcher` agent to summarize the conversation manually.

