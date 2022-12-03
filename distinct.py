import distinctipy
import json


def main() -> None:
    square = 8

    pastels = [
        distinctipy.distinctipy.get_rgb256(colour)
        for colour in distinctipy.get_colors(square**2, pastel_factor=0.7)  # type: ignore
    ]

    with open("distincts.json", "w") as f:
        json.dump(pastels, f)


if __name__ == "__main__":
    main()
