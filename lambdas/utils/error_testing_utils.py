import json
import os

def check_manual_error_conditions(type: str):
    if type == "TIMEOUT":
        trigger_timeout_error()
    if type == "MEMORY":
        trigger_memory_error()


def trigger_memory_error(): 
    memoryBreakString = 'string_length_to_double_each_iteration'
    for x in range(1000000000000000000000000000000000):
        memoryBreakString = memoryBreakString

def trigger_timeout_error():
    memoryBreakString = 'string_to_set_each_iteration'
    for x in range(1000000000000000000000000000000000):
        memoryBreakString = memoryBreakString
