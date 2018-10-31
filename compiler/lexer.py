import string
from enum import Enum
from .lexbase import TBaseLexer
from . import *

# constants
MaxLineLength = 80
numChars = {
    countup('0', '9'), countup('a', 'z'), countup('A', 'Z')
}
SymChars = {
    countup('a', 'z'), countup('A', 'Z'),
    countup('0', '9'), countup('\x80', '\xFF')
}
SymStartChars = {
    countup('a', 'z'), countup('A', 'Z'), countup('\x80', '\xFF')
}
OpChars = {
    '+', '-', '*', '/', '\\', '<', '>', '!', '?',
    '^', '.', '|', '=', '%', '&', '$', '@', '~', ':'
}


TTokType = Enum("TTokType", [
    "tkInvalid", "tkEof",               # order is important here!
    "tkSymbol", 
    # keywords:
    "tkAddr", "tkAnd", "tkAs", "tkAsm",
    "tkBind", "tkBlock", "tkBreak", "tkCase", "tkCast",
    "tkConcept", "tkConst", "tkContinue", "tkConverter",
    "tkDefer", "tkDiscard", "tkDistinct", "tkDiv", "tkDo",
    "tkElif", "tkElse", "tkEnd", "tkEnum", "tkExcept", "tkExport",
    "tkFinally", "tkFor", "tkFrom", "tkFunc",
    "tkIf", "tkImport", "tkIn", "tkInclude", "tkInterface",
    "tkIs", "tkIsnot", "tkIterator",
    "tkLet",
    "tkMacro", "tkMethod", "tkMixin", "tkMod", "tkNil", "tkNot", "tkNotin",
    "tkObject", "tkOf", "tkOr", "tkOut",
    "tkProc", "tkPtr", "tkRaise", "tkRef", "tkReturn",
    "tkShl", "tkShr", "tkStatic",
    "tkTemplate",
    "tkTry", "tkTuple", "tkType", "tkUsing",
    "tkVar", "tkWhen", "tkWhile", "tkXor",
    "tkYield",

    # types
    "tkIntLit", "tkInt8Lit", "tkInt16Lit", "tkInt32Lit", "tkInt64Lit",
    "tkUIntLit", "tkUInt8Lit", "tkUInt16Lit", "tkUInt32Lit", "tkUInt64Lit",
    "tkFloatLit", "tkFloat32Lit", "tkFloat64Lit", "tkFloat128Lit",
    "tkStrLit", "tkRStrLit", "tkTripleStrLit",
    "tkGStrLit", "tkGTripleStrLit", "tkCharLit",

    # punctuation
    "tkParLe", "tkParRi", "tkBracketLe",
    "tkBracketRi", "tkCurlyLe", "tkCurlyRi",
    "tkBracketDotLe", "tkBracketDotRi",  # [. and .]
    "tkCurlyDotLe", "tkCurlyDotRi",  # {. and .}
    "tkParDotLe", "tkParDotRi",  # (. and .)
    "tkComma", "tkSemiColon",
    "tkColon", "tkColonColon",
    
    # operators
    "tkEquals", "tkDot", "tkDotDot", "tkBracketLeColon",
    "tkOpr",

    "tkComment", # ordinary comment
    "tkAccent", "tkSpaces", "tkInfixOpr", "tkPrefixOpr", "tkPostfixOpr"
])

TTokTypes = set(TTokType)

weakTokens = set([TTokType.tkComma, TTokType.tkSemiColon, TTokType.tkColon,
                  TTokType.tkParRi, TTokType.tkParDotRi, TTokType.tkBracketRi, TTokType.tkBracketDotRi,
                  TTokType.tkCurlyRi])

tokKeywordLow = TTokType(TTokType.tkSymbol.value + 1)
tokKeywordHigh = TTokType(TTokType.tkIntLit.value - 1)

