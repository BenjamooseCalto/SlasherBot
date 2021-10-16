# no matter what number you enter here, it will always converge to a loop of 4 > 2 > 1. This script stops at 1.


def magicmath(number):

    start = number
    list = []
    steps = []

    def threex(n=int):
        step = 0
        while True:
            step += 1
            if n == 1:
                return False
            if n % 2 == 0:
                n = n / 2
            else:
                n = n * 3 + 1
            n = int(n)
            steps.append(step)
            list.append(n)

    threex(number)

    maximum = max(list) if start < max(list) else start
    diff = maximum / number

    if start == maximum:
        return f"{number:,} converged to 1 in {len(steps):,} steps, with the starting value being the maximum value."
    else:
        return f"{number:,} converged to 1 in {len(steps):,} steps with {maximum:,} being the highest value. This is {int(diff)}x bigger than the starting value."
