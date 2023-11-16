import regex as re
FILENAME = './bolq.md'

class Book:
    # Object containing section objects.
    def __init__(self, filename=FILENAME):
        self.raw_text = ''
        self.introduction = []
        # A list of section objects.
        self.sections = self.get_sections(filename)
        self.make_links()

    def get_sections(self, filename):
        # Return a list of section objects
        sections = []
        with open(filename, 'r') as f:
            data = f.readlines()
            self.raw_text = data
            blob = []
            in_introduction = True
            start_of_chapter = False
            current_chapter = ''
            line_count = len(data)
            for index, line in enumerate(data):
                if not line.startswith('## Chapter 1') and in_introduction:
                    # If in part before the content begins.
                    self.introduction.append(line)
                    continue
                in_introduction = False
                if line.startswith('## '):
                    sections.append(Section(blob, index, start_of_chapter, current_chapter))
                    start_of_chapter = True
                    current_chapter = line
                    blob = []
                    continue
                if line.startswith('### '):
                    if blob == ['\n']:
                        # New chapters result in an additional newline to the section.
                        blob = []
                    # If information has accrued
                    if len(blob) > 1:
                        # Save the accrued blob as a section
                        sections.append(Section(blob, index, start_of_chapter, current_chapter))
                        start_of_chapter = False
                        blob = []
                    # Store new blob name
                    blob.append(line)
                if index == line_count - 1:
                    blob.append(line)
                    sections.append(Section(blob, index, start_of_chapter, current_chapter))

                else:
                    # In section, keep adding
                    blob.append(line)


        return sections

    def make_links(self):
        # For each section finds and connects the markdown-linked sections
        # Links must only be in preceeding part of document.

        for section in self.sections:
            for link in section.parent_names:
                for referenced_section in self.sections:
                    if referenced_section.linkable_name == link:
                        if referenced_section.line_number > section.line_number:
                            print(f'\nLink rule violation, must only link to prior sections:\
\n\tAt line {section.line_number}: section {section.title}\
\tA later section at line {referenced_section.line_number} was referenced: {referenced_section.title}')
                        else:
                            section.parents.append(referenced_section)



class Section:
    # The content of each section
    def __init__(self, section_lines, line_number, start_of_chapter, current_chapter):
        # List of line strings for the section
        self.raw_lines = section_lines
        # Line number in original document
        self.line_number = line_number
        # Number of lines the section occupies.
        self.line_count = None
        self.is_start_of_chapter = start_of_chapter
        self.chapter_name = current_chapter
        self.title = ''
        self.simple = ''
        self.middle = ''
        self.hard = ''
        self.linkable_name = ''
        # String names in markdown link convention (lowercase, hyphenated, no special)
        self.parent_names = []
        # Name compatible with .puml files (underscores replace hyphens)
        self.puml_name = ''
        self.link_count = None
        self.parents = []
        self.digest_raw()
        self.digest_links()
        self.diagram_rel_path = ''
        # Some sections don't have enought links to warrant connection diagrams.
        self.needs_diagram = False

    def __print__(self):
        return 'section with title', self.title

    def __repr__(self):
        completeness = ''
        if self.simple or self.middle or self.hard == 'TODO':
            completeness = f'(TODOs line {self.line_number}) '
        return f'Section {completeness} (links = {self.link_count}) on {self.title}'

    def digest_raw(self):
        '''
        Gets the three text areas from each section.
        Using start and end positions of each section based on reliable markers.
        '''
        simple_index = []
        middle_index = []
        hard_index = []

        for index, line in enumerate(self.raw_lines):
            if line.startswith('###'):
                self.title = line
            if line == '```md\n':
                simple_index = [index + 1]
            if line == '```\n':
                simple_index.append(index - 1)
                middle_index = [index + 2]
            if line.startswith('*'):
                hard_index = [index]
                middle_index.append(index - 2)
            if line.endswith('*\n'):
                hard_index.append(index)
        if len(simple_index) < 2:
            self.simple = 'TODO\n'
        else:
            # Save section based on where it is relative to the above index.
            simple_text =  self.raw_lines[simple_index[0]: simple_index[1] + 1]
            for x in simple_text:
                self.simple += x
        if len(middle_index) < 2:
            self.middle = 'TODO\n'
        else:
            # Save sections
            middle_text =  self.raw_lines[middle_index[0]: middle_index[1] + 1]
            for x in middle_text:
                self.middle += x
        if len(hard_index) < 2:
            self.hard = 'TODO\n'
        else:
            # Save sections
            hard_text =  self.raw_lines[hard_index[0]: hard_index[1] + 1]
            for x in hard_text:
                self.hard += x

        # Makes the markdown compliant name for this section
        linkable = re.sub(r'[!,*)@#%(&$_?.^]', '', self.title[4:].split('\n')[0])
        self.linkable_name = '#' + linkable.replace(' ','-').lower()
        self.puml_name = self.linkable_name.replace('-', '_').replace('#','').replace("'","")

    def digest_links(self):
        # Looks for markdown links and registers the relevant section.
        # Used for constructing Plant UML diagrams.

        pattern = re.compile(r'\[([^][]+)\](\(((?:[^()]+|(?2))+)\))')
        text = ''.join([self.middle, self.hard])
        for match in pattern.finditer(text):
            _, _, link = match.groups()
            self.parent_names.append(link)
        self.link_count = len(self.parent_names)

        # Check if any links are referencing later sections.
        # TODO


if __name__=="__main__":
    book = Book(FILENAME)
    print('done')
