cwlVersion: v1.0
class: CommandLineTool
baseCommand: mjob2.js
inputs:
  file1:
    type: File
    inputBinding:
      position: 1
  fout : string
outputs:
  fileout:
    type: File
    outputBinding:
      glob: $(inputs.fout)
