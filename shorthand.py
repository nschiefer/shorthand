import gui
import database

if __name__ == "__main__":
    d = database.Database(database.NOTES_FOLDER)
    app = gui.Base(d)
    app.main()
