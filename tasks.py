from server.task import Task

tasks = []

task1 = Task("./montage-tasks-js/mProjectPP", ["-x", "0.99330", "-X", "2mass-atlas-990502s-j1420198.fits", "p2mass-atlas-990502s-j1420198.fits", "big_region.hdr"])
inFiles  = ["2mass-atlas-990502s-j1420198.fits", "big_region.hdr"]
outFiles = ["p2mass-atlas-990502s-j1420198.fits", "p2mass-atlas-990502s-j1420198_area.fits"]
task1.input_files(inFiles)
task1.output_files(outFiles)
tasks.append(task1)

task2 = Task("./montage-tasks-js/mProjectPP", ["-x", "0.99339", "-X", "2mass-atlas-990502s-j1420186.fits", "p2mass-atlas-990502s-j1420186.fits", "big_region.hdr"])
inFiles  = ["2mass-atlas-990502s-j1420186.fits", "big_region.hdr"]
outFiles = ["p2mass-atlas-990502s-j1420186.fits","p2mass-atlas-990502s-j1420186_area.fits"]
task2.input_files(inFiles)
task2.output_files(outFiles)
tasks.append(task2)

task3 = Task("./montage-tasks-js/mProjectPP", ["-x", "0.99321", "-X", "2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1430080.fits", "big_region.hdr"])
inFiles  = ["2mass-atlas-990502s-j1430080.fits", "big_region.hdr"]
outFiles = ["p2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1430080_area.fits"]
task3.input_files(inFiles)
task3.output_files(outFiles)
tasks.append(task3)

task4 = Task("./montage-tasks-js/mProjectPP", ["-x", "0.99321", "-X", "2mass-atlas-990502s-j1430092.fits", "p2mass-atlas-990502s-j1430092.fits", "big_region.hdr"])
inFiles  = ["2mass-atlas-990502s-j1430080.fits", "big_region.hdr"]
outFiles = ["p2mass-atlas-990502s-j1430092.fits", "p2mass-atlas-990502s-j1430092_area.fits"]
task4.input_files(inFiles)
task4.output_files(outFiles)
tasks.append(task4)

task5 = Task("./montage-tasks-js/mDiff", ["p2mass-atlas-990502s-j1420198.fits", "p2mass-atlas-990502s-j1420186.fits", "diff.000001.000002.fits", "big_region.hdr"])
inFiles = ["p2mass-atlas-990502s-j1420198.fits", "p2mass-atlas-990502s-j1420198_area.fits", "p2mass-atlas-990502s-j1420186.fits", "p2mass-atlas-990502s-j1420186_area.fits", "big_region.hdr"]
outFiles = ["diff.000001.000002.fits", "fit.000001.000002.txt"]
task5.input_files(inFiles)
task5.output_files(outFiles)
task5.depends_on(task1)
task5.depends_on(task2)
tasks.append(task5)

task51 = Task("./montage-tasks-js/mFitplane", ["diff.000001.000002.fits"])
inFiles = ["diff.000001.000002.fits"]
outFiles = ["diff.000001.000002.fits"]
task51.input_files(inFiles)
task51.output_files(outFiles)
task51.depends_on(task5)
tasks.append(task51)

task6 = Task("./montage-tasks-js/mDiff", ["p2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1420198.fits", "diff.000001.000003.fits", "big_region.hdr"])
inFiles = ["p2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1430080_area.fits", "p2mass-atlas-990502s-j1420198.fits", "p2mass-atlas-990502s-j1420198_area.fits", "big_region.hdr"]
outFiles = ["diff.000001.000003.fits", "fit.000001.000003.txt"]
task6.input_files(inFiles)
task6.output_files(outFiles)
task6.depends_on(task1)
task6.depends_on(task3)
tasks.append(task6)

task61 = Task("./montage-tasks-js/mFitplane", ["diff.000001.000003.fits"])
inFiles = ["diff.000001.000003.fits"]
outFiles = ["diff.000001.000003.fits"]
task61.input_files(inFiles)
task61.output_files(outFiles)
task61.depends_on(task6)
tasks.append(task61)

task7 = Task("./montage-tasks-js/mDiff", ["p2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1420186.fits", "diff.000002.000003.fits", "big_region.hdr"])
inFiles = ["p2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1430080_area.fits", "p2mass-atlas-990502s-j1420186.fits", "p2mass-atlas-990502s-j1420186_area.fits", "big_region.hdr"]
outFiles = ["diff.000002.000003.fits", "fit.000002.000003.txt"]
task7.input_files(inFiles)
task7.output_files(outFiles)
task7.depends_on(task2)
task7.depends_on(task3)
tasks.append(task7)

