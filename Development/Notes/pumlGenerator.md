# Puml Function Decomposition/Dataflow Generator Plan:

Input: Source code files, currently Java, however we will try to make it more universal, following certain patterns that define functions.

Output: puml file, which is a text representation of a uml diagram. The uml diagram can then be compiled by a Plantuml generator.

Comments: We will see if a dark mode colouration can be created, maybe we could alternate between light and dark mode uml shown, based on the theme selected by the user.

We would need to use a CI/CD workflow to take the .puml files and generate the diagrams which are then inserted into the markdown.