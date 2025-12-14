# `sdial`

Speed dial for the CLI-phile.

## Features

- Speed-dial long commands by number
- Multi-line shell snippets/editing via $EDITOR
- No translation: your snippet is your script
- Fast, OS shell-agnostic
- Plain-text, backup-friendly storage

## Installation

```bash
pip install sdial
```

Works on Linux, Mac, Windows (`cmd.exe`!), PowerShell, WSL. If Python runs somewhere, sdial probably does too.

## Quick Start

### Have a long command that you frequently type and execute?

Add it to `sdial`!

```bash
python -m sdial add 'docker run --rm -it -v $(pwd)/src:/app/src -v ~/.config/myapp:/root/.config/myapp --name myapp_dev_container mycompany/myapp:latest bash'
# Output to stdout: 0
```

That output means your command can now be dialed with 0:

```bash
python -m sdial dial 0
# Executes 'docker run --rm -it -v $(pwd)/src:/app/src -v ~/.config/myapp:/root/.config/myapp --name myapp_dev_container mycompany/myapp:latest bash'
```

### Want to add another multi line, snippet to speed dial?

```bash
python -m sdial add
# Opens $EDITOR, just like `git commit`.
# You type or paste your multi line snippet, then save and exit!
```

Say that you type the following:

```bash
while read file
do
    # The $1 here allows `sdial` to pass arguments!
    if grep -q "$1" "$file"
    then
        echo "$file"
    fi
done
```

Say after saving, `sdial` tells you to dial 1 to run this command.

You can then dial and provide an argument for `$1`:

```bash
find . -name '*.py' | python -m sdial dial 1 "TODO"
```

This allows you to use one pipe to filter all `.py` files under the current directory containing the string "TODO".

How does that work? `sdial` just launches:

```sh
$SHELL $snippet_file arg1 arg2 ...
```

That means your speed dial snippet gets executed by $SHELL as a script, with arguments in `$1`, `$2`, etc.

It's dead simple: $SHELL semantics, no translation layer. Anything you can do in a $SHELL script (loops, pipes,
arguments) just works.

### What if you forgot which commands have speed dial numbers, and what each command's number is?

```bash
python -m sdial
```

This prints out something resembling the following CSV:

```csv
number,command
0,"docker run --rm -it -v $(pwd)/src:/app/src -v ~/.config/myapp:/root/.config/myapp --name myapp_dev_container mycompany/myapp:latest bash"
1,"while read file\ndo\n    # The $1 here allows `sdial` to pass arguments!\n    if grep -q \"$1 \"$file\"\n    then\n        echo \"$file\"\n    fi\ndone"
```

### What if you made a mistake when entering a command?

```bash
python -m sdial edit 1
```

This opens $EDITOR and allows you to edit what number 1 speed dials.

### What if you want to unregister a command?

```bash
python -m sdial remove 1
```

In this case, if we remove command with number `n`, then:

- The commands originally with numbers `n + 1`, `n + 2`, ...
- Are reassigned the numbers `n`, `n + 1`, ...

## FAQ and Tips

### Can I use variables, pipes, and advanced shell scripting?

**Yes** - your snippets are executed as `$SHELL $snippet_file $args...`. This means:

- All shell scripting works: variables ($1, $2), loops, functions, pipes, etc.
- You can use here docs, pipe to other commands, etc.

### How do you store the commands?

- Each command is stored as a file under `~/.sdial/`. The filenames are ordered using fractional base58 to allow easy
  insertion and deletion without renaming every file.
- Listing (`python -m sdial`) reads their sorted names and shows the commands.

### Does this work with cmd.exe or PowerShell?

- **Yes!** Just beware that cmd.exe and PowerShell have their own syntax and semantics.

### Environment variables and context?

- Commands/scripts run with the **current environment** (`$PWD`, `$PATH`, etc.) as when you invoke `sdial`.
- On Unix, use `VARIABLE=value python -m sdial $n` to set them.

### How do I back up all my dials or share them?

- Simply copy `~/.sdial/` - all your scripts are plain text files!

### What if I want to reset or wipe all commands?

```bash
rm -rf ~/.sdial/
```

Or selectively delete individual files in there.

## Why? Because Nobody Else Had The Guts.

- No one combined numbered launching, fractional indexing, $EDITOR multi-line, and Shell and OS-agnostic design.
- We did.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

MIT - no nonsense, use it however you want.
