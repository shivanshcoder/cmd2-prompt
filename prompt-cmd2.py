import cmd2
import re

from prompt_toolkit.completion import Completer, Completion, WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory      
from prompt_toolkit import PromptSession

class MyCompleter(Completer):

    def __init__(self, app):
        self.app = app

    def get_completions(self, document, complete_event):

        if True:
            the_text = document.text_before_cursor


            if len(document.text):
                last_word = the_text.split().pop()
            else:
                last_word = ""

            
            if the_text.endswith(" "):
                last_word = ""
                mydoc = Document("", 0)

            else:
                mydoc = document

            self.app.completer_func(last_word, the_text, len(the_text) - len(last_word), len(the_text))
            
            completer = WordCompleter(self.app.completion_matches, pattern=re.compile(r"([a-zA-Z0-9_\\\/]+|[^a-zA-Z0-9_\s]+)"))

            for words in completer.get_completions(mydoc, complete_event):  
                word_text = words.text
                if word_text.endswith('\\') or word_text.endswith('/'):
                    words.text = word_text[:-1]
                yield words


class PromptCmd(cmd2.Cmd):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.myhistory = FileHistory(".example-history-file")
        self.mysession = PromptSession(history=self.myhistory)
        self.mycompleter = MyCompleter(self)


    def completer_func(self, text, my_orig_line, org_begidx, orig_endidx):

        orig_line = my_orig_line
        line = orig_line.lstrip()
        num_stripped = len(orig_line) - len(line)
      
        begidx = max(org_begidx - num_stripped, 0)
        endidx = max(orig_endidx - num_stripped, 0)

        shortcut_to_restore = ''
        if begidx == 0:
            for (shortcut, _) in self.statement_parser.shortcuts:
                if text.startswith(shortcut):
                    # Save the shortcut to restore later
                    shortcut_to_restore = shortcut
                    # Adjust text and where it begins
                    text = text[len(shortcut_to_restore):]
                    begidx += len(shortcut_to_restore)
                    break
        from cmd2.argparse_completer import _NoResultsError
        try:

            if begidx > 0:
                self._completion_for_command(text, line, begidx, endidx, shortcut_to_restore)
            else:
                from cmd2 import utils
                match_against = self._get_commands_aliases_and_macros_for_completion()
                self.completion_matches = utils.basic_complete(text, line, begidx, endidx, match_against)
        
        except _NoResultsError:
            self.completion_matches = []

            # Maybe later on print the hint statement in a toolbar
            #print("HINT")
            
    def read_input(self, prompt: str, *, allow_completion: bool = False) -> str:
        if allow_completion:
            from prompt_toolkit.completion import WordCompleter
            return self.mysession.prompt(prompt, completer=self.mycompleter)
        else:
            return input(prompt).rstrip('\r\n')



class BasicApp(PromptCmd):
    CUSTOM_CATEGORY = 'My Custom Commands'

    def __init__(self):
        super().__init__(multiline_commands=['echo'],
                         startup_script='scripts/startup.txt', use_ipython=True)

        self.intro = "Example for prompt-Cmd" 

        # Allow access to your application in py and ipy via self
        self.self_in_py = True

        # Set the default category name
        self.default_category = 'cmd2 Built-in Commands'

    
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_intro(self, arg):
        """Display the intro banner"""

        self.complete(arg.args,0)
        self.poutput(self.completion_matches)

    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_echo(self, arg):
        """Example of a multiline command"""
        self.poutput(arg)


if __name__ == '__main__':
    app = BasicApp()
    app.cmdloop()
