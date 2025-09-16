quitting_commands = ['quit', 'q', 'exit']
changing_subject_commands = ['change subject', 'change', 'c']

def format_command_options(command_options):
    return ", ".join(f"'{s}'" for s in command_options[:-1]) + f", or '{command_options[-1]}'"

def is_quitting(user_input):
    return user_input in quitting_commands

def is_changing_subject(user_input):
    return user_input in changing_subject_commands

def print_instructions():
    print("To quit write " + format_command_options(quitting_commands))
    print("To change subject write " + format_command_options(changing_subject_commands))