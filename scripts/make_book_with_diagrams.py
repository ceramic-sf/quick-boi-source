from book_parser import Book
from diagram_generator import generate_single
'''
- Uses BOLQ.md data
- Generates diagrams
- Adds diagram links to their own sections
- Saves new markdown file

After running this file all the .puml files (diagrams/complete)

Maybe diagrams are only generated if link depth is > 2 to prevent too many diagrams.
'''


TARGET_DIR = ''
BASE_FILENAME = 'bolq_with_diagrams'

def write_section(file, section):
    # Generate the .puml
    generate_single(section)

    if section.is_start_of_chapter:
        file.write(f'{section.chapter_name}\n')
    file.write(section.title)
    file.write(f'\n```md\n{section.simple}```\n')
    file.write(f'\n{section.middle}')
    file.write(f'\n{section.hard}')
    if section.needs_diagram:
        file.write(f'\n![connections_for_{section.puml_name}](./{section.diagram_rel_path})\n\n')
    else:
        file.write('\n')

def generate_book_with_diagrams(book):
    # Make the new file.
    path = TARGET_DIR + BASE_FILENAME + '.md'

    with open(path, 'w') as file:
        [file.write(line) for line in book.introduction]
        [write_section(file, section) for section in book.sections]
    pass

if __name__=='__main__':
    book = Book()
    generate_book_with_diagrams(book)
    print(f'.puml files created. Markdown file with links made.\n\n\
        Please now generate the .svg files using .puml files in ./diagrams/complete')