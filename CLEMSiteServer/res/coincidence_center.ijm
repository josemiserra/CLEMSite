arg = getArgument()
print("Running batch analysis with arguments:")
print(arg)
run("Batch process", arg )
print("Done.")
eval("script", "System.exit(0);");

run("Smooth");
