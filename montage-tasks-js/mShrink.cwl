cwlVersion: v1.0
class: CommandLineTool
baseCommand: mShrink.js

arguments: ["1"]

inputs:
  mosaic:
    type: File
    inputBinding:
      position: 1
  shrunken:
    type: string
    inputBinding:
      position: 2
  
outputs:
  shrunken_out:
    type: File
    outputBinding:
      glob: $(inputs.shrunken)
