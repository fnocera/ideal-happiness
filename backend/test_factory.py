# test_factory.py

import re
import os
import json
from openai import AzureOpenAI
import yaml

from openapi_to_functions import openapi_to_functions

class TestFactory:
    def __init__(self):
        self.openapi_spec_path = os.getenv('OPENAPI_SPEC_PATH', './openapi.yaml')
        self.intents_file_path = os.getenv('INTENTS_FILE_PATH', './intents.txt')
        self.output_file_path = os.getenv('OUTPUT_FILE_PATH', './output.json')
        self.azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_openai_key = os.getenv('AZURE_OPENAI_KEY')
        self.azure_openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-05-01-preview')
        self.azure_openai_deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        self.client = AzureOpenAI(
            azure_endpoint=self.azure_openai_endpoint, 
            api_key=self.azure_openai_key, 
            api_version=self.azure_openai_api_version
        )
        self.openapi_spec = self.load_openapi_spec()
        self.intents = self.load_intents()
        self.tools = openapi_to_functions(self.openapi_spec)

        # Initialize the Azure OpenAI client

    def load_openapi_spec(self):
        with open(self.openapi_spec_path, 'r') as f:
            return yaml.safe_load(f)

    def load_intents(self):
        with open(self.intents_file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def generate_for_intent(self, intent):
        # First API call: Get function calls
        prompt = (f"You are a test data generator. Given an OpenAPI spec that defines a set of tools and an intent, "
                 f"provide the function calls required. You may need to call MULTIPLE FUNCTIONS. If there are any "
                 f"parameters passed from one function call to the next mark these like <xxxx>.")
        function_call_messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Intent: {intent}"},
        ]

        # Make the initial API call to get function calls
        response = self.client.chat.completions.create(
            model=self.azure_openai_deployment_name,
            messages=function_call_messages,
            tools=self.tools,
            tool_choice="auto",
        )
        # print(response)

        # Process the model's response
        response_message = response.choices[0].message
        print(response_message)
        # messages.append(response_message)

        function_calls = []
        if not response_message.tool_calls:
            print("No function calls were made by the model.")

        # Handle function calls
        spec_messages = []
        for tool_call in response_message.tool_calls:

            # function_call = response_message["function_call"]
            # function_name = function_call["name"]
            # function_args = json.loads(function_call["arguments"])
            # print(f"Function called: {function_name}")
            # print(f"Function arguments: {function_args}")

            # Mark parameters passed from one function to the next with <xxx>
            # for key, value in function_args.items():
            #     if isinstance(value, str) and value.startswith('param_from_'):
            #         function_args[key] = f"<{value}>"

            function_args = json.loads(tool_call.function.arguments)

            function_call = {
                'name': tool_call.function.name,
                'arguments': function_args
            }
            function_calls.append(function_call)

            # Simulate function execution
            # function_response_content = json.dumps({
            #     "result": f"Simulated response for {function_name}"
            # })

            spec_messages.append({
                "role": "user",
                "content": str(function_call)
            })

        # Second API call: Get relevant portions of the OpenAPI spec
        spec_messages.append({
            "role": "user",
            "content": ("Provide the relevant portions of the below OpenAPI spec for the above function calls."
                        "They should be verbatim from the spec. Delimit them with two newlines.")
            })
        spec_messages.append({"role": "user", "content": json.dumps(self.openapi_spec)})
        response = self.client.chat.completions.create(
            model=self.azure_openai_deployment_name,
            messages=spec_messages
        )

        # Process the response to get spec portions
        response_message = response.choices[0].message
        print(response_message.content)
        spec_content = response_message.content.strip()
        # Assuming the spec portions are separated by two newlines
        spec_portions = spec_content.split('\n\n')

        # Validate spec portions
        valid_spec_portions = []
        openapi_spec_str = re.sub(r'\s+', ' ', json.dumps(self.openapi_spec).replace("\\n", ""))
        bypass_validation = True
        for portion in spec_portions:
            if re.sub(r'\s+', ' ', portion.replace("\\n", "")) in openapi_spec_str or bypass_validation:
                valid_spec_portions.append(portion)

        return function_calls, valid_spec_portions

    def persist_output(self, intent, corrected_function_calls):
        if os.path.exists(self.output_file_path):
            with open(self.output_file_path, 'r') as f:
                output_data = json.load(f)
        else:
            output_data = {}

        output_data[intent] = corrected_function_calls

        with open(self.output_file_path, 'w') as f:
            json.dump(output_data, f, indent=2)
