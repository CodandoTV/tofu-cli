import os
import shutil

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completion, Completer


# Auto-suggestion for search existing modules
class SearchCompleter(Completer):
    def __init__(self, words):
        self.words = words

    def get_completions(self, document, complete_event):
        # Get the current word the user has typed
        text = document.text_before_cursor.lower()

        # Suggest words that start with the typed text
        for word in self.words:
            if word.lower().startswith(text):
                yield Completion(word, start_position=-len(text))


def find_folders_with_build_gradle_script(root_path):
    matching_folders = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        if "build.gradle.kts" in filenames:  # Check if the file exists in the current folder
            matching_folders.append(dirpath)

    return matching_folders


def convert_module_path_to_module_name(module, folder_path):
    module_name = module.replace(folder_path, "").replace("/", ":")
    return module_name


def convert_module_name_to_module_path(module_name, folder_path):
    module_path = folder_path + module_name.replace(":", "/")
    return module_path


def main():
    folder_path = os.getcwd()
    directories_modules = find_folders_with_build_gradle_script(root_path=folder_path)

    search_suggestions = []

    for module in directories_modules:
        module_name = convert_module_path_to_module_name(module=module, folder_path=folder_path)
        search_suggestions.append(module_name)

    completer = SearchCompleter(search_suggestions)

    print("What module you want to use as base:")

    # Use the completer in the prompt
    base_module_name = prompt('Search: ', completer=completer)

    new_module_name = input("Type the new module name. You should use the pattern :module:my-feature:\n")

    new_module_path = convert_module_name_to_module_path(module_name=new_module_name, folder_path=folder_path)

    # Create the new directory where the module will live
    os.makedirs(new_module_path)

    # Copy existing build.gradle.kts to this new module
    build_gradle_base_module_path = convert_module_name_to_module_path(module_name=base_module_name,
                                                                       folder_path=folder_path) + "/" + "build.gradle.kts"
    shutil.copy2(build_gradle_base_module_path, new_module_path)

    # Update settings.gradle.kts adding the new module
    with open(folder_path + "/" + "settings.gradle.kts", "a") as file:
        file.write("include(\"" + new_module_name + "\")")

    # Display the chosen input
    print("Now you just need to sync your project...")


if __name__ == "__main__":
    main()
