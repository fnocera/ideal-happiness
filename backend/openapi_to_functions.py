import jsonref
import re

def openapi_json_to_functions(openapi_spec_path):
    with open('openapi_spec_path', 'r') as f:
        openapi_spec = jsonref.loads(f.read())
        return openapi_to_functions(openapi_spec, using_json_ref=True)

def openapi_to_functions(openapi_spec, using_json_ref=False):
    functions = []
    for path, methods in openapi_spec["paths"].items():
        for method, spec_with_ref in methods.items():
            # 1. Resolve JSON references.
            if using_json_ref:
                spec = jsonref.replace_refs(spec_with_ref)
            else:
                spec = spec_with_ref

            # 2. Extract a name for the functions.
            function_name = spec.get("operationId", "")
            if not re.match(r'^[a-zA-Z0-9_-]+$', function_name):
                raise ValueError(f"Invalid operationId '{function_name}' in path '{path}' and method '{method}'")

            # 3. Extract a description and parameters.
            desc = spec.get("description") or spec.get("summary", "")

            schema = {"type": "object", "properties": {}}

            req_body = (
                spec.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema")
            )
            if req_body:
                schema["properties"]["requestBody"] = req_body

            params = spec.get("parameters", [])
            if params:
                param_properties = {
                    param["name"]: param["schema"]
                    for param in params
                    if "schema" in param
                }
                schema["properties"]["parameters"] = {
                    "type": "object",
                    "properties": param_properties,
                }

            functions.append(
                {"type": "function", "function": {"name": function_name, "description": desc, "parameters": schema}}
            )

    print(functions)
    return functions

# def get_functions_from_openapi(self):
    #     """Generate functions (tools) from the OpenAPI spec."""
    #     functions = []
    #     paths = self.openapi_spec.get('paths', {})
    #     for path, methods in paths.items():
    #         for method, details in methods.items():
    #             # Construct function name, e.g., "get_flights"
    #             function_name = f"{method}_{path.strip('/').replace('/', '_')}"
    #             description = details.get('summary', 'No description available')
    #             parameters = details.get('parameters', [])
    #             request_body = details.get('requestBody', {})
    #             # Build parameters schema
    #             params_schema = {
    #                 "type": "object",
    #                 "properties": {},
    #                 "required": []
    #             }
    #             for param in parameters:
    #                 param_name = param.get('name')
    #                 param_required = param.get('required', False)
    #                 param_schema = param.get('schema', {"type": "string"})
    #                 param_description = param.get('description', '')
    #                 params_schema['properties'][param_name] = {
    #                     "type": param_schema.get('type', 'string'),
    #                     "description": param_description
    #                 }
    #                 if param_required:
    #                     params_schema['required'].append(param_name)
    #             # Handle request body parameters
    #             if request_body:
    #                 content = request_body.get('content', {})
    #                 for media_type, media_details in content.items():
    #                     schema = media_details.get('schema', {})
    #                     if schema.get('type') == 'object':
    #                         for prop_name, prop_details in schema.get('properties', {}).items():
    #                             params_schema['properties'][prop_name] = {
    #                                 "type": prop_details.get('type', 'string'),
    #                                 "description": prop_details.get('description', '')
    #                             }
    #                             if prop_name in schema.get('required', []):
    #                                 params_schema['required'].append(prop_name)
    #             function = {
    #                 "name": function_name,
    #                 "description": description,
    #                 "parameters": params_schema
    #             }
    #             functions.append(function)
    #     return functions