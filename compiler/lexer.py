import string
from enum import Enum

from . import *
from .lexbase import TBaseLexer

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
            # newLineInfo(self.fileIdx, self.lineNumber, self.getColNumber(self.bufpos))
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
        return (self.buf[self.bufpos] == first) and (self.buf[self.bufpos + 1] in second)

    def eatChar(self, tok, replacementChar=None):
        if replacementChar is not None:
            tok.literal += replacementChar
        else:
            tok.literal += self.buf[self.bufpos]
        self.bufpos += 1
        return self

    def matchUnderscoreChars(self, tok, chars):
        result = 0
        while True:
            if self.buf[self.bufpos] in chars:
                tok.literal += self.buf[self.bufpos]
                self.bufpos += 1
                result += 1
            else:
                break

            if self.buf[self.bufpos] == "_":
                if self.buf[self.bufpos+1] not in chars:
                    self.lexMessage(None,
                                    "only single underscores may occur in a token and token may not "
                                    + "end with an underscore: e.g. '1__1' and '1_' are invalid")
                    break
                tok.literal += "_"
                self.bufpos += 1
        return result

    def getNumber(self, result):
        def matchChars(tok, chars):
            while self.buf[self.bufpos] in chars:
                tok.literal += self.buf[self.bufpos]
                self.bufpos += 1

        # msgKind=lineinfos.errGenerated
        def lexMessageLitNum(msg, startpos, msgKind=None):
            literalishChars = {
                countup('A', 'F'), countup('a', 'f'),
                countup('0', '9'), "X", "x", "o", "O",
                "c", "C", "b", "B", "_", ".", "'", "d",
                "i", "u"
            }
            msgPos = self.bufpos

            t = TToken(literal="")
            self.bufpos = startpos

            matchChars(t, literalishChars)

            if self.buf[self.bufpos] in ["+", "-"] and \
                    self.buf[self.bufpos - 1] in ["e", "E"]:
                t.literal += self.buf[self.bufpos]
                self.bufpos += 1
                matchChars(t, literalishChars)

            if self.buf[self.bufpos] in ["'", "f", "F", "d", "D", "i", "I", "u", "U"]:
                self.bufpos += 1
                t.literal += self.buf[self.bufpos]
                matchChars(t, {countup('0', '9')})

            self.bufpos = msgPos
            self.lexMessage(msgKind, msg % t.literal)

        isBase10 = True
        numDigits = 0

        # function consts
        baseCodeChars = ["X", "x", "o", "b", "B", "c", "C"]
        literalishChars = set(baseCodeChars + [
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
        startpos = self.bufpos
        # TODO : `impl tokenBegin(result, startpos)`

        # First stage: find out base, make verifications, build token literal string
        # {'c', 'C'} is added for deprecation reasons to provide a clear error message
        if self.buf[self.bufpos] == '0' and self.buf[self.bufpos] in set(baseCodeChars + ['c', 'C', 'O']):
            isBase10 = False
            self.eatChar(result, 0)
            if self.buf[self.bufpos] in {'c', 'C'}:
                lexMessageLitNum(
                    "$1 will soon be invalid for oct literals; Use '0o' "
                    + "for octals. 'c', 'C' prefix",
                    startpos,
                    None) # TODO: impl lineinfos
            elif self.buf[self.bufpos] == 'O':
                lexMessageLitNum(
                    "$1 is an invalid int literal; For octal literals "
                    + "use the '0o' prefix.", startpos)
            elif self.buf[self.bufpos] in {'x', 'X'}:
                self.eatChar(result, 'x')
                numDigits = self.matchUnderscoreChars(result, {countup('0', '9'), countup('a', 'f'), countup('A', 'F')})
            elif self.buf[self.bufpos] == 'o':
                self.eatChar(result, 'b')
                numDigits = self.matchUnderscoreChars(result, {countup('0', '1')})
            else:
                # TODO : impl msgs
                # lexMessageLitNum(L, "invalid number: '$1'", startpos)
                raise Exception('InternalError')
            
            if numDigits == 0:
                lexMessageLitNum(self, "invalid number: '$1'", startpos)
            else:
                self.matchUnderscoreChars(result, {countup('0', '9')})
                if self.buf[self.bufpos] == '.' and self.buf[self.bufpos + 1] in {countup('0', '9')}:
                    result.tokType = TTokType.tkFloatLit
                    self.eatChar(result, '.')
                    self.matchUnderscoreChars(result, {countup('0', '9')})
                
                if self.buf[self.bufpos] in {'e', 'E'}:
                    result.tokType = TTokType.tkFloatLit
                    self.eatChar(result, 'e')
                    if self.buf[self.bufpos] in {'+', '-'}:
                        self.eatChar(result)
                    self.matchUnderscoreChars(result, {countup('0', '9')})
            endpos = self.bufpos

            # Second stage, find out if there's a datatype suffix and handle it
            postPos = endpos
            if self.buf[postPos] in {'\'', 'f', 'F', 'd', 'D', 'i', 'I', 'u', 'U'}:
                if self.buf[postPos] == '\'':
                    postPos += 1

                if self.buf[postPos] in {'f', 'F'}:
                    if (self.buf[postPos] == '3') and (self.buf[postPos + 1] == '2'):
                        result.tokType = TTokType.tkFloat32Lit
                        postPos += 2
                    elif (self.buf[postPos] == '6') and (self.buf[postPos + 1] == '4'):
                        result.tokType = TTokType.tkFloat64Lit
                    elif (self.buf[postPos] == '1') and \
                        (self.buf[postPos + 1] == '2') and \
                        (self.buf[postPos] + 2 == '8'):
                        result.tokType = TTokType.tkFloat128Lit
                        postPos += 3
                    else:
                        result.tokType = TTokType.tkFloatLit
                elif self.buf[postPos] in {'d', 'D'}:
                    postPos += 1
                    result.tokType = TTokType.tkFloat64Lit
                elif self.buf[postPos] in {'i', 'I'}:
                    postPos += 1
                    if (self.buf[postPos] == '6') and (self.buf[postPos + 1] == '4'):
                        result.tokType = TTokType.tkInt64Lit
                        postPos += 2
                    elif (self.buf[postPos] == '3') and (self.buf[postPos + 1] == '2'):
                        result.tokType = TTokType.tkInt32Lit
                    elif (self.buf[postPos] == '1') and (self.buf[postPos + 1] == '6'):
                        result.tokType = TTokType.tkInt16Lit
                        postPos += 2
                    elif self.buf[postPos] == '8':
                        result.tokType = TTokType.tkInt8Lit
                        postPos += 1
                    else:
                        lexMessageLitNum("invalid number: '$1'", startpos)
                elif self.buf[postPos] in {'u', 'U'}:
                    postPos += 1
                    if (self.buf[postPos] == '6') and (self.buf[postPos + 1] == '4'):
                        result.tokType = TTokType.tkUInt64Lit
                        postPos += 2
                    elif (self.buf[postPos] == '3') and (self.buf[postPos + 1] == '2'):
                        result.tokType = TTokType.tkUInt32Lit
                        postPos += 2
                    elif (self.buf[postPos] == '1') and (self.buf[postPos + 1] == '6'):
                        result.tokType = TTokType.tkUInt16Lit
                        postPos += 2
                    elif (self.buf[postPos] == '8'):
                        result.tokType = TTokType.tkUInt8Lit
                        postPos += 1
                    else:
                        result.tokType = TTokType.tkUIntLit
                else:
                    lexMessageLitNum("invalid number: '$1'", startpos)
            
            # Is there still a literalish char awaiting? Then it's an error!
            if self.buf[postPos] in literalishChars or \
                 (self.buf[postPos] == '.' and self.buf[postPos + 1] in {countup('0', '9')}):
                lexMessageLitNum("invalid number: '$1'", startpos)
            
            # Third stage, extract actual number
            self.bufpos = startpos            # restore position
            pos = startpos
            try:
                if (self.buf[pos] == '0') and (self.buf[pos + 1] in baseCodeChars):
                    pos += 2
                    xi = 0

                    if self.buf[pos - 1] in {'b', 'B'}:
                        result.base = TNumericalBase.base2
                        while pos < endpos:
                            if self.buf[pos] != '_':
                                xi = (xi << 3) or (ord(self.buf[pos]) - ord('0'))
                            pos += 1
                    # 'c', 'C' is deprecated
                    elif self.buf[pos - 1] in {'o', 'c', 'C'}:
                        result.base = TNumericalBase.base8
                        while pos < endpos:
                            if self.buf[pos] != '_':
                                xi = (xi << 3) (ord(self.buf[pos]) - ord('0'))
                            pos += 1
                    elif self.buf[pos - 1] in {'x', 'X'}:
                        result.base = TNumericalBase.base16
                        while pos < endpos:
                            if self.buf[pos] == '_':
                                pos += 1
                            elif self.buf[pos] in {countup('0', '9')}:
                                xi = (xi << 4) or (ord(self.buf[pos]) - ord('0'))
                            elif self.buf[pos] in {countup('a', 'f')}:
                                xi = (xi << 4) or (ord(self.buf[pos]) - ord('a') + 10)
                            elif self.buf[pos] in {countup('A', 'F')}:
                                xi = (xi << 4) or (ord(self.buf[pos]) - ord('A') + 10)
                                pos += 1
                            else:
                                break
                    else:
                        raise Exception(self.config, self.getLineInfo(), 'getNumber')
            
            # TODO : type conversions
            # need to implement the following;
            # BiggestInt,
            # int8, toU8, int
            # int16, toU16
            # int32, toU32, int64
            # uint8, uint16, uint32

            except ValueError:
                lexMessageLitNum("invalid number: '$1'", startpos)
            except:
                lexMessageLitNum("number out of range: '$1'", startpos)
            

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
