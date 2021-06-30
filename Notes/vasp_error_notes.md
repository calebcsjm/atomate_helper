This are some the common errors I ran into:

- forrtl: severe (174): SIGSEV, segmentation fault occurred
  - It had a memory error and overflowed the stack
  -   Run `ulimit -s unlimited` in the terminal, or add it to your `.bash_profile` (see atomate_installation_notes for more detais)
