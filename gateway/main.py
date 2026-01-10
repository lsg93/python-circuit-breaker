import time

from fastapi import FastAPI

app = FastAPI()


def main():
    print("Hello from gateway!")
    print(time.time())


if __name__ == "__main__":
    main()
