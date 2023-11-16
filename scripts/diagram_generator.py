from book_parser import Book

"""
Creates a plant UML (.puml) diagram showing the links between concepts in BOLQ.
A diagram can contain a set of concepts to display, some of which may have common
connections. See ./puml_demo.puml for format
"""

TARGET_DIR = 'diagrams/complete/'
BASE_FILENAME = 'bolq_diagram_'

def add_sections_to_file(section_list, name):
    path = TARGET_DIR + BASE_FILENAME + name + '.puml'


    with open(path, 'w') as file:
        file.write('@startuml ' + BASE_FILENAME + name)

        for section in section_list:
            # Add section details
            file.write(f'\n\nobject {section.puml_name} ' + '{')
            file.write(f'\n{section.simple}')
            file.write('____')
            hard = section.hard.replace('*','')
            file.write(f'\n{hard}')
            file.write('}')

            # Add connections
            for parent in section.parents:
                file.write(f'\n{parent.puml_name} <-- {section.puml_name}')

            # Record diagram location
            unique = f'{BASE_FILENAME}{name}'
            section.diagram_rel_path = f'out/{TARGET_DIR}{unique}/{unique}.svg'


        file.write('\n@enduml')

def generate_single(section):
    # Accepts book and sections objects.
    # Walk the tree of nodes, breadth first
    included = [section]
    queue  = [section]
    while queue:
        next = queue.pop(0)
        for parent in next.parents:
            if parent not in included:
                included.append(parent)
                queue.append(parent)

    # Determine if diagram is needed.
    if len(section.parents) > 0:
        section.needs_diagram = True
        '''
        # For less diagrams.
        # If any parent link itself has a parent link, make diagram.
        for parent in section.parents:
            if len(parent.parents) != 0:
                section.needs_diagram = True
        '''

    if section.needs_diagram:
        add_sections_to_file(included, section.puml_name)

def generate_by_name(book, name):
    # Supply underscore style name and generate a graph of linked concepts
    main_section = None
    for candidate in book.sections:
        if candidate.puml_name == name:
            main_section = candidate
    generate_single(main_section)

if __name__=="__main__":
    book = Book()
    # Test one diagram:
    # generate_by_name(book, 'brains_are_universal_turing_machines')
    print('done')



# A .puml file will have a header and footer and then for each section an object
# The connections are individually recorded (parent --> child) and can be placed anywhere
# The script will append them chronologically.

"""
@startuml BOLQ_concept_diagram
object concept_a_name {
    A description
}
object concept_b_name {
    B description
}
concept_a_name --> concept_b_name
@enduml
"""