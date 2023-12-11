from openai import OpenAI
import json
from calendarapi import CalendarAPI
from datetime import datetime
import os
import logging

class OpenAIAPI:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    tools = json.load(open("tools.json", "r"))
    

    def __init__(self, calendar: CalendarAPI) -> None:
        self.calendar = calendar
        self.messages = [
        {
            "role": "system",
            "content": f"Ты - ассистент, помогающий людям планировать свои дела. Перед вызовом функции убедись, что правильно понял человека, не додумывай аргументы. Уточни перед вызовом функции. Сейчас {datetime.now()}.",
        }
    ]
    def run_tool(self, tool_call):
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        logging.info(f"Running tool {function_name} with args {function_args}")
        match function_name:
            case "add_event_to_calendar":
                function_response = self.calendar.add_event_to_calendar(**function_args)
            case "get_events_at_time":
                function_response = self.calendar.get_events_at_time(**function_args)
            case "get_events_by_name":
                function_response = self.calendar.get_events_by_name(**function_args)
            case "remove_event_from_calendar":
                function_response = self.calendar.remove_event_from_calendar(**function_args)
            case _:
                function_response = "Неизвестная функция"
        self.messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )

    def run_conversation(self, message):
        self.messages.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
        response_message = response.choices[0].message
        self.messages.append(response_message)
        while response_message.tool_calls:
          tool_calls = response_message.tool_calls
          for tool_call in tool_calls:
              self.run_tool(tool_call)
          response = self.client.chat.completions.create(
              model="gpt-3.5-turbo-1106",
              messages=self.messages,
          )
          response_message = response.choices[0].message
        return response_message.content
