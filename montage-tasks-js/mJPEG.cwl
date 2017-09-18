cwlVersion: v1.0
class: CommandLineTool
baseCommand: mJPEG.js

inputs:
  in1:
    type: string
    inputBinding:
      prefix: -ct
      valueFrom: "1"
      position: 1
  shrunken:
    type: File
    inputBinding:
      prefix: -gray
      position: 2
  in2:
    type: string
    inputBinding:
      prefix: 0.00%
      valueFrom: 100.00%
      position: 3
  in3:
    type: string
    inputBinding:
      valueFrom: gaussian
      position: 4
  jpeg:
    type: string
    inputBinding:
      prefix: -out
      position: 5
  
outputs:
  jpeg_out:
    type: File
    outputBinding:
      glob: $(inputs.jpeg)
