# Author: fellaini27
# https://github.com/abhin-T

# V1.0

# Binds a weapon mod to a specific character

# Usage: Requires name of character and 'position_vb' hash of said character
#        as arguments. Need to run script inside of a folder containing only
#        ONE .ini file. The script will disable the old .ini file and create
#        a new one that binds the weapon mod to the character that you want.

import os
import argparse

def main():
    # creating command line argument
    parser = argparse.ArgumentParser(description="Limits a weapon mod to a specific character")
    parser.add_argument('char', metavar='CHARACTER', type=str, help='character name')
    parser.add_argument('char_hash', metavar='HASH', type=str, help='position hash for character')
    args = parser.parse_args()

    char = args.char
    char_hash = args.char_hash

    # Code taken from Murren#0001 in BindModToCharacter.py (finds .ini file)
    print("Finding .ini...")
    ini_file = [x for x in os.listdir("./") if ".ini" in x and "DISABLED" not in x]
    if len(ini_file) != 1:
        print("Error finding .ini. Make sure there is only one .ini file in the folder.")
        return
    print(".ini found!")
    file = ini_file[0]

    constants = '; Constants -------------------------\n'
    overrides = '; Overrides -------------------------\n'
    resources = '; Resources -------------------------\n'
    newline = '\n'

    with open(file, 'r') as f:
        old_config = f.readlines()

    # Disables old .ini file
    os.rename(file, "DISABLED{filename}".format(filename = file))
    print("Disabling old .ini file")

    # checks for title in .ini file
    try:
        new_config = list(old_config[0])
    except IndexError:
        print('Config file is not in correct format')
        return

    # adding constants section
    new_config.append(newline)
    new_config.append(constants)
    new_config.append(newline)
    new_config.append('[Constants]\n')
    new_config.append('global $active = 0\n')
    new_config.append(newline)
    new_config.append('[Present]\n')
    new_config.append('post $active = 0\n')
    new_config.append(newline)

    print("Added constants section")

    # checks for overrides and resources sections in file
    try:
        overrides_line_index = old_config.index(overrides)
        resources_line_index = old_config.index(resources)
    except ValueError:
        print('Config file is not in correct format')
        return

    overrides_section = old_config[overrides_line_index:resources_line_index]

    # Rewrites the whole overrides section with conditionals depending on the
    # $active variable. Takes care of a few edge cases aswell.
    index = 0
    while index < len(overrides_section):
        line = overrides_section[index]
        if line.startswith('hash') and index+1 < len(overrides_section) and \
                overrides_section[index+1].startswith('$'):
            index+=4
            continue
        if line != 'endif\n':
            new_config.append(line)
        if line.startswith('hash') and index+1 < len(overrides_section) and \
                overrides_section[index+1] != '\n' and \
                not overrides_section[index+1].startswith('['):
            new_config.append('if $active==1\n')
            while (index+1) < len(overrides_section) and \
                overrides_section[index+1] != '\n' and \
                not overrides_section[index+1].startswith('['):
                index+=1
                if overrides_section[index] == '\tmatch_priority = 1\n' or \
                        overrides_section[index] == 'endif\n':
                    break
                if overrides_section[index].startswith('if'):
                    continue
                elif overrides_section[index].startswith('\t'):
                    new_config.append(overrides_section[index])
                    continue
                tabbed_line = "\t{old_line}".format(old_line = overrides_section[index])
                new_config.append(tabbed_line)
            new_config.append('\tmatch_priority = 1\n')
            new_config.append('endif\n')
        index+=1

    print("Added all conditionals")

    # Changes active variable to 1 when the specific character is active
    new_config.append('[TextureOverride{Character}Position]\n'.format(Character = char))
    hash_line = "hash = {char_hash}\n".format(char_hash = char_hash)
    new_config.append(hash_line)
    new_config.append('$active=1\n')
    new_config.append('match_priority = 1\n')
    new_config.append(newline)

    print("Added [TextureOverride{Character}Position]".format(Character = char))

    # Copies rest of the old .ini file
    new_config.extend(old_config[resources_line_index:])

    print("Copied all resources")

    # Creates new config file with appropriate adjustments
    new_file = file
    with open(new_file, 'w') as f:
        f.writelines(new_config)

    print("Done! Now the weapon containing the ini file: {filename}, is bound "
          "to {char}.".format(filename = new_file, char = char))

if __name__ == "__main__":
    main()