TokTypeToStr = [
    "tkInvalid", "[EOF]",
    "tkSymbol",
    "addr", "and", "as", "asm",
    "bind", "block", "break", "case", "cast",
    "concept", "const", "continue", "converter",
    "defer", "discard", "distinct", "div", "do",
    "elif", "else", "end", "enum", "except", "export",
    "finally", "for", "from", "func", "if",
    "import", "in", "include", "interface", "is", "isnot", "iterator",
    "let",
    "macro", "method", "mixin", "mod",
    "nil", "not", "notin", "object", "of", "or",
    "out", "proc", "ptr", "raise", "ref", "return",
    "shl", "shr", "static",
    "template",
    "try", "tuple", "type", "using",
    "var", "when", "while", "xor",
    "yield",
    "tkIntLit", "tkInt8Lit", "tkInt16Lit", "tkInt32Lit", "tkInt64Lit",
    "tkUIntLit", "tkUInt8Lit", "tkUInt16Lit", "tkUInt32Lit", "tkUInt64Lit",
    "tkFloatLit", "tkFloat32Lit", "tkFloat64Lit", "tkFloat128Lit",
    "tkStrLit", "tkRStrLit",
    "tkTripleStrLit", "tkGStrLit", "tkGTripleStrLit", "tkCharLit", "(",
    ")", "[", "]", "{", "}", "[.", ".]", "{.", ".}", "(.", ".)",
    ",", ";",
    ":", "::", "=", ".", "..", "[:",
    "tkOpr", "tkComment", "`",
    "tkSpaces", "tkInfixOpr",
    "tkPrefixOpr", "tkPostfixOpr"
]

TNumericalBase = Enum("TNumericalBase", [
    "base10",  # base10 is the first element so that it is the correct default value
    "base2", "base8", "base16"
])

CursorPosition = Enum("CursorPosition", [
    "None", "InToken", "BeforeToken", "AfterToken"
])


class TToken:
    def __init__(self, **kwargs):
        self.tokType = kwargs.get("tokType")
        self.indent = kwargs.get("indent")
        self.ident = kwargs.get("ident")
        self.iNumber = kwargs.get("iNumber")
        self.fNumber = kwargs.get("fNumber")
        self.base = kwargs.get("base")
        self.strongSpaceA = kwargs.get("strongSpaceA")
        self.strongSpaceB = kwargs.get("strongSpaceB")
        self.literal = kwargs.get("literal")
        self.line = kwargs.get("line")
        self.col = kwargs.get("col")

    def initToken(self):
        self.tokType = TTokType.tkInvalid
        self.iNumber = 0
        self.indent = 0
        self.strongSpaceA = 0
        self.literal = ""
        self.fNumber = 0.0
        self.base = TNumericalBase.base10
        self.ident = None

    def fillToken(self):
        self.tokType = TTokType.tkInvalid
        self.iNumber = 0
        self.indent = 0
        self.strongSpaceA = 0
        self.literal = ""
        self.fNumber = 0.0
        self.base = TNumericalBase.base10
        self.ident = None


