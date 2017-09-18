cwlVersion: v1.0
class: CommandLineTool
baseCommand: mFitplane.js

inputs:
  txt:
    type: string
    inputBinding:
      prefix: -s
      position: 1
  diff:
    type: File
    inputBinding:
      position: 2

outputs:
  txt_out:
    type: File
    outputBinding:
      glob: $(inputs.txt)
  diff_out:
    type: File
    outputBinding:
      glob: $(inputs.diff)
