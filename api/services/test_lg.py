import diff_match_patch as dmp_module

if __name__ == "__main__":
    dmp = dmp_module.diff_match_patch()
    diff = dmp.diff_main("Hello World.", "Hello World..")
    # Result: [(-1, "Hell"), (1, "G"), (0, "o"), (1, "odbye"), (0, " World.")]
    dmp.diff_cleanupSemantic(diff)
    # Result: [(-1, "Hello"), (1, "Goodbye"), (0, " World.")]
    print(diff)
