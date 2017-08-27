import json
import re

# Regular expression for comments
comment_re = re.compile(
    r'^[^\S\n]*//[^\n]*$',
    re.DOTALL | re.MULTILINE
)

def parse_json(filename):
    """ Parse a JSON file with comments
        First remove comments and then use the json module package
    """
    with open(filename) as f:
        content = ''.join(f.readlines())

        # Looking for comments
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)
        # Return json file
        return json.loads(content)