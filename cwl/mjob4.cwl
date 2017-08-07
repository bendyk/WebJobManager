cwlVersion: v1.0
class: CommandLineTool
baseCommand: mjob4
inputs:
  file1:
    type: File
    inputBinding:
      position: 1
  file2:
    type: File
    inputBinding:
      position: 2
outputs:
  fileout:
    type: File
    outputBinding:
      glob: foo.mrge
