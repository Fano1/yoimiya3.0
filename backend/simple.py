import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from protocol import sysPrompt, toolList, toolMap, api_key

# Structured output schema 
class Schema(BaseModel):
    reply: str = Field(..., description="Model's natural language reply")
    tool_used: Optional[str] = Field(None, description="Tool invoked, if any")
    emotion: str = Field(..., description="Emotion of the reply regarding the context, one of [neutral, angry, fun, joy, sorrow, surprised, flirty, extremespicy]")

# Session-based conversation state
conversations: Dict[str, List] = {}

#  Load environment
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = api_key

# Initialize models
def init():
    base_model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        top_p=0.9,
        top_k=40,
        max_output_tokens=1024,
        # FIXED: Less restrictive safety settings
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.OFF,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.OFF,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.OFF,
        },
        verbose=False,
        disable_streaming=True
    )

    tool_model = base_model.bind_tools(toolList)
    structured_model = base_model.with_structured_output(Schema, method="json_schema")
    return tool_model, structured_model

# session-aware message handling 
def aiMsg(tool_model, structured_model, user_input, session_id="default", history=None):
    global conversations
    
    # Initialize session conversation if it doesn't exist
    if session_id not in conversations:
        conversations[session_id] = [SystemMessage(content=sysPrompt)]
    
    conversation = conversations[session_id]
    
    # Add history if provided and conversation is fresh (only system prompt)
    if history and len(conversation) == 1:
        for msg in history[-10:]:  # Limit history to prevent context overflow
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                conversation.append(HumanMessage(content=content))
            elif role == "assistant":
                conversation.append(AIMessage(content=content))
    
    conversation.append(HumanMessage(content=user_input))
    
    #  (system prompt + last 20 messages)
    if len(conversation) > 21:
        conversation = [conversation[0]] + conversation[-20:]  # Keep system prompt + recent messages
    
    try:
        # Invoke model (tool-aware)
        response = tool_model.invoke(conversation)

        # tool handling 
        if getattr(response, "tool_calls", None) and len(response.tool_calls) > 0:
            conversation.append(AIMessage(content=response.content or ""))
            tool_call = response.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            # execute tool
            try:
                tool_result = str(toolMap[tool_name](tool_args))
            except Exception as e:
                tool_result = f"Tool execution failed: {str(e)}"
            
            conversation.append(ToolMessage(content=tool_result, tool_call_id=tool_id))

            # get structured response after tool execution
            final_response = structured_model.invoke(conversation)
            if final_response is None or getattr(final_response, "reply", None) is None:
                final_response = Schema(
                    reply="Hmm, something went wrong there. Let me try again! 😏",
                    tool_used=tool_name,
                    emotion="neutral"
                )
            else:
                final_response.tool_used = tool_name
            
            conversation.append(AIMessage(content=final_response.reply))

        else:
            # no tool used, just structured output
            final_response = structured_model.invoke(conversation)
            if final_response is None or getattr(final_response, "reply", None) is None:
                final_response = Schema(
                    reply="Hey there! I'm having a bit of trouble responding right now, but I'm still here! 😉",
                    tool_used=None,
                    emotion="flirty"
                )
            conversation.append(AIMessage(content=final_response.reply))

    except Exception as e:
        print(f"Error in aiMsg for session {session_id}: {str(e)}")
        final_response = Schema(
            reply="Oops! Something went a bit haywire on my end. Mind trying that again? 😏",
            tool_used=None,
            emotion="fun"
        )

    # update the global conversation fuking state
    conversations[session_id] = conversation
    
    # return as JSON
    return json.dumps(final_response.dict(), ensure_ascii=False)

# reset specific session 
def reset_conversation(session_id="default"):
    global conversations
    if session_id in conversations:
        del conversations[session_id]