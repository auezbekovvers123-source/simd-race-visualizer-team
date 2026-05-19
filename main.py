"""Entry point — Person 1 owns this file."""

from person1.app_shell import SimdScalarRaceApp


def main() -> None:
    app = SimdScalarRaceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
