Root cause is the reader: the base-class Constant.Value read (read_str / OpConstValue_v1, class 'Constant') returns a void/empty variant for non-String (here array) constants, so gate A1b could not pass regardless of the write.
Test separates 'reader blind' from 'write failed': read #101 through a type-aware route (a property node of its specific class, e.g. ArrayConstant; an indicator wired to it and a run) or read a known-filled array constant with the same reader.
VERDICT: change NEXT
DEFECT: major - stub