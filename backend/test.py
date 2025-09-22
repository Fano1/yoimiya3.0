import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional
from protocol import sysPrompt, toolList, toolMap, api_key

class Schema(BaseModel):
    reply: str = Field(..., description="Model's natural language reply")
    tool_used: Optional[str] = Field(None, description="Tool invoked, if any")
    emotion: str = Field(..., description="Emotion of the reply")

# Conversation state  
conversation = []

# Load environment
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = api_key

def init():
    base_model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        top_p=0.9,
        top_k=40,
        max_output_tokens=1024,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        },
        verbose=False,
        disable_streaming=True
    )
    
    tool_model = base_model.bind_tools(toolList)
    structured_model = base_model.with_structured_output(Schema)
    return tool_model, structured_model

def aiMsg(model, user_input, history=None):
    """Send message and get structured response with tool support"""
    global conversation
    
    prompt_messages = ChatPromptTemplate.from_messages([
        ("system", sysPrompt),
        ("human", "{inputr}")
    ]).format_messages(inputr=user_input)
    
    if history:
        conversation.extend(history)
    conversation.extend(prompt_messages)
    
    tool_model, structured_model = init()
    
    # Get model response for tool detection
    response = tool_model.invoke(conversation)
    

    if response.tool_calls:
        conversation.append(AIMessage(content=response.content))
        
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]
        
        result = str(toolMap[tool_name](tool_args))
        tool_msg = ToolMessage(content=result, tool_call_id=tool_id)
        conversation.append(tool_msg)
        
        final_response = structured_model.invoke(conversation)
        
        conversation.append(AIMessage(content=final_response.reply))
        
        final_response.tool_used = tool_name
        return final_response
    
    else:
        structured_response = structured_model.invoke(conversation)
        conversation.append(AIMessage(content=structured_response.reply))
        return structured_response

toolBind = init()

if __name__ == "__main__":
    while True:
        inp = input(">> ")
        if inp.lower() in ['quit', 'exit']:
            break
        result = aiMsg(toolBind, inp)
        print(f"Reply: {result.reply}")
        if result.tool_used:
            print(f"Tool used: {result.tool_used}")
        print(f"Emotion: {result.emotion}")