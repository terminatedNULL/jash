<p align="center">
  <img width="600" src="https://github.com/user-attachments/assets/63aef7bc-fa87-47ae-9507-e107e91bc9d7">
</p>
 
---

The Jython Advanced Syntax Highlighter (JASH) is a tool for jython development in limited or python-only environments.
JASH takes inputted JAR files, decompiles them, and generates python "stub" files in the exact file structure as in the JAR.
Each of the generated stub files are all variables, classes, and functions from the original Java code, but stripped of their internal logic.
These definitions are fully typed, including any exceptions and class heirarchy.

These stub files allow for accurate syntax highlighting and code completion, while not requiring a full Jython environment [^1].
Due to Jython's import resolution methods, Jython imports are prioritized over local imports, meaning that the real Jython files
will be targeted during compilation.

JASH includes tools for generation size estimation, generation targeting, and built-in [Java standard library](https://github.com/openjdk/jdk/tree/master/src/java.base/share/classes) generation.

[^1]: This is useful for restricted developent environments, custom Jython installations, or for those who wish to develop 
using Jython in a Python IDE.
