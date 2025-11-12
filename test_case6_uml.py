#!/usr/bin/env python3
"""CASO 6: Generar Diagrama UML desde Codigo"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.ai.agents.meta.uml_generator_agent import UMLGeneratorAgent

print("CASO 6: Generar Class Diagram desde codigo Python\n")

agent = UMLGeneratorAgent(config=None)

codigo = """
class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def login(self):
        return True

class Admin(User):
    def __init__(self, email, password, permissions):
        super().__init__(email, password)
        self.permissions = permissions

    def grant_permission(self, user, permission):
        user.permissions.append(permission)
"""

result = agent.generate_class_diagram(code=codigo)

print(f"Success: {result.success}")
print(f"Method: {result.generation_method}")
print(f"Diagram type: {result.diagram_type}")
print(f"\nClasses found: {codigo.count('class ')}")
print(f"Methods found: {codigo.count('def ')}")

if result.success:
    print("\nPlantUML code generated:")
    print("-" * 50)
    print(result.plantuml_code)
    print("-" * 50)
