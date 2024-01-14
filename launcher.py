import subprocess

PROCESS = []


def main():
    while True:
        answer = input("Выберите действие: q - выход, s - запустить сервер и клиенты, x - закрыть все окна: ")

        if answer == "q":
            break
        elif answer == "x":
            for proc in PROCESS:
                proc.kill()
        elif answer == "s":
            PROCESS.append(subprocess.Popen(["python", "server.py"]))

            for _ in range(5):
                PROCESS.append(subprocess.Popen(["python", "client.py"]))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
