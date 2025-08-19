from openai import OpenAI
from qes_utils.chalk import print_warning, print_colorfully
import json
from typing import Protocol, Optional, List, Dict, Any


class OpenAIConfig(Protocol):
    """Protocol describing the required attributes for an OpenAI config object."""
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: Optional[str]
    MODEL_NAME: Optional[str]




class OpenAIClient():

    client: Optional[OpenAI] = None
    model: str = ''
    messages: List[Dict[str, Any]]
    tools: List[Any]
    temperature: float = 0.1  # Default temperature for creativity
    openai_config: OpenAIConfig

    def __init__(self, model: Optional[str], system_prompt: Optional[str] = None,
                 tools: List[Any] = None, temperature: float = 0.1,
                 messages: List[Dict[str, Any]] = None, openai_config: OpenAIConfig= None,**kwargs):
        self.model = model or ''
        self.tools = tools or []
        self.temperature = temperature
        self.messages = messages or []  # Initialize messages
        self.openai_config = openai_config
        # Roles: system, user, assistant, tool
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def init(self):
        cfg = self.openai_config
        self.client = OpenAI(
            api_key=cfg.OPENAI_API_KEY,  # Set your OpenAI API key here or use environment variable
            base_url=cfg.OPENAI_BASE_URL,  # Set your OpenAI base URL here if needed
        )

    def add_message(self, role, content):
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})

    def add_message_for_obj(self, message_obj):
        self.messages.append(message_obj)

    def embeddings(self, input_texts):
        """Get embeddings for the input texts."""
        if not self.client:
            return
        print(f"Getting embeddings for model: {self.model}")
        response = self.client.embeddings.create(
            model=self.model,
            input=input_texts
        )
        return [item['embedding'] for item in response.data]

    def invoke(self, prompt, stream=True):
        if not self.client:
            return
        print(f"Invoking LLM with model: {self.model}")
        print(f"Question: {prompt}")
        self.messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,  # Use the inputs list as messages
            stream=stream,  # Set to True if you want to stream the response
            # max_tokens=150,  # Adjust the max tokens as needed
            temperature=self.temperature,  # Adjust the temperature for creativity
            tools=self.tools,  # Add tools if any
            tool_choice='auto',  # Automatically choose the best tool
            parallel_tool_calls=True  # Enable parallel tool calls if needed,
        )
        if (not stream):
            context = response.choices[0].message.content.strip()
            print(f"Response: {context}")
            return context
        else:
            # If streaming, handle the response as a generator
            result = ''
            for chunk in response:
                if len(chunk.choices) >= 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        print(f"{delta.content}", end='')
                        result += delta.content

            return result

    async def invoke_stream(self, prompt, enable_thinking=True):
        print(f"Invoking LLM with model: {self.model}")
        print(f"Question: {prompt}")
        if prompt is not None:
            self.messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,  # Use the inputs list as messages
            stream=True,  # Set to True if you want to stream the response
            # max_tokens=150,  # Adjust the max tokens as needed
            temperature=self.temperature,  # Adjust the temperature for creativity
            tools=self.tools,  # Add tools if any
            tool_choice='auto',  # Automatically choose the best tool
            parallel_tool_calls=True,  # Enable parallel tool calls if needed,
            extra_body={
                "enable_thinking": enable_thinking,  # Enable thinking process
                "thinking_budget": 200
            },  # Enable thinking process
        )

        # If streaming, handle the response as a generator
        result = ''
        tool_calls = []
        for chunk in response:
            if len(chunk.choices) >= 0:
                # Available options: stop, eos, length, tool_calls
                # 处理结束信号
                finish_reason = chunk.choices[0].finish_reason
                if (finish_reason is not None):
                    print(print_warning(
                        f'\n\nfinish_reason: {finish_reason}\n'))
                    if (finish_reason == 'stop'):
                        yield f'data: [DONE] \n\n'
                        break
                    if (finish_reason == 'tool_calls'):
                        self.messages.append(
                            {"role": "assistant", "content": result, "tool_calls": tool_calls})
                        yield f'data: {{"type":"tool_calls", "content":{json.dumps(tool_calls)}}}\n\n'
                        yield f'data: [DONE] \n\n'

                        break
                delta = chunk.choices[0].delta

                # 处理工具调用
                # 一个工具调用可能会有多个chunk,参数需要拼接
                if delta.tool_calls is not None:
                    print(f'\nfunction_call: {delta.tool_calls}')
                    for tool_call in delta.tool_calls:
                        t = [i for i, item in enumerate(
                            tool_calls) if item['index'] == tool_call.index]
                        if len(t) > 0:
                            tool_calls[t[0]]["function"]["arguments"] += tool_call.function.arguments
                        else:
                            tool_calls.append({
                                "id": tool_call.id,
                                "index": tool_call.index,
                                "type": tool_call.type,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            })
                        print(
                            f"Tool call: {tool_call.id} {tool_call.function.name}({tool_call.function.arguments})")
                        # yield f'data: {{"type":"tool_call", "content":{tool_call}}}\n'
                    # yield f'data: {{"type":"function_call", "content":{delta.function_call}}}\n'
                    # continue

                # 处理思考过程
                if (delta.model_extra is not None):
                    reasoning = delta.model_extra.get(
                        'reasoning_content', None)
                    if reasoning:
                        print(f"{print_colorfully(reasoning, 'gray')}", end='')
                        yield f'data: {{"type":"think", "content":"{reasoning}"}}\n\n'

                # 处理返回内容
                if delta.content:
                    print(f"{print_colorfully(delta.content)}", end='')

                    result += delta.content
                    yield f'data: {{"type":"reply", "content":"{delta.content}"}}\n\n'
        # print(f"\nFinal Response: {result}")
        # Final yield for result and tool_calls if needed
        # yield f'data: {{"type":"final", "result":{json.dumps(result)}, "tool_calls":{json.dumps(tool_calls)}}}\n\n'
