import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_core.messages import HumanMessage, ToolMessage
from langchain.prompts import ChatPromptTemplate
from protocol import sysPrompt, toolList, toolMap, api_key

#   Conversation state  
conversation = []

# Load environment
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = api_key

def init():
    #   Safety settings  
    safety_settings = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.OFF,
    }

    #   Initialize Gemini model  
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        top_p=0.9,
        top_k=40,
        max_output_tokens=1024,
        safety_settings=safety_settings,
        verbose=False,
        disable_streaming=True  # safer for scripts
    )

    #   Bind tools  
    toolBind = model.bind_tools(toolList)
    return toolBind

toolBind = init()

def aiMsg(toolBind, user_input):
    #   Build prompt messages  
    prompt_messages = ChatPromptTemplate.from_messages([
        ("system", sysPrompt),
        ("human", "{inputr}")
    ]).format_messages(inputr=user_input)

    #   Add messages to conversation  
    conversation.extend(prompt_messages)

    #   Model turn  
    msg = toolBind.invoke(conversation)
    conversation.append(msg)

    #   Handle tool calls if any  
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        result = str(toolMap[tool_name](tool_args))
        tool_msg = ToolMessage(content=result, tool_call_id=tool_id)
        conversation.append(tool_msg)

        # Model reacts after tool output
        fres = toolBind.invoke(conversation)
        conversation.append(fres)
        print(fres.content)
        return fres.content

    else:
        print(msg.content)
        return msg.content
