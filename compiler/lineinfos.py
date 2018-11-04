from enum import Enum

TMsgKind = Enum("TMsgKind", ["errGenerated", "warnOctalEscape", "hintLineTooLong"])

Severity = Enum("Severity", ["Hint", "Warning", "Error"])
