#!/bin/bash

# Updated script with variable expansions fixed

LOCAL_BIN="~/.local/bin"

# Some code... 

if ! grep -q "\${LOCAL_BIN}" "${HOME}/.config/fish/config.fish" 2>/dev/null; then
    # Do something
fi

# Some more code... 

if ! grep -q "\${LOCAL_BIN}" "${HOME}/.bashrc" 2>/dev/null; then
    # Do something
fi

# Some other code... 

if ! grep -q "\${LOCAL_BIN}" "${HOME}/.zshrc" 2>/dev/null; then
    # Do something
fi

# End of script