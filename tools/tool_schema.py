Tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a text file. Returns the file content with line numbers. For large files, use offset and limit to read specific portions. Cannot read binary files (images, executables, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read (relative to working directory or absolute)"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Line number to start reading from (1-based). Defaults to 1"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of lines to read. If not specified, reads entire file."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates the file if it doesn't exist, or overwrites if it does. Parent directories are created automatically. Use this for creating new files or completely replacing file contents. For partial modifications, use the edit tool instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write (relative to working directory or absolute)"
                    },
                    "content": {
                        "type": "string",
                        "description": "content to write the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search for a regex pattern in file contents. Returns matching lines with file paths and line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the file"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Regular expression pattern to search for"
                    },
                    "case_insensitive": {
                        "type": "boolean",
                        "description": "Case-insensitive search (default: false)"
                    }
                },
                "required": ["path", "pattern", "case_insensitive"]
            }
        }
    },
   {
    "type": "function",
    "function": {
        "name": "glob",
        "description": "Find files matching a pattern (e.g., '**/*.py').",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern, e.g., '**/*.js' or '*.json'"
                },
                "path": {
                    "type": "string",
                    "description": "Root directory to search (required)"
                }
            },
            "required": ["pattern", "path"]
        }
    }
},
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit a file by replacing text. The old_string must match exactly (including whitespace and indentation) and must be unique in the file unless replace_all is true. Use this for precise, surgical edits. For creating new files or complete rewrites, use write_file instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to edit (relative to working directory or absolute path)"
                    },
                    "old_content": {
                        "type": "string",
                        "description": "The exact text to find and replace. Must match exactly including all whitespace and indentation. For new files, leave this empty."
                    },
                    "new_content": {
                        "type": "string",
                        "description": "The text to replace old_string with. Can be empty to delete text"
                    },
                    "replace_all": {
                        "type": "boolean",
                        "description": "Replace all occurrences of old_string (default: false)"
                    }
                },
                "required": ["path", "old_content", "new_content"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "shell",
            "description": "Execute a shell command. Use for file deletion, running scripts, git, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute (e.g., 'del test.py' on Windows, 'rm test.py' on Unix)"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory (default: current directory)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 120)"
                    }
                },
                "required": ["command"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List contents of a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list (default: current directory)"
                    },
                    "hidden_file": {
                        "type": "boolean",
                        "description": "Whether to include hidden files and directories (default: false)"
                    }
                },
                "required": ["path"]
            }
        }
    }
]
