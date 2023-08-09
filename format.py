
def format(data):
    names = []
    for i in data:
        names.append(i.split('/')[-1])

    result = ['https://t.me/' + name.lstrip('@') for name in names]

    return result