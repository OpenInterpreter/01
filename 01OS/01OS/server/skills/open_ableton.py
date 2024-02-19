def openAbleton():
    """open ableton"""

    import os
    os.system("open /Applications/Ableton\ Live\ 10\ Suite.app")


    import os

    # Search can be slow if there are many files
    # This will search in the Applications folder only
    applications = "/Applications/"

    # walk function will generate the file names in a directory tree
    # We will look for any application that contains "Ableton" in its name
    for foldername, subfolders, filenames in os.walk(applications):
        for filename in filenames:
            if "Ableton" in filename:
                ableton_path = os.path.join(foldername, filename)
                break

    ableton_path


    os.system("open /Applications/Ableton\ Live\ 11\ Intro.app")
