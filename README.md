# llama3.2_DnD_AI_text_game
This repo is to test the limit of llama3.2 running locally. The purpose is to play Dungeon &amp; Dragons game with AI agent and modify the instructions given to Agent to improve the user experience. This repo is developed in Linux Ubuntu 24.04 OS.

# Environment Setup
Repo
```
git clone https://github.com/TanJianKwang/llama3.2_DnD_AI_text_game.git
```

Conda setup
```
conda create -n DnD python==3.12.9
conda activate DnD
```

Ollama setup
```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

# Run
```
python main.py
```
Make sure the message is up: * Running on local URL:  http://127.0.0.1:7860

# Game
1. On web browser, visit http://127.0.0.1:7860
2. Type "start" to start the DnD text game with AI Agent.
3. For the next option, always copy and paste the full text of option. For example, type in "A) Talk to NPC" rather than just "A".
(Remember llama3.2 is not as powerful as ChatGPT Agent and won't be the perfect game master.)
5. Enjoy the game!
