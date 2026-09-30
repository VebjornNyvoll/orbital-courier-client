"""Print a cargo label. We will turn this function into a CLI together."""


def label(item: str):
    print(f"Cargo: {item}")


if __name__ == "__main__":
    label("food")
