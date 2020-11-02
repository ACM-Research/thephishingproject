import uuid, os, sys

# validate args
if len(sys.argv) != 3:
    print('Usage: {} [directory] [.extension]'.format(__file__))
    exit()

# init filenames from directory and extension
dir, ext = sys.argv[1:]

filenames = os.listdir(dir)
filenames = [fn for fn in filenames if os.path.splitext(fn)[1] == ext]

# ask for confirmation
print('\n'.join(filenames) + '\n')
while True:
    print('Are you ABSOLUTELY sure you want to rename the above files? [Y/n]: ')

    ans = input().strip()
    if ans.upper() == 'N':
        print('Cancelled!')
        exit()
    elif ans.upper() == 'Y':
        break

# rename and log new names
for fn in filenames: 
    oldFn = os.path.join(dir, fn)
    # new file name is last 12 chars
    newFn = os.path.join(dir, '{} {}{}'.format(
                str(uuid.uuid4())[-12:], 
                fn[:15].strip(), 
                ext)
    )
    print(oldFn, '\n  ->', newFn)
    os.rename(oldFn, newFn)


print('Done.')