task71 = Task("./montage-tasks-js/mFitplane", ["diff.000002.000003.fits"])
inFiles = ["diff.000002.000003.fits"]
outFiles = ["diff.000002.000003.fits"]
task71.input_files(inFiles)
task71.output_files(outFiles)
task71.depends_on(task7)
tasks.append(task71)

task8 = Task("./montage-tasks-js/mDiff", ["p2mass-atlas-990502s-j1430092.fits", "p2mass-atlas-990502s-j1420186.fits", "diff.000002.000004.fits", "big_region.hdr"])
inFiles = ["p2mass-atlas-990502s-j1430092.fits", "p2mass-atlas-990502s-j1430092_area.fits", "p2mass-atlas-990502s-j1420186.fits", "p2mass-atlas-990502s-j1420186_area.fits", "big_region.hdr"]
outFiles = ["diff.000002.000004.fits", "fit.000002.000004.txt"]
task8.input_files(inFiles)
task8.output_files(outFiles)
task8.depends_on(task2)
task8.depends_on(task4)
tasks.append(task8)

task81 = Task("./montage-tasks-js/mFitplane", ["diff.000002.000004.fits"])
inFiles = ["diff.000002.000004.fits"]
outFiles = ["diff.000002.000004.fits"]
task81.input_files(inFiles)
task81.output_files(outFiles)
task81.depends_on(task8)
tasks.append(task81)

task9 = Task("./montage-tasks-js/mDiff", ["p2mass-atlas-990502s-j1430092.fits", "p2mass-atlas-990502s-j1430080.fits", "diff.000003.000004.fits", "big_region.hdr"])
inFiles = ["p2mass-atlas-990502s-j1430092.fits", "p2mass-atlas-990502s-j1430092_area.fits", "p2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1430080_area.fits", "big_region.hdr"]
outFiles = ["diff.000003.000004.fits", "fit.000003.000004.txt"]
task9.input_files(inFiles)
task9.output_files(outFiles)
task9.depends_on(task3)
task9.depends_on(task4)
tasks.append(task9)

task91 = Task("./montage-tasks-js/mFitplane", ["diff.000003.000004.fits"])
inFiles = ["diff.000003.000004.fits"]
outFiles = ["diff.000003.000004.fits"]
task91.input_files(inFiles)
task91.output_files(outFiles)
task91.depends_on(task9)
tasks.append(task91)

task10 = Task("./montage-tasks-js/mConcatFit", ["statfile.tbl", "fits.tbl", "."])
inFiles = ["statfile.tbl", "fits.tbl", "fit.000001.000002.txt", "fit.000001.000003.txt", "fit.000002.000003.txt", "fit.000002.000004.txt", "fit.000003.000004.txt"]
outFiles = ["corrections.tbl"]
task10.input_files(inFiles)
task10.output_files(outFiles)
task10.depends_on(task51)
task10.depends_on(task61)
task10.depends_on(task71)
task10.depends_on(task81)
task10.depends_on(task91)
tasks.append(task10)

task11 = Task("./montage-tasks-js/mBgModel", ["-i", "100000", "pimages.tbl", "fits.tbl", "corrections.tbl"])
inFiles = ["pimages.tbl", "fits.tbl"]
outFiles = ["corrections.tbl"]
task11.input_files(inFiles)
task11.output_files(outFiles)
task11.depends_on(task10)
tasks.append(task11)

task12 = Task("./montage-tasks-js/mBackground", ["-t", "p2mass-atlas-990502s-j1420198.fits", "c2mass-atlas-990502s-j1420198.fits", "pimages.tbl", "corrections.tbl"])
inFiles = ["p2mass-atlas-990502s-j1420198.fits""p2mass-atlas-990502s-j1420198_area.fits", "pimages.tbl", "corrections.tbl"]
outFiles = ["c2mass-atlas-990502s-j1420198.fits", "c2mass-atlas-990502s-j1420198_area.fits"]
task12.input_files(inFiles)
task12.output_files(outFiles)
task12.depends_on(task1)
task12.depends_on(task11)
tasks.append(task12)

