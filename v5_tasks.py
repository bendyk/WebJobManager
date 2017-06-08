from server.task import Task

tasks = []

#task = Task("./montage-tasks-js/mArchiveList.js", ["2MASS", "J", "275.1964", "-16.1717", "eq", "j2000", "0.20", "0.20", "remote_big.tbl"])
#task.input_files([])
#task.output_files(["remote_big.tbl"])
#tasks.append(task)

#task = Task("./montage-tasks-js/mSubset.js", ["-f", "remote_big.tbl", "region.hdr", "remote.tbl"])
#task.input_files(["remote_big.tbl"])
#task.output_files(["remote.tbl"])
#tasks.append(task)

#task = Task("./montage-tasks-js/mArchiveExec.js", ["remote.tbl"])
#task.input_files(["remote.tbl"])
#task.output_files()
#tasks.append(task)

#task = Task("./montage-tasks-js/mArchiveGet.js", ["http://irsa.ipac.caltech.edu/ibe/data/twomass/full/full/990502"])
#task.input_files(["remote.tbl"])
#task.output_files()
#tasks.append(task)


#1 path:mArchiveList cmdv[0]:mArchiveList || cmdv[1]:2MASS || cmdv[2]:J || cmdv[3]:275.1964 -16.1717 eq j2000 || cmdv[4]:0.20 || cmdv[5]:0.20 || cmdv[6]:remote_big.tbl || cmdc:7
#  2 path:mSubset cmdv[0]:mSubset || cmdv[1]:-f || cmdv[2]:remote_big.tbl || cmdv[3]:region.hdr || cmdv[4]:remote.tbl || cmdc:5
#  3 path:mArchiveExec cmdv[0]:mArchiveExec || cmdv[1]:../remote.tbl || cmdc:2
#  4 path:mArchiveGet cmdv[0]:mArchiveGet || cmdv[1]:http://irsa.ipac.caltech.edu/ibe/data/twomass/full/full/990502s/s142/image/ji1420198.fits.gz || cmdv[2]:2mass-atlas-990502s-j14    20198.fits || cmdc:3
#  5 path:mArchiveGet cmdv[0]:mArchiveGet || cmdv[1]:http://irsa.ipac.caltech.edu/ibe/data/twomass/full/full/990502s/s142/image/ji1420186.fits.gz || cmdv[2]:2mass-atlas-990502s-j14    20186.fits || cmdc:3
#  6 path:mArchiveGet cmdv[0]:mArchiveGet || cmdv[1]:http://irsa.ipac.caltech.edu/ibe/data/twomass/full/full/990502s/s143/image/ji1430080.fits.gz || cmdv[2]:2mass-atlas-990502s-j14    30080.fits || cmdc:3
#  7 path:mImgtbl cmdv[0]:mImgtbl || cmdv[1]:-c || cmdv[2]:. || cmdv[3]:rimages_full.tbl || cmdc:4
#  8 path:mCoverageCheck cmdv[0]:mCoverageCheck || cmdv[1]:rimages_full.tbl || cmdv[2]:rimages.tbl || cmdv[3]:-header || cmdv[4]:region.hdr || cmdc:5
task1 = Task("./montage-tasks-js/mProjectPP", ["-b", "1", "-x", "0.99330", "-X", "2mass-atlas-990502s-j1420198.fits", "p2mass-atlas-990502s-j1420198.fits", "big_region.hdr"])
inFiles  = ["2mass-atlas-990502s-j1420198.fits", "big_region.hdr"]
outFiles = ["p2mass-atlas-990502s-j1420198.fits"]
task1.input_files(inFiles)
task1.output_files(outFiles)
tasks.append(task1)

task2 = Task("./montage-tasks-js/mProjectPP", ["-b", "1", "-x", "0.99339", "-X", "2mass-atlas-990502s-j1420186.fits", "p2mass-atlas-990502s-j1420186.fits", "big_region.hdr"])
inFiles  = ["2mass-atlas-990502s-j1420186.fits", "big_region.hdr"]
outFiles = ["p2mass-atlas-990502s-j1420186.fits"]
task2.input_files(inFiles)
task2.output_files(outFiles)
tasks.append(task2)

task3 = Task("./montage-tasks-js/mProjectPP", ["-b", "1", "-x", "0.99321", "-X", "2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1430080.fits", "big_region.hdr"])
inFiles  = ["2mass-atlas-990502s-j1430080.fits", "big_region.hdr"]
outFiles = ["p2mass-atlas-990502s-j1430080.fits"]
task3.input_files(inFiles)
task3.output_files(outFiles)
tasks.append(task3)

task4 = Task("./montage-tasks-js/mImgtbl", ["-c", "projected", "pimages.tbl"])
outFiles = ["pimages.tbl"]
task4.output_files(outFiles)
task4.depends_on(task1)
task4.depends_on(task2)
task4.depends_on(task3)
tasks.append(task4)

task5 = Task("./montage-tasks-js/mOverlaps", ["pimages.tbl", "diffs.tbl"])
inFiles = ["pimages.tbl"]
outFiles = ["diffs.tbl"]
task5.input_files(inFiles)
task5.output_files(outFiles)
task5.depends_on(task4)
tasks.append(task5)

task6 = Task("./montage-tasks-js/mDiff", ["p2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1420198.fits", "diff.000000.000001.fits", "big_region.hdr"])
inFiles = ["p2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1420198.fits", "big_region.hdr"]
outFiles = ["diff.000000.000001.fits"]
task6.input_files(inFiles)
task6.output_files(outFiles)
task6.depends_on(task1)
task6.depends_on(task3)
tasks.append(task6)

