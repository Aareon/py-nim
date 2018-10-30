# constants
Lrz = ' '
Apo = '\''
Tabulator = '\x09'
ESC = '\x1B'
CR = '\x0D'
FF = '\x0C'
LF = '\x0A'
BEL = '\x07'
BACKSPACE = '\x08'
VT = '\x0B'
EndOfFile = '\0'
CR, LF = '\r', '\n'
NewLines = [CR, LF]


class TBaseLexer:
    def __init__(self, buf_pos, buf, buf_len, stream, line_number, sentinel, line_start, offset_base):
        self.buf_pos = buf_pos
        self.buf = buf
        self.buf_len = buf_len
        self.stream = stream            # llstream object
        self.line_number = line_number
        self.sentinel = sentinel
        self.line_start = line_start
        self.offset_base = offset_base

    def openBaseLexer(self, input_stream, buf_len:int=8192):
        assert buf_len > 0

        self.buf_pos = 0
        self.offset_base = 0
        self.buf_len = buf_len
        # L.buf = cast[cstring](alloc(bufLen * chrSize))
        # This would normally store a new `cstring` in `L.buf` w/ a given size,
        # but 1. we don't need to allocate memory on the heap, and 2. we haven't
        # started messing with `cstring`s yet. For now we make `self.buf = None`
        self.buf = None
        self.sentinel = buf_len - 1
        self.line_start = 0
        self.line_number = 1
        self.stream = input_stream
        self.fillBuffer()
        self.skipUTF8_BOM()

    def closeBaseLexer(self):
        self.buf = None
        # TODO : self.stream.close()

    def getCurrentLine(self, marker:bool=True):
        result = ""
        i = self.line_start
        while self.buf[i] not in [CR, LF, EndOfFile]:
            result += self.buf[i]
            i += 1

        result += "\n"

        if marker:
            result += (" " * self.getColNumber(self.buf_pos)) + "^\n"
        return result

    def getColNumber(self, pos:int):
        return abs(pos - self.line_start)

    def handleCR(self, pos:int):
        assert self.buf[pos] == CR

        self.line_number += 1
        result = self.fillBaseLexer(pos)
        if self.buf[result] == LF:
            result = self.fillBaseLexer(result)
        return result

    def handleLF(self, pos:int):
        assert self.buf[pos] == LF

        self.line_number += 1
        return self.fillBaseLexer(pos)

    def skipUTF8_BOM(self):
        if self.buf[0] == '\xEF' and self.buf[1] == '\xBB' and self.buf[2] == '\xBF':
            self.buf_pos += 3
            self.line_start += 3
        return self

    def fillBaseLexer(self, pos:int):
        assert pos <= self.sentinel

        if pos < self.sentinel:
            self.line_start = pos + 1   # nothing to do
        else:
            self.fillBuffer()
            self.offset_base += pos + 1
            self.buf_pos = 0
            self.line_start = 0
        return self

    def fillBuffer(self):
        assert self.sentinel < self.buf_len

        to_copy = self.buf_len - self.sentinel - 1
        assert to_copy >= 0

        if to_copy > 0:
            self.buffer = self.buf[self.sentinel + 1]

        chars_read = self.stream.read(self.buf[to_copy], (self.sentinel + 1))
        s = to_copy + chars_read

        if chars_read < (self.sentinel + 1):
            self.buf[s] = EndOfFile
            self.sentinel = s
        else:
            s -= 1
            while True:
                assert s < self.buf_len

                while (s >= 0) and not (self.buf[s] in NewLines):
                    s -= 1

                if s >= 0:
                    self.sentinel = s
                    break
                else:
                    old_buf_len = self.buf_len
                    self.buf_len *= 2

                    # TODO : L.buf = cast[cstring](realloc(L.buf, L.bufLen * chrSize))
                    # unlike the work-around for `alloc` in `openBaseLexer`, this
                    # portion might require some thought...
                    assert self.buf_len - old_buf_len == old_buf_len

                    chars_read /= self.stream.read(self.buf[old_buf_len])
                    if chars_read < old_buf_len:
                        self.buf[old_buf_len + chars_read] = EndOfFile
                        self.sentinel = old_buf_len + chars_read
                        break
                    
                    s = self.buf_len + 1
        return self