task13 = Task("./montage-tasks-js/mBackground", ["-t", "p2mass-atlas-990502s-j1420186.fits", "c2mass-atlas-990502s-j1420186.fits", "pimages.tbl", "corrections.tbl"])
inFiles = ["p2mass-atlas-990502s-j1420186.fits""p2mass-atlas-990502s-j1420186_area.fits", "pimages.tbl", "corrections.tbl"]
outFiles = ["c2mass-atlas-990502s-j1420186.fits", "c2mass-atlas-990502s-j1420186_area.fits"]
task13.input_files(inFiles)
task13.output_files(outFiles)
task13.depends_on(task2)
task13.depends_on(task11)
tasks.append(task13)

task14 = Task("./montage-tasks-js/mBackground", ["-t", "p2mass-atlas-990502s-j1430080.fits", "c2mass-atlas-990502s-j1430080.fits", "pimages.tbl", "corrections.tbl"])
inFiles = ["p2mass-atlas-990502s-j1430080.fits""p2mass-atlas-990502s-j1430080_area.fits", "pimages.tbl", "corrections.tbl"]
outFiles = ["c2mass-atlas-990502s-j1430080.fits", "c2mass-atlas-990502s-j1430080_area.fits"]
task14.input_files(inFiles)
task14.output_files(outFiles)
task13.depends_on(task3)
task14.depends_on(task11)
tasks.append(task14)

task15 = Task("./montage-tasks-js/mBackground", ["-t", "p2mass-atlas-990502s-j1430092.fits", "c2mass-atlas-990502s-j1430092.fits", "pimages.tbl", "corrections.tbl"])
inFiles = ["p2mass-atlas-990502s-j1430092.fits""p2mass-atlas-990502s-j1430092_area.fits", "pimages.tbl", "corrections.tbl"]
outFiles = ["c2mass-atlas-990502s-j1430092.fits", "c2mass-atlas-990502s-j1430092_area.fits"]
task15.input_files(inFiles)
task15.output_files(outFiles)
task13.depends_on(task4)
task15.depends_on(task11)
tasks.append(task15)

task16 = Task("./montage-tasks-js/mImgtbl", [".", "-t", "cimages.tbl", "newcimages.tbl"])
inFiles = ["cimages.tbl", "c2mass-atlas-990502s-j1420198.fits", "c2mass-atlas-990502s-j1420186.fits", "c2mass-atlas-990502s-j1430080.fits", "c2mass-atlas-990502s-j1430092.fits"]
outFiles = ["newcimages.tbl"]
task16.input_files(inFiles)
task16.output_files(outFiles)
task16.depends_on(task12)
task16.depends_on(task13)
task16.depends_on(task14)
task16.depends_on(task15)
tasks.append(task16)

task17 = Task("./montage-tasks-js/mAdd", ["-e", "newcimages.tbl", "region.hdr", "mosaic.fits"])
inFiles = ["newcimages.tbl", "region_hdr", "c2mass-atlas-990502s-j1420198.fits", "c2mass-atlas-990502s-j1420186.fits", "c2mass-atlas-990502s-j1430080.fits", "c2mass-atlas-990502s-j1430092.fits", "c2mass-atlas-990502s-j1420198_area.fits", "c2mass-atlas-990502s-j1420186_area.fits", "c2mass-atlas-990502s-j1430080_area.fits", "c2mass-atlas-990502s-j1430092_area.fits"]
outFiles = ["mosaic.fits", "mosaic_area.fits"]
task17.input_files(inFiles)
task17.output_files(outFiles)
task17.depends_on(task12)
task17.depends_on(task13)
task17.depends_on(task14)
task17.depends_on(task15)
task17.depends_on(task16)
tasks.append(task17)

#task18 = Task("./montage-tasks-js/mShrink", ["mosaic.fits", "shrunken.fits", "1"])
#inFiles = ["mosaic.fits"]
#outFiles = ["shrunken.fits"]
#task18.input_files(inFiles)
#task18.output_files(outFiles)
#task18.depends_on(task17)
#tasks.append(task18)


task19 = Task("./montage-tasks-js/mJPEG", ["-ct", "1", "-gray", "mosaic.fits", "min", "max", "gaussianlog", "-out", "mosaic.jpg"])
inFiles = ["mosaic.fits"]
outFiles = ["mosaic.jpg"]
task19.input_files(inFiles)
task19.output_files(outFiles)
#task19.depends_on(task18)
task19.depends_on(task17)
tasks.append(task19)






