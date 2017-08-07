#!/usr/bin/env python
from cwltool.load_tool import fetch_document, validate_document
from cwltool.resolver import tool_resolver


def print_file(file_path):
  document_loader, workflowobj, uri = fetch_document(file_path, resolver=tool_resolver, fetcher_constructor=None)
  document_loader, avsc_names, processobj, metadata, uri = validate_document(document_loader, workflowobj, uri,
                                    enable_dev=False, strict=True,
                                    preprocess_only=False,
                                    fetcher_constructor=None)
  print(processobj)

print_file("./mjob_example.cwl")
print("----------------------------------------------------")
print_file("./mjob2.cwl")
