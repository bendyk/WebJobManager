cwlVersion: v1.0
class: CommandLineTool
baseCommand: mImgtbl.js

inputs:
  cimages:
    type: File
    inputBinding:
      prefix: -t
      position: 1
  newcimages:
    type: string
    inputBinding:
      prefix: .
      valueFrom: new$(inputs.cimages)
      position: 2
  c2mass1:
    type: File
  c2mass2:
    type: File
  c2mass3:
    type: File
  c2mass4:
    type: File
  
outputs:
  cimages_out:
    type: File
    outputBinding:
      glob: $(inputs.newcimages)
