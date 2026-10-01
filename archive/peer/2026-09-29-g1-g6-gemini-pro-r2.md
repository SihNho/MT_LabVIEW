# g1-g6-gemini-pro-r2

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-29 20:24:34
- **outcome:** ANSWERED (50s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

On an NTFS volume in Windows, a file is deleted and a new file with the same name is then created in the same folder shortly afterwards. What creation timestamp does the new file have, and what is the mechanism called?

Search the web and cite the URL of every source you used.

## Answer

The new file receives the **original creation timestamp** of the deleted file.

This mechanism is called **File System Tunneling**.

**Reasoning:**
When a file is deleted or renamed on an NTFS (or FAT) volume, Windows caches its metadata—including the creation timestamp and short file name—for a brief period, which defaults to 15 seconds. If a new file with the exact same name is created in the same folder during this window, Windows applies the cached metadata to the newly created file instead of assigning it a fresh creation timestamp. 

This behavior exists by design to support the "safe save" process used by many applications. Programs often save changes by writing to a temporary file, deleting the original, and then renaming the temporary file to the original file's name. Without tunneling, this process would constantly destroy the file's original creation date every time it was saved.

**Sources:**
- [The apocryphal history of file system tunnelling](https://devblogs.microsoft.com/oldnewthing/20050715-00/?p=34923) (Raymond Chen, Microsoft Developer Blog)
- [Why does Windows keep the original creation date when I delete and recreate a file?](https://superuser.com/questions/431411/why-does-windows-keep-the-original-creation-date-when-i-delete-and-recreate-a-fi) (Super User discussion on the safe-save mechanism and the 15-second window)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
