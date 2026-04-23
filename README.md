# AZØR TRAINING

- gemini-CLI
  - download Gemini CLI: https://github.com/google-gemini/gemini-cli
  - set up Gemini API key: https://aistudio.google.com/app/api-keys
- open router: https://openrouter.ai/workspaces/
- openAI: https://platform.openai.com/settings/organization/billing/overview
- SDKs:
  - python (download platform): https://www.python.org/downloads/
  - nodejs (download platform): https://nodejs.org/en/download

## Question

(!) What are the patterns / tricks to overcome limitations of the context window?

- short-term memory vs long-term memory?
- who needs planning (such as in cursor, claude code, etc)
- how do commands work (cursor, claude code)
- claude code uses codebase indexing / vector dbs. Claude Code doesn't. What's the tradeoff behind it?
- how subagents works and how to use them efficiently
- what tooling is being used when running a model locally?
- how does an AI API/SDK know where to send requests?
- how to make a jailbreak?

## Design/Implementation exercises

- [IMPL] SUPPORT PARAMETERS (top p, top k, temperature) for client APIs used in Azor
- [DESIGN/IMPL] MORE ASSISTANTS / CHANGE THE ASSISTANT
  - the session should have information about the selected assistant (the assistant is defined per session)
    - when saving a session, not only the conversation history is saved, but also the assistant
    - when loading an old session – similarly
    - changing the assistant during a session leaves a trace in the conversation history so that the model knows in subsequent steps that a change has occurred (then, based on the prompt system, it will better understand the context)
- [DESIGN/IMPL] PROVIDE SESSION TITLE:
  - You should give the conversation a TITLE, so that when you search for a conversation from the list, you can see the title in addition to the ID.
    - Design a solution - who, when, and how determines the title?
    - Minimalist variant - a separate shot at the model at the beginning of the thread...
    - Do your research and design a solution to see how the "minimalist" variant can be improved.
  - **persistence**: the conversation title is stored and saved in the session (and the session file).
  - The title can be changed (e.g., based on the new command `/session rename NEW_TITLE`)
  - It can also be previewed (e.g., based on the new command `/session title` -> `EXISTING_TITLE`)
- [DESIGN/IMPL] CLARIFY QUESTION/TASK
  - gives the model the ability to ask the user when something is unclear:
    - the user wants something from the model
    - the model responds with a question, giving, for example, 4 options to choose from (like perplexity)
    - the user selects one of the options
    - the model finally responds
- [DESIGN] AUTONOMUOUS CONVERSATION BETWEEN 2 ASSISTANTS
  - initially human sets the topic via prompt
  - human interaction is done
  - assistant 1 answers to human prompt
  - assistant 2 answers to assistant 1
  - assistant 1 answers to assistant 2
  - assistant 2 answers to assistant 1
  - assistant 1 answers to assistant 2
  - ...
  - human can only close the conversation somehow (SIGINT, whatever)
