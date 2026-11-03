# `model-meta-bridge`

This is a bridge application which surfaces basic data about a 
Blender scene file when a file is loaded and on save. This tool 
is intended for use with `model-meta`, but it's entirely possible 
to leverage the queries for your own needs.

## Functionality

The only purpose of this addon is to communicate live updates to 
the `model-meta` application by surfacing a websocket-like connection
for the tool to connect to.