from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
from pydantic import BaseModel

def setup_system_prompt():
    reader = PdfReader("DnD_BasicRules_2018.pdf")
    basics = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            basics += text

    game = "Dungeon and Dragons"
    system_prompt = f"You are acting as a game master for {game}. \
    Your responsibility is to provide the details of the great adventure \
    and control the flow of the {game}. Your task is to interact with user \
    on the website as engaging as possible. If any of the user's decision breaks \
    the rules, say so. Always provide User with at least 3 options to continue the story."
    system_prompt += f"\n\n## Rules: {basics}\n\n"
    system_prompt += f"With this context, please chat with the user. You should be \
    leading the chat, with what comes next like this is a standard video game. \
    Once the game started, continue the story based on user last reply."
    return system_prompt

def setup_eval_prompt():
    reader = PdfReader("DnD_BasicRules_2018.pdf")
    basics = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            basics += text

    game = "Dungeon and Dragons"
    eval_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
    You are provided with a conversation between a User and an Agent. Your task is to decide whether \
    the Agent's latest response is acceptable, which it follows the flow of the game. The response \
    must be answering to the latest reply from user. The Agent is playing the role of game master of \
    {game} and is instructed to be professional and engaging, as if talking to the video game player. \
    The Agent has been instructed to always provide User with mutliple options to continue the story. \
    The Agent has been provided with the context on {game}. Here's the information:"
    eval_prompt += f"\n\n## Rules: {basics}\n\n"
    eval_prompt += f"With this context, please evaluate the latest response, replying with whether the \
    response is acceptable and your feedback."
    eval_prompt += f"When the User chose the next step, generate the story with User choice and continue the game."
    eval_prompt += f"Reject the Agent if the message do not end with at least 3 options for User to choose."
    eval_prompt += f"Reject the Agent if the new message story do not continue from the history."
    return eval_prompt

def chat(message, history):
    system_prompt = setup_system_prompt()
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]

    response = ollama.chat.completions.create(
        model=model_name,
        messages=messages
    )
    reply = response.choices[0].message.content

    evaluation = evaluate(reply, message, history)

    rejects = []
    while not evaluation.is_acceptable:
        rejects.append(reply)
        print("Failed evaluation - retrying")
        print(evaluation.feedback)
        reply = rerun(reply, message, history, evaluation.feedback + f"Please try diffently than {rejects}")
    return reply

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt

def evaluate(reply, message, history) -> Evaluation:
    eval_prompt = setup_eval_prompt()
    messages = [{"role": "system", "content": eval_prompt}] + [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]

    response = ollama.chat.completions.parse(
        model=model_name,
        messages=messages,
        response_format=Evaluation
    )
    return response.choices[0].message.parsed

def rerun(reply, message, history, feedback):
    system_prompt = setup_system_prompt()
    updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply,\
    but the quality control rejected your reply.\n"
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    response = ollama.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return response.choices[0].message.content

if __name__=="__main__":
    load_dotenv(override=True)
    ollama = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    model_name = "llama3.2"
    
    gr.ChatInterface(chat).launch()