# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Custom HTML builder.

This is used to verify that snippets do not get stale.

See http://www.sphinx-doc.org/en/stable/extdev/tutorial.html to learn
how to write a custom Sphinx extension.
"""

from sphinx.writers import html


import json
import os


VISITED = []
DOCS_DIR = os.path.abspath(os.path.dirname(__file__))
LITERALS_FI = os.path.join(DOCS_DIR, 'literals.json')


class CustomHTMLWriter(html.SmartyPantsHTMLTranslator):
    """Custom HTML writer.

    This makes sure that code blocks are all tested. It does this by
    asserting that a code block has a language other than Python **OR**
    that the code block has test node type ``doctest``.
    """

    def visit_literal_block(self, node):
        """Visit a ``literal_block`` node.

        This verifies the state of each literal / code block.
        """
        node_info = {
            'source': node.attributes.get('source'),
            'language': node.attributes.get('language'),
            'testnodetype': node.attributes.get('testnodetype'),
            'line': node.line,
            'node-source': node.source,
        }
        # NOTE: We could also use self.builder.info(...)
        VISITED.append(node_info)
        with open(LITERALS_FI, 'w') as file_obj:
            json.dump(VISITED, file_obj, sort_keys=True,
                      indent=2, separators=(',', ': '))
            file_obj.write('\n')
        # The base classes are not new-style, so we can't use super().
        return html.SmartyPantsHTMLTranslator.visit_literal_block(self, node)
