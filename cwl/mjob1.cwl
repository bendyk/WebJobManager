cwlVersion: v1.0
class: CommandLineTool
baseCommand: mjob1
inputs:
  text:
    type: string
    inputBinding: {}
outputs:
  fileout1:
    type: File
    outputBinding:
      glob: foo.arr1
  fileout2:
    type: File
    outputBinding:
      glob: foo.arr2
