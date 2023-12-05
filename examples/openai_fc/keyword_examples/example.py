import nexusraven

import sqlite3

# Example Adapted From: https://www.datacamp.com/tutorial/open-ai-function-calling-tutorial
client = nexusraven.Client(api_url = "INSERT YOUR URL", api_key = "INSERT YOUR KEY")

custom_functions = [
{
  "type" : "function",
  "function" : 
    {
        'name': 'extract_student_info',
        'description': 'Get the student information from the body of the input text',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'Name of the person'
                },
                'major': {
                    'type': 'string',
                    'description': 'Major subject.'
                },
                'school': {
                    'type': 'string',
                    'description': 'The university name.'
                },
                'grades': {
                    'type': 'integer',
                    'description': 'GPA of the student.'
                },
                'club': {
                    'type': 'string',
                    'description': 'School club for extracurricular activities. '
                }
                
            },
            "required" : ["name", "major", "school", "grades", "club"]
        }
    },
    },
    {
    "type" : "function",
    "function" : 
    {
        'name': 'extract_school_info',
        'description': 'Get the school information from the body of the input text',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'Name of the school.'
                },
                'ranking': {
                    'type': 'integer',
                    'description': 'QS world ranking of the school.'
                },
                'country': {
                    'type': 'string',
                    'description': 'Country of the school.'
                },
                'no_of_students': {
                    'type': 'integer',
                    'description': 'Number of students enrolled in the school.'
                }
            },
            "required" : ["name", "ranking", "country", "no_of_students"]
        }
    }}
]

school_1_description = "Stanford University is a private research university located in Stanford, California, United States. It was founded in 1885 by Leland Stanford and his wife, Jane Stanford, in memory of their only child, Leland Stanford Jr. The university is ranked #5 in the world by QS World University Rankings. It has over 17,000 students."
student_1_description = "David Nguyen is a sophomore majoring in computer science at Stanford University. He has a 3.8 GPA. David is known for his programming skills and is an active member of the university's Robotics Club. He hopes to pursue a career in artificial intelligence after graduating."

description = [student_1_description, school_1_description]
for i in description:
  response = client.chat.completions.create(
      messages = [{'role': 'user', 'content': i}],
      tools=custom_functions,
      include_reasoning = False,
      max_new_tokens=300,
  )
  print (response)