task7 = Task("./montage-tasks-js/mFitplane", ["diff.000000.000001.fits"])
inFiles = ["diff.000000.000001.fits"]
outFiles = ["diff.000000.000001.fits"]
task7.input_files(inFiles)
task7.output_files(outFiles)
task7.depends_on(task6)
tasks.append(task7)

task8 = Task("./montage-tasks-js/mDiff", ["p2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1420186.fits", "diff.000000.000002.fits", "big_region.hdr"])
inFiles = ["p2mass-atlas-990502s-j1430080.fits", "p2mass-atlas-990502s-j1420186.fits", "big_region.hdr"]
outFiles = ["diff.000000.000002.fits"]
task8.input_files(inFiles)
task8.output_files(outFiles)
task8.depends_on(task2)
task8.depends_on(task3)
tasks.append(task8)

task9 = Task("./montage-tasks-js/mFitplane", ["diff.000000.000002.fits"])
inFiles = ["diff.000000.000002.fits"]
outFiles = ["diff.000000.000002.fits"]
task9.input_files(inFiles)
task9.output_files(outFiles)
task9.depends_on(task8)
tasks.append(task9)

task10 = Task("./montage-tasks-js/mDiff", ["p2mass-atlas-990502s-j1420198.fits", "p2mass-atlas-990502s-j1420186.fits", "diff.000001.000002.fits", "big_region.hdr"])
inFiles = ["p2mass-atlas-990502s-j1420198.fits", "p2mass-atlas-990502s-j1420186.fits", "big_region.hdr"]
outFiles = ["diff.000001.000002.fits"]
task8.input_files(inFiles)
task8.output_files(outFiles)
task8.depends_on(task1)
task8.depends_on(task2)
tasks.append(task10)

task11 = Task("./montage-tasks-js/mFitplane", ["diff.000001.000002.fits"])
inFiles = ["diff.000001.000002.fits"]
outFiles = ["diff.000001.000002.fits"]
task11.input_files(inFiles)
task11.output_files(outFiles)
task11.depends_on(task10)
tasks.append(task11)

task12 = Task("./montage-tasks-js/mBgModel", ["-i", "100000", "pimages.tbl", "fits.tbl", "corrections.tbl"])
inFiles = ["pimages.tbl", "fits.tbl"]
outFiles = ["corrections.tbl"]
task12.input_files(inFiles)
task12.output_files(outFiles)
task12.depends_on(task4)
tasks.append(task12)

task13 = Task("./montage-tasks-js/mTblSort", ["pimages.tbl", "cntr", "IMGTBLHgkheE"])
inFiles = ["pimages.tbl"]
outFiles = ["IMGTBLHgkheE"]
task13.input_files(inFiles)
task13.output_files(outFiles)
task13.depends_on(task4)
tasks.append(task13)

task14 = Task("./montage-tasks-js/mTblSort", ["corrections.tbl", "id", "CORTBLTyOTiW"])
inFiles = ["corrections.tbl"]
outFiles = ["CORTBLTyOTiW"]
task14.input_files(inFiles)
task14.output_files(outFiles)
task14.depends_on(task12)
tasks.append(task14)

task15 = Task("./montage-tasks-js/mBackground", ["p2mass-atlas-990502s-j1430080.fits", "c2mass-atlas-990502s-j1430080.fits", "-2.71977e-03", "-2.82974e-04", "-3.47189e-01"])
inFiles = ["p2mass-atlas-990502s-j1430080.fits"]
outFiles = ["c2mass-atlas-990502s-j1430080.fits"]
task15.input_files(inFiles)
task15.output_files(outFiles)
task15.depends_on(task12)
tasks.append(task15)

task16 = Task("./montage-tasks-js/mBackground", ["p2mass-atlas-990502s-j1420198.fits", "c2mass-atlas-990502s-j1420198.fits", "-1.37708e-04", "1.57113e-04", "1.83842e-01"])
inFiles = ["p2mass-atlas-990502s-j1420198.fits"]
outFiles = ["c2mass-atlas-990502s-j1420198.fits"]
task16.input_files(inFiles)
task16.output_files(outFiles)
task16.depends_on(task12)
tasks.append(task16)

task17 = Task("./montage-tasks-js/mBackground", ["p2mass-atlas-990502s-j1420186.fits", "c2mass-atlas-990502s-j1420186.fits", "-1.48093e-04", "1.58784e-04", "4.34890e-01"])
inFiles = ["p2mass-atlas-990502s-j1420186.fits"]
outFiles = ["c2mass-atlas-990502s-j1420186.fits"]
task17.input_files(inFiles)
task17.output_files(outFiles)
task17.depends_on(task12)
tasks.append(task17)

task18 = Task("./montage-tasks-js/mImgtbl", ["-c", "corrected", "cimages.tbl"])
inFiles = ["c2mass-atlas*"]
outFiles = ["cimages.tbl"]
task18.input_files(inFiles)
task18.output_files(outFiles)
task18.depends_on(task15)
task18.depends_on(task16)
task18.depends_on(task17)
tasks.append(task18)

task19 = Task("./montage-tasks-js/mAdd", ["-p", "corrected", "cimages.tbl", "region.hdr", "mosaic.fits"])
inFiles = ["cimages.tbl", "region_hdr", "c2mass-atlas*"]
outFiles = ["mosaic.fits"]
task19.input_files(inFiles)
task19.output_files(outFiles)
task19.depends_on(task18)
tasks.append(task19)

task20 = Task("./montage-tasks-js/mJPEG", ["-ct", "1", "-gray", "mosaic.fits", "min", "max", "gaussianlog", "-out", "mosaic.jpg"])
inFiles = ["mosaic.fits"]
outFiles = ["mosaic.jpg"]
task20.input_files(inFiles)
task20.output_files(outFiles)
task20.depends_on(task19)
tasks.append(task20)






