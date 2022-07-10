'''
Python script to convert files using \r\n as their newline characters to only use \n.
This is used to ensure parsing of resource files is not dependent on specific newline characters used.
'''

kInputFilename = 'splinter_base_types.txt'
kOutputFilename = 'splinter_base_types_no_carriage_return.txt'

def main():
    lines = []
    with open(kInputFilename) as f:
        for line in f:
            lines.append(line.strip())
    with open(kOutputFilename, 'w', newline='') as f:
        f.write('\n'.join(lines))

if (__name__ == '__main__'):
    main()