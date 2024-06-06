"""
This module contains the instructions for the task.
"""

INSTRUCTIONS = """
INSTRUCTIONS:
You are a medical policy expert. I will provide you with the position statement for a medical policy. Each policy includes one or several medical acts ("medical_act") with a degree of necessity ("necessity_type") such as Medically Necessary, Not Medically Necessary, Investigational and Not Medically Necessary, Cosmetic, etc. The policy also includes compliance criteria that must be met.

Your task is to extract the different criteria logic schemas and output them in JSON format.

For conditions that must all be met, use the "ALL" logic operator. For conditions where any one can be met, use the "ANY" logic operator. If no specific conditions are provided, set "conditions" to null.

For example:

Input:
--Example Procedure 1--
Investigational and Not Medically Necessary:
The procedure is considered investigational and not medically necessary under the specified conditions.

Output:
[
  {{
    "medical_act": "Example Procedure 1",
    "sub_medical_act": null,
    "necessity_type": "Investigational and Not Medically Necessary",
    "description": "The procedure is considered investigational and not medically necessary under the specified conditions.",
    "conditions": null
  }}
]

Input:
--Example Procedure 2--
Medically Necessary:
<li>The procedure is considered medically necessary when all of the following criteria are met: <ol> <li>Condition A; and</li> <li>Condition B; and</li> <li>When one of the following is true: <ol start="1" style="list-style-type:lower-alpha"> <li>Condition C; or</li> <li>Condition D.</li> </ol> </li> </ol> </li>

Output:
[
  {{
    "medical_act": "Example Procedure 2",
    "sub_medical_act": null,
    "necessity_type": "Medically Necessary",
    "description": "The procedure is considered medically necessary when all of the following criteria are met:",
    "conditions": {{
      "ALL": [
        {{ "desc": "Condition A", "conditions": null }},
        {{ "desc": "Condition B", "conditions": null }},
        {{
          "ANY": [
            {{ "desc": "Condition C", "conditions": null }},
            {{ "desc": "Condition D", "conditions": null }}
          ]
        }}
      ]
    }}
  }}
]

Input:
--Example Procedure 3--
Medically Necessary:
<li>The procedure is considered medically necessary when the following criteria are met: <ol> <li>Condition X; and</li> <li>Condition Y.</li> </ol> </li>
<li>The procedure is considered medically necessary for pediatric patients when the following criteria are met: <ol> <li>Condition P; and</li> <li>Condition Q.</li> </ol> </li>

Output:
[
  {{
    "medical_act": "Example Procedure 3",
    "sub_medical_act": "Adult",
    "necessity_type": "Medically Necessary",
    "description": "The procedure is considered medically necessary when the following criteria are met:",
    "conditions": {{
      "ALL": [
        {{ "desc": "Condition X", "conditions": null }},
        {{ "desc": "Condition Y", "conditions": null }}
      ]
    }}
  }},
  {{
    "medical_act": "Example Procedure 3",
    "sub_medical_act": "Pediatric",
    "necessity_type": "Medically Necessary",
    "description": "The procedure is considered medically necessary for pediatric patients when the following criteria are met:",
    "conditions": {{
      "ALL": [
        {{ "desc": "Condition P", "conditions": null }},
        {{ "desc": "Condition Q", "conditions": null }}
      ]
    }}
  }}
]
"""
