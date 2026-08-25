from typing import List
from agents import(
    function_tool,
)

@function_tool
def email_sender(to_list:list, cc_list:list, Subject:str, body:str):
    return "Failed to send email due to poor network connection"