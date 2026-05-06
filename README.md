Step 1: Check the converted files

Open File Explorer (Windows key + E) and go to your WolvenKit project folder. If you don't remember where you saved it, it's usually in your Documents folder under WolvenKit Projects.
Inside your project folder, click into the folder called source, then into raw. You should see folders called base and ep1 with more folders inside them.
Click around until you find some .json files. Right-click one and choose Open with → Notepad. You're looking for readable dialogue text — things like character names and lines of speech, with words like femaleVariant and maleVariant nearby.
If the file is full of confusing code with no readable dialogue, the WolvenKit conversion didn't finish. Go back to WolvenKit and redo the convert-to-JSON step before continuing.

Step 2: Install Python

Python is a free program that runs the script we'll use. You only need to install it once. Press the Windows key, type cmd, and press Enter. A black window will open. In that black window, type python and press Enter. The Microsoft Store will open to a Python page. Click the Install (or Get) button.
Wait for it to finish installing. Close the black window completely. We'll open a fresh one in the next step.

Step 3: Set up a folder for the script

Open File Explorer.
Go to your C: drive (in the left sidebar, click This PC, then double-click your C: drive).
Right-click in an empty space and choose New → Folder. Name it subs.
Save the compile_subtitles.py file into this new C:\subs folder.

Step 4: Open Command Prompt in the right place

Open File Explorer and navigate into C:\subs.
Click on the address bar at the top of the window (the part that shows the folder path). It will turn into an editable text box.
Delete what's there, type cmd, and press Enter.
A black window will open. It's already set to your C:\subs folder — you don't need to do anything else to "navigate" anywhere.

Step 5: Find the path to your converted files

You need to tell the script where your converted JSON files are. Here's the easiest way to get the right path:

Open another File Explorer window.
Navigate to your WolvenKit project folder, then into source, then raw.
Click the address bar at the top — it will show the full path.
Right-click and choose Copy. You'll paste this in the next step.

Step 6: Run the script

Go back to the black Command Prompt window from Step 4.
Type this exactly, including the quotes — but don't press Enter yet:

   python compile_subtitles.py "

Right-click in the black window to paste the path you copied. It should appear after the opening quote.
Type a closing quote and then output, so the whole line looks like this:

   python compile_subtitles.py "C:\Users\YourName\Documents\WolvenKit Projects\YourProject\source\raw" output

Press Enter.

Step 7: Find your subtitles

In File Explorer, go to C:\subs\output. You'll find:

all_lines.txt — every line of dialogue in one big file. Double-click to open it in Notepad.
by_quest — a folder containing one subfolder for each quest. Phantom Liberty quests start with ep1_. Inside each quest folder is a subtitles.txt file.

Lines look like this:
[41003] [F] V: Wasn't sure I would.  ||  [M] V: Wasn't sure I'd make it.
The [F] and [M] markers only show up when the female V and male V say something different. Most of the time they say the same thing and the line just appears once.
If something goes wrong
The black window says "'python' is not recognized" — close that window completely and open a fresh one. Python only becomes available in new windows opened after it was installed.
"Parsed 0 lines" — the WolvenKit conversion didn't actually work. Go back to Step 1, open one of the JSON files in Notepad, and confirm you can see readable dialogue. If you can't, the conversion step in WolvenKit needs to be redone.
Files showing up in a folder called _misc — nothing's broken. These are usually tutorial messages or generic background chatter whose filenames don't follow the standard quest naming pattern.
If you get stuck, copy the error message exactly and paste it back here and I'll help you sort it.