class TLexer(TBaseLexer):
    def __init__(self):
        self.fileIdx = None         # TODO : impl FileIndex
        self.indentAhead: int = None
        self.currLineIndent: int = None
        self.strongSpaces: bool = None
        self.allowTabs: bool = None
        self.cursor: CursorPosition = None
        self.errorHandler = None    # TODO : impl TErrorHandler
        self.cache = None           # TODO : impl IdentCache
        self.config = None          # TODO : impl ConfigRef

    def getLineInfo(self, tok: TToken = None):
        if tok is not None:
            # TODO : impl `msgs.newLineInfo`
            # newLineInfo(self.fileIdx, tok.lineNumber, tok.col)
            return None
        else:
            # newLineInfo(self.fileIdx, self.lineNumber, self.getColNumber(self.buf_pos))
            return None

    def openLexer(self, fileIdx, inputstream, cache, config):
        self.openBaseLexer(inputstream)
        self.fileIdx = fileIdx
        self.indentAhead = -1
        self.currLineIndent - 0
        self.lineNumber += inputstream.lineOffset
        self.cache = cache
        self.config = config

    def closeLexer(self):
        if self.config is not None:
            self.config.linesCompiled += self.lineNumber
        self.closeBaseLexer()

    def dispMessage(self, info, msg, arg):
        if self.errorHandler.isNil:
            # TODO : impl `msgs.message`
            # msgs.message(self.config, info, msg, arg)
            pass
        else:
            # TODO :  impl `TErrorHandler`
            # self.errorHandler(self.config, info, msg, arg)
            pass

    def lexMessage(self, msg, arg=""):
        return self.dispMessage(self.getLineInfo(), msg, arg)

    def lexMessageTok(self, msg, tok, arg=""):
        info = None     # newLineInfo(self.fileIdx, tok.line, tok.col)
        return self.dispMessage(info, msg, arg)

    def lexMessagePos(self, msg, pos, arg=""):
        # newLineInfo(self.fileIdx, self.lineNumber, pos - self.lineStart)
        info = None
        return self.dispMessage(info, msg, arg)

    def matchTwoChars(self, first, second):
        return (self.buf[self.buf_pos] == first) and (self.buf[self.buf_pos + 1] in second)

    def eatChar(self, tok, replacementChar=None):
        if replacementChar is not None:
            tok.literal += replacementChar
        else:
            tok.literal += self.buf[self.buf_pos]
        self.buf_pos += 1
        return self

    def matchUnderscoreChars(self, tok, chars):
        result = 0
        while True:
            if self.buf[self.buf_pos] in chars:
                tok.literal += self.buf[self.buf_pos]
                self.buf_pos += 1
                result += 1
            else:
                break

            if self.buf[self.buf_pos] == "_":
                if self.buf[self.buf_pos+1] not in chars:
                    self.lexMessage(None,
                                    "only single underscores may occur in a token and token may not "
                                    + "end with an underscore: e.g. '1__1' and '1_' are invalid")
                    break
                tok.literal += "_"
                self.buf_pos += 1
        return result

    def getNumber(self, result):
        def matchChars(self, tok, chars):
            while self.buf[self.buf_pos] in chars:
                tok.literal += self.buf[self.buf_pos]
                self.buf_pos += 1
            return self

        # msgKind=lineinfos.errGenerated
        def lexMessageLitNum(self, msg, startpos, msgKind=None):
            literalishChars = {
                countup('A', 'F'), countup('a', 'f'),
                countup('0', '9'), "X", "x", "o", "O",
                "c", "C", "b", "B", "_", ".", "'", "d",
                "i", "u"
            }
            msgPos = self.buf_pos

            t = TToken(literal="")
            self.buf_pos = startpos

            self.matchChars(t, literalishChars)

            if self.buf[self.buf_pos] in ["+", "-"] and \
                    self.buf[self.buf_pos - 1] in ["e", "E"]:
                t.literal += self.buf[self.buf_pos]
                self.buf_pos += 1
                self.matchChars(t, literalishChars)

            if self.buf[self.buf_pos] in ["'", "f", "F", "d", "D", "i", "I", "u", "U"]:
                self.buf_pos += 1
                t.literal += self.buf[self.buf_pos]
                self.matchChars(t, [c for c in string.digits])

            self.buf_pos = msgPos
            self.lexMessage(msgKind, msg % t.literal)

        isBase10 = True
        numDigits = 0

        # function consts
        baseCodeChars = {"X", "x", "o", "b", "B", "c", "C"}
        literalishChars = set(list(baseCodeChars) + [
            countup('A', 'F'),
            countup('a', 'f'),
            countup('0', '9'),
            "_", "'"
        ])
        floatTypes = {
            TTokType.tkFloatLit, TTokType.tkFloat32Lit,
            TTokType.tkFloat64Lit, TTokType.tkFloat128Lit
        }
        result.tokType = TTokType.tkIntLit
        result.literal = ""
        result.base = TNumericalBase.base10
        startpos = self.buf_pos
        # TODO : `impl tokenBegin(result, startpos)`


# TODO : impl `tokenBegin(tok, pos)` template
#             `tokenEnd(tok, pos)` template
#             `tokenEndIgnore(tok, pos)` template
#             `tokenEndPrevious(tok, pos)` template


def unsafeParseUInt(s, b, start=0):
    i = start
    if i < len(s) and s[i] in string.digits:
        b = 0
        while i < len(s) and s[i] in string.digits:
            b *= 10 + (ord(s[i]) - ord("0"))
            i += 1
            while i < len(s) and s[i] == "_":
                i += 1
        return i - start
