# g1-g6-gemini-pro-r1

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-29 20:23:39
- **outcome:** ANSWERED (43s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

On an NTFS volume in Windows, a file is deleted and a new file with the same name is then created in the same folder shortly afterwards. What creation timestamp does the new file have, and what is the mechanism called?

Search the web and cite the URL of every source you used.

## Answer

**Creation Timestamp:** The new file inherits the creation timestamp of the *original deleted file*.
**Mechanism:** **File System Tunneling** (or NTFS Tunneling).

**Reasoning:**
Windows temporarily caches the metadata of a deleted or renamed file (including its creation timestamp) for a short period—typically 15 seconds by default. If a new file is created with the exact same name in the same directory within that time window, the operating system applies the cached metadata to the new file. 

This is an intentional feature designed to support applications that perform "safe saves" (i.e., saving data to a temporary file, deleting the original file, and then renaming the temporary file to the original name). Without tunneling, the creation timestamp would constantly reset to the "save" time, which can confuse users or break software that relies on the original creation date.

**Sources:**
- Microsoft Developer Blog, Raymond Chen: ["The apocryphal history of file system tunnelling"](https://devblogs.microsoft.com/oldnewthing/20050715-14/)
- [SuperUser: Why does a new file share the same creation time as a deleted file with the same name?](https://superuser.com/questions/172314/why-does-a-new-file-share-the-same-creation-time-as-a-deleted-file-with-the-same)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
