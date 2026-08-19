from updater import update
from gui import SQLAlterApp

if __name__ == '__main__':
    # Check for updates
    try:
        update()
    except Exception:
        pass    # Dont quit the app in case of problem

    app = SQLAlterApp()
    app.mainloop()