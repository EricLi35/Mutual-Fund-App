import concurrent.futures

def func1(input1):
    pass


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    msgs = executor.map(func1, [i for i in range(10)])
