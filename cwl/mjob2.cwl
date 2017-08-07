cwlVersion: v1.0
class: CommandLineTool
baseCommand: mjob2
inputs:
  file1:
    type: File
    inputBinding:
      position: 1
outputs:
  fileout:
    type: File
    outputBinding:
      glob: "foo.srt"
