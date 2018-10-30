import sys
from enum import Enum
from io import TextIOWrapper

from . import FileMode

# consts
line_continuation_oprs = ['+', '-', '*', '/', '\\', '<', '>', '!', '?', '^',
                          '|', '%', '&', '$', '@', '~', ',']
additional_line_continuation_oprs = ['#', ':', '=']

TLLStreamKind = Enum("TLLStreamKind", [
    "llsNone", "llsString", "llsFile", "llsStdIn"
])


class TLLStream:
    def __init__(self):
        self.kind = None
        self.f = None
        self.s = None
        self.rd = None
        self.wr = None
        self.line_offset = None


class PLLStream(TLLStream):
    def open(self, **kwargs):
        if len(kwargs) == "":
            self.kind = TLLStreamKind.llsNone
            return self

        data = kwargs.get("data")
        if data is not None and isinstance(data, str):
            self.s = data
            self.kind = TLLStreamKind.llsString
            return self

        f = kwargs.get("f")
        if f is not None and isinstance(f, TextIOWrapper):
            self.f = f
            self.kind = TLLStreamKind.llsFile
            return self

        filename = kwargs.get("filename")
        if filename is not None and isinstance(filename, str):
            mode = kwargs.get("mode")
            if mode is not None and isinstance(mode, FileMode):
                self.kind = TLLStreamKind.llsFile
                try:
                    self.f = open(filename, mode)
                except:
                    self.f = None
                return self

    def close(self):
        if self.kind == TLLStreamKind.llsFile:
            self.f.close()

    def llReadFromStdin(self, buf, buf_len:int):
        self.s = ""
        self.rd = 0
        line = ""
        triples = 0

        while True:
            line = readLineFromStdin(">>> " if len(self.s) == 0 else "... ")
            if not line:
                break
            
            self.s += line + "\n"
            triples += count_triples(line)
            if not continue_line(line, (triples and 1) == 1):
                break

        self.line_offset += 1
        result = min(buf_len, len(self.s) - self.rd)
        if result > 0:
            buf = self.s[self.rd]
            self.rd += result

        return result, buf

    def llStreamRead(self, buf, buf_len:int):
        if self.kind == TLLStreamKind.llsNone:
            result = 0
        elif self.kind == TLLStreamKind.llsString:
            result = min(buf_len, len(self.s) - self.rd)
            if result > 0:
                buf = self.s[0 + self.rd]
                self.rd += result
        elif self.kind == TLLStreamKind.llsFile:
            result = self.f.read(buf_len)
        elif self.kind == TLLStreamKind.llsStdIn:
            result = self.llReadFromStdin(buf, buf_len)
        
        return result, buf

    def llStreamReadLine(self):
        line = ""
        if self.kind == TLLStreamKind.llsNone:
            return True
        elif self.kind == TLLStreamKind.llsNone:
            while self.rd < len(self.s):
                if self.s[self.rd] == "\x0D":
                    self.rd += 1
                    if self.s[self.rd] == "\x0A":
                        self.rd += 1
                    break
                elif self.s[self.rd] == "\x0A":
                    self.rd += 1
                    break
                else:
                    line += self.s[self.rd]
                    self.rd += 1
            return len(line) > 0 or self.rd < len(self.s)
        elif self.kind == TLLStreamKind.llsFile:
            return self.f.readline()
        elif self.kind == TLLStreamKind.llsStdIn:
            return sys.stdin.readline()

    def llStreamWrite(self, data=None):
        if self.kind in [TLLStreamKind.llsNone, TLLStreamKind.llsStdIn]:
            pass
        elif self.kind == TLLStreamKind.llsString:
            self.s += data
            self.wr += len(data)
        elif self.kind == TLLStreamKind.llsFile:
            self.f.write(data)
        return self

    def llStreamReadAll(self):
        buf_size = 2048
        if self.kind in [TLLStreamKind.llsNone, TLLStreamKind.llsStdIn]:
            return ""
        elif self.kind == TLLStreamKind.llsString:
            if self.rd == 0:
                result = self.s
            else:
                result = self.s[self.rd:]
            self.rd = len(self.s)
            return result
        elif self.kind == TLLStreamKind.llsFile:
            c = self.f.read(buf_size)
            num_bytes = len(c)
            i = num_bytes
            result = f"{c}"
            while num_bytes == buf_size:
                result = result[:(i + buf_size)]
                c = self.f.read(buf_size)
                num_bytes = len(c)
                result = "{result[:i + 0]}{c}"
                i += num_bytes
            result = result[:i]
            return result


def readLineFromStdin(prompt:str):
    sys.stdout.write(prompt)
    result = sys.stdin.readline()
    if not result:
        sys.stdout.write("\n")
        sys.exit(0)
    else:
        return result


def endsWith(x:str, s:list):
    i = len(x)-1
    while i >= 0 and x[i] == ' ':
        i -= 1
    if i >= 0 and x[i] in s:
        return True
    else:
        return False


def endsWithOpr(x:str):
    return x.endswith(line_continuation_oprs)


def continue_line(line:str, in_triple_string:bool):
    return in_triple_string or len(line) > 0 and (
        line[0] == " " or
        line.endswith(line_continuation_oprs+additional_line_continuation_oprs)
    )


def count_triples(s:str):
    result = 0

    i = 0
    while i < len(s):
        if s[i] == "\"" and s[i+1] == "\"" and s[i+2] == "\"":
            result += 1
            i += 2
        i += 1
    return result

