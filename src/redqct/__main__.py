from typing import List
from redqct.lib import cube, Number


def main() -> None:
    print("Running main!")
    xs: List[Number] = [42, 69, 8.21]
    cubes = [cube(x) for x in xs]
    print(f"The cubes of {xs} are {cubes}")


if __name__ == "__main__":
    main()
